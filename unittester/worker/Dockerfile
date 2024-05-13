FROM maven:latest 
WORKDIR /worker/
COPY . .
RUN apt-get update 
RUN apt-get install -y python3
ENTRYPOINT ["bash"]
CMD ["unittest.sh", "https://github.com/ZHENFENG13/My-Blog.git"]
