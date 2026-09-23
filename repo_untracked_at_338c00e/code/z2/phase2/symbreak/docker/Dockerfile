FROM satbox
RUN apt-get update && apt-get install -y --no-install-recommends cmake git build-essential ca-certificates && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 https://github.com/meelgroup/breakid /opt/breakid && cd /opt/breakid && mkdir build && cd build && cmake .. && make -j4 && (cp breakid /usr/local/bin/ 2>/dev/null || cp */breakid /usr/local/bin/ || find . -name breakid -type f -exec cp {} /usr/local/bin/ \;)
WORKDIR /work
