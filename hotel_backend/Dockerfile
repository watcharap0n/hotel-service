FROM python:3.10-slim

WORKDIR hotel_service

COPY ./requirements.txt .

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

RUN pip install --upgrade pip
RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

COPY server .
WORKDIR ../


CMD ["uvicorn", "hotel_service.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8001"]
