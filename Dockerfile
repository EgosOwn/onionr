FROM ubuntu:xenial

#Base settings
ENV HOME /root

#Install needed packages
RUN apt update && apt install -y python3 python3-dev python3-pip tor

WORKDIR /srv/
ADD ./requirements.txt /srv/requirements.txt
RUN pip3 install -r requirements.txt


WORKDIR /root/
#Add Onionr source
COPY . /root/
VOLUME /root/data/

#Set upstart command
CMD bash

#Expose ports
EXPOSE 8080
