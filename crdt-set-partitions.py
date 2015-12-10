#!/usr/bin/env python

from __future__ import print_function

import argparse
import random
import sys

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


def compare_sets(nodes):
    SETS = {}
    for node, port in NODES.items():
        node_set = get_set(port)

        for other, other_set in SETS.items():
            if other_set != node_set:
                print("Set of node '%s' differs with set of node '%s':" % (node, other))
                print(" %s: %s" % (node, node_set))
                print(" %s: %s" % (other, other_set))
                print("Difference: %s; %s" % (node_set.difference(other_set), other_set.difference(node_set)))
                return False
        SETS[node] = node_set
    return True


class SetOperation(interact.Operation):

    def operation(self, idx, state):
        op = random.choice(['add', 'remove'])
        value = random.randint(1, MAX_VALUE)
        return '%s %d' % (op, value)


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='start CRDT ORSet chaos test')
    PARSER.add_argument('-i', '--iterations', type=int, default=5)
    PARSER.add_argument('--interval', type=float, default=0.1)
    PARSER.add_argument('--settle', type=int, default=60)

    ARGS = PARSER.parse_args()
    NODES = {'location1': 10001, 'location2': 10002, 'location3': 10003}
    OP = SetOperation()

    if not interact.requests_with_chaos(OP, HOST, NODES, ARGS.iterations, ARGS.interval, ARGS.settle):
        sys.exit(1)

    # validate current set values
    if not compare_sets(NODES):
        sys.exit(1)
