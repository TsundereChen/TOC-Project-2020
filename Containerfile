FROM public.ecr.aws/bitnami/python:3.9-prod
MAINTAINER TsundereChen email me@tsunderechen.io

WORKDIR /app
RUN apt update && apt install -y graphviz libgraphviz-dev gcc

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY *.py /app

CMD ["python", "/app/app.py"]
