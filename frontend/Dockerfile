FROM nginx:alpine

ENV NGINX_ENVSUBST_VARS='$PORT $BACKEND_URL'

COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY pages/ /usr/share/nginx/html/pages/
COPY js/ /usr/share/nginx/html/js/
COPY css/ /usr/share/nginx/html/css/
COPY index.html /usr/share/nginx/html/index.html

# El entrypoint de nginx:alpine procesa /etc/nginx/templates/*.template con envsubst
# (sustituye ${PORT} y ${BACKEND_URL} en nginx.conf antes de arrancar)
