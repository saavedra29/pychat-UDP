from gui import MainWindow
import socket, threading, time, ntplib, datetime, errno, client
from pack import PacketOut, PacketIn


class setDebug(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message
    def run(self):
        timeText = time.strftime('%H:%M:%S ==> ')
        totalMessage = timeText + self.message
        app.debug_label.configure(text=totalMessage)
        time.sleep(5)
        app.debug_label.configure(text = '')

# Main application window
class AppWin(MainWindow):
    def __init__(self):
        MainWindow.__init__(self)
        self.DEBUG = False
        self.LOCAL_PORT = 50001
        self.REMOTE_PORT = 50001
        self.MAX_BYTES = 65535
        # Creating and starting server thread
        self.t1 = threading.Thread(target=self.server)
        self.t1.start()
        # Thread for showing always the current state (ONLINE, OFFLINE, CONNECTED)
        self.statusThread = threading.Thread(target=self.statusRefresh)
        self.statusThread.start()

        self.currentIP = ''
        self.dataSequence = 0   # Sequence number of current sending data packet
        # List with sequence numbers of data packet's sent that haven't yet been uknowledged
        self.dataSeqForAckList = []
        # Sequence numbers of data packets that have already been received at least once
        self.dataSeqList = []
        self.getTimeOffset()    # Create offset between the local machine and ntp time
        # Two substates according to who sent first connection requesting packet
        self.requestingConnection = False
        self.receivingConnection = False

        self.peerIsAlive = False

    # Cler lists every time a new session starts
    def clearSession(self):
        self.dataSeqForAckList = []
        self.dataSeqList = []

    # Set 'Debug = True' at the beginning of the file for some console debug
    def packetDebug(self, packet):
        print('------------------------')
        if type(packet) == PacketOut:
            print('--- Outgoing packet ----')
        else:
            print('--- Incoming packet ----')
        print()
        print('Data: ' + packet.getMessage())
        print('Control: ', end='')
        if packet.isControl(): print('Set')
        else: print('Unset')
        print('Acknowledge: ', end='')
        if packet.isAcknowledge(): print('Set')
        else: print('Unset')
        print('State: ' + packet.getState())
        print('Sequence: ' + str(packet.getSequenceNumber()))
        if packet.getState == 'pong': print('Pong packet!')
        elif packet.getState == 'ping': print('Ping packet!')
        timeStamp = packet.getTimeStamp()
        # print('Timestamp: ' + str(timeStamp))
        time = datetime.datetime.fromtimestamp(timeStamp)
        print(time.strftime('%H:%M:%S.%f')[:-2])
        print();print()

    # Key method for giving currentIP the entry value from the user
    def on_setPeer(self):
        if status == 0:
            if self.ipEntry.get() != '':
                self.currentIP = self.ipEntry.get()
                self.insert_text('Server ==> IP of hostname set!')
            else:
                self.insert_text('Server ==> Please enter IP or Hostname.')
        else:
            self.insert_text('Server ==> You have to stop the server in order to change'
                             ' IP/hostname.')

    # Function run when pressing the connect button. Checks if status == 1 and if yes
    # checks to see if remote peer is listening. If no one has requested a connection
    # we request first. Else we just accept the connection and change the status to 2
    def on_connect(self):
        global status
        if status == 0:
            self.insert_text('Server ==> You have to start the set IP/hostname and start '
                             'the server before connecting.')
            return
        elif status == 1:
            if self.peerAlive() == True:
                # receive - False / request - False
                if (self.receivingConnection == False) and (self.requestingConnection == False):
                    self.requestingConnection = True
                    self.insert_text('Server ==> Requesting a connection...')
                    # Create connection packet and send
                    self.sendPacket('connect')
                    return
                # receive - True / request - False
                elif (self.receivingConnection == True) and (self.requestingConnection == False):
                    # You connect
                    self.sendPacket('acceptConnect')
                    status = 2
                    self.clearSession()
                    self.statusRefresh()
                    self.insert_text('Server ==> You are connected.')
                    self.receivingConnection = False
                    return
            else:
                self.insert_text('Server ==> Remote peer doesn\'t respond')
                return
        else:
            return

    # Function run when pressing the disconnect button. If status is 1, and we received
    # a connection request we just REJECT it, else if we have requested a connection
    # we just ABORT it. If status is 2 then we return to status 1 (ONLINE) but not connected
    def on_disconnect(self):
        global status
        if status == 0:
            return
        elif status == 1:
            # request - False / accept - True
            if (self.requestingConnection == False) and (self.receivingConnection == True):
                self.sendPacket('disconnect')
                self.receivingConnection = False
                self.insert_text('Server ==> You rejected the connection.')
                return
            elif (self.requestingConnection == True) and (self.receivingConnection == False):
                self.requestingConnection = False
                self.sendPacket('disconnect')
                self.insert_text('Server ==> You aborted the connection.')
                return
            else:
                return
        else:
            self.sendPacket('disconnect')
            self.insert_text('Server ==> You disconnected.')
            status = 1
            self.statusRefresh()
            return

    # Function run when we press the "server/start" button
    def on_start_server(self):
        global status
        if status == 0:
            if self.currentIP == '':
                self.throw_error_win('You have to set a peer ip address or hostname first.')
            else:
                status = 1
                self.statusRefresh()

    # Function run when we press the "server/stop" button
    def on_stop_server(self):
        global status
        if (status == 2) or (status == 1):
            self.sendPacket('disconnect')
            self.receivingConnection = False
        status = 0
        self.statusRefresh()

    # Function run when we press enter on the input widget
    def on_enter_press(self, event):
        if (status == 0) or (status == 1):
            app.userInputEntry.delete(0, 'end')     # Delete whatever is inside the entry widget
            return
        else:
            inputText = app.userInputEntry.get()
            app.userInputEntry.delete(0, 'end')     # Delete whatever is inside the entry widget
            self.insert_text(inputText)     # Print the text in the text widget
            # Send the message to the remote peer
            t = client.Client(inputText, self)
            t.start()

    # Take local time and NTP time and get create an offset in seconds
    def getTimeOffset(self):
        try:
            c = ntplib.NTPClient()
            response = c.request('pool.ntp.org')
            ntpTime = response.tx_time
            localTime = time.time()
            self.offset = localTime - ntpTime
        except socket.gaierror:
            self.throw_error_win('Problem accessing NTP server, please check your internet'
                                 ' connection.')
            self.error_button.configure(command=self.on_exit)
            self.error_window.lift()

    # Takes local time and return NTP time
    def toNTPTime(self, time):
        return time - self.offset

    # Takes NTP time and returns local time
    def toLocalTime(self, time):
        return time + self.offset

    # Sends all kinds of Control (non data) packets. Type is required for any kind of packets.
    # error is required for "error" type packets and "packeForAck" is required for acknowledges
    def sendPacket(self, type, error=None, packetForAck=None):
        global status
        # Packet types:
        # 'connect', 'acceptConnect', 'disconnect', 'error', 'pong', 'acknowledge'
        packet = PacketOut()    # Create new packet instance
        packet.setControl()     # Make it control packet
        if type == 'acknowledge':
            packForAck = packetForAck   # Take from the parameters the actual packet to acknowledge
            packet.setAcknowledge()     # Make the sending packet of acknowledge type
            # Take the number to acknowledge and set it to the appropriate field
            packet.setAckSequenceNumber(packForAck.getSequenceNumber())
        elif type == 'error':
            packet.setState('error')
            packet.setError(error)
        elif type == 'connect':
            packet.setState('connect')
        elif type == 'acceptConnect':
            packet.setState('acceptConnect')
        elif type == 'disconnect':
            packet.setState('disconnect')
        elif type == 'pong':
            packet.setState('pong')
        else:
            raise Exception('Wrong type of packet to send..')

        # Add timestamp to every packet
        packet.setTimeStamp(app.toNTPTime(time.time()))
        try:
            self.serverSock.sendto(packet.getTotalPacket(), (self.currentIP, self.REMOTE_PORT))
        except socket.error as err:
            if err.errno == errno.ENETUNREACH:
                debugThread = setDebug('Network Unreachable')
                debugThread.start()
                status = 0
                self.statusRefresh()
        except socket.gaierror:
            debugThread = setDebug('Problem with DNS resolution')
            debugThread.start()
        except UnicodeError:
            debugThread = setDebug('Please provide a valid IP or hostname')
            debugThread.start()

        if self.DEBUG:
            self.packetDebug(packet)

    # Method runing as thread displaying current status
    def statusRefresh(self):
        self.offlineConf = {'text': 'Offline', 'foreground': 'red'}
        self.onlineConf = {'text': 'Online', 'foreground': 'orange'}
        self.connectedConf = {'text': 'Connected', 'foreground': 'green'}

        if status == 0:
            self.status_label.configure(self.offlineConf)
        elif status == 1:
            self.status_label.configure(self.onlineConf)
        else:
            self.status_label.configure(self.connectedConf)

    # Checks is remote peer is alive berore doing specific actions.
    # Changes peerIsAlive bollean accordingly
    def peerAlive(self):
        global status
        pingPacket = PacketOut()
        pingPacket.setControl()
        pingPacket.setState('ping')
        pingPacket.setTimeStamp(app.toNTPTime(time.time()))
        try:
            self.serverSock.sendto(pingPacket.getTotalPacket(), (self.currentIP, self.REMOTE_PORT))
        except socket.error as err:
            if err.errno == errno.ENETUNREACH:
                debugThread = setDebug('Network Unreachable')
                debugThread.start()
                status = 0
                self.statusRefresh()
        except socket.gaierror:
            debugThread = setDebug('Problem with DNS resolution')
            debugThread.start()
        except UnicodeError:
            debugThread = setDebug('Please provide a valid IP or hostname')
            debugThread.start()

        if self.DEBUG:
            self.packetDebug(pingPacket)
        time.sleep(1)
        if self.peerIsAlive:
            self.peerIsAlive = False
            return True
        else:
            return False

    # The server thread-method. Binds the local IP and port 50001 to the socket and enters a loop.
    # Takes the data and checks if the first 8 bytes are the string 'odyaris1'. Then acts
    # according to the status. If status is 0 simply sends 'disconnect' packet on every 'accept'
    # packet it arrives. Ignores any other packet. Case of status 1 and 2 are commented below.
    def server(self):
        global status
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind(('', self.LOCAL_PORT))
        while True:
            data, address = self.serverSock.recvfrom(self.MAX_BYTES)
            packet = PacketIn(data)
            if self.DEBUG:
                self.packetDebug(packet)
            if packet.getProtoCode() != 'odyaris1':
                continue

            if status == 0:
                if packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'connect'):
                    self.sendPacket('disconnect')

            elif status == 1:
                # If it's "error" packet and the error is "parallelConnect" means that the
                # remote peer sent a "connect" packet and insted of "acceptConnect" or "disconnect"
                # received again "connect" packet. This preventes from forever waiting loop.
                if packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'error'):
                    if packet.getError() == 'parallelConnect':
                        self.sendPacket('disconnect')
                        self.requestingConnection = False
                        self.insert_text('Server ==> Parallel connection Error,'
                                         ' please try again..')

                # If it's "connect" packet and we haven't already sent anything it means the
                # peer is requesting connection. So the local user is informed and
                # receiving connection is becoming True.
                # If requestingConnection is True then it means we've send already a "connect"
                # packet so except "disconnect" or "acceptConnect". So now we have "parallel
                # connection" error. We send the appropriate error packet and set
                # requestingConnection to False.
                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'connect'):
                    if (self.requestingConnection == False) and \
                            (self.receivingConnection == False):
                        self.receivingConnection = True
                        self.insert_text('Server ==> Peer ' + str(self.currentIP) +
                                         ' wants to connect.')
                    elif (self.requestingConnection == True) and \
                            (self.receivingConnection == False):
                        self.sendPacket('disconnect')
                        self.requestingConnection = False
                        self.sendPacket('error', error='parallelConnect')
                        self.insert_text('Server ==> Parallel connection Error.'
                                         ' Please try again..')

                # If it's "acceptConnect" packet and have already requested a connection
                # we go to status 2 and begin the connection.
                elif packet.isControl and not packet.isAcknowledge() and \
                        (packet.getState() == 'acceptConnect'):
                    if (self.requestingConnection == True) and \
                            (self.receivingConnection == False):
                        self.requestingConnection = False
                        self.insert_text('Server ==> Connection started!')
                        status = 2
                        self.clearSession()
                        self.statusRefresh()

                # If it's "disconnect" packet then if we had requested connection the request
                # is refused and we turn requestingConnection back to False.
                # Else if a "request" had been sent by the remote peer it means it aborts the
                # connection request. receivingConnection is set back to False.
                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'disconnect'):
                    if (self.requestingConnection == True) and \
                            (self.receivingConnection == False):
                        self.requestingConnection = False
                        self.insert_text('Server ==> Connection refused.')
                    elif (self.requestingConnection == False) and \
                            (self.receivingConnection == True):
                        self.receivingConnection = False
                        self.insert_text('Server ==> Connection aborted from remote peer.')

                # If packet is "pong" then set peerIsAlive to True. It's used by peerAlive().
                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'pong'):
                    self.peerIsAlive = True
                # If packet is ping send pong
                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'ping'):
                    self.sendPacket('pong')

            else:
                # Status is 2 (connected)
                if packet.isControl():
                    # If it's acknowledge get the sequence number of the packet it acknowledges
                    # and remove it from the list
                    if packet.isAcknowledge():
                        ack = packet.getAckSequenceNumber()
                        if len(self.dataSeqForAckList) is not 0:
                            if ack in self.dataSeqForAckList:
                                self.dataSeqForAckList.remove(ack)

                    # If the packet is "disconnect" change status to 1
                    elif packet.getState() == 'disconnect':
                        self.insert_text('Server ==> Remote peer disconnected.')
                        status = 1
                        self.statusRefresh()

                    # If the packet is "connect" and the ip is the same as when you first
                    # connected clear the session and send "acceptConnect".
                    # Continue connection like nothing happened.
                    elif (packet.getState() == 'connect') and (address[0] == self.currentIP):
                        self.sendPacket('acceptConnect')
                        self.clearSession()

                    elif packet.getState() == 'ping':
                        self.sendPacket('pong')
                else:
                    # If the packet is data, if it's been received before ignore it, else
                    # append it to dataSeqList, send acknowledge and print the message
                    seq = packet.getSequenceNumber()
                    if seq in self.dataSeqList:
                        continue
                    else:
                        self.dataSeqList.append(seq)
                        self.sendPacket('acknowledge', packetForAck=packet)
                        message = packet.getMessage()
                        self.insert_text('Peer ==> ' + message)





if __name__ == "__main__":
    status = 0  # 0 offline, 1 online, 2 connected

    # Create gui
    app = AppWin()
    app.mainloop()
