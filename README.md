### Local run

 - `pip install -r requirements.txt`
 - `./manage.py migrate`
 - `./manage.py runserver 0.0.0.0:8080`

### File JSON loader
 - `./manage.py import_patients patients.json`
 - `./manage.py import_payments payments.json`

### HTTP JSON loader
 - `POST 127.0.0.1:8080/patients/`
 - `POST 127.0.0.1:8080/payments/`
 
### HTTP JSON fetch
 - `GET 127.0.0.1:8080/patients/?payment_min=<val>&payment_max=<val>`
 - `GET 127.0.0.1:8080/payments/?external_id=<id>`
 
 
### Database 

SQLite database is used for simplicity. However, it can be replaced with Postgres or Oracle or Mysql as easy as modifying DATABASES settings in settings.py file. 

### Tests
  - `./manage.py test`
