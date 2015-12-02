Eventuate chaos testing utilities
=================================

This is very early work in progress on chaos testing utilities for [Eventuate][eventuate] and [Apache
Cassandra](http://cassandra.apache.org/). They support running Cassandra clusters and Eventuate applications with
[Docker][docker] and using [blockade][blockade] to easily generate failures like stopping and restarting of containers
and introducing network failures as partitions, packet loss and slow connections.

Prerequisites
-------------

### Installed Software

#### Linux

- [docker][docker] (tested with docker >= 1.6)
- [blockade][blockade]
- [sbt](http://www.scala-sbt.org/download.html) 0.13.x or higher

##### Initial setup

Given your [docker][docker] daemon is running and you have [blockade][blockade] in your `$PATH` you are basically ready
to go. All you have to do once is to pull or build the necessary [docker][docker] containers the test cluster is based
on:

``` bash
# cassandra image
$ docker pull cassandra:2.2.3

# sbt + scala + java8 base image
$ docker build -t uhlenheuer/sbt .
```

After that is done you can start the minimal docker DNS container that is used to identify the containers with each
other:

    $ ./start-dns.sh

This script will look for the default `docker0` network interface and start a `dnsdock` image on port 53 for DNS
discovery. You may have to specify the location to your *docker socket* via `$DOCKER_SOCKET` in case the script does not
find it by itself:

    $ DOCKER_SOCKET=/var/run/docker.sock ./start-dns.sh

These steps only have to be taken once for the initial bootstrapping.

#### Mac OS

- [Vagrant][vagrant] (tested with 1.7.4)
- [VirtualBox](https://www.virtualbox.org/)

##### Initial setup

As [docker][docker] does not run natively on Mac OS you have to use an existing *docker machine* setup and follow the
steps under [Linux](#Linux) or use the pre-configured [Vagrant][vagrant] image that ships with this repository. If you
choose the latter you just have to build the image by running `vagrant up` and ssh into your new machine:

```bash
$ vagrant up
$ vagrant ssh

# inside your virtual machine you can find the repository contents
# mounted under /vagrant as usual
cd /vagrant
```

Running a Cassandra cluster
---------------------------

### blockade chaos cluster

Now that you have all prerequisites fulfilled you can start up the [blockade][blockade] test cluster as it is configured
in the `blockade.yml` shipped with this repository. From this point on you may freely experiment and modify all given
parameters and configurations as this is just a toolkit to get you started as quickly as possible.

> Note that all blockade commands require root permissions.

```bash
$ sudo blockade up
```

Depending on the cassandra version (> 2.1) you have to configure a reasonable startup delay for every cassandra node
(i.e. 60 seconds). This may increase the initial startup time a lot. Once all nodes are up and running you can inspect
your running cluster via `blockade status`:

```bash
$ sudo blockade status
NODE            CONTAINER ID    STATUS  IP              NETWORK    PARTITION
c1              8ccf90e8f76e    UP      172.17.0.3      NORMAL
c2              5c65f3ca62ec    UP      172.17.0.5      NORMAL
c3              4b630db6a19e    UP      172.17.0.4      NORMAL
c4              928f68f3754c    UP      172.17.0.7      NORMAL
chaos           bb8c89f615ef    UP      172.17.0.6      NORMAL
```

### failures

From now on you may introduce any kind of failure the [blockade][blockade] tool supports. This is my personal preference
but I like to inspect the current [eventuate][eventuate] node's status in a [tmux](https://tmux.github.io/) split window
while I modify the cluster's condition with `tmux split-window docker logs -f chaos`.

##### partition one cassandra node

``` bash
$ sudo blockade partition c2
NODE            CONTAINER ID    STATUS  IP              NETWORK    PARTITION
c1              8ccf90e8f76e    UP      172.17.0.3      NORMAL     2
c2              5c65f3ca62ec    UP      172.17.0.5      NORMAL     1
c3              4b630db6a19e    UP      172.17.0.4      NORMAL     2
c4              928f68f3754c    UP      172.17.0.7      NORMAL     2
chaos           bb8c89f615ef    UP      172.17.0.6      NORMAL     2
```

##### partition two cassandra nodes on its own

``` bash
$ sudo blockade partition c1 c3
NODE            CONTAINER ID    STATUS  IP              NETWORK    PARTITION
c1              8ccf90e8f76e    UP      172.17.0.3      NORMAL     1
c2              5c65f3ca62ec    UP      172.17.0.5      NORMAL     3
c3              4b630db6a19e    UP      172.17.0.4      NORMAL     2
c4              928f68f3754c    UP      172.17.0.7      NORMAL     3
chaos           bb8c89f615ef    UP      172.17.0.6      NORMAL     3
```

##### flaky network connection of the eventuate node

``` bash
$ sudo blockade flaky chaos
NODE            CONTAINER ID    STATUS  IP              NETWORK    PARTITION
c1              8ccf90e8f76e    UP      172.17.0.3      NORMAL     1
c2              5c65f3ca62ec    UP      172.17.0.5      NORMAL     3
c3              4b630db6a19e    UP      172.17.0.4      NORMAL     2
c4              928f68f3754c    UP      172.17.0.7      NORMAL     3
chaos           bb8c89f615ef    UP      172.17.0.6      FLAKY      3
```

##### restart of nodes

You may also restart one or multiple nodes and inspect the effect on the [eventuate][eventuate] application as well:

    $ sudo blockade restart c2 c4

### Example configuration

The examplary `blockade.yml` consists of 4 cassandra nodes (`c1` being the initial seed node) and one
[eventuate][eventuate] [ChaosActor](./blob/master/src/test/scala/com/rbmhtechnology/eventuate/chaos/ChaosActor.scala).
You can find further information on the [blockade github page][blockade] regarding its configuration and the
possibilities you have in addition to what is mentioned in here already.

``` yaml
containers:
  c1:
    image: cassandra:2.2.3

  c2:
    image: cassandra:2.2.3
    start_delay: 60
    links:
      c1: "c1"
    environment:
      CASSANDRA_SEEDS: "c1.cassandra.docker"

  c3:
    image: cassandra:2.2.3
    start_delay: 60
    links:
      c1: "c1"
    environment:
      CASSANDRA_SEEDS: "c1.cassandra.docker"

  c4:
    image: cassandra:2.2.3
    start_delay: 60
    links:
      c1: "c1"
    environment:
      CASSANDRA_SEEDS: "c1.cassandra.docker"

  chaos:
    image: uhlenheuer/sbt
    command: ["test:run-main com.rbmhtechnology.eventuate.chaos.ChaosActor -d"]
    volumes:
      "/vagrant": "/app"
    links:
      c1: "c1"
    environment:
      CASSANDRA_NODES: "c1.cassandra.docker,c2.cassandra.docker,c3.cassandra.docker,c4.cassandra.docker"
```


[docker]: https://www.docker.com/
[blockade]: https://github.com/kongo2002/blockade
[vagrant]: https://www.vagrantup.com/
[eventuate]: https://github.com/RBMHTechnology/eventuate
