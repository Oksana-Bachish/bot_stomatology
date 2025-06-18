#!/bin/sh

if [ "$POSTGRES_DB" = "stoma_bot" ]
then
    echo "Ждем postgres..."

    while ! nc -z "db_bot" $POSTGRES_PORT; do
      sleep 0.5
    done

    echo "PostgreSQL запущен"
fi

exec "$@"
