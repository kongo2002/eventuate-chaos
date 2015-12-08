#!/usr/bin/env python

import argparse
import socket
import sys
import time
import threading
import random


BUFFER_SIZE = 64

class SetWorker(threading.Thread):
    def __init__(self, host, nodes, get_op, operations=None, interval=0.5):
        threading.Thread.__init__(self)

        self.host = host
        self.nodes = nodes
        self.operations = operations
        self.interval = interval
        self.is_cancelled = False
        self.get_op = get_op

    def run(self):
        ports = self.nodes.values()

        while (self.operations is None or self.operations > 0) and not self.is_cancelled:
            if self.operations:
                self.operations -= 1

            port = random.choice(ports)
            request(self.host, port, self.get_op())

            time.sleep(self.interval)

    def cancel(self):
        self.is_cancelled = True

def request(ip, port, message):
    # connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    sock.connect((ip, port))

    # request
    sock.send(message)
    data = []

    try:
        while True:
            received = sock.recv(BUFFER_SIZE)
            if not received:
                break
            data.append(received)
    except socket.timeout:
        pass
    finally:
        # disconnect
        sock.close()
    return ''.join(data)

def is_healthy(ip, port, message, verbose=True):
    try:
        data = request(ip, port, message)
    except socket.error:
        return False

    if data and len(data) > 0:
        if verbose:
            print(data)
        return True
    return False

def wait_to_be_running(host, nodes):
    print('Waiting for %d nodes to be up and running' % (len(nodes)))
    while True:
        all_running = all(is_healthy(host, port, 'get', False) for port in nodes.values())
        if all_running:
            return True
        time.sleep(2)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Simple interaction with a TCP endpoint')
    PARSER.add_argument('-p', '--port', type=int, default=8080, help='port of the remote endpoint')
    PARSER.add_argument('-i', '--ip', default='127.0.0.1', help='IP of the remote endpoint')
    PARSER.add_argument('message', nargs='*', default=['persist'])

    ARGS = PARSER.parse_args()
    MESSAGE = ' '.join(ARGS.message)

    if not is_healthy(ARGS.ip, ARGS.port, MESSAGE):
        sys.exit(1)
