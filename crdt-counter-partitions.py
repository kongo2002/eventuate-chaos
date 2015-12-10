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
    if len(nodes) < 1:
        raise ValueError('no nodes given')

    counters = []
    for node, port in nodes.items():
        counter = interact.request(HOST, port, 'get')
        equal = all(x == counter for x in counters)

        if not equal:
            print('Counter of node "%s" [%d] does not match with other counters: %s' %
                  (node, port, str(counters)))
            return None
        counters.append(counter)

    # all counters are the same -> return the first one for reference
    return int(counters[0])


class CounterOperation(interact.Operation):

    def init(self, host, nodes):
        # get first counter value
        counter = int(interact.request(host, nodes.values()[0], 'get'))
        return {'counter': counter}

    def operation(self, idx, state):
        op = random.choice(['inc', 'dec'])
        value = random.randint(1, MAX_VALUE)

        if op == 'inc':
            state['counter'] += value
        else:
            state['counter'] -= value

        return '%s %d' % (op, value)


def start_worker(nodes, interval):
    print('Starting requests...')

    worker = interact.RequestWorker(HOST, nodes, CounterOperation(), interval=interval)
    worker.start()

    return worker


def _print_partitions(partitions):
    if len(partitions) < 1:
        print('Cluster joined')
    else:
        for idx, part in enumerate(partitions):
            print('Partition %d: %s' % (idx+1, ', '.join(part)))


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

    # wait for system to be ready and initialized
    interact.wait_to_be_running(HOST, NODES)
    if check_counters(NODES) is None:
        sys.exit(1)

    try:
        WORKER = start_worker(NODES, ARGS.interval)

        # trigger some random partitions
        CFG = blockade.cli.load_config('blockade.yml')
        BLK = blockade.cli.get_blockade(CFG)

        def random_network(node):
            failure = random.choice([BLK.fast, BLK.flaky, BLK.slow])
            failure([node], None)

        for idx in xrange(ARGS.iterations):
            part = BLK.random_partition()
            _print_partitions(part)
            print('-' * 25)
            time.sleep(5)

            random_network(random.choice(NODES.keys()))
            time.sleep(5)
    except (KeyboardInterrupt, blockade.errors.BlockadeError):
        WORKER.cancel()
        WORKER.join()
        BLK.join()
        BLK.fast(None, None)

        print('Test interrupted')
        sys.exit(1)

    WORKER.cancel()
    WORKER.join()

    print('Joining cluster - waiting %d seconds to settle...' % SETTLE_TIMEOUT)
    BLK.join()
    BLK.fast(None, None)

    time.sleep(SETTLE_TIMEOUT)

    print('Processed %d requests in the meantime' % WORKER.iterations)

    EXPECTED_VALUE = WORKER.state['counter']
    COUNTER_VALUE = check_counters(NODES)
    if COUNTER_VALUE is None:
        sys.exit(1)

    if COUNTER_VALUE != EXPECTED_VALUE:
        print('Expected counter value: %d; actual %d' % (EXPECTED_VALUE, COUNTER_VALUE))
        sys.exit(1)

    print('Counter value (%d) matches up correctly' % EXPECTED_VALUE)

