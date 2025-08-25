# Используем официальный образ Nginx
FROM nginx:latest

# Копируем конфигурацию Nginx в контейнер
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем статические файлы веб-сайта
COPY html/ /usr/share/nginx/html/

# Открываем порт 80
EXPOSE 80
