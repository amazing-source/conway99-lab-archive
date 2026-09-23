FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends build-essential git ca-certificates && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/arminbiere/kissat /opt/kissat && cd /opt/kissat && ./configure && make -j4 && cp build/kissat /usr/local/bin/
RUN git clone --depth 1 https://github.com/arminbiere/cadical /opt/cadical && cd /opt/cadical && ./configure && make -j4 && cp build/cadical /usr/local/bin/
WORKDIR /work
