FROM node:alpine

RUN apk update

# install python and pip
RUN apk add python3 python3-dev py3-pip
RUN pip3 install Flask tqdm pyparsing Flask-Cors

COPY . /opt/linkat
WORKDIR /opt/linkat
RUN ./install-linkat.sh
WORKDIR /opt/linkat/front
RUN npm install
RUN npm run build
RUN npm install -g serve

ENTRYPOINT [ "serve", "-s", "build"]