# Backend Koperasi — FastAPI + Uvicorn
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Jakarta

WORKDIR /app

# Layer dependensi dulu supaya build ulang cepat kalau hanya kode yang berubah.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY scripts ./scripts

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# /health juga mem-ping MongoDB: unhealthy = backend hidup tapi DB tidak terjangkau.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)" || exit 1

# --proxy-headers: IP asli pengguna (untuk audit trail) diambil dari X-Forwarded-For yang dikirim nginx.
# forwarded-allow-ips="*" aman di sini karena port 8000 TIDAK dibuka ke luar; hanya container nginx yang bisa menjangkaunya.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
