FROM ubuntu:xenial

#Base settings
ENV HOME /root

#Install needed packages
RUN apt update && apt install -y python3 python3-dev python3-pip tor

#Add Onionr source
COPY . /root
VOLUME /root/data

WORKDIR /root

RUN pip3 install -r requirements.txt

#Set upstart command
#CMD (! ${ENABLE_TOR} || tor&) && python zeronet.py --ui_ip 0.0.0.0 --fileserver_port 26552
CMD bash

#Expose ports
EXPOSE 8080
