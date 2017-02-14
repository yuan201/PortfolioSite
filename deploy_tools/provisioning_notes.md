1. Basic Server Setup
	1. Install Ubuntu Server 16.03 LTS
	2. update and upgrade
	3. get git, emacs, Nginx, Gunicorn, Virtualenv and Wrapper
	4. setup /etc/network/interface properly

2. Setup SSH
	1. use ssh-keygen to generate the key
	2. ssh-copy-id -i ~/.ssh/id_rsa user@stageserver
	3. scp user@stageserver:~/.ssh/authorized_keys ~/.ssh/staging.pub
	4. paste the public key to Github

3. Setup router
	1. Port forward 9000 to stageserver:80 (remember to save it!)
	2. Test to make sure it works

4. Config pip
	1. create/modify ~/.pip/pip.conf to trust local server (enable it globally will cause mkvirtualenv to fail)

5. Setup Virtualenv
    1. git clone something
	2. cd something
	3. mkvirtualenv someenv --python=/usr/bin/python3
	4. pip install -i http://pypi.douban.com/simple -r requirements.txt
	5. note tushare doesn't work properly with the others, might need to manually install its dependency first
	6. psycopg2 is a big trouble, it need to be compiled from source.
    	1. sudo apt install ligpq-dev python3-dev build-essential postgresql-server-dev-all
	    2. pip install psocopg2
	7. python manage.py collectstatic


6. Setup PostgreSQL
	1. sudo apt-get install postgresql
	2. sudo -u postgres psql postgres
	3. CREATE ROLE yuan LOGIN CREATEDB PASSWORD 'labview';
	4. \q
	5. psql postgres
	6. CREATE DATABASE portfolios;
	7. \q

7. Try the Server
	1. run unittests
	2. python manage.py migrate
	3. python manage.py runserver ipaddr:8000 (default to 127.0.0.1 doesn't work when accessed from external interface)

8. Gunicorn Setup
	1. Install gunicorn using pip (so it's under virtualenv)
	2. test gunicorn with "gunicorn portfoliosite.wsgi:application"
	3. with Whitenoise support, all the static files should work properly
	4. update nginx conf file to use socket under /tmp
    5. copy .service tempalte to /etc/systemd/system
    6. copy gunicorn_start.sh to ~/
    7. systemctl start gunicorn_systemd.service to enable the service
    8. reboot and test
 

