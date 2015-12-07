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

  implicit val ec = context.dispatcher
  implicit val timeout = Timeout(1.seconds)

  IO(Tcp)(context.system) ! Tcp.Bind(self, endpoint)

  println(s"Now listening on port $port")

  def receive: Receive = {
    case Tcp.Connected(remote, _) =>
      sender ! Tcp.Register(self)

    case Tcp.Received(bs) =>
      val content = bs.utf8String
      val requester = sender

      content match {
        case command(c, value) if c == "add" =>
          service.add("foo", value.toInt).map { set =>
            requester ! Tcp.Write(ByteString(set.mkString(",") + "\n"))
          }
        case command(c, value) if c == "remove" =>
          service.remove("foo", value.toInt).map { set =>
            requester ! Tcp.Write(ByteString(set.mkString(",") + "\n"))
          }
        case c if c.startsWith("quit") =>
          context.system.terminate()
        case _ =>
          sender ! Tcp.Write(ByteString("-1"))
          sender ! Tcp.Close
      }

    case Tcp.Closed =>
    case Tcp.PeerClosed =>
  }
}

