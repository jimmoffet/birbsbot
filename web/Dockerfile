FROM jimmoffet/hub:1.4
#################################################################
### SEE DockerfileBoilerplate for detail on the hub:1.4 image ###
#################################################################
ENV DEBIAN_FRONTEND=noninteractive
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
