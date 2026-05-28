FROM nginx:alpine

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY pages/ /usr/share/nginx/html/pages/
COPY js/ /usr/share/nginx/html/js/
COPY css/ /usr/share/nginx/html/css/
COPY index.html /usr/share/nginx/html/index.html

# nginx:alpine con envsubst: usa /etc/nginx/templates/ para sustituir variables de entorno
# Genera config.js con BACKEND_URL y luego arranca nginx (que procesa templates automaticamente)
CMD ["/bin/sh", "-c", "echo \"window.BACKEND_URL = '${BACKEND_URL:-}'\" > /usr/share/nginx/html/js/config.js && /docker-entrypoint.sh nginx -g 'daemon off;'"]
