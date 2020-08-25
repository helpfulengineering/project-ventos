FROM ubuntu:latest

# Set the working directory.
WORKDIR /app

# suppress warnings during build
ARG DEBIAN_FRONTEND=noninteractive

# Install Python, PyLint, PyTest, GCC etc
RUN DEBIAN_FRONTEND=noninteractive \
apt-get -yq update && apt-get upgrade -yq \
&& apt-get install python3.7 -y \
&& ln -s /usr/bin/python3 /usr/bin/python \
&& apt-get install pylint -y \
&& apt-get install -y --no-install-recommends bzip2 curl unzip \
&& apt-get install -yq ca-certificates \
&& apt-get install -y build-essential \
&& curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh \
&& curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py -o get-platformio.py \
&& python3 get-platformio.py

RUN apt-get install python3-pip -y
RUN pip3 install pandas validator_collection pyyaml tabulate \
&& pip3 install -U pytest
RUN apt-get install inotify-tools -y

# Set path so it work in Bash
ENV PATH=${PATH}:/app/bin:~/.platformio/penv/bin

# Copy all local files to the docker container
COPY . .
