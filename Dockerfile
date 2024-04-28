FROM python:3.11.4-slim-bullseye
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ENV API_PORT="15372" \
    NGINX_PORT="15373" \
    UMASK=000
WORKDIR "/app"
COPY . .
RUN cp -r lib_deb/sources.list /etc/apt/sources.list \
    && apt-get update -o Acquire::Check-Valid-Until=false  \
    && apt-get install -y libmediainfo0v5 libzen0v5  \
    && pip install -r requirements_api.txt --trusted-host mirrors.aliyun.com --default-timeout=600 -i https://mirrors.aliyun.com/pypi/simple/  \
    && pip uninstall opencv-python -y  \
    && pip install opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
USER root
EXPOSE 15372 15373
ENV PYTHONPATH=${PYTHONPATH}:.
CMD [ "python", "src/main.py"]