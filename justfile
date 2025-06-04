start-docker-mysql-northwind:
  docker run --platform linux/amd64 -d -p 3307:3306 --name northwind -e MYSQL_ROOT_PASSWORD=supersecret manchestercodes/northwind

stop-docker-mysql-northwind:
  docker stop $(docker ps -a -q --filter "status=running" --filter "ancestor=manchestercodes/northwind")

docker-rm-stopped-mysql-northwind:
  docker rm $(docker ps -a -q --filter "status=exited" --filter "ancestor=manchestercodes/northwind")

docker-update-dates:
  docker exec -i northwind mysql -uroot -psupersecret northwind < update_dates.sql

run: docker-update-dates
  uv run src/main.py --host 127.0.0.1 --port 8887


