echo "run local VIMVer at 10.1.2.200 (don't forget to deactivate !)"
cd /home/vimver-client/VIMVer/
source /home/vimver-client/Environments/djangoProject_blankDjango/bin/activate

echo "check file access authorizations"
sudo chown vimver-client -fR ./
sudo chown :www-data -f ViralOceanView/
sudo chown :www-data -f ViralOceanView/db.sqlite3
sudo chown :www-data -fR ViralOceanView/static/

echo "check apache2 server"
sudo service apache2 restart