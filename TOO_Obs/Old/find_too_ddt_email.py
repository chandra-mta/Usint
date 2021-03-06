#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################################
#                                                                                                               #
#   find_too_ddt_email.py: find newly approved ddt and/or too observations and update ddt_list and too_list     #
#                                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                           #
#                                                                                                               #
#           last update: Mar 20, 2018                                                                           #
#                                                                                                               #
#################################################################################################################


import sys
import os
import string
import re
import getpass

#
#--- reading directory list
#

#path = '/proj/web-cxc/cgi-gen/mta/Obscat/ocat/Info_save/dir_list_new'           #---- test directory list path
#path = '/data/mta4/CUS/www/Usint/TOO_Obs/too_dir_list'                                #---- live directory list path
#path = '/data/udoc1/ocat/Info_save/too_dir_list_py'
path = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

#
#--- append path to a private folder
#

sys.path.append(bin_dir)

import readSQL         as tdsql
import tooddtFunctions as tdfnc

#
#--- check who is the user, and set a path to Log location
#
user = getpass.getuser()
user = user.strip()
if user == 'mta':
    temp_dir = mtemp_dir
elif user == 'cus':
    temp_dir = ctemp_dir
elif user == 'html':
    temp_dir = htemp_dir
else:
    temp_dir = './'


#-----------------------------------------------------------------------------------------------------
#-- read_ddt_too_from_email: extreact TOO/DDT obsid from cus email archive                         ---
#-----------------------------------------------------------------------------------------------------

def read_ddt_too_from_email():

    """
    extreact TOO/DDT obsid from cus email achive. 
    input:  none, but read from the current email archive
    output: [tooList, ddtList]  --- a list of tooList and ddtList
    """
    #ifile = '/stage/mail/mta'
    ifile = '/data/mta4/CUS/www/Usint/TOO_Obs/Mscript/mta_mail'

    f     = open(ifile, 'r')
    data  = [line.strip() for line in f.readlines()]
    f.close()

    tooSet = []
    ddtSet = []

    chk    = 0
    for ent in data:
        if chk == 0:
            mc1 = re.search('Recently Approved ', ent)
            if mc1 is not None:
                mc = re.search('Subject', ent)
                if mc is not None:
                    mc = re.search('Re:', ent)
                    if mc is None:
                        chk = 1
            else:
                continue
        else:
            mc2 = re.search('From:',  ent)
            if mc2 is not None:
                chk = 0
                continue

            mc3 = re.search('Obsid ', ent)
            if mc3 is not None:
                atemp = re.split('\s+', ent)
                obsid = atemp[1].strip()

                mc = re.search('DDT', ent)
                if mc is not None:
                    ddtSet.append(int(obsid))
                else:
                    tooSet.append(int(obsid))

                chk = 0
#
#--- TOO case
#
    tooList = []
    if len(tooSet) > 0:
#
#---- remove duplicated entries
#
        tempList = tdfnc.removeDuplicate(tooSet, sorted='yes')
#
#---- only "unobserved" status ones are probably actually new. 
#
        if len(tempList) > 0:
            for ent in tempList:
                status = get_obs_status(ent)
                if status == 'unobserved':
                    tooList.append(ent)
#
#--- DDT case
#
    ddtList = []
    if len(ddtSet) > 0:
        tempList = tdfnc.removeDuplicate(ddtSet, sorted='yes')

        if len(tempList)> 0:
            for ent in tempList:
                status = get_obs_status(ent)
                if status == 'unobserved':
                    ddtList.append(ent)

    return [tooList, ddtList]


#---------------------------------------------------------------------------------------------
#-- get_obs_status: get a status of obsid                                                   --
#---------------------------------------------------------------------------------------------

def get_obs_status(obsid):
    """
    get a status of obsid
    input:  obsid   --- obsid   
    output: status  --- status. if it is not assigned, 'na' will be returned
    """
    try:
        monitor = []
        group   = []
        sqlinfo = tdsql.get_target_info(obsid, monitor, group)
        status  = sqlinfo[8]
    except:
        status  = 'na'

    return status

#---------------------------------------------------------------------------------------------
#-- remove_old_obs: remved archived or cancelled observations and updated obs idate of list --
#---------------------------------------------------------------------------------------------

def remove_old_obs(list):
    """
    remved archived or cancelled observations and update obs date of the list
    input:  list    --- too_list or ddt_list
    outpu:  none, but update <list> 
    """

    file = too_dir + list 
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    fo   = open(file, 'w')
    for ent in data:
        atemp = re.split('\s+', ent)

        try:
            monitor = []
            groupid = []
            sqlinfo = tdsql.get_target_info(atemp[2], monitor, groupid)
            status  = sqlinfo[8]
            lts_lt_plan = sqlinfo[12]
            soe_st_sched_date = sqlinfo[11]
    
            if soe_st_sched_date is not  None:
                date = soe_st_sched_date
            elif lts_lt_plan is not None:
                date = lts_lt_plan
            else:
                date = 'TBD'
    
        except:
            status = atemp[3]
            date   = atemp[5]

        if (status == 'observed') or (status == 'unobserved'):
            line = atemp[0] + '\t' + atemp[1] + '\t' + atemp[2] + '\t'
            line = line + str(status) + '\t' + atemp[4] + '\t' + atemp[5] + '\t' 
            line = line + str(date) + '\n'
            fo.write(line)

    fo.close()
    
#---------------------------------------------------------------------------------------------
#-- update_too_ddt_from_email: find approved obsid from email and update too/ddt lists -------
#---------------------------------------------------------------------------------------------

def update_too_ddt_from_email():

    """
    find approved obsid from email and update too/ddt lists.
    no input, but read from email achive. update too_dr/too_list and ddt_list

    """

#
#--- read existing TOO/DDT observations
#
    line = too_dir + 'too_list'
    tooObsid = tdfnc.read_current_obsid(line)
    line = too_dir + 'ddt_list'
    ddtObsid = tdfnc.read_current_obsid(line)

#
#--- read email and find whether any notificaiton of new DDT/TOO observations available
#

    tooNew  = []
    ddtNew  = []

    [tooList, ddtList] = read_ddt_too_from_email()         #--- function to pick up obsid from email archive

#
#--- extract only totally new Obsids
#
    if len(tooList) > 0:
        tooNew = list(set(tooList).difference(set(tooObsid)))

        if len(tooNew) > 0:
            tdfnc.update_list('too_list', tooNew)

    if len(ddtList) > 0:
        ddtNew = list(set(ddtList).difference(set(ddtObsid)))

        if len(ddtNew) > 0:
            tdfnc.update_list('ddt_list', ddtNew)
#
#--- remove archived and canceled observations and update obs date from the list
#
    remove_old_obs('ddt_list')
    remove_old_obs('too_list')


#---------------------------------------------------------------------------------------------

if __name__ == '__main__':

    update_too_ddt_from_email()

#    cmd = 'chgrp mtagroup ' + too_dir + '* '
#    os.system(cmd)
