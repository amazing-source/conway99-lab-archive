FROM satbox:latest
RUN git clone --depth 1 https://github.com/marijnheule/CnC /opt/CnC && cd /opt/CnC/march_cu && make CFLAGS="-O3 -fno-strict-aliasing -fcommon -DNDEBUG" && cp march_cu /usr/local/bin/
