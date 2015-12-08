#!/usr/bin/env python

import random
import time
import sys

import blockade.cli
import interact

HOST = '127.0.0.1'
MAX_VALUE = 100

def check_counters(nodes):
    counters = []
    for node, port in nodes.items():
        counter = interact.request(HOST, port, 'get')
        equal = all(x == counter for x in counters)

        if not equal:
            print('Counter of node "%s" [%d] does not match with other counters: %s' %
                  (node, port, str(counters)))
            return False
        counters.append(counter)
    return True

if __name__ == '__main__':
    SETTLE_TIMEOUT = 30
    NODES = {'chaos1': 10001, 'chaos2': 10002, 'chaos3': 10003}

    interact.wait_to_be_running(HOST, NODES)

    if not check_counters(NODES):
        sys.exit(1)

    def random_op():
        op = random.choice(['inc', 'dec'])
        value = random.randint(1, MAX_VALUE)
        return '%s %d' % (op, value)

    print('Starting requests...')

    WORKER = interact.SetWorker(HOST, NODES, random_op, interval=0.1)
    WORKER.start()

    # trigger some random partitions
    CFG = blockade.cli.load_config('blockade.yml')
    BLK = blockade.cli.get_blockade(CFG)

    def random_network(node):
        failure = random.choice([BLK.fast, BLK.flaky, BLK.slow])
        failure([node], None)

    for idx in xrange(30):
        # partition a random chaos node
        node = random.choice(NODES.keys() + [None])

        if node:
            print('Partition of "%s"' % node)
            BLK.partition([[node]])
        else:
            print('Join of cluster')
            BLK.join()

        time.sleep(5)

        random_network(random.choice(NODES.keys()))
        time.sleep(5)

    WORKER.cancel()
    WORKER.join()

    print('Joining cluster - waiting %d seconds to settle...' % SETTLE_TIMEOUT)
    BLK.join()
    BLK.fast(None, None)

    time.sleep(SETTLE_TIMEOUT)

    if not check_counters(NODES):
        sys.exit(1)

    print('counter values match up correctly')

