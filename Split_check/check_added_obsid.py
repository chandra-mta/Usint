#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################
#                                                                                                                       #
#   check_added_obsid.py: check obsid which is newly added for existing proposal id, send out a warning email to poc    #
#                                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                                   #
#                                                                                                                       #
#           last update: Jun 23, 2015                                                                                   #
#                                                                                                                       #
#########################################################################################################################

import sys
import os
import string
import re
import math
import random

path = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_dir_list_py'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

sys.path.append(bin_dir)
sys.path.append(mta_dir)

import convertTimeFormat    as tcnv
import tooddtFunctions      as tdfnc
import mta_common_functions as mcf
import readSQL              as sql

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)


#-----------------------------------------------------------------------------------------------
#-- compare_prop_lists: find newly added obsids and send warning eamil to poc                ---
#-----------------------------------------------------------------------------------------------

def compare_prop_lists():
    """
    find obsids which are newly added to the existing proposal id as it is possible candidates
    of split or clone observations, and send out a warning email to poc.
    input:  none 
    output: email to poc
    """
#
#--- read and create poc <---> email address dictionary
#
    f    = open('/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/usint_personal', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    email_list = {}
    for ent in data:
        atemp = re.split(':', ent)
        email_list[atemp[0]] = atemp[5]
#
#---- read the last prop_id <---> obsid list dictionary
#
    (prop_list, prop_dict, poc_dict) = read_prop_obsiid_table()
#
#---- get the most current prop_id <---> obsid list dictionary
#
    (temp_list, new_dict)  = get_prop_obsid_list(poc_dict)
#
#--- compare current and new list of obsids and find any changes
#
    save_change = []
    for ent in prop_list:
        prev_list = prop_dict[ent]
        new_list  = new_dict[ent]

        diff_list = list(set(new_list) - set(prev_list))
        if len(diff_list) > 0:
            line = str(ent) + '<>' + str(diff_list[0])

            for i in range(1, len(diff_list)):
                line = line + ':' + str(diff_list[i])
            save_change.append(line)
#
#--- find newly added obsids
#
    if len(save_change) > 0:
        for ent in save_change:
            atemp = re.split('<>', ent)
#
#--- find poc for the observations
#
            try:
                poc = poc_dict[atemp[0]]
            except:
                poc = find_poc(atemp[0], atemp[1])
  
            obsid = atemp[1]
#
#--- the following information is used by /data/mta4/obs_ss/find_scheduled_obs.perl
#
            fo    = open('/data/mta4/CUS/www/Usint/TOO_Obs/Split_check/no_sign_off_list', 'a')
            fo.write(obsid)
            fo.write('\n')
            fo.close()
#
#--- find email address of the poc
#
            try:
                email = email_list[poc]
                chk   = 0
            except:
                email = 'tisobe@cfa.harvard.edu'
                chk   = 1
#
#--- find the proposal title
#
            title = find_title(obsid)
#
#--- create a warning email and send to the poc
#
            line = "It seems obsid: " + str(atemp[1]) + ' of Proposal #: ' + str(atemp[0]) 
            line = line + ' (Proposal Title: ' + title + ') is added to '
            line = line + 'under your responsibility. Please check whether this observation is indeed yours,  '
            line = line + ' and if so, initiate the standard procedure.\n\n'
            line = line + '(POC: ' + email + ')\n'

            if chk = 1:
                aline = 'The following notification is created for unknown POC. Check the prop-id <---> poc list.\n\n'
                line  = aline + line                

            fo = open(zspace, 'w')
            fo.write(line)
            fo.close()

            cmd = 'cat ' + zspace + '| mailx -s"Subject: Possible Split Observation (poc: ' + email + ')" isobe@head.cfa.harvard.edu '
            os.system(cmd)
            if chk == 0:
                cmd = 'cat ' + zspace + '| mailx -s"Subject: Possible Split Observation (poc: ' + email + ')" swolk@head.cfa.harvard.edu'
                os.system(cmd)
##
##                cmd = 'cat ' + zspace + '| mailx -s"Subject: Possible Split Observation (test version)" -ccus@head.cfa.harvard.edu ' + email
##                os.system(cmd)

#
#---- find a proposer/observer's email and send email to her/him
#
#            [observer, omail]  = find_observer_email(obsid)
#
#            cmd = 'cat ' + zspace + '| mailx -s"Subject: Possible Split Observation (test version)" -ccus@head.cfa.harvard.edu ' + omail
#            os.system(cmd)

            cmd = 'rm ' + zspace
            os.system(cmd)



#-----------------------------------------------------------------------------------------------
#-- find_poc: find a poc for given proposal id and/or obsid                                  ---
#-----------------------------------------------------------------------------------------------

def find_poc(prop_no, obsid):
    """
    find a poc for given proposal id and/or obsid
    input:  prop_no --- proposal id 
            obsid   --- obsid
            it also needs access to:
                sybase
                /data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/propno_poc_list
                /data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/special_obsid_poc_list
    output: poc     --- poc
    """
#
#--- find basic information from sybase
#
    (group_id, pre_id, pre_min_lead, pre_max_lead, grating, type, instrument, obs_ao_str, status, \
    seq_nbr, ocat_propid, soe_st_sched_date, lts_lt_plan,targname) = sql.get_target_info(int(obsid), [],[])
#
#--- check only unobserved or scheduled observations
#
    if (status != 'unobserved') and (status != 'scheduled') :
        return 'na'
#
#--- check too and ddt cases
#
    f    = open('/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/propno_poc_list', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    tooddt = {}
    for ent in data:
        atemp = re.split('<>', ent)
        tooddt[atemp[0]] = atemp[1]
#
#--- if it is too or ddt but poc is not assigned, return 'TBD'
#
    try:
        poc = tooddt[prop_no]
        return poc
    except:
        if type == 'too' or type == 'ddt':
            poc = 'TBD'
            return poc
#
#--- check none-standard poc assignment
# 
    f    = open('/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/special_obsid_poc_list', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- find proposal # based of ocat_propid
#
    cmd      = 'select prop_num from prop_info  where ocat_propid= ' + str(ocat_propid)
    out      = sql.readSQL(cmd, 'axafocat')
    prop_num = out['prop_num']

    special_assignment = {}
    prev = ''
    for ent in data:
        atemp  = re.split('\s+', ent)
        poc    = atemp[2]
        propno = atemp[3]
        if propno != prev:
            special_assignment[propno] = poc
            prev = propno
        else:
            continue

    try:
        poc = special_assignment[prop_num]
    except:
#
#--- give back the standard poc
#
        poc = tdfnc.match_usint_person(type, grating, int(seq_nbr), instrument, targname)

    return poc

#-----------------------------------------------------------------------------------------------
#-- read_prop_obsiid_table: read prop_obsid_list and create prop_id <---> [obsid list] dictionary 
#-----------------------------------------------------------------------------------------------

def read_prop_obsiid_table():
    """
    read prop_obsid_list and create prop_id <---> [obsid list] dictionary
    input: None, but read from prop_obsid_list
    output: prop_list   --- a list of proposal id
            prop_dict   --- a dictionary of of prop_id <---> [obsid list]
    """
    
    f    = open('./prop_obsid_list', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    prop_dict = {}
    poc_dict  = {}
    prop_list = []
    for ent in data:
        atemp = re.split('<>', ent)
        btemp = re.split(':', atemp[2])

        prop_dict[atemp[0]] = btemp
        poc_dict[atemp[0]]  = atemp[1]
        prop_list.append(atemp[0])

    return (prop_list, prop_dict, poc_dict)
         

#-----------------------------------------------------------------------------------------------
#-- get_prop_obsid_list: read sot_ocat.out and create prop_id<---> obsid list dictionary     ---
#-----------------------------------------------------------------------------------------------

def get_prop_obsid_list(poc_dict):
    """
    read sot_ocat.out and create prop_id<---> obsid list dictionary
    input:  none, but read from /data/mta4/obs_ss/sot_ocat.out
    output  ulist       --- a list of proposal ids
            prop_dict   --- a dictionary of prop_id <---> obsid list
    """

#
#--- read sot_ocat.out data to extract proposal id and obsid
#
    f    = open('/data/mta4/obs_ss/sot_ocat.out')
    data = [line.strip() for line in f.readlines()]
    f.close()

    obsid = []
    prop  = []
    i = 0
    for ent in data:
        atemp = re.split('\^', ent)

        obsid.append(atemp[1].strip())
        prop.append(atemp[19].strip())
#
#--- create a proposal id list
#
    sprop = sorted(prop)
    prev  = sprop[0]
    ulist = [prev]
    for i in range(1, len(sprop)):
        if sprop[i] == prev:
            continue
        else:
            ulist.append(sprop[i])
            prev = sprop[i]
#
#--- create an empty list for each proposal id to hold obsid corresponding to the prop id
#
    for ent in ulist:
        exec "list_%s = []" % str(ent)
#
#--- go through the all list and put obsids into appropriate lists
#
    for i in range(0, len(obsid)):
       exec "list_%s.append('%s')" % (prop[i], str(obsid[i]))

    os.system('mv ./prop_obsid_list ./prop_obsid_list~')
#
#--- get poc list from new_obs_list
#
    ndict = find_poc_from_new_list()
#
#--- print out the most recent prop_id <---> obsid list  table
#
    fo = open('./prop_obsid_list', 'w')
    prop_dict = {}
    for ent in ulist:
        exec "olist = list_%s" % (ent)
#
#--- get poc
#
        prop_dict[ent] = olist
        try:    
            poc = poc_dict[ent]
        except:
#
#--- if poc is not in the original list, try from poc list created from new_obs_list
#
            poc = 'TBD'
            for obsid in olist:
                try:
                    poc = ndict[obsid]
                    break
                except:
                    continue

        line = ent +  "<>" + poc + "<>"
        line = line + str(olist[0])
        for i in range(1, len(olist)):
                line = line + ':' + str(olist[i])

        line = line +  '\n'
        fo.write(line)

    fo.close()
        
    return (ulist, prop_dict)

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def find_poc_from_new_list():

    f =  open('/data/mta4/CUS/www/Usint/ocat/Info_save/too_contact_info/new_obs_list', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    ndict = {}
    for ent in data:
        atemp = re.split('\s+', ent)
        ndict[atemp[2]] = atemp[4]

    return ndict


#-----------------------------------------------------------------------------------------------
#-- find_observer_email:  for a given obsid, find a contact email address                     --
#-----------------------------------------------------------------------------------------------

def find_observer_email(obsid):
    """
    for a given obsid, find a contact email address
    input:  obsid   --- obsid
                this also needs the database access
    output: name    --- observer's name
            email   --- observer's email address
    """
#
#--- find ocat proposal id
#
    database    = 'axafocat'

    cmd         = 'select ocat_propid from target where obsid = ' + str(obsid)
    out         = sql.readSQL(cmd, database)
    ocat_propid = out['ocat_propid']
    
#
#--- check whether the proposer and the observer are different
# 
    database    = 'axafusers'
    
    cmd         = 'select coi_contact from person_short s,axafocat..prop_info p where p.ocat_propid = ' 
    cmd         = cmd +  str(ocat_propid)
    out         = sql.readSQL(cmd, database)
    coi_contact = out['coi_contact']
#
#--- if the observer is different from the porposer, extract the observer's email address
# 
    if coi_contact == 'Y':
    
        cmd   = 'select email from person_short s,axafocat..prop_info p where p.ocat_propid = ' 
        cmd   = cmd + str(ocat_propid) + ' and p.coin_id = s.pers_id'
        out   = sql.readSQL(cmd, database)
        email = out['email']
    
        cmd   = 'select last from person_short s,axafocat..prop_info p where p.ocat_propid = ' 
        cmd   = cmd + str(ocat_propid) + '  and p.coin_id = s.pers_id'
        out   = sql.readSQL(cmd, database)
        name  = out['last']
    
    else:
        cmd   = 'select email from person_short s,axafocat..prop_info p where p.ocat_propid = ' 
        cmd   = cmd + str(ocat_propid) + ' and s.pers_id = p.piid'
        out   = sql.readSQL(cmd, database)
        email = out['email']

        cmd  = 'select last from person_short s,axafocat..prop_info p where p.ocat_propid = ' 
        cmd  = cmd + str(ocat_propid) + '  and s.pers_id = p.piid'
        out  = sql.readSQL(cmd, database)
        name = out['last']

    return [name, email]

#-----------------------------------------------------------------------------------------------
#-- find_title: for a given obsid, find  the proposal title                                  ---
#-----------------------------------------------------------------------------------------------

def find_title(obsid):
    """
    for a given obsid, find  the proposal title
    input:  obsid   --- obsid
                this also needs the database access
    output: title   --- proposal title
    """
#
#--- find ocat proposal id
#
    database    = 'axafocat'

    cmd         = 'select ocat_propid from target where obsid = ' + str(obsid)
    out         = sql.readSQL(cmd, database)
    ocat_propid = out['ocat_propid']
    
    cmd         = 'select title from prop_info where ocat_propid = ' + str(ocat_propid)
    out         = sql.readSQL(cmd, database)
    title       = out['title']

    return title
    

#----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    compare_prop_lists()


