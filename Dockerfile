FROM node:16 as stylebuild

WORKDIR /home

COPY style/package.json .
COPY style/webpack.config.js .
COPY style/src ./src

RUN npm install
RUN npm run build


FROM python:3.9.7


WORKDIR /home

COPY --from=stylebuild /home/static /home/static

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src /home

CMD ["uvicorn", "--port", "8000", "--host", "0.0.0.0", "src:app"]