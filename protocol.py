

# Names for the header locations
P8_Code 			= slice(0, 8)	# 8 byte - last byte is version

P1_Type				= 8				# Check type of package

P1_State 			= 9				# Check state of sender

P1_ErrorType        = 10			# Error type

P4_Sequence 		= slice(12, 16)	# Packet sequence number
P4_AckSequence 		= slice(16, 20)	# Sequence number of packet to acknowledge
P8_TimeStamp 		= slice(20, 28)	# Timestamp of current packet
P2_TotalSize 		= slice(28, 30)	# Total packet size

## MASKS
# P1_Ctrl1 - 1 bit masks
b1_Ctrl 			= 0				# If set: Control - else: Data
b1_Ack 				= 1				# If set: Acknowlede - else: Normal
b1_AckCtrlData 		= 2				# If set: Control acknowledge - else: Data Acknowledge
b1_Encryption       = 3             # If set: Data encrypted

# P1_State
B1_Ping             = 0x01
B1_Pong             = 0x02
B1_Connect          = 0x03
B1_AcceptConn       = 0x04
B1_Disconnect       = 0x05
B1_RefuseConn       = 0x06
B1_Error            = 0x07

# P1_ErrorType
B1_ParallelConnect  = 0x01



