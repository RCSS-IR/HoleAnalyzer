for x in `find . -name '*_log.tar.gz'`
do
	echo $x
	tar xvfz $x
done
# for x in `find . -name '*.tar.gz'`
# do
# 	echo $x
# 	tar xvfz $x
# done
mkdir rcl/
for x in `find . -name '*.rcg'`
do
	echo 'removing' $x
	rm $x
done
for x in `find . -name '*.rcl'`
do
	echo 'moving' $x
	cp $x rcl/
	rm $x
done
