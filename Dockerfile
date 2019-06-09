FROM phusion/baseimage:0.9.19

# Use baseimage-docker's init system.
CMD ["/sbin/my_init"]

ENV TERM=xterm-256color

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install necessary packages
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
RUN add-apt-repository -y ppa:deadsnakes/ppa

RUN echo "deb http://downloads.skewed.de/apt/xenial xenial universe" | tee -a /etc/apt/sources.list

RUN echo "deb-src http://downloads.skewed.de/apt/xenial xenial universe" | tee -a /etc/apt/sources.list

RUN apt-get update && apt-get install -y --allow-unauthenticated \
    wget \
    build-essential \
    r-base \
    python3.6-dev \
    libpython3.6

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.5 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2


RUN apt-get update && apt-get install -y --allow-unauthenticated \
    python3-pip \
    python3-graph-tool

# Install Python requirements
RUN mkdir -p /usr/src/link
COPY requirements.txt /usr/src/link/
COPY setup.py /usr/src/link/
RUN pip3 install --upgrade pip

# Install R packages
RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.us.r-project.org'; options(repos = r);" > ~/.Rprofile
RUN Rscript -e "install.packages('sp')"
RUN Rscript -e "install.packages('tbart')"

WORKDIR /usr/src
RUN wget https://download.osgeo.org/gdal/2.2.4/gdal-2.2.4.tar.gz
RUN tar xzf gdal-2.2.4.tar.gz
WORKDIR ./gdal-2.2.4
RUN ./configure
RUN make
RUN make install

WORKDIR /usr/src
RUN curl -L http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz | tar xz
WORKDIR ./spatialindex-src-1.8.5
RUN ./configure
RUN make
RUN make install
RUN ldconfig

# setup environment variables
RUN export GT="1"
RUN export TBART="1"
RUN export DO_API_KEY="insert_your_url_here"
RUN export DO_URL="insert_your_url_here"

WORKDIR /usr/src/link/
## Copy the files from the host to the container
COPY . .
## Install module
RUN pip3 install --ignore-installed -r requirements.txt

RUN mkdir /app
RUN mkdir /app/logs
RUN touch /app/logs/gunicorn.log

RUN chmod 777 -R *

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN echo Starting python and starting the Flask service...
ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver"]

