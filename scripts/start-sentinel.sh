#!/bin/sh
set -e

echo "⏳ Ожидание доступности redis..."

# Проверяем доступность Redis через TCP (без установки пакетов)
until redis-cli -h redis ping > /dev/null 2>&1; do
  echo "🟡 Жду, пока Redis станет доступным..."
  sleep 1
done

echo "✅ Redis доступен. Запускаю Sentinel..."
exec redis-sentinel /etc/redis/sentinel.conf