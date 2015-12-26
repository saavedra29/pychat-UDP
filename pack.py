"""
This file contains 2 kinds of packets - input and output
Constructors:
	Input packet: Takes byte type object directy from the socket
	Output packet: Takes a string for message else takes message calling setMessage()

Methods contained on BOTH Input and Output packets (getters):
	getHeader() 			====>	Returns header as <bytes>
	getMessage() 			====>	Returns message as <string>
	isControl()				====>	Returns True if it is a Control packet - False if it is Data packet
	isAcknowledge()			====>	Returns True if it is an Acknowledge packet - False for Normal packet
	isControlAcknowledge()	====> 	Returns True if it is Acknowledge for Control packet else False if
									it is for Data packet
	isEncrypted()           ====>   Returns True if the packet is encrypted or else False
	getState()				====>	Returns a state: 'ping', 'pong', 'connect', 'acceptConnect',
	'disconnect', 'refuseConnect', 'error' as <string> else just empty <string>
	getSequenceNumber()		====>	Returns the sequence number of the packet as 4 byte <integer>
	getAckSequenceNumber()  ====>	Returns the sequence number of the packet to acknowledge if any as 4 byte <integer>
	getTimeStamp()			====>	Returns the timestamp of the current packet as a 4 byte <float>


Methods contained ONLY in Output packets (setters):
	getTotalPackage()		====>	Special method, returns the whole packet as <bytes> in order to pass
									it straight to the socket
	setHeader(bytes)		====>	"Brutal" way to set header. Takes <bytes> or <bytearray>
	setMessage(string)		====>	Takes <string> to set the packet message
	setControl()			====>	Make the packet of Control type
	setAcknowledge()		====>	Make the packet Acknowledge packet
	setControlAcknowledge()	====>	Make the packet Acknowledge for Control type packet
	setState(string)		====>	Takes a <string> to set state: 'ping', 'pong', 'connect',
	'acceptConnect', 'disconnect', 'refuseConnect', 'error'
	setSequenceNumber(int)	====>	Takes an <int> to set the packet's sequence number
	setAckSequenceNumber(int) ==>	If Ack packet, takes an <int> to set the sequence number of the packet to acknowledge
	setTimeStamp(int)		====>	Takes <float> to set the packet's timestamp
	setTotalSize()			====> 	Set's the packet's total size. YOU'LL NEVER NEED TO CALL THIS.
	encrypt(crypto)         ====>   Takes a cryptography (Fernet) object and returns the encrypted token

Method contained ONLY in Input packets:
	getTotalSize()			====>	Return the total size of the packet in bytes 1 - 65556 as <unsigned short>
	getProtoCode()			====>	Returns the first 8 bytes of the header as <string>

"""

import struct
import protocol as pro
from cryptography import fernet

HEADER_SIZE = 32
PROTOCODE = b'odyaris1'


##### INPUT PACKET
class PacketIn:
    def __init__(self, incomingPacket):
        self.totalPacket = incomingPacket
        self.header = self.totalPacket[0:HEADER_SIZE]
        self.message = self.totalPacket[HEADER_SIZE:]

    # Getters
    def getHeader(self):
        return self.header

    def getMessage(self):
        messageOut = self.message.decode('utf8')
        return messageOut

    def isControl(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_Ctrl):
            return True
        else:
            return False

    def isAcknowledge(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_Ack):
            return True
        else:
            return False

    def isControlAcknowledge(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_AckCtrlData):
            return True
        else:
            return False

    def isEncrypted(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_Encryption):
            return True
        else:
            return False

    def getState(self):
        if self.header[pro.P1_State] == pro.B1_Ping:
            return 'ping'
        elif self.header[pro.P1_State] == pro.B1_Pong:
            return 'pong'
        elif self.header[pro.P1_State] == pro.B1_Connect:
            return 'connect'
        elif self.header[pro.P1_State] == pro.B1_AcceptConn:
            return 'acceptConnect'
        elif self.header[pro.P1_State] == pro.B1_Disconnect:
            return 'disconnect'
        elif self.header[pro.P1_State] == pro.B1_RefuseConn:
            return 'refuseConnect'
        elif self.header[pro.P1_State] == pro.B1_Error:
            return 'error'
        else:
            return ''

    def getError(self):
        if self.header[pro.P1_ErrorType] == pro.B1_ParallelConnect:
            return 'parallelConnect'
        elif self.header[pro.P1_ErrorType] == pro.B1_WrongEncryptionKey:
            return 'wrongEncryptionKey'
        else:
            return ''

    def getSequenceNumber(self):
        unpackedSequence = struct.unpack('I', self.header[pro.P4_Sequence])
        return unpackedSequence[0]

    def getAckSequenceNumber(self):
        ackSequence = struct.unpack('I', self.header[pro.P4_AckSequence])
        return ackSequence[0]

    def getTimeStamp(self):
        timeStamp = struct.unpack('d', self.header[pro.P8_TimeStamp])
        return timeStamp[0]

    def getTotalSize(self):
        totalSize = struct.unpack('H', self.header[pro.P2_TotalSize])
        return totalSize[0]

    def getProtoCode(self):
        code = self.header[pro.P8_Code].decode('utf8')
        return code

    def decrypt(self, cryptoObject):
        self.message = cryptoObject.decrypt(self.message)


##### OUTPUT PACKET
class PacketOut:
    def __init__(self, message=''):
        self.message = bytes(message, 'utf8')
        self.header = bytearray(HEADER_SIZE)
        self.header[pro.P8_Code] = PROTOCODE

    def getTotalPacket(self):  # Method to send data!!!
        self.totalPacket = self.header + self.message
        self.setTotalSize()
        return self.totalPacket

    # Setters
    def setHeader(self, header):  # Takes type byteArray
        self.header = header

    def setMessage(self, msg):  # Takes type string
        self.message = bytes(msg, 'utf8')

    def setControl(self):  # Set the control bit
        self.header[pro.P1_Type] |= 1 << pro.b1_Ctrl

    def setAcknowledge(self):  # Set the acknowledge bit
        self.header[pro.P1_Type] |= 1 << pro.b1_Ack

    def setControlAcknowledge(self):  # Set the control acknowledge bit
        self.header[pro.P1_Type] |= 1 << pro.b1_AckCtrlData

    def setState(self, state):  # Set state: 'error', 'pong', 'disconnect'
        if state == 'ping':
            self.header[pro.P1_State] = pro.B1_Ping
        elif state == 'pong':
            self.header[pro.P1_State] = pro.B1_Pong
        elif state == 'connect':
            self.header[pro.P1_State] = pro.B1_Connect
        elif state == 'acceptConnect':
            self.header[pro.P1_State] = pro.B1_AcceptConn
        elif state == 'disconnect':
            self.header[pro.P1_State] = pro.B1_Disconnect
        elif state == 'refuseConnect':
            self.header[pro.P1_State] = pro.B1_RefuseConn
        elif state == 'error':
            self.header[pro.P1_State] = pro.B1_Error
        else:
            raise Exception("Wrong state inserted")

    def setError(self, error):
        if error == 'parallelConnect':
            self.header[pro.P1_ErrorType] = pro.B1_ParallelConnect
        elif error == 'wrongEncryptionKey':
            self.header[pro.P1_ErrorType] = pro.B1_WrongEncryptionKey
        else:
            raise Exception('Wrong error inserted')

    def setSequenceNumber(self, seqNumber):  # Set sequence number (int)
        sequenceNumber = struct.pack('I', seqNumber)
        self.header[pro.P4_Sequence] = sequenceNumber

    def setAckSequenceNumber(self, acknowledgeSeqNumber):  # Set acknowledge sequence number (int)
        acknowledgeSequenceNumber = struct.pack('I', acknowledgeSeqNumber)
        self.header[pro.P4_AckSequence] = acknowledgeSequenceNumber

    def setTimeStamp(self, tmStamp):  # Set timestamp (float)
        timeStamp = struct.pack('d', tmStamp)
        self.header[pro.P8_TimeStamp] = timeStamp

    def setTotalSize(self):
        self.totalPacket[pro.P2_TotalSize] = struct.pack('H', len(self.totalPacket))

    def setEncryption(self):
        self.header[pro.P1_Type] |= 1 << pro.b1_Encryption


    # Getters
    def getHeader(self):
        return self.header

    def getMessage(self):
        messageOut = self.message.decode('utf8')
        return messageOut

    def isControl(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_Ctrl):
            return True
        else:
            return False

    def isAcknowledge(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_Ack):
            return True
        else:
            return False

    def isControlAcknowledge(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_AckCtrlData):
            return True
        else:
            return False

    def isEncrypted(self):
        if self.header[pro.P1_Type] & (1 << pro.b1_Encryption):
            return True
        else:
            return False

    def getState(self):
        if self.header[pro.P1_State] == pro.B1_Ping:
            return 'ping'
        elif self.header[pro.P1_State] == pro.B1_Pong:
            return 'pong'
        elif self.header[pro.P1_State] == pro.B1_Connect:
            return 'connect'
        elif self.header[pro.P1_State] == pro.B1_AcceptConn:
            return 'acceptConnect'
        elif self.header[pro.P1_State] == pro.B1_Disconnect:
            return 'disconnect'
        elif self.header[pro.P1_State] == pro.B1_RefuseConn:
            return 'refuseConnect'
        elif self.header[pro.P1_State] == pro.B1_Error:
            return 'error'
        else:
            return ''

    def getSequenceNumber(self):
        sequence = struct.unpack('I', self.header[pro.P4_Sequence])
        return sequence[0]

    def getAckSequenceNumber(self):
        ackSequence = struct.unpack('I', self.header[pro.P4_AckSequence])
        return ackSequence[0]

    def getTimeStamp(self):
        timeStamp = struct.unpack('d', self.header[pro.P8_TimeStamp])
        return timeStamp[0]

    def encrypt(self, cryptoObject):
        self.message = cryptoObject.encrypt(self.message)

