package com.rbmhtechnology.eventuate.chaos

import akka.actor.Props
import com.rbmhtechnology.eventuate.ReplicationEndpoint
import com.rbmhtechnology.eventuate.crdt.CounterService

object ChaosCounter extends ChaosLeveldbSetup {
  val service = new CounterService[Int](name, endpoint.logs(ReplicationEndpoint.DefaultLogName))
  endpoint.activate()

  val interface = system.actorOf(Props(new ChaosCounterInterface(service)))
}
