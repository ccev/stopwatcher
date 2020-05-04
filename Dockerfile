# docker build -t stopwatcher .
# docker run --rm -v "$(pwd)"/config:/usr/src/app/config -t stopwatcher python3 stop_watcher.py --init
# docker run --rm -v "$(pwd)"/config:/usr/src/app/config -t stopwatcher

FROM python:3.7-slim
WORKDIR /usr/src/app
COPY . .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD ["python3","stop_watcher.py"]