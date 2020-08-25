FROM ubuntu:latest

# Set the working directory.
WORKDIR /app

# Install Python, PyLint, PyTest, GCC etc
RUN apt-get -yq update && apt-get upgrade -yq \
&& apt-get install python3.7 -y \
&& ln -s /usr/bin/python3 /usr/bin/python \
&& apt-get install pylint -y \
&& apt-get install -y --no-install-recommends bzip2 curl unzip \
&& apt-get install -yq ca-certificates \
&& apt-get install -y build-essential \
&& apt-get install inotify-tools -y \
&& curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh \
&& curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py -o get-platformio.py \
&& python3 get-platformio.py \
&& apt-get install python3-pip -y \
&& pip3 install pandas validator_collection pyyaml tabulate \
&& pip3 install -U pytest

# Set path so it work in Bash
ENV PATH=${PATH}:/app/bin:~/.platformio/penv/bin

# Copy all local files to the docker container
COPY . .
