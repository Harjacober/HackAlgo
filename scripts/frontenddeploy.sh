sudo git pull https://github.com/Harjacober/HackAlgo-Front-end-.git
sudo npm run build
sudo cp -r dist/ /var/www/html/
sudo systemctl restart nginx