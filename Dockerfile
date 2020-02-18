FROM python:3.7-alpine
MAINTAINER ContestPlatform developers
# Insatalling c
RUN apk add --no-cache gcc musl-dev linux-headers python2
#install go lang
RUN apk add --no-cache git make musl-dev go
ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH
RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin
#installing node js
RUN apk add --update nodejs npm
# installing java
RUN apk update
RUN apk fetch openjdk8
RUN apk add openjdk8
# installing php
RUN apk add php7 php7-fpm php7-opcache

#Build application
WORKDIR /home
COPY . .
RUN pip install -r requirement.txt
ENV PYTHONPATH "${PYTHONPATH}:/home"
ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk
ENV PATH="$JAVA_HOME/bin:${PATH}"
RUN chmod +x scripts/*
CMD sh "scripts/build"

