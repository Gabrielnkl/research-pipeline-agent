FROM node:18-alpine

WORKDIR /app

# Install dependencies FIRST
COPY package.json package-lock.json* ./
RUN npm install

# Then copy code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]