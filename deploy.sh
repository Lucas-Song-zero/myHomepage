HOST="www.weitao-jiang.cn"
WORKDIR="/srv/homepage/Home"
SERVICENAME="homepage"


if [ "$(id -u)" = "0" ]; then
    echo "Switching to user runner"
    su - runner -c "$0"
    exit
fi
# git clone

cd $WORKDIR
git pull origin master
cd $WORKDIR/..
echo "Build python dependency"

python3 -m venv venv
source venv/bin/activate

pip install -r $WORKDIR/requirements.txt -q
pip install gunicorn -q

echo "Checking database integrity..."
python $WORKDIR/scripts/check_and_migrate_db.py

echo "Restarting service $SERVICENAME"
sudo systemctl restart $SERVICENAME

echo "Deployment completed, visit https://$HOST"