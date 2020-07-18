#!/bin/bash

BASEDIR=$(dirname "$0")
rm $BASEDIR/db.sqlite3
PYTHONPATH=$BASEDIR/.. python $BASEDIR/manage.py migrate
echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', 'admin@example.org', 'admin')" | \
  PYTHONPATH=$BASEDIR/.. python $BASEDIR/manage.py shell
