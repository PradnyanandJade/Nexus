FROM python:3.12-slim

WORKDIR /app/backend

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# CMD ["python","run.py"]  # This will be used for local developement on windows instead of above CMD 