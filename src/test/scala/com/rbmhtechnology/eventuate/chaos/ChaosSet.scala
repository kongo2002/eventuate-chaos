package com.rbmhtechnology.eventuate.chaos

import akka.actor.ActorSystem
import akka.actor.Props
import com.rbmhtechnology.eventuate.ReplicationConnection
import com.rbmhtechnology.eventuate.ReplicationEndpoint
import com.rbmhtechnology.eventuate.crdt.ORSetService
import com.rbmhtechnology.eventuate.log.cassandra.CassandraEventLog
import com.typesafe.config.ConfigFactory

object ChaosSet extends App {
  def defaultConfig(hostname: String, seeds: Seq[String]) = ConfigFactory.parseString(
    s"""
       |akka.actor.provider = "akka.remote.RemoteActorRefProvider"
       |akka.remote.enabled-transports = ["akka.remote.netty.tcp"]
       |akka.remote.netty.tcp.hostname = "$hostname"
       |akka.remote.netty.tcp.port = 2552
       |akka.test.single-expect-default = 10s
       |akka.loglevel = "ERROR"
       |
       |eventuate.log.cassandra.contact-points = [${seeds.map(quote).mkString(",")}]
       |eventuate.log.cassandra.replication-factor = ${seeds.size}
     """.stripMargin)

  private def quote(str: String) = "\"" + str + "\""

  val cassandras = sys.env.get("CASSANDRA_NODES").map(_.split(","))
    .getOrElse(Array("c1.cassandra.docker", "c2.cassandra.docker"))

  if (args.length < 1) {
    Console.err.println("missing <nodename> argument")
    sys.exit(1)
  }

  val name = args(0)
  val hostname = sys.env.getOrElse("HOSTNAME", s"$name.sbt.docker")

  implicit val system = ActorSystem.create("location", defaultConfig(hostname, cassandras))

  // replication connection to other node(s)
  val connections = args.drop(1).map { conn =>
    conn.split(":") match {
      case Array(host, port) =>
        ReplicationConnection(host, port.toInt)
      case Array(host) =>
        ReplicationConnection(host, 2552)
    }
  }.toSet

  val endpoint = new ReplicationEndpoint(name, Set(ReplicationEndpoint.DefaultLogName), CassandraEventLog.props(_, batching = false), connections)
  endpoint.activate()

  val service = new ORSetService[Int](name, endpoint.logs(ReplicationEndpoint.DefaultLogName))

  val interface = system.actorOf(Props(new ChaosSetInterface(service)))
}

