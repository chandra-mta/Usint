#!/usr/bin/env /data/mta/Script/Python3.6/envs/ska3/bin/python

#################################################################################################
#                                                                                               #
#           updated_fill.py: update updated.html  page                                          #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Feb 01, 2021                                                       #
#                                                                                               #
#################################################################################################

import math
import re
import sys
import os
import string
import time
import Chandra.Time
import numpy
#
#--- reading directory list
#
path = '/data/mta4/CUS/www/Usint/ocat/Info_save/too_dir_list_py3'
with  open(path, 'r') as f:
    data = [line.strip() for line in f.readlines()]

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec("%s = %s" %(var, line))
#
#--- append a path to a privte folder to python directory
#
sys.path.append(bin_dir)
#
#--- cus common functions
#
import cus_common_functions         as ccf
#
#--- temp writing file name
#
import random
rtail    = int(time.time() * random.random())
zspace   = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------
#-- updated_fill: update updated.html page                                           ---
#---------------------------------------------------------------------------------------

def updated_fill():
    """
    update updated.html page
    input:  none
    output: <cusdir>/updated.html
            <cusdir>/Save_month_htmll/<Mmm>_<yyyy>.html
    """
#
#--- update main page on 1st of every month
#
    mday = time.strftime('%d', time.gmtime())
    mday = int(float(mday))
    if mday == 1:
        update_main_page()
#
#--- update sub pages
#
    update_sub_page()

#---------------------------------------------------------------------------------------
#-- update_sub_page: update/create sub html pages                                   ----
#---------------------------------------------------------------------------------------

def update_sub_page():
    """
    update/create sub html pages
    input:  none, but read from <ocat_dir>/>/udates_table.list
    output: <cusdir>/Save_month_html/<mmm>_<yyyy>.html
    """
#
#--- read updates_table.list; key format of s_dict is <yyyy>_<mm>
#
    [n_list, s_dict] = extract_data()
#
#--- find today's date
#
    out    = time.strftime('%Y:%m:%d', time.gmtime())
    atemp  = re.split(':', out)
    tyear  = int(float(atemp[0]))
    tmon   = int(float(atemp[1]))
    tmday  = int(float(atemp[2]))
#
#--- update/create the last one year of the htmls
#
    lyear = tyear - 1

    for year in [lyear, tyear]:
        for  mon in range(1, 13):
            if (year == lyear) and (mon < tmon):
                continue

            if (year == tyear) and (mon > tmon):
                break
#
#--- extract the data set for the year/month
#
            key      = str(year) + '_' + ccf.add_leading_zero(mon)
            try:
                data_set = s_dict[key][1]
            except:
                continue
#
#--- create a html page content
#
            lmon     = ccf.change_month_format(mon)
            iyear    = str(year)
            hline    = create_sub_html_page(data_set, lmon, iyear)
#
#--- print out the  page
#
            ofile    = cusdir + 'Save_month_html/' + lmon + '_' + iyear + '.html'
            with open(ofile, 'w') as fo:
                fo.write(hline)

#---------------------------------------------------------------------------------------
#-- extract_data: read status data from udates_table.list                            ---
#---------------------------------------------------------------------------------------

def extract_data():
    """
    read status data from udates_table.list
    input:  none, but read from <ocat_dir>/udates_table.list
    output: n_list  --- a list of name <yyyy>_<mm>
            s_dict  --- a dictionary of  
    """
    ifile = ocat_dir + 'updates_table.list'
    data  = ccf.read_data_file(ifile)

    s_dict = {}
    n_list = []
    for ent in data:
        atemp = re.split('\t+', ent)
        if len(atemp) < 7:
            continue
        if atemp[4] == 'NA':
            continue

        btemp = re.split('\s+', atemp[4])
        vdate = re.split('\/',  btemp[1])
#
#--- format for the year is <yy> e.g., 99 for 1999, or 20 for 2020
#
        try:
            val   = float(vdate[2])
        except:
            continue

        if val == 99:
            name  = '19' + vdate[2] + '_' + vdate[0]
            ltime = int(float('19' + vdate[2] + vdate[1] + vdate[0]))
        else:
            name  = '20' + vdate[2] + '_' + vdate[0]
            ltime = int(float('20' + vdate[2] + vdate[1] + vdate[0]))
#
#--- saveing data in a dictionary form. key: <yyyy>_<mm>. It also save time in <yyyy><mm><dd> format
#
        try:
            out   = s_dict[name]
            out[0].append(ltime)
            out[1].append(ent)
            s_dict[name] = out

        except:
            s_dict[name] = [[ltime],[ent]]

        n_list.append(name)
#
#--- remove duplicated names and sort in time order
#
    n_list = sorted(list(set(n_list)))
#
#--- sort each data set in the time order
#
    for name in n_list:
        s_dict[name] = sort_data_by_date(s_dict[name])

    return [n_list, s_dict]

#---------------------------------------------------------------------------------------
#-- sort_data_by_date: sort the list by time                                          --
#---------------------------------------------------------------------------------------

def sort_data_by_date(alist):
    """
    sort the list by time
    input:  alist   --- a list of lists: [[time list], [data list]]
    ouput:  time sorted list of lists
    """
    t_array = numpy.array(alist[0])     #--- a list of time 
    d_array = numpy.array(alist[1])     #--- a list of data

    idx     = numpy.argsort(t_array)
    t_list  = list(t_array[idx])
    d_list  = list(d_array[idx])

    return [t_list, d_list]

#---------------------------------------------------------------------------------------
#-- create_sub_html_page: create a html page content                                  --
#---------------------------------------------------------------------------------------

def create_sub_html_page(data_list, lmon, iyear):
    """
    create a html page content
    input:  data_list   --- a list of data
            lmon        --- month of the data file
            iyear       --- year of the data file
    output: out         --- a html code for the page
    """
#
#--- read templates
#
    ifile = house_keeping + 'Updated/Templates/header_part'
    with open(ifile, 'r') as f:
        head_part = f.read()

    head_part = head_part.replace('#LMON#',  lmon)
    head_part = head_part.replace('#IYEAR#', iyear)

    ifile = house_keeping + 'Updated/Templates/tail_part'
    with open(ifile, 'r') as f:
        tail_part = f.read()
#
#--- start creating each line
#
    line = ''
    data_list.reverse()
    for ent in data_list:
        atemp       = re.split('\t+', ent)
        obsrev      = atemp[0]
        gen_status  = atemp[1]
        acis_status = atemp[2]
        si_status   = atemp[3]
        dsi_status  = atemp[4]
        seqnum      = atemp[5]
        user        = atemp[6]
#
#--- find the file  modificaiton time
#
        dfile = ocat_dir + 'updates/' + obsrev
        try:
            ftime = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(dfile)))
        except:
            ftime = 'missing'
        
        if dsi_status == 'NA':
            continue
#
#--- create each html data line
#
        line = line + '<tr>\n'
        line = line + '<td><a href="https://icxc.harvard.edu/uspp/updates/' + obsrev + '">'
        line = line + obsrev + '</a><br />' + seqnum + '<br />'
        line = line + ftime  + '<br />' + user + '</td>\n'
        line = line + '<td>' + gen_status + '</td><td>' + acis_status + '</td><td>'
        line = line + si_status + '</td><td style="color=#005C00">' + dsi_status + '</td>\n'
        line = line + '</tr>\n'
#
#--- combine header body and tail to crate a page
#
    out = head_part + line + tail_part

    return out

#---------------------------------------------------------------------------------------
#-- check_last_update: check whether the data are updated in the last 24 hrs         ---
#---------------------------------------------------------------------------------------

def check_last_update():
    """
    check whether the data are updated in the last 24 hrs 
    input:  none, but read from <cusdir>Save_month_html/last_update
    output: True/False
            updated <cusdir>Save_month_html/last_update
        NOT USED IN THIS SCRIPT
    """
#
#--- current time in sec from 1998.1.1
#
    ltime = time.strftime('%Y:%j:H:%M:%S', time.gmtime())
    stime = int(Chandra.Time.DateTime(ltime).secs)
#
#--- read the last log
#
    ifile = cusdir + 'Save_month_html/last_update'
    with open(ifile, 'r') as f:
        ptime = f.read().strip()
        ptime = int(float(ptime))

    diff = stime - ptime
    if diff > 86400:
        with open(ifile, 'w') as fo:
            fo.write(str(stime) + '\n')

        return True
    else:
        return False
 
#---------------------------------------------------------------------------------------
#-- update_main_page: update main page                                                --
#---------------------------------------------------------------------------------------

def update_main_page():
    """
    update main page
    input:  none
    output: <cusdir>/updated.html
    """
#
#--- find today's date
#
    out = time.strftime('%Y:%m', time.gmtime())
    atemp = re.split(':', out)
    tyear = int(float(atemp[0]))
    tmon  = int(float(atemp[1]))
#
#--- read templates
#
    ifile = house_keeping + 'Updated/Templates/main_page'
    with open(ifile, 'r') as f:
        head_part = f.read()

    ifile = house_keeping + 'Updated/Templates/main_tail'
    with open(ifile, 'r') as f:
        tail_part = f.read()
#
#--- start a table part
#
    line = '<tr><th>Year</th>\n'
    for year in range(2000, tyear+1):
        line = line + '<th>' + str(year) + '</th>\n'
    line = line + '</tr>\n'

    yspan  = tyear - 1999
    yspans = yspan - 1

    for mon in range(1, 13):
        lmon = ccf.change_month_format(mon)
        line = line + '<tr><th>' + lmon + '</th>\n'

        for i in range(0, yspan):
            year = 2000 + i
            fname = lmon + '_' + str(year) + '.html'
            if i < yspans:
                line = line + '<td><a href="./Save_month_html/'
                line = line + fname + '">' + lmon + '</a></td>\n'
            else:
                if mon > tmon:
                    line = line + '<td>&#160;</td>\n'
                else:
                    line = line + '<td><a href="./Save_month_html/'
                    line = line + fname + '">' + lmon + '</a></td>\n'
        line = line + '</tr>'
#
#--- combine them
#
    line = head_part + line + tail_part
#
#--- print out the page
#
    ofile = cusdir + 'updated.html'
    with open(ofile, 'w') as fo:
        fo.write(line)

#---------------------------------------------------------------------------------------

if __name__ == "__main__":
    
    updated_fill()




