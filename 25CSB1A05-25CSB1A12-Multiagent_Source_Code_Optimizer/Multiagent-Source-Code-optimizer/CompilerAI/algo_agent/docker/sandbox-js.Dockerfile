# OptAgent JavaScript Sandbox Image (Node 22 LTS + Babel facts extractor)
FROM node:22-slim

RUN mkdir -p /opt/jsfacts && cd /opt/jsfacts && \
    npm init -y >/dev/null 2>&1 && \
    npm install --no-audit --no-fund @babel/parser @babel/traverse >/dev/null 2>&1

ENV NODE_PATH=/opt/jsfacts/node_modules
WORKDIR /tmp
