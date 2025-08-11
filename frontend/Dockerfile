FROM node:18

WORKDIR /app

COPY package.json tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts ./
COPY src ./src
COPY index.html ./

RUN npm install

CMD ["npm", "run", "dev"]
