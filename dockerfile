FROM python:3.10-slim

ENV INSTALL_PATH="/favsync"
RUN mkdir -p $INSTALL_PATH

ENV OUTPUT_DIR="/data"
RUN mkdir -p $OUTPUT_DIR

ENV PYTHONBUFFERED="1"

COPY favsync $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /data

ENTRYPOINT ["/usr/local/bin/python", "__main__.py"]

CMD [""]
