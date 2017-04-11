# -*- coding: UTF-8 -*-
import re
import io
import datetime
import time
from dateutil.parser import parse
import itertools
from operator import itemgetter
import sys


# Method to convert epoch to [01/Jul/1995:00:00:12 -0400] format
# ----------------------------------------------------------------------------------------------------------------------
def epoch_to_string(m):
    t = datetime.datetime.fromtimestamp (float (m))
    month_num = t.strftime ('%m')
    month_num = int (month_num)
    day_num = t.strftime ('%d')
    year_num = t.strftime ('%Y')
    hour_num = t.strftime ('%H')
    minute_num = t.strftime ('%M')
    second_num = t.strftime ('%S')
    n = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }
    month_month = n[month_num]
    month_string = day_num + '/'
    month_string += month_month
    month_string += '/'
    month_string += year_num
    month_string += ':'
    month_string += hour_num
    month_string += ':'
    month_string += minute_num
    month_string += ':'
    month_string += second_num

    try:
        return month_string
    except:
        raise ValueError('Not a number')
# ----------------------------------------------------------------------------------------------------------------------


# Method to return integer numbers from [01/Jul/1995:00:00:12 -0400] format
# ----------------------------------------------------------------------------------------------------------------------
def numbers_from_datetime(string):

    def month_string_to_number(string):  # Method to return the corresponding number of month's string
        m = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12
        }
        s = string.strip()[:3].lower()

        try:
            out = m[s]
            return out
        except:
            raise ValueError('Not a month')

    # Formatting the date so that we can use the numeric data
    [day, month, rest] = string.split('/')
    [year, hours, minutes, rest] = rest.split(':')
    [seconds, timezone] = rest.split(' -')
    month = month_string_to_number(month)
    year = int(year)  # Converting everything to integer
    month = int(month)
    day = int(day)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    return year, month, day, hours, minutes, seconds
# ----------------------------------------------------------------------------------------------------------------------

# Opening the file and parsing and splitting the data
# ----------------------------------------------------------------------------------------------------------------------
with io.open(sys.argv[1], 'r', encoding='latin-1') as infile:  # We don't have to infile.close() using 'with'
    # Need to use encoding = latin-1, otherwise file will be opened with our OS dependent system default codec
    # Common ones are Latin-1 and UTF-8

    # Declare lists for the all data members
    list_of_IP_address = []
    list_of_time = []
    list_of_resource_site = []
    list_of_reply_code = []
    list_of_bytes = []

    no_of_rows = 0

    for line in infile:  # looping through the lines
        line = line.strip()  # remove all the leading and trailing spaces
        no_of_rows += 1  # Keeping track of no of entries

        # Splitting the line into different data members
        # --------------------------------------------------------------------------------------------------------------
        [a, b] = (line.split("- -"))  # split using "--" to separate IP address from the rest
        a = a.replace(" ", "")  # removing the space(s) since the log file can be noisy
        q = re.compile('\d{2}\]')
        r = q.findall(b)
        r = str(r)
        r = r.replace("['", "")
        r = r.replace("']", "")

        [b, c] = b.split(r)
        b = b.replace("[", "")
        b = b.strip()
        c = c.strip()

        p = re.compile('\" \d{3}')
        d = p.findall(c)
        d = str(d)
        d = d.replace('\'" ', '')
        d = d.replace('\'', '')
        d = d.replace('[', '')
        d = d.replace(']', '')

        gg = " " + d + " "
        [c, e] = c.split(gg)
        e = e.strip()
        if e == "-":  # Some lines in the log file will list - in the bytes field.
            e = "0"   # For the purposes of this challenge, that should be interpreted as 0 bytes.
        #c = c.replace("GET /", "")  # need to get rid of 'GET'
    # ------------------------------------------------------------------------------------------------------------------

        # Appending the relevant data members in the list
        # --------------------------------------------------------------------------------------------------------------
        list_of_IP_address.append(a)  # IP address
        list_of_time.append(b) # would be done later after formatting to appropriate style
        list_of_resource_site.append(c)  # resource site
        list_of_reply_code.append(d)  # reply code--401 bad request
        list_of_bytes.append(e)  # bytes
# ----------------------------------------------------------------------------------------------------------------------


# Feature 1 : Top 10 Most active host/IP address that have accessed the site
# ----------------------------------------------------------------------------------------------------------------------
#  Turning a list of IP addresses into a IP addresses vs their frequencies Dictionary
dict_of_IP = {}  # Empty Dictionary of IP addresses
for IP_address in list_of_IP_address:  # We need exception handling since the dictionary is empty in the beginning
    try:
        dict_of_IP[IP_address] += 1  # Increment with each repetition
    except KeyError:
        dict_of_IP[IP_address] = 1  # First count if not repeated
        # Here dict_of_IP[IP_address] is the value where their frequency is the key

# Sorts the Dictionary by the value first in descending order, then by lexicographical order by Keys for ties
top_10_active_ip = sorted(dict_of_IP.items(), key=lambda k: (-k[1], k[0]))[:10]  # k(1) is the value, k(0) is the key

# Writing a dictionary to a text file with one line for every 'key:value'
my_file = open(sys.argv[2], "w")  # Top 10 most active host/IP that have accessed the site
for key, value in top_10_active_ip:
    my_file.write(str(key)+"," + str(value)+"\n")
# ----------------------------------------------------------------------------------------------------------------------


# Feature 2: Top 10 resource that consume the most bandwidth
# ----------------------------------------------------------------------------------------------------------------------
# Iterating through two lists - resource and bytes simultaneously
# Note that zip in python 3 does the same task as itertools.izip  in python 2
dict_of_resources_bytes = {}
for resource_site, bytes_consumed in zip(list_of_resource_site, list_of_bytes):  # Here it returns a iterable
    bytes_consumed = int(bytes_consumed)  # Changing into integer for addition
    try:
        dict_of_resources_bytes[resource_site] += bytes_consumed
    except KeyError:
        dict_of_resources_bytes[resource_site] = bytes_consumed

# Sorts the Dictionary by the value first in descending order
top_10_bandwidth_consuming_resources = sorted(dict_of_resources_bytes.items(), key=lambda k: k[1], reverse=True)[:10]
                                                                                # k(1) is the value, k(0) is the key

# Writing a dictionary to a text file with one line for every 'key:value', top 10 bandwidth consuming resources
my_file = open(sys.argv[4], "w")
for key, value in top_10_bandwidth_consuming_resources:
    for ch in ['"POST ', ' HTTP/1.0"', '"GET ', '"HEAD ', '"']:  # Getting rid of these
        if ch in key:
            key = key.replace(ch, '')
    key = key.strip()

    my_file.write(str(key)+"\n")
# ----------------------------------------------------------------------------------------------------------------------

# Feature 3: List in descending order the site’s 10 busiest (i.e. most frequently visited) 60-minute period.
# ----------------------------------------------------------------------------------------------------------------------
occurance = 0  # Variable to Track Count of elements in array
index=0
dict_of_occurance =[]
list_of_window_start = []
year_No3, month_No3, day_No3, hours_No3, minutes_No3, seconds_No3 = numbers_from_datetime(list_of_time[0])
time_stamp_No3 = int(datetime.datetime(year_No3, month_No3, day_No3, hours_No3, minutes_No3, seconds_No3).timestamp())  # Epoch of the first data point
CONST_EPOCH = (time_stamp_No3)  # EPOCH OF STARTING TIME OF OUR DATA
window_start = int(time_stamp_No3)-CONST_EPOCH  # Normalizing to 0 
window_size = int(3600)  # 60 minutes window 
window_end = window_start + window_size

for i in range(0,len(list_of_time),1):
    for j in range(0,len(list_of_time),1):
        year_No4, month_No4, day_No4, hours_No4, minutes_No4, seconds_No4 = numbers_from_datetime(list_of_time[j])
        time_stamp_No4 = int(datetime.datetime(year_No4, month_No4, day_No4, hours_No4, minutes_No4, seconds_No4).timestamp())  # Epoch
        time_stamp_No4 = time_stamp_No4-CONST_EPOCH # Time stamp of the first data from the log file 
        if time_stamp_No4 <= window_end and time_stamp_No4>=window_start: # If the first data's time stamp remains in our first 60 min window 
            occurance = occurance + 1
    window_start_for_conversion = epoch_to_string(window_start+ CONST_EPOCH) # Converting back to string for our purpose 
    if(index<10): # Since we are sorting and keeping only the top 10 
        dict_of_occurance.insert(index,{
                    "Start Time": window_start_for_conversion,
                    "Count": occurance
                })
    else:
                dict_of_occurance=sorted(dict_of_occurance, key=itemgetter('Count'),reverse=True)#sort the list
                if  occurance > dict_of_occurance[9]['Count']: # We need to eliminate anything more than 10 itmes 
                    dict_of_occurance.pop (9)# Pop the lowest elemet
                    dict_of_occurance.insert (index, {
                    "Start Time": window_start_for_conversion,
                    "Count": occurance
                })

    index += 1
    occurance = 0
    window_start += 1
    window_end += 1

#  Writing a dictionary to a text file with one line for every 'key:value', top 10 60 minutes period
my_file = open(sys.argv[3], "w")
for key in dict_of_occurance:
    my_file.write(str(key['Start Time'])+' -0400,' + str(key['Count'])+"\n")
# # --------------------------------------------------------------------------------------------------------------------


# Feature 4: Detect patterns of three consecutive failed login attempts over 20 seconds in order to block all further
#            attempts to reach the site from the same IP address for the next 5 minutes.
#            Each attempt that would have been blocked should be written to a log file named blocked.txt.
# ----------------------------------------------------------------------------------------------------------------------

rejected_list_of_everything = []

# Declare blocked lists for the all data members
blocked_list_of_IP_address = []
blocked_list_of_time = []
blocked_list_of_resource_site = []
blocked_list_of_reply_code = []
blocked_list_of_bytes = []

n = 0  # just keeping track of number of blocked items
for i in range(len(list_of_reply_code)):  # iterating through the entire rows of log file
    if list_of_reply_code[i] == '401':
        n = n + 1
        rejected_list_of_everything.append({
           'URL address': list_of_IP_address[i],
           'time': list_of_time[i],
           'resource_site': list_of_resource_site[i],
           'reply code': list_of_reply_code[i],
           'bytes': list_of_bytes[i],
        })

sorted_by_URL_rejected_list_of_everything = sorted(rejected_list_of_everything, key=itemgetter('URL address'))  # group and sort the rejected list by URL

i = 0  # Counter for the loop of rejected items
alist = []  # This list is later used to remove duplicate items
while i < (len(sorted_by_URL_rejected_list_of_everything)-2):

    # Accessing a list item inside a dictionary and comparing them for repetition
    if (sorted_by_URL_rejected_list_of_everything[i]['URL address'] ==
       sorted_by_URL_rejected_list_of_everything[i + 1]['URL address'] ==
       sorted_by_URL_rejected_list_of_everything[i + 2]['URL address']):
        # Checking if the repetition has occurred with 20 secs
        # year1, month1, time_stamp1... for first occurrence, year3, month3, time_stamp3 for third occurrence
        year1, month1, day1, hours1, minutes1, seconds1 = numbers_from_datetime(sorted_by_URL_rejected_list_of_everything[i]['time'])
        time_stamp_1 = (datetime.datetime(year1, month1, day1, hours1, minutes1, seconds1).timestamp())
        year3, month3, day3, hours3, minutes3, seconds3 = numbers_from_datetime(sorted_by_URL_rejected_list_of_everything[i + 2]['time'])
        time_stamp_3 = (datetime.datetime(year3, month3, day3, hours3, minutes3, seconds3).timestamp())

        if(time_stamp_3-time_stamp_1) < 21:  # If 3 consecutive failed log in attempts in 20 seconds, then we need to log successful & unsuccessful attempts for 5 mins from the main list
            for jk in range(0,no_of_rows,1):  # Iterating through the main log file
                year4, month4, day4, hours4, minutes4, seconds4 = numbers_from_datetime(list_of_time[jk])
                time_stamp_4 = (datetime.datetime(year4, month4, day4, hours4, minutes4, seconds4).timestamp())

                if sorted_by_URL_rejected_list_of_everything[i]['URL address'] == list_of_IP_address[jk] and time_stamp_4 > time_stamp_3 and (time_stamp_4 - time_stamp_3) < 301:  # less than 5 mins block

                    alist.append(jk)  # Append for the logged items so that we can remove the repeated ones later

                if time_stamp_4 - time_stamp_3 > 300:  # Need not to go beyond 5 minutes
                    break
    i = i + 1
alist1 = list(set(alist))  # Removes duplicate elements since when we iterate, we will encounter already logged URL again
alist1 = sorted(alist1)

# Appending the blocked relevant data members in the list ------------
for k in alist1:
    blocked_list_of_IP_address.append(list_of_IP_address[k])
    blocked_list_of_time.append(list_of_time[k])
    blocked_list_of_resource_site.append(list_of_resource_site[k])
    blocked_list_of_reply_code.append(list_of_reply_code[k])
    blocked_list_of_bytes.append(list_of_bytes[k])
# ---------------------------------------------------------------------

alist1 = []  # Emptying the list for next iteration

# Writing a list to a text file with one line for every 'key:value'
my_file = open(sys.argv[5], "w")
for (IP, time, resource, reply_code, byte) in zip(blocked_list_of_IP_address, blocked_list_of_time, blocked_list_of_resource_site, blocked_list_of_reply_code, blocked_list_of_bytes):
    my_file.write(str(IP)+" - - " + "["+str(time) + "00] " + resource + " "+reply_code + " "+byte+"\n")
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
print ('Done')
