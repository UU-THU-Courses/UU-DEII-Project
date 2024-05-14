FROM maven:latest

WORKDIR /worker/
COPY . .

RUN apt-get update 
RUN apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["service.py", "--pulsar"]

# ENTRYPOINT ["bash"]
# CMD ["unittest.sh", "https://github.com/ZHENFENG13/My-Blog.git"]
