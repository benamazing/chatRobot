#!/usr/bin/sh

cd /data/study/python/chatRobot
echo "Copying static js/css files to Nginx root directory..."
cp -rf ./static /usr/share/nginx/html/stock/
echo "Change owner to nginx"
chown -R nginx:nginx /usr/share/nginx/html/stock
echo "Done!"

