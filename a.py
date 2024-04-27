# using datetime module
import datetime;
 
# ct stores current time
ct = datetime.datetime.now()
print(ct.year, " ", ct.month, " ", ct.day)
print("current time:-", ct)
 
# ts store timestamp of current time
ts = ct.timestamp()
print("timestamp:-", ts)