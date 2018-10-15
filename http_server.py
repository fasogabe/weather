#!/usr/bin/env python

# http_server.py
# Fabian Gaspero-Beckstrom

'''
    This is a simple http server using the socket module from the python
    standard library. It runs a seperate file, weather_data, to produce
    a svg file in the current directory.

    To test, run this program with localhost as the server_ip argument
    and any port number (such as 8888). When it is ready to serve, open
    a browser and access the svg file by using the following format:

            <server_ip>:<server_port>/<filename>.svg

    Currently, weather_data creates a file called temps.svg.
'''


from socket import *
import sys
import thread
import os
import weather_data

# Constants
BACKLOG = 1
BUFF_SIZE = 1024
_debug = True

def main():
    if len(sys.argv) <= 2: # Verify command line usage
        print 'Usage: "python http_server.py server_ip server_port"\n'
        sys.exit(2)

    weather_data.main()

    # Set host ip and port to command line arguments
    if sys.argv[1] == 'localhost':
        server_host = ''
    else:
        server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    try:
        # Create server socket
        serverSock = socket(AF_INET, SOCK_STREAM)

        # Prepare server socket
        serverSock.bind((server_host, server_port))
        serverSock.listen(BACKLOG)

    # Error handling
    except error, (value, message):
        if serverSock:
            serverSock.close()
        print 'Error:', message
        sys.exit(1)

    print 'Server up and running \nHost IP:', server_host, ' Port:', server_port

    while 1:
        print '\nReady to serve...'
        # Accept a connection
        clientSock, addr = serverSock.accept()
        print '\nConnection received from IP:', addr[0], ' Port:', addr[1]
        # Start new thread upon request
        thread.start_new_thread(sockThread,(clientSock, addr))

    #Close server socket
    serverSocket.close()

def sockThread(clientSock, addr):

    # Receive message
    message = clientSock.recv(BUFF_SIZE)

    # Parse message
    filename = message.split()[1]
    outputdata = ""
    try:
        # Open file
        f = open(filename[1:])
        outputdata = f.readlines()

        if _debug:
            print message + '\n'

    except IOError:
        #Send response message for file not found
        clientSock.send('404 Not Found')
        clientSock.close()
        sys.exit(0)

    try:
        #Send one HTTP header line into socket
        clientSock.send('HTTP/1.0 200 OK\r\n\r\n')

        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            clientSock.send(outputdata[i])

        print 'File transmission successful.\n\n'

    except error, (value, message):
        print 'Error:', message

    #Close client socket
    clientSock.close()



main()
