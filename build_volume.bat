@REM builds named volume and populates it with the contents of icc_git_input, expects icc_git_input to be one directory up from this script

docker volume create --name icc_git_input
docker container create --name dummy --volume icc_git_input:/icc_git_input alpine
docker cp ../icc_git_input dummy:/
docker rm dummy
