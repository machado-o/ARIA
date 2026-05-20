# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app/SAM

ENV DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    git libgl1 libglib2.0-0

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --timeout 300 torch torchvision --index-url https://download.pytorch.org/whl/cu128

COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --timeout 300 -r /tmp/requirements.txt

CMD ["python", "inference.py"]
