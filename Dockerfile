# For creating a container on a Raspberry Pi
FROM arm32v7/python:3.9
WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ./device.sh