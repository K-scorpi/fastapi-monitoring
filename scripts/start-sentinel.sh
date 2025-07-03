#!/bin/sh
set -e

echo "🔍 Проверка окружения..."

# Выведем текущую сеть и DNS
cat /etc/resolv.conf
nslookup redis

while true; do
  echo "⏳ Проверяю доступность redis..."
  ping -c1 redis && break || sleep 1
done

echo "✅ Redis доступен. Запускаю Sentinel..."
exec redis-sentinel /etc/redis/sentinel.conf