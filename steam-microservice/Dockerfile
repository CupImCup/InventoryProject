FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN npm install steam-user
RUN npm install globaloffensive


COPY . .

CMD ["node", "index.js"]