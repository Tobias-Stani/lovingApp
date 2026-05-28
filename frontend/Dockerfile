FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY pages/ /usr/share/nginx/html/pages/
COPY js/ /usr/share/nginx/html/js/
COPY css/ /usr/share/nginx/html/css/
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 3000

# Entrypoint: inyecta BACKEND_URL en config.js antes de arrancar nginx
CMD ["/bin/sh", "-c", "echo \"window.BACKEND_URL = '${BACKEND_URL:-}'\" > /usr/share/nginx/html/js/config.js && nginx -g 'daemon off;'"]
