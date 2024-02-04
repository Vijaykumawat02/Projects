#!/bin/python3
import socket
import sys
import threading

usage = "python3 scanner.py <target> <start_port> <end port>"

print("-"*100)
print("Python port scanner")
print("-"*100)

if(len(sys.argv) != 4):
	print(usage)
	sys.exit()

try:
	target = socket.gethostbyname(sys.argv[1])
except sockket.gaierror:
	print("Can not resolve host")
	sys.exit()
	
start_port = int(sys.argv[2])
end_port = int(sys.argv[3])

def port_scan(port):
	s = socket.socket()
	s.settimeout(2)
	conn = s.connect_ex((target, port))
	if(conn == 0):
		print("port {} is open".format(port))
	s.close()

for port in range(start_port, end_port+1):
	thread = threading.Thread(target = port_scan, args = (port,))
	thread.start()
