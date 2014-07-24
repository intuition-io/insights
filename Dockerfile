# hivetech/insights
# VERSION 0.1.0

FROM hivetech/intuition
MAINTAINER Xavier Bruhiere <xavier.bruhiere@gmail.com>

# Install R libraries
RUN wget -qO- http://bit.ly/L39jeY | R --no-save

# TA-Lib support
RUN apt-get install -y libopenblas-dev liblapack-dev gfortran && \
  wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
# Python wrapper
RUN pip install Cython==0.20.1 && pip install --allow-external TA-Lib --allow-unverified TA-Lib TA-Lib==0.4.8

ADD . /insights
# We want to be able to modify insights algorithms so we install just dependencies
RUN cd /insights && pip install -r requirements.txt

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
