#!/bin/bash
set -e

# Создаём папку для дашбордов
mkdir -p generated-dashboards

# Генерируем JSON
jsonnet -J vendor \
  monitoring/dashboards/fastapi-dashboard.libsonnet \
  > generated-dashboards/fastapi-dashboard.json

echo "✅ Dashboard успешно сгенерирован!"