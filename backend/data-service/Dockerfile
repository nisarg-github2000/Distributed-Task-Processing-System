FROM python:3.8

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./main.py /app/main.py
COPY . /app
EXPOSE 9393
CMD ["/bin/bash","-c", "uvicorn main:app --host 0.0.0.0 --port 9393 --reload" ]