import threading, ntplib, socket
from pack import PacketOut

ACK_WAIT_TIME = 1.0

# Thread for sending the data packets. It sends the packet, get's into sleep for some time, checks
# if acknowledge has been received. If yes it exits, else it doubles the time to sleep and resends
# the packet. Does this until timeToSleep has reached 1 second.
class Client(threading.Thread):
    def __init__(self, message, application):
        self.application = application
        threading.Thread.__init__(self)
        self.message = message
        self.packet = PacketOut(self.message)   # Create new packet instance with the message
        self.application.dataSequence += 1
        # Take a copy of dataSequence because it may be changed the same time by other running
        # threads
        self.tmpDataSequence = self.application.dataSequence
        self.packet.setSequenceNumber(self.tmpDataSequence) # Set sequence number
        self.application.dataSeqForAckList.append(self.tmpDataSequence)  # Put it in the list for acknowledge
        if self.application.localEncryptionState == True:                # Check for encryption
            self.packet.encrypt(self.application.crypto)
            self.packet.setEncryption()
        # Create variables for counting the time
        self.timeToSleep = 0.01
        self.newTime = 0
        self.timestamp = self.oldTime = ntplib.time.time()
        self.packet.setTimeStamp(self.application.toNTPTime(self.timestamp)) # Set timestamp to the packet

    def run(self):
        # print('key: ' + app.key.decode('utf8'))
        print('Type: ' + str(type(self.application.key)))
        while True:
            try:
                self.application.serverSock.sendto(self.packet.getTotalPacket(), (self.application.currentIP,
                                                                         self.application.REMOTE_PORT))
                if self.application.DEBUG:
                    self.application.packetDebug(self.packet)
                ntplib.time.sleep(self.timeToSleep)
                self.timeToSleep *= 2
                if self.tmpDataSequence not in self.application.dataSeqForAckList:
                    # The server socket has found that an acknowledge is received and removed the
                    # sequence number from the list. So we exit.
                    break
                if self.newTime > ACK_WAIT_TIME:
                    # The "time out" has been reached so the packet won't be sent again
                    self.application.insert_text('Server ==> Unpredicted disconnection..')
                    self.application.status = 1
                    # self.application.statusRefresh()
                    break
            except socket.error as err:
                if err.errno == socket.errno.ENETUNREACH:
                    debugThread = self.application.setDebug('Network Unreachable')
                    debugThread.start()
                    self.application.status = 0
                    # self.application.statusRefresh()
            except socket.gaierror:
                debugThread = self.application.setDebug('Problem with DNS resolution')
                debugThread.start()
            except UnicodeError:
                debugThread = self.application.setDebug('Please provide a valid IP or hostname')
                debugThread.start()
            # Renewing the time to sleep
            timeLap = ntplib.time.time() - self.oldTime
            self.oldTime = ntplib.time.time()
            self.newTime += timeLap
