# Start from weaveworks/scope, so that we have a docker client built in.
FROM python:2
LABEL maintainer.name="Carlos Gomez Cainzos" \
      maintainer.email=" <carlos.gomezcainzos@gmail.com>" \
      version="0.1.0" \
      works.weave.role=system

RUN pip install docker-py

# Add our plugin
ADD ./docker-network.py /usr/bin/docker-network.py
ENTRYPOINT ["/usr/bin/docker-network.py"]
