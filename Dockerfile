FROM python:3.7
EXPOSE 8080

USER root

RUN mkdir /app
WORKDIR /app

ENV ONIONR_DOCKER=true

#Install needed packages
RUN apt-get update && apt-get install -y tor locales

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

ADD ./requirements.txt /app/requirements.txt
RUN pip3 install --require-hashes -r requirements.txt

#Add Onionr source
COPY . /app/

VOLUME /app/data/

#Default to running as nonprivileged user
RUN chmod g=u -R /app
USER 1000
ENV HOME=/app

CMD ["bash", "./run-onionr-node.sh"]
