# Frontend Dockerfile
FROM nginx:alpine

# Copy frontend files
COPY public /usr/share/nginx/html/public
COPY css /usr/share/nginx/html/css
COPY js /usr/share/nginx/html/js

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
