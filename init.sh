export PROJ_DIR=.

if [ ! -d ${PROJ_DIR}/antlr-4.9.2-complete.jar ]; then

fi

export ANTLR_JAR=${PROJ_DIR}/antlr-4.9.2-complete.jar

python3 -m venv .env

pip3 install antlr4-python3-runtime==4.9.2

mkdir -p test/testcases/
mkdir -p test/solutions
