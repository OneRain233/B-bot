FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./ /app/

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple