

FROM python:3.12.3-slim
# the working dir in the container
WORKDIR /app
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 


EXPOSE 8000
CMD ["python3","app.py"]