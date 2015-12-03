from gui import MainWindow
import socket, threading, time, ntplib, datetime, errno
from pack import PacketOut, PacketIn

LOCAL_PORT = 50001
REMOTE_PORT = 50001
MAX_BYTES = 65535
ACK_WAIT_TIME = 1.0
DEBUG = False


class AppWin(MainWindow):
    def __init__(self):
        MainWindow.__init__(self)
        # Creating server thread
        self.t1 = threading.Thread(target=self.server)
        self.t1.start()  # Starting the server thread
        self.statusThread = threading.Thread(target=self.statusRefresh)
        self.statusThread.start()

        self.currentIP = ''
        self.dataSequence = 0  # Sequence number for sending data packets
        self.dataSeqForAckList = []
        self.dataSeqList = []
        self.lostPackets = 0  # Total number of lost packets
        self.getTimeOffset()  # Create offset for time synchronization
        self.requestingConnection = False
        self.acceptingConnection = False
        self.peerIsAlive = False

    def clearSession(self):
        self.dataSeqForAckList = []
        self.dataSeqList = []

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

    def setDebug(self, message):
        timeText = time.strftime('%H:%M:%S ==> ')
        totalMessage = timeText + message
        self.debug_label.configure(text=totalMessage)

    def on_setPeer(self):
        if status == 0:
            self.currentIP = self.ipEntry.get()
            self.insert_text('Server ==> IP of hostname set!')
        else:
            self.insert_text('Server ==> You have to stop the server in order to change'
                             ' IP/hostname.')

    # Connect button function
    def on_connect(self):
        global status
        if status == 0:
            return
        elif status == 1:
            if self.peerAlive() == True:
                # accept - False / request - False
                if (self.acceptingConnection == False) and (self.requestingConnection == False):
                    self.requestingConnection = True
                    self.insert_text('Server ==> Requesting a connection...')
                    # Create connection packet and send
                    self.sendPacket('connect')
                    return
                # accept - True / request - False
                elif (self.acceptingConnection == True) and (self.requestingConnection == False):
                    # You connect
                    self.sendPacket('acceptConnect')
                    status = 2
                    self.clearSession()
                    self.statusRefresh()
                    self.insert_text('Server ==> You are connected.')
                    self.acceptingConnection = False
                    return
            else:
                self.insert_text('Server ==> Remote peer doesn\'t respond')
                return
        else:
            return

    # Disonnect button function
    def on_disconnect(self):
        global status
        if status == 0:
            return
        elif status == 1:
            # request - False / accept - True
            if (self.requestingConnection == False) and (self.acceptingConnection == True):
                self.sendPacket('disconnect')
                self.acceptingConnection = False
                self.insert_text('Server ==> You rejected the connection.')
                return
            elif (self.requestingConnection == True) and (self.acceptingConnection == False):
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

    def on_start_server(self):
        global status
        if status == 0:
            if self.currentIP == '':
                self.throw_error_win('You have to set a peer ip address or hostname first.')
            else:
                status = 1
                self.statusRefresh()

    def on_stop_server(self):
        global status
        if (status == 2) or (status == 1):
            self.sendPacket('disconnect')
            self.acceptingConnection = False
        status = 0
        self.statusRefresh()

    # Send_data function
    def on_enter_press(self, event):
        if (status == 0) or (status == 1):
            app.userInputEntry.delete(0, 'end')
            return
        else:
            inputText = app.userInputEntry.get()
            app.userInputEntry.delete(0, 'end')
            self.insert_text(inputText)
            t = client(inputText)
            t.start()

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

    def toNTPTime(self, time):
        return time - self.offset

    def toLocalTime(self, time):
        return time + self.offset


    def sendPacket(self, type, error=None, packetForAck=None):
        # 'connect', 'acceptConnect', 'disconnect', 'error', 'pong', 'acknowledge'
        packet = PacketOut()
        packet.setControl()
        if type == 'acknowledge':
            packForAck = packetForAck
            packet.setAcknowledge()
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

        packet.setTimeStamp(app.toNTPTime(time.time()))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(packet.getTotalPacket(), (self.currentIP, REMOTE_PORT))
            sock.close()
        except socket.error as err:
            if err.errno == errno.ENETUNREACH:
                self.setDebug('Network Unreachable.')
        except socket.gaierror:
            self.setDebug('Problem with DNS resolution')
        except UnicodeError:
            self.setDebug('Please provide a valid IP or hostname.')

        if DEBUG:
            self.packetDebug(packet)

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

    def peerAlive(self):
        pingPacket = PacketOut()
        pingPacket.setControl()
        pingPacket.setState('ping')
        pingPacket.setTimeStamp(app.toNTPTime(time.time()))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(pingPacket.getTotalPacket(), (self.currentIP, REMOTE_PORT))
            sock.close()
        except socket.error as err:
            if err.errno == errno.ENETUNREACH:
                self.setDebug('Network Unreachable.')
        except socket.gaierror:
            self.setDebug('Problem with DNS resolution')
        except UnicodeError:
            self.setDebug('Please provide a valid IP or hostname.')

        if DEBUG:
            self.packetDebug(pingPacket)
        time.sleep(1)
        if self.peerIsAlive:
            self.peerIsAlive = False
            return True
        else:
            return False

    def server(self):
        global status
        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSock.bind(('', LOCAL_PORT))
        while True:
            data, address = self.serverSock.recvfrom(MAX_BYTES)
            packet = PacketIn(data)
            if DEBUG:
                self.packetDebug(packet)
            if packet.getProtoCode() != 'odyaris1':
                continue

            if status == 0:
                if packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'connect'):
                    self.sendPacket('disconnect')

            elif status == 1:
                if packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'error'):
                    if packet.getError() == 'parallelConnect':
                        self.sendPacket('disconnect')
                        self.requestingConnection = False
                        self.insert_text('Server ==> Parallel connection Error, please try again..')

                # Request or accept connection
                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'connect'):
                    if (self.requestingConnection == False) and \
                            (self.acceptingConnection == False):
                        self.acceptingConnection = True
                        self.insert_text('Server ==> Peer ' + str(self.currentIP) +
                                         ' wants to connect.')
                    elif (self.requestingConnection == True) and \
                            (self.acceptingConnection == False):
                        # Send error - both requesting connection
                        self.sendPacket('disconnect')
                        self.requestingConnection = False
                        self.sendPacket('error', error='parallelConnect')
                        self.insert_text('Server ==> Parallel connection Error. Please try again..')

                elif packet.isControl and not packet.isAcknowledge() and \
                        (packet.getState() == 'acceptConnect'):
                    if (self.requestingConnection == True) and \
                            (self.acceptingConnection == False):
                        self.requestingConnection = False
                        self.insert_text('Server ==> Connection started!')
                        status = 2
                        self.clearSession()
                        self.statusRefresh()

                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'disconnect'):
                    if (self.requestingConnection == True) and \
                            (self.acceptingConnection == False):
                        self.requestingConnection = False
                        self.insert_text('Server ==> Connection refused.')
                    elif (self.requestingConnection == False) and \
                            (self.acceptingConnection == True):
                        self.acceptingConnection = False
                        self.insert_text('Server ==> Connection aborted from remote peer.')

                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'pong'):
                    self.peerIsAlive = True

                elif packet.isControl() and not packet.isAcknowledge() and \
                        (packet.getState() == 'ping'):
                    self.sendPacket('pong')

            else:
                # Receiving messages
                if packet.isControl():
                    if packet.isAcknowledge():
                        ack = packet.getAckSequenceNumber()
                        if len(self.dataSeqForAckList) is not 0:
                            if ack in self.dataSeqForAckList:
                                self.dataSeqForAckList.remove(ack)

                    elif packet.getState() == 'disconnect':
                        self.insert_text('Server ==> Remote peer disconnected.')
                        status = 1
                        self.statusRefresh()

                    elif (packet.getState() == 'connect') and (address[0] == self.currentIP):
                        self.sendPacket('acceptConnect')
                        self.clearSession()

                    elif packet.getState() == 'ping':
                        self.sendPacket('pong')
                else:
                    # packet is data
                    seq = packet.getSequenceNumber()
                    if seq in self.dataSeqList:
                        continue
                    else:
                        self.dataSeqList.append(seq)
                        self.sendPacket('acknowledge', packetForAck=packet)
                        message = packet.getMessage()
                        self.insert_text('Peer ==> ' + message)


class client(threading.Thread):
    def __init__(self, message):
        threading.Thread.__init__(self)
        self.message = message
        self.packet = PacketOut(self.message)
        app.dataSequence += 1
        self.ourDataSequence = app.dataSequence
        self.packet.setSequenceNumber(self.ourDataSequence)
        app.dataSeqForAckList.append(self.ourDataSequence)
        self.timeToSleep = 0.01
        self.newTime = 0
        self.timestamp = self.oldTime = time.time()
        self.packet.setTimeStamp(app.toNTPTime(self.timestamp))

    def run(self):
        global status
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(self.packet.getTotalPacket(), (app.currentIP, REMOTE_PORT))
                if DEBUG:
                    app.packetDebug(self.packet)
                time.sleep(self.timeToSleep)
                self.timeToSleep *= 2
                if self.ourDataSequence not in app.dataSeqForAckList:
                    sock.close()
                    break
                if self.newTime > ACK_WAIT_TIME:
                    sock.close()
                    app.insert_text('Server ==> Unpredicted disconnection..')
                    status = 1
                    app.statusRefresh()
                    break
            except socket.error as err:
                if err.errno == errno.ENETUNREACH:
                    app.setDebug('Network Unreachable.')
            except socket.gaierror:
                app.setDebug('Problem with DNS resolution')
            except UnicodeError:
                app.setDebug('Please provide a valid IP or hostname.')

            timeLap = time.time() - self.oldTime
            self.oldTime = time.time()
            self.newTime += timeLap


if __name__ == "__main__":
    status = 0  # 0 offline, 1 online, 2 connected

    # Create gui
    app = AppWin()
    app.mainloop()
