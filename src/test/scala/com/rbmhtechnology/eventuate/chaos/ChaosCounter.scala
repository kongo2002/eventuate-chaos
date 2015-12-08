package com.rbmhtechnology.eventuate.chaos

import akka.actor.Props
import com.rbmhtechnology.eventuate.ReplicationEndpoint
import com.rbmhtechnology.eventuate.crdt.CounterService

object ChaosCounter extends ChaosLeveldbSetup {
  implicit val system = getSystem
  val endpoint = getEndpoint

  val service = new CounterService[Int](name, endpoint.logs(ReplicationEndpoint.DefaultLogName))
  system.actorOf(Props(new ChaosCounterInterface(service)))
}
