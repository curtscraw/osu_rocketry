import datetime
from time import sleep
log = open("two_hour_test.log", "rw+")
print "Beginnig test..."
log.seek(0)
while 1:
	print datetime.datetime.utcnow()
	print "Writing to file..."
	log.write(str(datetime.datetime.utcnow()))
	log.write("\n")
	sleep(1)
