FROM python:3.11

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]