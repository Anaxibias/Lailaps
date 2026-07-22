#!/bin/bash

service ssh start

exec gunicorn --bind 0.0.0.0:8000 lailaps:app