#/bin/bash
set -x
docker stop $(docker ps -a -q  -f name=linkat)
docker rm $(docker ps -a -q  -f name=linkat)
docker run -p 5000:5000 -p 3000:3000 --name linkat -t linkat:latest &
sleep 5
docker cp $1  $(docker ps -f name=linkat -q):/tmp/trace.json
docker exec  $(docker ps -f name=linkat -q) /bin/sh -c "cd /tmp && linkat-run -f /tmp/trace.json"
echo "Linkat is running on port 5000"
echo "Ready. Please open http://localhost:3000/ in your browser."