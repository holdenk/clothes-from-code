# base image
FROM python:3.7.2-stretch

# set working directory
WORKDIR /usr/src/app

# Downoad firefox
RUN apt-get update && apt-get install -y apt-utils firefox-esr && rm -rf /var/cache/apt

# Download ubuntu fonts
RUN wget https://assets.ubuntu.com/v1/fad7939b-ubuntu-font-family-0.83.zip && unzip fad7939b-ubuntu-font-family-0.83.zip && mv *ubuntu-font-family-0.83* /usr/share/fonts/truetype/ && fc-cache -f -v

# Download gecko driver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz && \
    tar -xvf geckodriver-v0.24.0-linux64.tar.gz && \
    mv geckodriver /bin/ && \
    rm geckodriver-v0.24.0-linux64.tar.gz

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# add app
COPY . /usr/src/app

# Make entrypoint executable
RUN chmod a+x /usr/src/app/entrypoint.sh

# run server
CMD ["/usr/src/app/entrypoint.sh"]