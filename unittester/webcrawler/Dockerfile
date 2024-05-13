FROM python:3.9-buster
WORKDIR /webcrawler/
COPY . .
COPY ../taskqueue/producer.py .
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["crawler.py"]
