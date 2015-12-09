#!/usr/bin/env python

import argparse
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


def start_worker(nodes, interval):
    def random_op():
        op = random.choice(['inc', 'dec'])
        value = random.randint(1, MAX_VALUE)
        return '%s %d' % (op, value)

    print('Starting requests...')

    worker = interact.SetWorker(HOST, nodes, random_op, interval=interval)
    worker.start()

    return worker


if __name__ == '__main__':
    SETTLE_TIMEOUT = 30
    PARSER = argparse.ArgumentParser(description='start CRDT-counter chaos test')
    PARSER.add_argument('-i', '--iterations', type=int, default=30)
    PARSER.add_argument('--interval', type=float, default=0.1)
    PARSER.add_argument('-l', '--locations', type=int, default=3)

    ARGS = PARSER.parse_args()

    # we are making some assumptions in here:
    # every location is named 'location-<id>' and its TCP port 8080
    # is mapped to the host port '10000+<id>'
    NODES = dict(('location-%d' % idx, 10000+idx) for idx in xrange(1, ARGS.locations+1))

    print('Chaos iterations: %d' % ARGS.iterations)
    print('Request interval: %.3f sec' % ARGS.interval)

    print('Nodes:')
    for node in NODES.keys():
        print('  ' + node)

    interact.wait_to_be_running(HOST, NODES)

    if not check_counters(NODES):
        sys.exit(1)

    WORKER = start_worker(NODES, ARGS.interval)

    # trigger some random partitions
    CFG = blockade.cli.load_config('blockade.yml')
    BLK = blockade.cli.get_blockade(CFG)

    def random_network(node):
        failure = random.choice([BLK.fast, BLK.flaky, BLK.slow])
        failure([node], None)

    for idx in xrange(ARGS.iterations):
        BLK.random_partition()
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

