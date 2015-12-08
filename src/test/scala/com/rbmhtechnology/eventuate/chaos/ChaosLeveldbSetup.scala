package com.rbmhtechnology.eventuate.chaos

import akka.actor.ActorSystem
import com.rbmhtechnology.eventuate.ReplicationEndpoint
import com.rbmhtechnology.eventuate.log.leveldb.LeveldbEventLog
import com.typesafe.config.ConfigFactory

trait ChaosLeveldbSetup extends ChaosSetup {

  def config(hostname: String) = baseConfig(hostname)
    .withFallback(ConfigFactory.parseString(
      s"""
         |eventuate.snapshot.filesystem.dir = /tmp/test-snapshot
         |eventuate.log.leveldb.dir = /tmp/test-log
     """.stripMargin))

  implicit val system = ActorSystem.create("location", config(hostname))

  // create and activate eventuate replication endpoint
  lazy val endpoint = new ReplicationEndpoint(name,
    Set(ReplicationEndpoint.DefaultLogName),
    LeveldbEventLog.props(_), connections)
}
