#!/bin/bash
# Instalar dependencias
pip install -r requirements.txt

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Aplicar migraciones (opcional, recomendado solo si la DB es externa y está configurada)
# python manage.py migrate --noinput
