FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HELA_ACCESS_MODE=paid \
    HELA_PUBLISHER="PHKS Creation" \
    HELA_WHATSAPP="+94715954563"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 10000
CMD ["python", "app/server.py"]
