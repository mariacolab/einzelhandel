FROM python:3.9

WORKDIR /app
COPY watch_folder.py /app/

RUN pip install watchdog requests

CMD ["python3", "watch_folder.py"]
