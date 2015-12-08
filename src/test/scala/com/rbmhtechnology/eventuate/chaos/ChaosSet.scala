package com.rbmhtechnology.eventuate.chaos

import akka.actor.Props
import com.rbmhtechnology.eventuate.ReplicationEndpoint
import com.rbmhtechnology.eventuate.crdt.ORSetService

object ChaosSet extends ChaosCassandraSetup {
  val service = new ORSetService[Int](name, endpoint.logs(ReplicationEndpoint.DefaultLogName))
  endpoint.activate()

  val interface = system.actorOf(Props(new ChaosSetInterface(service)))
}

