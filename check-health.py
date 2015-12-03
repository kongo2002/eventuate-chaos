#!/usr/bin/env python

import socket
import sys


TCP_IP = '127.0.0.1'
TCP_PORT = 8080
BUFFER_SIZE = 64
MESSAGE = "persist"

def request(message=MESSAGE):
    # connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    # request
    s.send(message)
    data = s.recv(BUFFER_SIZE)

    if data:
        print(data)

    # disconnect
    s.close()

    try:
        return int(data) > 0
    except ValueError:
        return False

if __name__ == '__main__':
    message = MESSAGE if len(sys.argv) < 2 else sys.argv[1]
    if not request(message):
        sys.exit(1)
