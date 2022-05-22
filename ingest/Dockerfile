FROM python:3.9
WORKDIR /app
COPY src/gcloud_logger.py src/main.py ./src/
COPY requirements.txt weather_cron commands.sh ./
RUN apt-get update \
    && apt-get -y install cron 
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN crontab /app/weather_cron
RUN chmod +x /app/commands.sh
CMD ["/bin/bash", "-c", "/app/commands.sh"]
