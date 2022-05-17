FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
COPY requirements.txt .
RUN pip3 install wheel
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "--log-file=-", "--bind", "0.0.0.0:5000", "-k", "flask_sockets.worker", "run:app", "wsgi"]
