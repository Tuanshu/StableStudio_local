FROM node:20-alpine

LABEL description="StableStudio_local" version="0.1.0" maintainer="TS"

RUN apk update
RUN apk add git

RUN git clone https://github.com/Tuanshu/StableStudio_local.git
WORKDIR StableStudio_local

RUN yarn

EXPOSE 3000

# ENTRYPOINT yarn dev --host 
ENTRYPOINT yarn dev:use-webui-plugin --host