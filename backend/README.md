# Anwendung ausführen:

````bash
docker-compose build
docker-compose up
docker exec -it postgres_container psql -U postgres -d microservices_db -f /path/to/init_db.sql
````

# Unittest ausführen:

````bash
docker exec -it flask_app python -m unittest discover -s administrative-service/tests -p "test_*.py"
````

