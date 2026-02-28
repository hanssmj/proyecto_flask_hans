# Proyecto Flask + MySQL Hans Jeremi González Pin

## Requisitos
- Python 3.12
- XAMPP (Apache + MySQL)

## BD
1) Arranca Apache y MySQL en XAMPP
2) Abre phpMyAdmin: http://localhost/phpmyadmin
3) Importa `schema.sql` (crea `webapp_db` con `users` y `posts`)

## Pasos
1) Instalar XAMPP y arrancar Apache + MySQL

2) Importar el .sql en phpMyAdmin (crea BD + tablas + inserts)

3) python -m venv .venv

4) Activar venv

5) pip install -r requirements.txt

6) python -m flask --app app:app run

## Ejecutar (Windows)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m flask --app app:app run
