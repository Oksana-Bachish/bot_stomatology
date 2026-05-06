#!/bin/sh

echo "Ждем postgres..."

while ! nc -z db_bot 5432; do
  sleep 0.5
done

echo "PostgreSQL запущен"

exec "$@"