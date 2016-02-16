==========
Pychat-UDP
==========

|demo|

Description
~~~~~~~~~~~

    Chat client and server for two peers based on UDP and using 
    a custom protocol above UDP for creating connections and 
    ankowledment for the packets containing the chat messages.
    It can use message encryption on any side if selected. The
    application uses threads and is decentralized since every
    peer acts as server and client at the same time.

Dependencies
~~~~~~~~~~~~
    
    * tkinter 
    * cryptography
    * ntplib

Usage
~~~~~

    #. Set remote peer as a hostname or ip address
    #. Click on Server and select start
    #. Wait for remote peer to ask for connection or press connect to request connection
    #. On Encryption you can generate a new key or set the key taken from the remote peer in order to send encrypted data

.. |demo| image:: http://s20.postimg.org/9vvlj2dvx/udp_Chat.png

