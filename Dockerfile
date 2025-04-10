FROM node:16 as stylebuild

WORKDIR /home

COPY style/package.json .
COPY style/webpack.config.js .
COPY style/src ./src

RUN npm install
RUN npm run build

FROM python:3.9.7 as transcrypt

RUN apt update && apt install -y openjdk-11-jre-headless
WORKDIR /home

COPY src/static/terms.py .
COPY src/static/items.py .
COPY src/static/search.py .
COPY src/static/mirador.py .
COPY src/static/ui_util.py .

RUN pip install Transcrypt==3.9.0 htmltree==0.7.6


RUN transcrypt -bm terms.py && mv __target__ terms
RUN transcrypt -bm items.py && mv __target__ items
RUN transcrypt -bm search.py && mv __target__ search
RUN transcrypt -bm mirador.py && mv __target__ mirador

FROM python:3.9.7

COPY --from=stylebuild /home/static /home/src/static

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src /home/src
COPY scripts/*py /home/scripts/

COPY --from=transcrypt /home/terms /home/src/static/terms
COPY --from=transcrypt /home/items /home/src/static/items
COPY --from=transcrypt /home/search /home/src/static/search
COPY --from=transcrypt /home/mirador /home/src/static/mirador

WORKDIR /home/src

COPY data/CIT.dmp /home/src/
COPY data/CATALOG.dmp /home/src/

RUN python /home/scripts/convert_todb.py CIT.dmp CATALOG.dmp

CMD ["uvicorn", "--port", "8000", "--host", "0.0.0.0", "app:app"]