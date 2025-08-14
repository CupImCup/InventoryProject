
# importing datetime module for now()
import datetime

# using now() to get current time
current_time = datetime.datetime.now()


current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
# Printing value of now.
print ("Time now at greenwich meridian is : "
                                    , end = "")
print (current_time)