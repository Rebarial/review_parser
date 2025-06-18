FROM python:3.12

WORKDIR /code/review_parser

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/review_parser/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]