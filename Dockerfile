FROM python:3.9-slim

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY main.py .
COPY helper.py .
COPY variables.py .
COPY handlers/data_handler.py ./handlers/
COPY handlers/plot_handler.py ./handlers/
COPY databases/users.py ./databases/
COPY databases/polls.py ./databases/

CMD ["python", "./main.py"]
