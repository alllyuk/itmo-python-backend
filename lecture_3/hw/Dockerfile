FROM python:3.12 as base

WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

FROM base as app

CMD ["uvicorn", "shop_api.main:app", "--host", "0.0.0.0", "--port", "8080"]