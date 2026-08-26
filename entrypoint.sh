#!/bin/sh

service ssh start

cd /app/backend
exec gunicorn --bind 0.0.0.0:8000 lailaps:app