FROM docker.arvancloud.ir/python:3.11-slim

# Install supervisor
RUN apt-get -o Acquire::Check-Valid-Until=false update && apt-get install -y supervisor

# Copy the supervisor configuration file
COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app

# Use supervisor to run both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
