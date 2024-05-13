FROM python:3.9-buster
WORKDIR /controller/
COPY controller/ .
COPY taskqueue/producer.py .
COPY taskqueue/consumer.py .
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["service.py"]
