package com.rbmhtechnology.eventuate.chaos

import com.rbmhtechnology.eventuate.crdt.CounterService

class ChaosCounterInterface(service: CounterService[Int]) extends ChaosInterface {
  val testId = "test"

  def handleCommand = {
    case ("inc", Some(v), recv) =>
      service.update(testId, v)
        .map(value => reply(value.toString, recv))
    case ("dec", Some(v), recv) =>
      service.update(testId, -v)
        .map(value => reply(value.toString, recv))
    case ("get", None, recv) =>
      service.value(testId)
        .map(value => reply(value.toString, recv))
  }
}
