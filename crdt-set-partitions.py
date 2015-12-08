#!/usr/bin/env python

import time
import random

import blockade.cli
import interact

HOST = '127.0.0.1'
MAX_VALUE = 1000

def get_set(port):
    try:
        output = interact.request(HOST, port, 'get')
        if output and len(output) > 2:
            return set([int(i) for i in output[1:-1].split(',')])
        return set()
    except:
        return set()

if __name__ == '__main__':
    SETTLE_TIMEOUT = 60
    NODES = {'chaos1': 10001, 'chaos2': 10002, 'chaos3': 10003}

    interact.wait_to_be_running(HOST, NODES)

    def random_op():
        op = random.choice(['add', 'remove'])
        value = random.randint(1, MAX_VALUE)
        return '%s %d' % (op, value)

    print('Starting requests...')

    # start worker that randomly trigger 'add' and 'remove' commands
    WORKER = interact.SetWorker(HOST, NODES, random_op)
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

    # TODO: validate current set values
