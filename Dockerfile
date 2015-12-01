FROM java:8

RUN wget -nv "http://downloads.typesafe.com/scala/2.11.7/scala-2.11.7.deb" && \
    dpkg -i scala-2.11.7.deb && \
    apt-get update && \
    apt-get install scala && \
    rm scala-2.11.7.deb && \
    \
    wget -nv "https://dl.bintray.com/sbt/debian/sbt-0.13.9.deb" && \
    dpkg -i sbt-0.13.9.deb && \
    apt-get update && \
    apt-get install sbt && \
    rm sbt-0.13.9.deb && \
    \
    sbt version

VOLUME "/app"
WORKDIR "/app"

ENTRYPOINT ["sbt"]
CMD ["version"]
