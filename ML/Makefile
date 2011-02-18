all: ml ML_pb2.py

ml: ml.c
	gcc -o ml ml.c -I/usr/include/python2.6 -l python2.6

ML_pb2.py: ML.proto
	protoc --python_out=. ML.proto

ml.c: ml.pyx
	cython --embed ml.pyx

clean:
	rm -f ml ml.c
