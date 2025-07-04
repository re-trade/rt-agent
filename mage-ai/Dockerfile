FROM mageai/mageai:latest

WORKDIR /home/src

COPY ./data_exporters /home/src/data_exporters
COPY ./data_loaders /home/src/data_loaders
COPY ./pipelines /home/src/pipelines
COPY ./load_helpers /home/src/load_helpers
COPY ./transformers /home/src/transformers
COPY ./requirements.txt /home/src/requirements.txt

RUN apt-get update && apt-get install -y \
    python3-pip \
    build-essential \
    cmake \
    libpython3-dev

RUN pip install --no-cache-dir -r requirements.txt
