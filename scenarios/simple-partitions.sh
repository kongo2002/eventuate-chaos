#!/bin/bash -eu

CASSANDRAS="c1 c2 c3"
SETTLE_DELAY=${SETTLE_DELAY:-40}

function settle() {
    echo "waiting $SETTLE_DELAY seconds for cluster to settle..."
    sleep $SETTLE_DELAY
}

function wait_till_healthy() {
    echo "waiting till cluster is up and running..."
    while ! ./check-health.py >/dev/null 2>&1; do
        sleep 2
    done
}

wait_till_healthy

echo "*** checking working persistance with 1 node partition each"

for cassandra in $CASSANDRAS; do
    echo "partition of cassandra '$cassandra'"

    sudo blockade partition $cassandra
    settle

    echo "checking persistance..."
    ./check-health.py >/dev/null
done

echo "*** checking non-working persistance with 2 node partitions"

for cassandra in $CASSANDRAS; do
    echo "partition of chaos application + '$cassandra'"

    sudo blockade partition chaos,$cassandra
    settle

    echo "checking persistance..."
    ./check-health.py >/dev/null 2>&1 && (echo "persistance working when it shouldn't" && exit 1)

    # reconnect cluster for next partition
    sudo blockade join
    wait_till_healthy
done

echo "*** checking final reconnect"

./check-health.py >/dev/null

echo "test successfully finished"
