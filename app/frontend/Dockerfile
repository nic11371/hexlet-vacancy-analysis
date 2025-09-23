# Используем официальный образ Node.js
FROM node:20-alpine

# Устанавливаем рабочую директорию
WORKDIR /app/frontend
# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Экспонируем порт Vite
EXPOSE 5173

# Запускаем dev-сервер с горячей перезагрузкой
CMD ["npm", "run", "dev"]