#!/usr/bin/env /usr/local/bin/python

#########################################################################################################
#													#
#	write_this_week_too_poc.py: write out this week's POC to /data/mta/TOO-POC			#
#													#
#		author: t. isobe (tisobe@cfa.harvard.edu)						#
#													#
#		last update: Jun 27, 2013								#
#													#
#########################################################################################################

import sys
import os
import string
import re
import getpass

#
#--- set a couple of directory path
#
info_dir = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/'
temp_space = '/data/mta4/CUS/www/Usint/ocat/Working_dir/mta/write_this_week_too_poc'
#
#--- read POC list
#
cmd = 'cat ' + info_dir + 'this_week_person_in_charge > ' + temp_space
os.system(cmd)

f    = open(temp_space, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

cmd = 'rm ' + temp_space
os.system(cmd)
#
#--- exteact an email address of POC
#
for ent in data:
    m = re.search('#', ent)
    if m is not None:
	continue

    atemp = re.split('\,', ent)
    email = atemp[4]
    break
#
#--- write it out
#
f    = open('/home/mta/TOO-POC', 'w')
f.write(email)
f.write('\n')
f.close()
