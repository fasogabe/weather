#!/usr/bin/env python

# proxy_server.py
# Fabian Gaspero-Beckstrom


'''
    This is a simple http proxy server using the socket module from the python
    standard library. It runs a seperate file, weather_data, to produce a svg
    file in the current directory.

    To test, run this program with any port number (such as 8888). When it is
    ready to serve, open a browser and access the svg file by using the
    following format:

            localhost:<server_port>/<filename>.svg

    Currently, weather_data creates a file called temps.svg.
'''

from socket import *
import sys
import os
import thread
import waether_data

# Constants
BACKLOG = 1
BUFF_SIZE = 1024
DEF_PORT = 80
_debug = True

def main():

	if len(sys.argv) < 2: # Verify command line usage
		print 'Usage: "python proxy_server.py server_port"\n'
		sys.exit(2)

	weather_data.main()

	# Set ip address and port number
	proxy_host = ''
	proxy_port = int(sys.argv[1])
	try:
		# Create a server socket
		tcpSerSock = socket(AF_INET, SOCK_STREAM)

		# Bind socket to port and start listening
		tcpSerSock.bind((proxy_host, proxy_port))
		tcpSerSock.listen(BACKLOG)

	# Error handling for socket error
	except error, (value, message):
		if tcpSerSock:
			tcpSerSock.close()
		print 'Error:', message
		sys.exit(1)

	print 'Proxy up and running on port', proxy_port
	print '\nReady to serve...\n'

	while 1:
		# Listen for connection requests
		client_socket, addr = tcpSerSock.accept()
		print 'Connection received from IP:', addr[0], 'Port:', addr[1], '\n'

		# Start proxy thread upon request
		thread.start_new_thread(proxy_thread,(client_socket, addr))

	tcpSerSock.close()

def proxy_thread(client_socket, addr):

	# Receive message
	message = client_socket.recv(BUFF_SIZE)
	# Split message
	lines = message.split('\n')
	url = lines[0].split()[1]

	# DEBUG
	if _debug:
		print 'MSG:' + message + '\n'
		print 'LINES:', lines
		print 'URL:' + url + '\n'

	# Parse line to find requested address
	i = url.find("://")
	if i == -1:
		address = url
	else:
		address = url[(i+3):]

	# Check cache for hit
	hit = check_cache(client_socket, address)

	if (~hit):
		# Locate path and/or port delimiters
		j = address.find("/")
		k = address.find(":")

		# Bypass first slash
		if j == 0:
			address = address[1:]
			j = address.find("/")
			if j == -1:
				j = len(address)

		# DEBUG
		if _debug:
			print address + '\n'

		# Set hostname and port number
		hostname = ""
		port = DEF_PORT
		if k == -1 or j < k:
			hostname = address[:j]
		else:
			port = int((address[(k+1):])[:j-k-1])
			hostname = address[:k]

		print 'Host Name:', hostname
		print 'Port:', port

		# Create socket
		c = socket(AF_INET, SOCK_STREAM)

		try:
			# Connect to the socket to port 80 (or specified port)
			c.connect((hostname, port))

			print 'Conectection established'

			# Create a temporary file on this socket and ask port 80 for the file requested by the client
			fileobj = c.makefile('r', 0)
			ver = lines[0].split()[2]
			request = "GET http://" + address + " " + ver + "\n" + "Host:" + hostname + "\r\n"
			for line in lines[2:]:
				if line[:7] != 'Cookie':
					request = request + line + "\n"

			# Write request to file
			fileobj.write(request)

			# DEBUG
			if _debug:
				print 'REQUEST: ' + request + '\n'
		except error, (value,message):
			print 'Error:', message
			if c:
				c.close()
				sys.exit(0)

		while 1:

			# Read the response into buffer
			response_buff = c.recv(BUFF_SIZE)

			if len(response_buff) > 0:
				# Create a new file in the cache for the requested file.
				try:
					temp = open("./" + address, "wb")
					for data in response_buff:
						temp.write(data)
				except IOError:
					print 'File could not be written'
					if c:
						c.close()
						sys.exit(0)

				# DEBUG
				if _debug:
					print 'WRITTEN:' + response_buff

				# Also send the response in the buffer to client socket and the corresponding file in the cache
				client_socket.send(response_buff)

			else:
				break

		# Close socket
		c.close()


	if client_socket:
		client_socket.close()
		sys.exit(0)


def check_cache(client_socket, address):
	fileExist = False
	try:
		# Check wether the file exists in the cache
		f = open(address[1:], "r")
		outputdata = f.readlines()
		fileExist = True
		print 'File found in cache\n'
		# ProxyServer finds a cache hit and generates a response message
		client_socket.send("HTTP/1.1 200 OK\r\n")
		client_socket.send("Content-Type:text/html\r\n")
		for i in range(0, len(outputdata)):
			client_socket.send(outputdata[i])
		print 'Successfully sent\n'
	# Error handling for file not found in cache
	except IOError:
		print 'File not found in cache\n'
	return fileExist






main()


