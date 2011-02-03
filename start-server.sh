#! /bin/bash -e
cd communication
. set-classpath.sh
java Server $*
