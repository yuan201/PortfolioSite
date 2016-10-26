#!/bin/bash

NAME="chelinfeite"
DJANGODIR=/home/yuan/github/portfoliosite
SOCKFILE=/tmp/chelinfeite.ddns.org.9000.socket
USER=yuan


cd $DJANGODIR

exec /home/yuan/.virtualenvs/ptf/bin/gunicorn PortfolioSite.wsgi:application \
     --name $NAME \
     --user $USER \
     --bind=unix:$SOCKFILE
