FROM python:3.9-buster
WORKDIR /webui/
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["./app.py","--host=0.0.0.0","--port=5100","--debug"]
