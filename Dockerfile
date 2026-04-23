FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app
COPY requirements.txt .

#RUN grep -v "sentence-transformers" requirements.txt > requirements_filtered.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501

CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port 8000 & streamlit run app/ui/app.py --server.port 8501 --server.address 0.0.0.0"]