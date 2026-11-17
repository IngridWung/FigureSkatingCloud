FROM python:3.12-slim

WORKDIR /app
COPY server.py ./
COPY web ./web

RUN mkdir data && chown 10001:10001 data
USER 10001:10001

ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["python", "server.py"]
