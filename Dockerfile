FROM python:3.8.7-alpine3.12
COPY . .
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk del tzdata
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
CMD python3 main.py