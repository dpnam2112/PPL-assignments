# Activate the virtual environment and required environment variables

export PROJ_DIR=$(pwd)

mkdir -p $PROJ_DIR/src/test/testcases/
mkdir -p $PROJ_DIR/src/test/solutions/

export ANTLR_JAR=$PROJ_DIR/antlr-4.9.2-complete.jar

. $PROJ_DIR/.env/bin/activate
