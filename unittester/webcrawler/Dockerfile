FROM python:3.9-buster
WORKDIR /webcrawler/
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["crawler.py"]
#CMD ["crawler.py" , "--pulsar"]
