FROM python:3.11.4-slim-bullseye
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ENV API_PORT="15372" \
    NGINX_PORT="15373" \
    UMASK=000

RUN groupadd app && useradd -g app app
RUN usermod -d /app -m app
WORKDIR "/app"
COPY src src
COPY static static
COPY temp temp
COPY requirements.txt requirements.txt
RUN  pip install Cython --trusted-host mirrors.aliyun.com --default-timeout=600 -i https://mirrors.aliyun.com/pypi/simple/\
    && pip install -r requirements.txt --trusted-host mirrors.aliyun.com --default-timeout=600 -i https://mirrors.aliyun.com/pypi/simple/
RUN pip uninstall opencv-python -y
RUN pip install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

USER root
EXPOSE 15372 15373
ENV PYTHONPATH=${PYTHONPATH}:.
CMD [ "python", "src/main.py"]