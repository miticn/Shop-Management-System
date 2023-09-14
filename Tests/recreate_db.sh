docker-compose -f ../Authentication/auth.yaml down -v
docker-compose -f ../Store/store.yaml down -v
docker-compose -f ../Authentication/auth.yaml up -d
docker-compose -f ../Store/store.yaml up -d