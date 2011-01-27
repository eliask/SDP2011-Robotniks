#!/bin/sh

export CLASSPATH=.:lejos_nxj/lib/jtools.jar:lejos_nxj/lib/pccomm.jar:lejos_nxj/lib/pctools.jar:lejos_nxj/3rdparty/lib/bcel.jar:lejos_nxj/3rdparty/lib/bluecove-gpl.jar:lejos_nxj/3rdparty/lib/bluecove.jar:lejos_nxj/3rdparty/lib/commons-cli.jar:lejos_nxj/3rdparty/lib/cpptasks.jar

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:bluez-4.86/lib
javac *.java

