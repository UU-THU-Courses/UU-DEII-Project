FROM python:3.9-buster
WORKDIR /taskscheduler/
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["service.py"]
