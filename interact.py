#!/usr/bin/env python

import argparse
import socket
import sys


BUFFER_SIZE = 64

def request(ip, port, message):
    success = False

    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    sock.connect((ip, port))

    # request
    sock.send(message)
    data = sock.recv(BUFFER_SIZE)

    if data and len(data) > 0:
        success = True
        print(data)

    # disconnect
    sock.close()

    return success

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Simple interaction with a TCP endpoint')
    PARSER.add_argument('-p', '--port', type=int, default=8080, help='port of the remote endpoint')
    PARSER.add_argument('-i', '--ip', default='127.0.0.1', help='IP of the remote endpoint')
    PARSER.add_argument('message', nargs='*', default=['persist'])

    ARGS = PARSER.parse_args()
    MESSAGE = ' '.join(ARGS.message)

    if not request(ARGS.ip, ARGS.port, MESSAGE):
        sys.exit(1)
