FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

# Render などホスティング先が割り当てる $PORT を尊重（未設定ならローカル用に 8000）
CMD uvicorn api_main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --timeout-keep-alive 300
