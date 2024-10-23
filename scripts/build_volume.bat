@REM builds named volume and populates it with the contents of icc_dumps

docker volume create --name icc_dumps
docker container create --name dummy --volume icc_dumps:/icc_dumps alpine
docker cp %1/. dummy:/icc_dumps
docker rm dummy
