FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY pages/ /usr/share/nginx/html/pages/
COPY js/ /usr/share/nginx/html/js/
COPY css/ /usr/share/nginx/html/css/
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 3000
