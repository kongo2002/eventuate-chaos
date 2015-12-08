package com.rbmhtechnology.eventuate.chaos

import com.rbmhtechnology.eventuate.ReplicationConnection
import com.typesafe.config.ConfigFactory

trait ChaosSetup extends App {

  protected def baseConfig(hostname: String) = ConfigFactory.parseString(
    s"""
       |akka.actor.provider = "akka.remote.RemoteActorRefProvider"
       |akka.remote.enabled-transports = ["akka.remote.netty.tcp"]
       |akka.remote.netty.tcp.hostname = "$hostname"
       |akka.remote.netty.tcp.port = 2552
       |akka.test.single-expect-default = 10s
       |akka.loglevel = "ERROR"
     """.stripMargin)

  protected def quote(str: String) = "\"" + str + "\""

  def name = args(0)
  def hostname = sys.env.getOrElse("HOSTNAME", s"$name.sbt.docker")

  // replication connection to other node(s)
  def connections = args.drop(1).map { conn =>
    conn.split(":") match {
      case Array(host, port) =>
        ReplicationConnection(host, port.toInt)
      case Array(host) =>
        ReplicationConnection(host, 2552)
    }
  }.toSet
}
