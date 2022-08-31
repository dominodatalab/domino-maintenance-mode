FROM quay.io/domino/python-public:3.10.4-slim
RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip
WORKDIR /app
COPY setup.py .
RUN pip install -e .
COPY domino_maintenance_mode domino_maintenance_mode
RUN chown -R 1000:1000 /app
USER 1000
ENTRYPOINT ["dmm"]
CMD ["--help"]
