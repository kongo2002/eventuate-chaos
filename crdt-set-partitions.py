#!/usr/bin/env python

import time
import threading
import random
import sys

import blockade.cli
import interact

HOST = '127.0.0.1'
MAX_VALUE = 1000

class SetWorker(threading.Thread):
    def __init__(self, nodes, operations=100, interval=0.5):
        threading.Thread.__init__(self)

        self.values = set()
        self.nodes = nodes
        self.operations = operations
        self.interval = interval
        self.is_cancelled = False

    def run(self):
        num_nodes = len(self.nodes)
        nodemap = dict([(idx, v) for (idx, (k, v)) in enumerate(self.nodes.items())])

        while self.operations > 0 and not self.is_cancelled:
            self.operations -= 1

            value = random.randint(1, MAX_VALUE)
            node = random.randint(0, num_nodes-1)
            operation = random.choice(['add', 'remove'])

            interact.request(HOST, nodemap[node], '%s %d' % (operation, value))

            time.sleep(self.interval)

    def cancel(self):
        self.is_cancelled = True

def get_set(port):
    try:
        output = interact.request(HOST, port, 'get')
        if output and len(output) > 2:
            return set([int(i) for i in output[1:-1].split(',')])
        return set()
    except:
        return set()

def wait_to_be_running(nodes):
    print('Waiting for %d nodes to be up and running' % (len(nodes)))
    while True:
        all_running = True
        for _, port in nodes.items():
            all_running = all_running and interact.is_healthy(HOST, port, 'get', False)

        if all_running:
            return True
        time.sleep(2)

if __name__ == '__main__':
    SETTLE_TIMEOUT = 60
    NODES = {'chaos1': 10001, 'chaos2': 10002, 'chaos3': 10003}

    wait_to_be_running(NODES)

    print('Starting requests...')

    # start worker that randomly trigger 'add' and 'remove' commands
    WORKER = SetWorker(NODES)
    WORKER.start()

    # trigger some random partitions
    CFG = blockade.cli.load_config('blockade.yml')
    BLK = blockade.cli.get_blockade(CFG)

    for idx in xrange(6):
        # partition a random chaos node
        node = random.choice(NODES.keys())
        print('Partition of "%s"' % node)

        BLK.partition([[node]])
        time.sleep(10)

    WORKER.join()

    print('Joining cluster - waiting %d seconds to settle...' % SETTLE_TIMEOUT)
    BLK.join()
    time.sleep(SETTLE_TIMEOUT)
