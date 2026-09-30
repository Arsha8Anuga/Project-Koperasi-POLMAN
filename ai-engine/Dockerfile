# AI engine Toko Koperasi — worker Python (tanpa port HTTP)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Jakarta

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY engine ./engine

RUN useradd --create-home --uid 10001 appuser
USER appuser

# Sehat = denyut ke MongoDB masih diperbarui (lihat engine/healthcheck.py)
HEALTHCHECK --interval=60s --timeout=15s --start-period=60s --retries=3 CMD python -m engine.healthcheck || exit 1

CMD ["python", "-m", "engine"]
