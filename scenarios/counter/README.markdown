
# Chaos test of distributed CRDT-based counter application

This scenario is another example of an [Eventuate][eventuate] application that is being tested under network failures
and partitions.


## Test setup

This time the application is a [CRDT-based
counter](https://github.com/RBMHTechnology/eventuate/blob/master/src/main/scala/com/rbmhtechnology/eventuate/crdt/Counter.scala)
service that is distributed among three Eventuate nodes. The persistence of the event-sourced services is driven by
[LevelDB event logs](http://rbmhtechnology.github.io/eventuate/reference/event-log.html#leveldb-storage-backend).


#### Participating nodes

- `location-1`: TCP port 8080 -> `10001`
- `location-2`: TCP port 8080 -> `10002`
- `location-3`: TCP port 8080 -> `10003`


#### Scenario

The distributed counter value that is managed by the tested application can be incremented and decremented by issuing a
simple command via the TCP port of the respective node.

- `inc 15`: increment the counter by `15`
- `dec 2`: decrement by `2`
- `get`: retrieve the current counter value

Once again you may use the `interact.py` helper script that is shipped with this repository:

``` bash
# start up test scenario
scenarios/counter $ sudo blockade up

# increment counter at location-2
scenarios/counter $ ../../interact.py -p 10002 inc 20
20

# decrement counter at location-3
scenarios/counter $ ../../interact.py -p 10003 dec 4
16

# request counter value from location-1
scenarios/counter $ ../../interact.py -p 10001 get
16
```


#### Scripted chaos test

Just to give you another example on how you might automate your chaos testing you may use the
`crdt-counter-partitions.py` script to generate random network failures while requesting counter operations of the test
application:

``` bash
scenarios/counter $ sudo ../../crdt-counter-partitions.py
Chaos iterations: 30
Request interval: 0.100 sec
Nodes:
  location-1
  location-2
  location-3
Waiting for 3 nodes to be up and running
Starting requests...
Joining cluster - waiting 30 seconds to settle...
counter values match up correctly
```

Some parameters like request interval (`--interval`), number of network failures to inject (`--iterations`) and the
number of participating Eventuate nodes (`--locations`) may be configured at the command line as well.

> Please note the example script requires root permissions as it directly hooks into the blockade toolkit which itself
> needs administrative rights to instrument the underlying network.


### Configuration

As usual the configuration is done via a [blockade][blockade] configuration file:

``` yaml
containers:
  location-1:
    image: eventuate-chaos/sbt
    command: ["test:run-nobootcp com.rbmhtechnology.eventuate.chaos.ChaosCounter location-1 location-2.sbt.docker location-3.sbt.docker"]
    ports:
      10001: 8080
    volumes:
      "${PWD}/../..": /app
    environment:
      HOSTNAME: "location-1.sbt.docker"

  location-2:
    image: eventuate-chaos/sbt
    command: ["test:run-nobootcp com.rbmhtechnology.eventuate.chaos.ChaosCounter location-2 location-1.sbt.docker location-3.sbt.docker"]
    ports:
      10002: 8080
    volumes:
      "${PWD}/../..": /app
    environment:
      HOSTNAME: "location-2.sbt.docker"

  location-3:
    image: eventuate-chaos/sbt
    command: ["test:run-nobootcp com.rbmhtechnology.eventuate.chaos.ChaosCounter location-3 location-1.sbt.docker location-2.sbt.docker"]
    ports:
      10003: 8080
    volumes:
      "${PWD}/../..": /app
    environment:
      HOSTNAME: "location-3.sbt.docker"
```

[blockade]: https://github.com/kongo2002/blockade
[eventuate]: https://github.com/RBMHTechnology/eventuate
