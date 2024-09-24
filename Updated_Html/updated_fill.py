#!/proj/sot/ska3/flight/bin/python

#################################################################################################
#                                                                                               #
#           updated_fill.py: update updated.html  page                                          #
#                                                                                               #
#               author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                               #
#               last update: Sep 18, 2024                                                       #
#                                                                                               #
#################################################################################################

import re
import sys
import os
import time
import numpy
from calendar import month_abbr
import argparse
#
#--- Define Directory Pathing
#
CUS_DIR = "/data/mta4/CUS/www/Usint"
OCAT_DIR = "/data/mta4/CUS/www/Usint/ocat"
TEMPLATE_DIR = "/data/mta4/CUS/www/Usint/ocat/house_keeping/Updated/Templates"
CHKUPDATA_LINK = "https://cxc.cfa.harvard.edu/wsgi/cus/usint/chkupdata"

#---------------------------------------------------------------------------------------
#-- update_sub_page: update/create sub html pages                                   ----
#---------------------------------------------------------------------------------------

def update_sub_page(tyear, tmon):
    """
    update/create sub html pages
    input:  none, but read from <ocat_dir>/updates_table.list
    output: <cus_dir>/Save_month_html/<mmm>_<yyyy>.html
    """
#
#--- read updates_table.list; key format of s_dict is <yyyy>_<mm>
#
    [n_list, s_dict] = extract_data()
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
            key = f"{year}_{mon:>02}"
            try:
                data_set = s_dict[key][1]
            except:
                continue
#
#--- create a html page content
#
            lmon = month_abbr[mon]
            iyear    = str(year)
            hline    = create_sub_html_page(data_set, lmon, iyear)
#
#--- print out the  page
#
            with open(f"{CUS_DIR}/Save_month_html/{lmon}_{iyear}.html", 'w') as fo:
                fo.write(hline)

#---------------------------------------------------------------------------------------
#-- extract_data: read status data from udates_table.list                            ---
#---------------------------------------------------------------------------------------

def extract_data():
    """
    read status data from udates_table.list
    input:  none, but read from <ocat_dir>/updates_table.list
    output: n_list  --- a list of name <yyyy>_<mm>
            s_dict  --- a dictionary of  
    """
    with open(f"{OCAT_DIR}/updates_table.list") as f:
        data = [line.strip() for line in f.readlines()]

    s_dict = {}
    n_list = []
    for ent in data:
        atemp = re.split('\t+', ent)
        if len(atemp) < 8:
            continue
        if atemp[5] == 'NA':
            continue

        btemp = re.split('\s+', atemp[5])
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
    with open(f"{TEMPLATE_DIR}/header_part", 'r') as f:
        head_part = f.read()

    head_part = head_part.replace('#LMON#',  lmon)
    head_part = head_part.replace('#IYEAR#', iyear)

    with open(f"{TEMPLATE_DIR}/tail_part", 'r') as f:
        tail_part = f.read()
#
#--- start creating each line
#
    line = ''
    data_list.reverse()
    for ent in data_list:
        atemp         = re.split('\t+', ent)
        obsrev        = atemp[0]
        gen_status    = atemp[1]
        acis_status   = atemp[2]
        if gen_status == 'NULL':
            gen_status = acis_status
        si_status     = atemp[3]
        hrc_si_status = atemp[4]
        dsi_status    = atemp[5]
        seqnum        = atemp[6]
        user          = atemp[7]
#
#--- find the file modification time
#
        dfile = f"{OCAT_DIR}/updates/{obsrev}"
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
        line = line + f'<td><a href="{CHKUPDATA_LINK}/{obsrev}">'
        line = line + obsrev + '</a><br />' + seqnum + '<br />'
        line = line + ftime  + '<br />' + user + '</td>\n'
        line = line + '<td>' + gen_status + '</td><td>' + si_status + '</td><td>'
        line = line + hrc_si_status + '</td><td style="color=#005C00">' + dsi_status + '</td>\n'
        line = line + '</tr>\n'
#
#--- combine header body and tail to crate a page
#
    out = head_part + line + tail_part

    return out
 
#---------------------------------------------------------------------------------------
#-- update_main_page: update main page                                                --
#---------------------------------------------------------------------------------------

def update_main_page():
    """
    update main page
    input:  none
    output: <cus_dir>/updated.html
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
    with open(f"{TEMPLATE_DIR}/main_page", 'r') as f:
        head_part = f.read()

    with open(f"{TEMPLATE_DIR}/main_tail", 'r') as f:
        tail_part = f.read()
#
#--- start a table part
#
    line = '<tr><th>Year</th>\n'
    for year in range(2005, tyear+1):
        line = line + '<th>' + str(year) + '</th>\n'
    line = line + '</tr>\n'

    yspan  = tyear - 2004
    yspans = yspan - 1

    for mon in range(1, 13):
        lmon = month_abbr[mon]
        line = line + '<tr><th>' + lmon + '</th>\n'

        for i in range(0, yspan):
            year = 2005 + i
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
    with open(f"{CUS_DIR}/updated.html", 'w') as fo:
        fo.write(line)

#---------------------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mode", choices = ['flight','test'], required = True, help = "Determine running mode.")
    parser.add_argument("-p", "--path", required = False, help = "Directory path to determine output location of web files.")
    parser.add_argument("--main", action=argparse.BooleanOptionalAction, help = "Select whether ot update the main page or not.")
    parser.add_argument("-y", "--year", type=int, required = False, help = "Select year for report generation. Defaults to current year")
    args = parser.parse_args()

#
#--- Select running of main options if running on the frist day of the month
#
    if args.main == None:
        if int(time.strftime('%d', time.gmtime())) == 1:
            RUN_MAIN = True
        else:
            RUN_MAIN= False
    else:
        RUN_MAIN = args.main
#
#--- Select year for report generation
#
    atemp  = re.split(':', time.strftime('%Y:%m', time.gmtime()))
    curr_year = int(atemp[0])
    curr_mon = int(atemp[1])
    if args.year == None or args.year == curr_year:
        tyear = curr_year
        tmon = curr_mon
    elif args.year < curr_year:
        tyear = args.year
        tmon = 12
    else:
        parser.error(f"Invalid Year: {args.year}")

#
#--- Determine if running in test mode and change pathing if so
#
    if args.mode == "test":
#
#--- Define Directory Pathing
#
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        CUS_DIR = f"{SCRIPT_DIR}/test/outTest"
        TEMPLATE_DIR = f"{SCRIPT_DIR}/Templates"
        os.makedirs(f"{CUS_DIR}/Save_month_html", exist_ok = True)

        if RUN_MAIN:
            update_main_page()
        update_sub_page(tyear, tmon)

    elif args.mode == "flight":
#
#--- Create a lock file and exit strategy in case of race conditions
#
        import getpass
        name = os.path.basename(__file__).split(".")[0]
        user = getpass.getuser()
        if os.path.isfile(f"/tmp/{user}/{name}.lock"):
            sys.exit(f"Lock file exists as /tmp/{user}/{name}.lock. Process already running/errored out. Check calling scripts/cronjob/cronlog.")
        else:
            os.system(f"mkdir -p /tmp/{user}; touch /tmp/{user}/{name}.lock")

        if RUN_MAIN:
            update_main_page()
        update_sub_page(tyear, tmon)
#
#--- Remove lock file once process is completed
#
        os.system(f"rm /tmp/{user}/{name}.lock")




