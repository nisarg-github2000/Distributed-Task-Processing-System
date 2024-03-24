FROM python:3.8

WORKDIR /app
COPY . .
# COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# COPY ./worker.py /app/worker.py
CMD ["python" ,"./worker.py" ]