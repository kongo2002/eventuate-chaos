package com.rbmhtechnology.eventuate.chaos

import java.net.InetSocketAddress

import akka.actor.Actor
import akka.io.IO
import akka.io.Tcp
import akka.util.ByteString
import akka.util.Timeout

import com.rbmhtechnology.eventuate.crdt.ORSetService

import scala.concurrent.duration._

class ChaosSetInterface(service: ORSetService[Int]) extends Actor {
  val port = 8080
  val endpoint = new InetSocketAddress(port)

  val command = """(?s)(\w+)\s+(\d+).*""".r
  val setId = "test"

  implicit val ec = context.dispatcher
  implicit val timeout = Timeout(1.seconds)

  IO(Tcp)(context.system) ! Tcp.Bind(self, endpoint)

  println(s"Now listening on port $port")

  private def writeSet(set: Set[Int]) = {
    Tcp.Write(ByteString(s"[${set.mkString(",")}]"))
  }

  def receive: Receive = {
    case Tcp.Connected(remote, _) =>
      sender ! Tcp.Register(self)

    case Tcp.Received(bs) =>
      val content = bs.utf8String
      val requester = sender

      content match {
        case command(c, value) if c == "add" =>
          service.add(setId, value.toInt).map { set =>
            requester ! writeSet(set)
          }
        case command(c, value) if c == "remove" =>
          service.remove(setId, value.toInt).map { set =>
            requester ! writeSet(set)
          }
        case c if c.startsWith("get") =>
          service.value(setId).map { set =>
            requester ! writeSet(set)
          }
        case c if c.startsWith("quit") =>
          context.system.terminate()
        case _ =>
          sender ! Tcp.Close
      }

    case Tcp.Closed =>
    case Tcp.PeerClosed =>
  }
}

