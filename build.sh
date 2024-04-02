#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt


(cd app/static_src/ &&
 npm install &&
 npm run build
)

# Convert static asset files
python manage.py collectstatic --no-input
python manage.py makemigrations app
python manage.py migrate