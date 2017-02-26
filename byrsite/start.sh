#!/bin/bash

export PATH=/usr/local/bin:$PATH

cd  /tmp/byrsite

gunicorn --max-requests-jitter 100 \
         --max-requests 200 \
         --timeout 120 \
         --graceful-timeout 120 \
         --worker-class=gevent \
         --access-logfile /tmp/byrsite/django_logs/access.log \
         --error-logfile /tmp/byrsite/django_logs/error.log \
         -n byrsearch_site -D \
         -p /tmp/byrsite/byrsearch_site.pid \
         --access-logformat "%(h)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s %(L)s \"%(f)s\" \"%(a)s\"" \
         byrsite.wsgi:application --bind 0.0.0.0:8080

sleep 2
pid=`cat /tmp/byrsite/byrsearch_site.pid 2>/dev/null`
status=`ps -ef | grep byrsearch_site | grep $pid | wc -l 2>/dev/null`
if [ $status -eq 2 ]; then
    echo "byrsearch_site start success, pid $pid"
else
    echo "byrsearch_site start failed."
fi
