#!/usr/bin/perl

BEGIN
{
    $ENV{SYBASE}   = "/soft/SYBASE16.0";
    $ENV{LANG}     = "en_US.UTF-8";
    $ENV{LC_CTYPE} = "en_US.UTF-8";
}

use DBI;
use DBD::Sybase;
use CGI qw/:standard :netscape /;

use Fcntl qw(:flock SEEK_END); # Import LOCK_* constants

#################################################################################
#                                                                               #
#   ocatdat2html_lite.cgi: smaller version of ocatdata2html.cgi                 #
#                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                               #
#                                                                               #
#       last update: Sep 21, 2021                                               #
#                                                                               #
#################################################################################

###############################################################################
#
#HISTORY OF UPDATES
#-------------------
# This is a first-draft script to dynamically create a page based on obsid.
# It works, as far as I can tell....
# Note:  Currently, this script MUST use the above version of perl and contain
# all the use statements above.
# Ok, that's probably not true - I don't think I'm using DBlib at all.
# It is more complex to use CTlib, but I'm told by the experts that
# DBlib is going to be discontinued.
# -Roy Kilgard, April 2000
#
# Some new inputs are added by T. Isobe (01 May, 2001)
#
# Preference selection added/ACIS window filter function modified
#                       T. Isobe (27 Jul. 2001)
#
# bugs related comments and remarks fixed (06 Sep. 2001)
# uninterrupt added (22 Jul. 2002)
#
# added several more entries (27 Aug. 2002)
# multitelescope  observatories
# From TOO database   type  trig  start,  stop  followup,  remarks
# proposal_hst, proposal_noao, proposal_xmm
#
# Major modifications are performed (29 Apr. 2003). Changes are:
#       1. submit.cgi and oredit.cgi are now absorbed into ocatdata2html.cgi.
#       2. ordr for time, roll, and window constraints are now able to handle
#          mulitiple ranks (upto 30).
#       3. tstart and tstop input time format are more flexible.
#       4. input error checking mechanism are updated.
#
#
# Adjusted for AO5 input/Sherry's requests, and several bugs fixed
# (15 Aug 2003)
#	1. added passowrd entry, special user status added
#
# The script is modified to accomodate both user and usint use, and
# several updates are done. The user version is moved to a secure are
#  (Oct 2, 2003)
#
# New display format is added
#   (Mar 23, 2004)
#
# Added automatic acis window constraints setting for the case energy filter lowest 
# energy is > 0.5 keV.
# General cleaning up of the code 
#   (June 15, 2006)
#
# Added: a new user sign off capacity (ask USINT to do everything)
#	 CCD selection has OPT1-5.
#   (Jul 20, 2006)
# 
# A fully updated to adjust AO8 requirements.
#   (Sep 28, 2006)
#
# Double entry revision # bug is fixed.
#   (Mar 20, 2007)
#
# sending email to MP only when the obs. is on OR list, and there are actually
# some modificaiton.
#   (Jul 17, 2007)
#
#  1. sub array type is now use subarray: yes/no
#
#  2. following entires are removed (no reading from DB and no display on the page):
#     bias_after, frequency, bias_request, fep, standard_chips, subarray_frame_time, bias_after
#   (Sep. 19, 2007)
#
#
#  canceled/archived/discarded/observed observation displays the status at the top.
#  it also does not show the link to thoese observations at monitoring constraint.
#  (Oct. 29, 2007)
#
#  for usint version, only usint users now can have full access to the file. All others ca
#  read, but edit
#  (Dec. 06, 2007)
#
#   description of the note changed
#   Aimpoint    1/8   1/4   1/2
#
#   ACIS-I    897   769   513
#   ACIS-S    449   385   257"
#   (Dec. 18, 2007)
#
#  all perl/cgi/html links are now have absolute pathes
#  (Feb. 05, 2008)
#
#  environment setting changed:
#	/proj/DS.ots/perl-5.10.0.SunOS5.8/bin/perl
#	 $ENV{SYBASE} = "/soft/SYBASE_OCS15"
#  (May 19, 2008)
#
#  a new value added: multitelescope_interval
#  (Sept 02, 2008)
#
#  si mode is required when submitted for approval
#  (Sept. 22, 2008)
#
#  when group id exists pre_id etc. can be visible, but not editable. 
#  if no group id or monitoring flag, all "pre" paramters will be null.
#  (Nov. 04, 2008)
#  a bug related to above is fixed.
#  (Nov 20, 2008)
#
#  A warning "CDO approval is requred" is changed to "Has CDO approved this instrument change?"
#  (Nov 24, 2008)
#
# https://icxc.harvard.edu/mta/CUS/ ---> https://icxc.harvard.edu/cus/index.html
#  (Aug 26, 2009)
#
# sub oredit is exported to oredit_sub.perl to increase speed and avoid double entiries of obsid
#  (Sep 23, 2009)
#
# dss/rosat/rass image access path fixed
#  (Oct 27, 2009)
#
# corrected ra/dec conversion problem./remvoed nohup option when running oredit_sub.perl
#  (Dec 07, 2009)
#
# duplicated start_form() tags are removed
#  (Dec 09, 2009)
#
#
#  perl pointing is changed from: /proj/DS.ots/perl-5.10.0.SunOS5.8/bin/perl 
#	                      to: /soft/ascds/DS.release/ots/bin/perl 
#  to accomodate Solaris 10.
#   (Apr 23, 2010)
#
#  determination of AO # is updated; it is now obtained from "prop_info", not from "target"
#   (Jul 06, 2010)
#
#  added notification of a wrong user name login attempt
#   (Jul 13, 2010)
#
#  special window bug fixed (no include option, if a new window is added)
#   (Jul, 20, 2010)
#
# oredit_sub.perl is re-integrated as sub oredit_sub, and some change of sccs routine to 
# shorten the potential hang up.
#  (Aug 09, 2010)
#
# ACIS Window Constraints format is updated. now you can assign "ordr", too.
#  (Oct 28, 2010)
#
# PHOTOMETORY_FLAG bug fixed
#  (Nov 22, 2010)
#
# a bug related to a left over junk file fixed
#  (Feb 24, 2011)
#
# directory paths is now read from a file kept in the info site
#  (Mar 01, 2011)
#
# updates_table.list permission change to 755
#  (Mar 08, 2011)
#
# multiple_spectral_lines and spectra_max_count are added to ACIS parameters
# (Mar 31, 2011)
#
# Min Int/Max Int names are modified with <br />(pre_min_lead)
# (Apr. 13 2011)
#
# EXTENDED_SRC is added / some descriptions are updated
# (Aug. 01, 2011)
#
# LOWER_THRESHOLD, PHA_RANGE etc  modified, and check mechanism updated.
# (Aug. 05, 2011)
#
# New requirements for ACIS-I/None Grating case check added.
# (Sep. 23, 2011)
#
# Time constraint and Roll Constraint now have null rank removing capacity
# (Oct, 20, 2011)
#
# sql reading update: $sqlh1 = $dbh1->prepare(qq(select soe_roll from soe where obsid=$obsid and unscheduled='N'));
# (Oct, 27, 2011)
#
# sccs is now pointing to /usr/local/bin/
# (Aug 28, 2012)
#
# sccs is replaced by flock
# (Oct 01, 2012)
#
# mailx -r option removed
# (Oct 02, 2012)
#
# time, order, and acis window constraint setting changed
# (Oct 18, 2012)
#
# flock bug fixed
# (Nov 28, 2012)
#
# ocat data value conversion problem corrected (line starting 9140 as of Nov 29, 2012)
# (Nov 29, 2012)
#
# window_flag/roll_flag bug fixed
# (Dec 06, 2012)
#
# https://cxc version
# (Mar 26, 2013)
#
# link to cdo changed to https://icxc.harvard.edu
# (Apr 03, 2013)
#
# mailx's  -r$cus_email option removed
# (Jun 27, 2013)
#
# BEP_PEAK option changed (F, VF, F+B, G ---  default: F)
# (Sep, 23, 2013)
#
# Link to PSPC page removed
# (Sep 25, 2013)
#
# Highest Energy display added
#  (Nov 14, 2013)
#
# BEP_PACK now has "NULL" option when the instrument is HRC
#  (Nov 14, 2013)
#
# Preference/Constraint change warning capacity added
#  (Nov 18, 2013)
#
# Definition of "Use Subarray" is modified 
# ACIS-I :	897	128	769	256	513	original
# ACIS-I :	897	128	768	256	513	
#  (Jan 09, 2014)
#
# Added a checking mechanism which notify REMARKS and COMMENTS are delted
#  (Feb 25, 2014)
#
# Input for Roll and Roll_tolerance is now limited to digit
#  (May 21, 2014)
#
# If the original value is <blank>, "Blank" will be desplayed on output
#  (Jun 12, 2014)
# Planned Roll has now have a range. 
#  (Aug 26, 2014)
#
# SYBASE link update (/soft/SYBASE15.7)
#  (Sep 23, 2014)
#
# Note to window constraint (exclusion) added.
#  (Oct 30, 2014)
# 
# Exposure Time is now not editable
# (Dec 21, 2014)
#
# CDO warning on change of Y/Z det offset added (>10arcmin)
# (Feb 13, 2015)
#
# Reordering the ranks of aciswin in increasing order
# (Jul 17, 2015)
#
#  /soft/ascds/DS.release/ots/bin/perl ---> /usr/bin/perl  (accessible from cxc)
#
# Aimpoint Chipx and Chipy values added
# (Oct 26, 2015)
#
# Observations in the Monitoring --> Remaining Observations in the Monitoring
# (May 10, 2016)
#
# Warning email to MP about the late submission (less than 10days to lts date)
# (May 26, 2016)
#
# Bug due to null lts_lt_plan date fixed
# (June 07, 2016)
#
# Warning email to MP now also sent to USINT user
# (Jun 30, 2016)
#
# the bug introduced by Jul 17, 2015 update (not showing the first row) fixed 
# (Aug 10, 2016)
#
# archive access user name(s) changed from brower to mtaops_internal/public
# (Nov 21, 2016)
#
# mjuda email address to HRC removed
# (Jan 3, 2017)
#
# mp eamil address is now mp@cfa.harvard.edu
# check_lts_date_coming: inverval checking changed from <10 to <=10
# (Jan 4, 2017)
#
# hrc si mode change only buttom added (create na na null output).
# (Jan 4, 2017)
# 
# lts warning is preceeded for or list waring to mp@cfa.havard.edu
# (Jan 6, 2017)
#
# added the language specification in ENV
# (Jul 6, 2017)
#
# mailx: cat is replaced with "cat"
# (Sep 29, 2017)
#
# mailx: back to the "cat"
# (Oct 02, 2017)
#
# si_mode is now not editable
# (Apr 18, 2018)
#
# mp_email bug fixed
# (May 02, 2018)
#
# hrc si mode check request email added
# (Sep 13, 2018)
#
# hrc si mode bug-- not setting si_mode=NA fixed
# (Sep 28, 2018)
#
# time constrain year range updated
# (Oct 03, 2018)
#
#  mailx: | tr -d '\015' is added to remove special characters
# (Oct 25, 2018)
# 
# hrc si mode comparison/notification changed 
# (Nov 18, 2018)
#
# permanent aimppoint values updated
# ref: https://cxc.harvard.edu/cal/Hrma/OpticalAxisAndAimpoint.html
# (Jul 17, 2019)
#
# if inst is hrc and hrc_si_mode is not changed, si_mode_status will be set 'NULL'
# (Aug 21, 2019)
#
# HRC SI Mode Only button removed
# (Aug 29, 2019)
#
# SI mode == HRC SI mode when inst is HRC
# (Sep 04, 2019)
#
# sot contact changed from swolk to bwargelin
# (Sep 24, 2019)
# 
# seq # is linked to https://cda.cfa.harvard.edu/chaser/startViewer.do
# (Aug 05, 2020)
#
# a major update, including added capacity to propagate parameter changes to several obsids
# (Oct 29, 2020)
# a bug not displaying asis submission page corrected
# (Dec 01, 2020)
#
# a bug related to duplicated acis param listing on report corrected
# (Dec 15, 2020) 
#
# ra no conversion bug in multi-obsid entry cases fixed
# (Jan 19, 2021)
#
# mailx subject line fixed
# (Jan 26, 2021)
#
# a new parameter pointing_constraint added
# (Feb 10, 2021)
#
# asc ops notification added
# (Mar 11, 2021)
#
# window_constraint missig NULL display value fixed
# (Mar 16, 2021)
#
# target name is now editable
# (Mar 24, 2021)
#
# MP warning email related to target name change added
# (Mar 25, 2021)
#
# ACIS parameter change <---> updates_table.list bug fixed with a better checking 
# (Apr 27, 2021)
#
# HRC SI mode column is added to the updates_table.list
# (Jun 28, 2021)
#
# Help pange link to each section added
# (Jul 14, 2021)
#
# TARGNAME is back in the <obsid>.<rev> data 
# (Sep 07, 2021)
#
# A bug: turning on acistag with multiple entry case fixed
# (Oct 18, 2021)
#
#-----Up to here were done by t. isobe (tisobe@cfa.harvard.edu)-----
#
# ----------
# sub list:
# ---------
#   password_check              open a user - a password input page
#   match_user                  check a user and a password matches
#   special_user                check whether the user is a special user
#   pi_check                    check whether pi has an access to the datau
#   pass_param                  passing cgi parameter values to the next window
#   read_databases              read out values from databases
#   ccd_on_check                convert display values to database values on ccd data
#   assign_dval                 convert database values to descriptive display values
#   data_input_page             create data input page--- Ocat Data Page
#   prep_submit                 preparing the data for submission
#   chk_entry                   entry_test to check input value range and restrictions
#   compare_to_original_val     sending a warning if there is preference/costraint changes
#   print_pwarning              print out preference/constrain change warning
#   entry_test                  check input value range and restrictions
#   restriction_check           check special restrictions for input
#   read_range                  read conditions
#   read_user_name              reading authorized user names
#   user_warning                warning a user, a user name mistake
#   submit_entry                check and submitting the modified input values
#   print_table_row             print out table row according to three different ways 
#   check_blank_entry           check "" and change it to <Blank> entry
#   read_name                   read descriptive name of database name
#   find_name                   match database name to descriptive name
#   oredit                      update approved list, updates_list, updates data, and send out email
#   update_order_case           
#   change_old_value_to_blank
#   mod_time_format             convert and devide input data format
#   change_lmon_to_nmon
#   adjust_digit
#   nmon_to_lmon
#   series_rev                  getting mointoring observation things
#   series_fwd                  getting monitoring observation things
#   find_planned_roll           get planned roll from mp web page
#   rm_from_approved_list       remove entry from approved list 
#   send_email_to_mp            sending email to MP if the obs is in an active OR list
#   oredit_sub                  
#   adjust_o_values             adjust output letter values to a correct one
#   send_lt_warning_email       send out a warning email to mp about a late submission
#   send_lt_warning_email2      send out a warning email to USINT  a late submission
#   check_obs_date_coming       check whether lts date is coming less than 10 days
#   obs_date_to_fyear           converting obs date format to fractional year format
#   is_leap_year                check a given year is a leap year
#   copy_split_observations     duplicate the records of the original obsid to split obsid in the given list
#   increment_obidrev           increment rev # of the obsid
#   find_rank                   find the starting rank which the new data will be saved
#   find_which_group             check which group the element belongs
#   check_element               check whether the element in the list
#   find_latest_rev             find the last revision number of the obsid
#   find_seq_nbr                find the sequence number for a given obsid
#   find_planned_date           find the planned observation date for a given obsid
#   split_obs_date_check        check whether lts dates of any of split obsid are coming less than 10 days
#   split_obsids_remove         removing all split observations from approved list
#   split_obsid_email           sending out email to dusty sci
#   split_string_to_list        create split obsid list from a string
#   make_obsid_list             create a display list of obsids
#   check_spl_obs_on_mp_list    check wether any of obsid on the split_list are on the active list
#   save_ranked_data            save the ranked parameter values of the main obsid (control func)
#   save_rank_values            save the ranked parameter values of the main obsid
#   update_rank_values_in_other update ranked parameter values of the secondary obsids (control func)
#   compare_rank_values         update ranked parameter values of the secondary obsids
#   reset_rank_data             reset rank parameters to NULL values
#   check_data_situation        check which conditions the data sets are in
#   check_null_value            check whether the value is in null set ("", "NULL", "E")
#   uniq_ent                    create a list of unqiue entries
#   sp_list_test                check whether the input string can convert to a list of obsids
#
# ----------------------------------
# data/files needed for this script
# ----------------------------------
#
#  $pass_dir/.htpasswd: 		user/password list.
#  $pass_dir/.htgroup:			read user names
#  $pass_dir/cxc_user:			cxc user list
#  $pass_dir/user_email_list: 	a list of user/usint list
#  $pass_dir/usint_users:     	a list of usint persons
#  $obs_ss/access_list:			a list of scheduled/unobserved list
#  $obs_ss/scheduled_obs_list:	a list of MP scheduled observations 
#  $obs_ss/mp_edit_permit		a list of MP scheduled observations, but have a eidt permission
#  $obs_ss/sot_ocat.out:		a list of all observations listed on sql database
#  $data_dir/ocat_values:		a file contains codtion/restriction for the param
#  $data_dir/name_list:			a file contains descritive names for params
#  $ocat_dir/approved:			an approved obsid list
#  $ocat_dir/updates_table.list	a file contains updated file list
#  $ocat_dir/updates/$obsid.*	database to save updated information
#  $ocat_dir/cdo_warning_list	a file containings a list of obsid/version of large coordinate shifts
#  $temp_dir:				    a dirctory where a temporary files are saved
#
#------------------------------------------------------------------------------------------------  

###############################################################################
#---- before running this script, make sure the following settings are correct.
###############################################################################
#
#--- set  " " <blank> value 
#
$blank  = '&lt;Blank&gt;';
$blank2 = '<Blank>';
#
#---- if this is usint version, set the following param to 'yes', otherwise 'no'
#
$usint_on = 'yes';			##### USINT Version
###$usint_on = 'test_yes';			##### Test Version USINT
#
#---- set a name and email address of a test/tech person
#
$test_user  = 'lina.pulgarin-duque';
$test_email = 'lina.pulgarin-duque@head.cfa.harvard.edu';
#
#--- admin contact email address
#
$sot_contact = 'bwargelin@head.cfa.harvard.edu';
$cus_email   = 'cus@head.cfa.harvard.edu';
#
#--- mp contact email address
#
$mp_email    = 'mp@cfa.harvard.edu';
$cdo_email   = 'cdo@cfa.harvard.edu';
#
#--- arcops email address
#
$arcops_email = 'arcops@cfa.harvard.edu';
#
#---- set directory pathes 
#
open(IN, '/data/mta4/CUS/www/Usint/ocat/Info_save/dir_list');

while(<IN>){
    chomp $_;
    @atemp    = split(/:/, $_);
    $atemp[0] =~ s/\s+//g;
    if($atemp[0] =~ /obs_ss/){
        $obs_ss   = $atemp[1];
    }elsif($atemp[0]  =~ /pass_dir/){
        $pass_dir = $atemp[1];
    }elsif($atemp[0]  =~ /htemp_dir/){
        $temp_dir = $atemp[1];
    }elsif($atemp[0]  =~ /data_dir/){
        $data_dir = $atemp[1];
    }elsif($atemp[0]  =~ /ocat_dir/){
        $real_dir = $atemp[1];
    }elsif($atemp[0]  =~ /test_dir/){
        $test_dir = $atemp[1];
    }
}
close(IN);
#
#--- if this is a test case, use the first directory, otherwise use the real one
#
if($usint_on =~ /test/i){
	$ocat_dir = $test_dir;
}else{
	$ocat_dir = $real_dir;
}
#
#--- set html pages
#

$usint_http   = 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/';	    #--- web site for usint users
$test_http    = 'https://cxc.cfa.harvard.edu/cgi-gen/mta/Obscat/';	#--- web site for test (not alive)
$mp_http      = 'https://cxc.cfa.harvard.edu/';			            #--- web site for mission planning related
$chandra_http = 'https://cxc.harvard.edu/';			                #--- chandra main web site
$cdo_http     = 'https://icxc.cfa.harvard.edu/cgi-bin/cdo/';	    #--- CDO web site
#
#--- set a few lists
#
@t_const = ("WINDOW_CONSTRAINT", "TSTART", "TSTOP");
@r_const = ("ROLL_CONSTRAINT", "ROLL_180", "ROLL", "ROLL_TOLERANCE");
@w_const = ('ORDR', 'CHIP', 'INCLUDE_FLAG', 'START_ROW', 'START_COLUMN',
            'HEIGHT', 'WIDTH', 'LOWER_THRESHOLD', 'PHA_RANGE', 'SAMPLE');

############################
#----- end of settings
############################

#------------------------------------------------------------------------
#--- find obsid requested if there are group id, it may append a new name
#------------------------------------------------------------------------

$temp  = $ARGV[0];
chomp $temp;
$temp  =~ s/\s+//g;	
@atemp = split(/\./, $temp);	
$obsid = $atemp[0];		
@otemp = split(//, $obsid);

if($otemp[0] eq '0'){
	shift @otemp;
	$line = '';
	foreach $ent (@otemp){
		$line = "$line"."$ent";
	}
	$obsid = $line;
}

#----------------------------------------------------------------
#--- a parameters to pass on: an access password and a user name
#--- these are appended only when the script wants to open up
#--- another obsid ocat page (e.g., group observations)
#----------------------------------------------------------------

$pass      = $atemp[1];
$submitter = $atemp[2];
$user      = $atemp[2];

#-------------------------------------------------------------------
#---- read approved list, and check whether this obsid is listed.
#---- if it does, send warning.
#-------------------------------------------------------------------

#open(FH, "$ocat_dir/approved");
$prev_app      = 0;

#--------------------------------------------------------------------
#----- here are non CXC GTOs who have an access to data modification.
#--------------------------------------------------------------------

$no_sp_user    = 2;				#--- number of special users

@special_user  = ("$test_user",  'mta');
@special_email = ("$test_email", "$test_email");

open(FH, "$pass_dir/usint_users");
while(<FH>){
	chomp $_;
	@atemp = split(//,$_);
	if($atemp[0] ne '#'){
		@btemp = split(/\s+/,$_);
		push(@special_user,  $btemp[0]);
		push(@special_email, $btemp[1]);
	}
}

#-------------------------------
#---- read a user-password list
#-------------------------------

open(FH, "<$pass_dir/.htpasswd");

%pwd_list = ();             	#--- save the user-password list
while(<FH>) {
    chomp $_;
    @passwd = split(/:/,$_);
    $pwd_list{"$passwd[0]"} = $passwd[1];
    push(@user_name_list, $passwd[0]);
}
close(FH);

#---------------------------------------------------
#---- read cookies for a user name and the password
#---------------------------------------------------

#-----------------------------------------
#--- treat special charactors for cookies
#-----------------------------------------

@Cookie_Encode_Chars = ('\%', '\+', '\;', '\,', '\=', '\&', '\:\:', '\s');

%Cookie_Encode_Chars = ('\%',   '%25',
            '\+',   '%2B',
            '\;',   '%3B',
            '\,',   '%2C',
            '\=',   '%3D',
            '\&',   '%26',
            '\:\:', '%3A%3A',
            '\s',   '+');

@Cookie_Decode_Chars = ('\+', '\%3A\%3A', '\%26', '\%3D', '\%2C', '\%3B', '\%2B', '\%25');

%Cookie_Decode_Chars = ('\+',       ' ',
            '\%3A\%3A', '::',
            '\%26',     '&',
            '\%3D',     '=',
            '\%2C',     ',',
            '\%3B',     ';',
            '\%2B',     '+',
            '\%25',     '%');

#----------------
#--- read cookies
#----------------

$submitter = cookie('submitter');
$pass_word = cookie('pass_word');

#-------------------
#--- decode cookies
#-------------------

foreach $char (@Cookie_Decode_Chars) {
    $submitter  =~ s/$char/$Cookie_Decode_Chars{$char}/g;
    $pass_word  =~ s/$char/$Cookie_Decode_Chars{$char}/g;
}

#-----------------------------------------------
#---- find out whether there are param passed on
#-----------------------------------------------

$submitter = param('submitter') || $submitter;
$pass_word = param('password')  || $pass_word;

#-------------------
#--- refresh cookies
#-------------------

$en_submitter = $submitter;
$en_pass_word = $pass_word;

foreach $char (@Cookie_Encode_Chars) {
    $en_submitter   =~ s/$char/$Cookie_Encode_Chars{$char}/g;
    $en_pass_word   =~ s/$char/$Cookie_Encode_Chars{$char}/g;
}

$user_cookie = cookie(-name    => 'submitter',
                      -value   => "$en_submitter",
                      -path    => '/',
                      -expires => '+8h');

$pass_cookie = cookie(-name    => 'pass_word',
                      -value   => "$en_pass_word",
                      -path    => '/',
                      -expires => '+8h');

#-------------------------
#---- new cookies worte in
#-------------------------

print header(-cookie=>[$user_cookie, $pass_cookie], -type => 'text/html;  charset=utf-8');

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print '<meta charset="UTF-8">';
print "<title>Ocat Data Page</title>";
print "<style  type='text/css'>";
print "table{border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
#
#--- javascript to open popup html page
#
print '<script>';
print '    function WindowOpener(html) {';
print '    msgWindow = open("","displayname","toolbar=no,directories=no,';
print '                     menubar=no, location=no,scrollbars=yes,status=no,';
print '                     width=1000,height=1500,resize=no");';
print '    msgWindow.document.write("<html><body>");';
print '    msgWindow.document.write("<iframe src=\'" + html + "\' border=0 width=980 height=1480>");';
print '    msgWindow.document.write("</body></html>");';
print '    msgWindow.document.close();';
print '    msgWindow.resizeTo(1000, 1500);';
print '    msgWindow.focus();';
print '}';
#
#--- javascript to open popup sky map
#
print '    function ImageOpener(img) {';
print '    imgWindow = open("", "displayname", "toolbar=no,directories=no,';
print '                     menubar=no, location=no,scrollbars=yes,status=no,';
print '                     width=700, height=700, resize=no");';
print '    imgWindow.document.write("<html><body><title>sky map</title>");';
print '    imgWindow.document.write("<img src=\'" + img + "\' border=0>");';
print '    imgWindow.document.write("</body></html>");';
print '    imgWindow.document.close();';
print '    imgWindow.resizeTo(700, 700);';
print '    imgWindow.focus();';
print '    }';
print '</script>';

print "</head>";

print "<body style='color:#000000;background-color:#FFFFE0'>";

#---------------------------------------
#------ read database to get the values
#---------------------------------------

read_databases($obsid, 0);			
#
#---- check which ones are not canceled, discarded, observed, or achived
#
@schdulable_list = ();
open(SIN, "$obs_ss/sot_ocat.out");
while(<SIN>){
  	chomp $_;
  	if($_ =~ /scheduled/ || $_ =~ /unobserved/){
      	@atemp    = split(/\^/, $_);
    	$atemp[1] =~ s/\s+//g;
        push(@schdulable_list, $atemp[1]);
   	}
}
close(SIN);

#------------------------------------------
#------ read MP scheduled observation list
#------------------------------------------

@mp_scheduled_list = ();
open(FH, "$obs_ss/scheduled_obs_list");

while(<FH>){
	chomp $_;
	@atemp = split(/\s+/, $_);
	push(@mp_scheduled_list, $atemp[0]);
}
close(FH);

#----------------------------------------------------------
#--- check whether the observation is in an active OR list
#----------------------------------------------------------

$mp_check = 0;
CHK_OUT:
foreach $check (@mp_scheduled_list){
	if($check =~ /$obsid/){
		$mp_check = 1;
		last;
	}
}

#----------------------------------------------------------------------------------
#------- start printing a html page here.
#------- there are three distinct html page. one is Ocat Data Page (data_input_page),
#------- second is Submit page (prep_submit), and the lastly, Oredit page (oredit).
#----------------------------------------------------------------------------------

print start_form();

$time_ordr_special = 'no';
$roll_ordr_special = 'no';
$ordr_special      = 'no';
$check             = param("Check");			#--- a param which indicates which page to be displayed 

#-------------------------------------------------
#--------- checking password!
#-------------------------------------------------

if($check eq ''){
	$chg_user_ind = param('chg_user_ind');
	match_user();               	            #--- sub to check inputed user and password

#---------------------------------------------------------------
#--------- if a user and a password do not match ask to re-type
#---------------------------------------------------------------

	if($chg_user_ind eq 'yes'){
		password_check();

	}elsif($pass eq '' || $pass eq 'no'){
    	if(($pass eq 'no') && ($submitter  ne ''|| $pass_word ne '')){
        	print "<h3 style='color:red'>Name and/or Password are not valid.</h3>";
    	}

    	password_check();       			    #--- this one create password input page

	}elsif($pass eq 'yes'){ 		    	    #--- ok a user and a password matched

#-------------------------------------------
#------ check whether s/he is a special user
#-------------------------------------------

		$sp_user   = 'yes';
		$access_ok = 'yes';
       	special_user();			                #--- sub to check whether s/he is a special user
        pi_check();			                    #--- sub to check whether the pi has an access

        data_input_page();                      #--- sub to display data for edit

	}else{
    	print 'Something wrong. Exit<br />';
    	exit(1);
	}
}

#----------------------------------
#--- password check finished.
#----------------------------------

pass_param();			                        #--- sub to pass parameters between submitting data

#-------------------------------------------------------------------------
#--- only if a user can access to the observation data, s/he can go futher
#-------------------------------------------------------------------------

if($access_ok eq 'yes'){	

#-------------------------------------------------------------------------
#--- if time, roll, and window constraints may need input page update...
#-------------------------------------------------------------------------

	if($check eq '     Add Time Rank     '){

    	pass_param();                           #--- a sub which passes all parameters between pages
    	$time_ordr         = param("TIME_ORDR");
    	$roll_ordr         = param("ROLL_ORDR");
    	$aciswin_no        = param("ACISWIN_NO");
    	$time_ordr_special = 'yes';
    	$roll_ordr_special = 'no';
    	$ordr_special      = 'no';
    	$time_ordr++;

    	data_input_page();                      #--- a sub to  print ocat data page

	}elsif($check eq 'Remove Null Time Entry '){

    	pass_param();
    	$time_ordr         = param("TIME_ORDR");
    	$roll_ordr         = param("ROLL_ORDR");
    	$aciswin_no        = param("ACISWIN_NO");
    	$time_ordr_special = 'yes';
    	$roll_ordr_special = 'no';
    	$ordr_special      = 'no';

    	data_input_page();

	}elsif($check eq '     Add Roll Rank     '){

    	pass_param();               
    	$time_ordr         = param("TIME_ORDR");
    	$roll_ordr         = param("ROLL_ORDR");
    	$aciswin_no        = param("ACISWIN_NO");
    	$time_ordr_special = 'no';
    	$roll_ordr_special = 'yes';
    	$ordr_special      = 'no';
    	$roll_ordr++;

    	data_input_page();              

	}elsif($check eq 'Remove Null Roll Entry '){

    	pass_param();
    	$time_ordr         = param("TIME_ORDR");
    	$roll_ordr         = param("ROLL_ORDR");
    	$aciswin_no        = param("ACISWIN_NO");
    	$time_ordr_special = 'no';
    	$roll_ordr_special = 'yes';
    	$ordr_special      = 'no';

    	data_input_page();

	}elsif($check eq '     Add Window Rank     '){

    	pass_param();               
    	$time_ordr         = param("TIME_ORDR");
    	$roll_ordr         = param("ROLL_ORDR");
    	$aciswin_no        = param("ACISWIN_NO");
    	$time_ordr_special = 'no';
    	$roll_ordr_special = 'no';
    	$ordr_special      = 'yes';
		
		$aciswin_no++;
	
		$add_window_rank   = 1;			        #--- need this to check whether ADD button is selected 
	
    	data_input_page();              

#------------------------------------------------
#--- or just s/he wants to update the main page.
#------------------------------------------------

	}elsif($check eq '     Update     '){
	
		pass_param();				
		data_input_page();			

#-------------------------------------------------------------------------------------------
#-------- change submitted to see no errors in the changes, and then display the information
#-------------------------------------------------------------------------------------------

	}elsif($check eq 'Submit'){
	
		pass_param();

        print hidden(-name=>'split_list', -value=>"$split_list");
        print "<input type='hidden' name='ORIG_TIME_ORDR'  value='$orig_time_ordr'>";
        print "<input type='hidden' name='ORIG_ROLL_ORDR'  value='$orig_roll_ordr'>";
        print "<input type='hidden' name='ORIG_ACISWIN_NO' value='$orig_aciswin_no'>";

		read_name();				            #--- sub to read descriptive name of database name

		prep_submit(0);				            #--- sub to  print a modification check page
	
		if($usr_ind == 0){
			user_warning();			            #--- sub to warn a user, a user name mistake 

#-----------------------------------------------------------------------------------
#---- ASIS and REMOVE cases, directly go to final submission. otherwise check errors.
#-----------------------------------------------------------------------------------

		}elsif($asis eq 'ASIS' || $asis eq 'REMOVE'){

			submit_entry(1, $obsid, $sf);       #--- check and submitting the modified input values

		}else{
			chk_entry();			            #--- check entries are in given ranges

			if($cdo_w_cnt > 0){
				$cout_name = "$obsid".'_cdo_warning';
				open(OUT, ">$temp_dir/$cout_name");
				foreach $ent (@cdo_warning){
					print OUT "$ent\n";
				}
				close(OUT);
			}
		}

#-----------------------------------------
#---- submit the change and send out email
#-----------------------------------------

	}elsif($check eq 'FINALIZE'){

		pass_param();
#
#--- if the asis is CLONE, make sure that split_list is empty
#
        if ($asis eq 'CLONE'){
            $split_list = '';
        }
#
#--- if this is a late submission (less than 10 days to scheduled date), warn MP
#
        if(length($soe_st_sched_date) > 0){
            $obs_time = $soe_st_sched_data;
        }else{
            $obs_time = $lts_lt_plan;
        }
        ($mchk, $sot_diff)  = check_obs_date_coming($obs_time);

        $schk = sp_list_test($split_list);
        if($schk == 1){
#
#--- checking whether any of the split observations is scheduled less than 10 days
#
            ($smchk, $sot_diff, @dummy) = split_obs_date_check($split_list, $sot_diff, $obsid);
            $mchk += $smchk;
#
#--- checking whether any of the split observations is in OR list
#
            ($smp_chk, @mp_w_list) = check_spl_obs_on_mp_list($split_list);
            $mp_check             += $smp_chk;
        }

        if($mchk > 0){
#
#--- read the sign off record list
#
            $ifile = "$ocat_dir/updates_table.list";
            open(FH, $ifile);
            @u_list = ();
            while(<FH>){
                chomp $_;
                push(@u_list, $_);
            }

            send_lt_warning_email();            #--- send mail to MP
            send_lt_warning_email2();           #--- send the copy to usint
#
#--- only when the observations is already on an active list, and there is actually
#--- changes, send a warning email to MP
#
		}elsif($mp_check > 0 && $cnt_modified > 0){
#
#--- read the sign off record list
#
            $ifile = "$ocat_dir/updates_table.list";
            open(FH, $ifile);
            @u_list = ();
            while(<FH>){
                chomp $_;
                push(@u_list, $_);
            }

			send_email_to_mp();		            #--- sending warning email to MP
        }
#
#--- sending warning emamil to CDO --- currently this is disabled
#
#        $cdo_notes = param('cdo_notes');
#        if(length($cdo_notes) > 0){
#            $cdo_notes =~ s/###/\n/g;
#            $cdo_notes =~ s/##/\n/g;
#            $cdo_notes =~ s/#/  /g;
#            send_email_to_cdo();
#        }
#
#--- sending warning emamil to MP
#
        $mp_notes = param('mp_notes');
        if(length($mp_notes) > 0){
            $mp_notes =~ s/###/\n/g;
            $mp_notes =~ s/##/\n/g;
            $mp_notes =~ s/#/  /g;
            send_email_to_mp();
        }

#--------------------------------------------------
#--- create data record and print email to send out
#--------------------------------------------------

        @base_list = ();
        $pbase     = 1;
#
#-- check whether split observation copy is requested
# 
        $schk = sp_list_test($split_list);
#
#--- checking whether to print the closing comment
#--- if "0", don't print the commnet since more submissions are coming
#
        $pind = 1;
        if($schk == 1){
            $pind = 0;
        }
		oredit($obsid, $sf, $pind);
        $pbase     = 0;

#--------------------------------------------------
#--- copy the current results to those on split_list
#--------------------------------------------------
        if($schk == 1){
            $asis_ind = param("ASIS");

            save_ranked_data();

            copy_split_observations($obsid, $split_list, $asis_ind);
        }
#
#------------------------------
#----- back to data entry page
#------------------------------

	}elsif($check eq 'PREVIOUS PAGE'){		    #--- this prints ocat data page without losing
							                    #--- input data typed in after moved to submitting page
		system("rm -f $temp_dir/*.$sf");

		pass_param();
		data_input_page();

#----------------------------------------------------------------------------------------------------
#--- if no action is taken yet, it comes here; you see this page first (after a user/a password page)
#----------------------------------------------------------------------------------------------------

	}else{
    	if($prev_app == 0){
        	data_input_page();                  #--- just print ocat data page
    	}
	}
}   ####---- the end of access_ok big loop

#
#--- end of the html document
#
print end_form();
print "</body>";
print "</html>";


#################################################################################################
#---- the main script finishes here. sub-scripts start here.
#################################################################################################



#########################################################################
### password_check: open a user - a password input page               ###
#########################################################################

sub password_check{
	print '<h3>Please type your user name and password</h3>';
    print '<table style="border-width:0px"><tr><th>Name</th><td>';
    print textfield(-name=>'submitter', -value=>'', -size=>20);
    print '</td></tr><tr><th>Password</th><td>';
    print password_field( -name=>'password', -value=>'', -size=>20);
    print '</td></tr></table><br />';

	print hidden(-name=>'Check', -override=>'', -value=>'');
    print '<input type="submit" name="Check" value="Submit">';
}

#########################################################################
### match_user: check a user and a password matches                   ###
#########################################################################

sub match_user{
	if($submitter eq ''){
    	$submitter = param('submitter');
    	$submitter =~s/^\s+//g;
    	$pass_word = param('password');
    	$pass_word =~s/^\s+//g;
	}
	
	$sp_status = 'no';
	if($usint_on =~ /yes/){
		$sp_status = 'yes';
	}
	if($pass eq 'yes'){
		$pass_status = 'match';
	}else{
    	OUTER:
    	foreach $test_name (@user_name_list){
        	$ppwd  = $pwd_list{"$submitter"};
        	$ptest = crypt("$pass_word","$ppwd");
	
        	if(($submitter =~ /$test_name/i) && ($ptest  eq $ppwd)){
            	$pass_status = 'match';
            	last OUTER;
        	}
    	}
	}

	if(($usint_on =~ /yes/) && ($sp_status eq 'yes') && ($pass_status eq 'match')){
		$pass = 'yes';
		print hidden(-name=>'pass', -override=>"$pass", -value=>"$pass");
    }else{
        $pass = 'no';
    }
}

#########################################################################
### special_user: check whether the user is a special user            ###
#########################################################################

sub special_user{

    $sp_user = 'no';
	$user    = lc($submitter);
    OUTER:
    foreach $comp (@special_user){
        if($user eq $comp){
            $sp_user = 'yes';
            last OUTER;
        }
    }
}

###################################################################################
### pi_check: check whether the observer has an access to the data              ###
###################################################################################

sub pi_check{
	if($sp_user eq 'yes'){
		$access_ok     = 'yes';
		$email_address = "$user".'@head.cfa.harvard.edu';
	}

	print hidden(-name=>'access_ok',     -value=>"$access_ok");
	print hidden(-name=>'pass',          -value=>"$pass");
	print hidden(-name=>'email_address', -value=>"$email_address");
}

################################################################################
### pass_param: passing cgi parameter values to the next window              ###
################################################################################

sub pass_param {
=comment
this sub receives parameter passed from the previous cgi page (form, pop-up window, hidden param etc),
converts them to variables which are usable for the new cgi page.
the most of the param were changed using @paramarray, but special cases (which allows multiple and
possibly undefind # of order), such as time constraint, roll constraint, and acis window constaint are
handled indivisually.
there are also a section which handles  different display names than database names.
=cut

#-------------------------------------------
#------- password check	and submiiter (user)
#-------------------------------------------

	$sp_user       = param('sp_user');
	$access_ok     = param('access_ok');
	$pass          = param('pass');
	$submitter     = param('submitter');
	$email_address = param('email_address');
	$si_mode       = param('SI_MODE');
	
#----------------------------
#------- other special cases
#----------------------------

	$awc_cnt       = param('awc_cnt');			    #--- ACIS Window Constraints Counter 
	$awc_ind       = param('awc_ind');			    #--- ACIS Window Constraints Indicator
	if($add_window_rank != 1){
		$aciswin_no    = param('ACISWIN_NO');		#--- ACIS Window Constraints Rank Counter
	}

#---------------------
#------- house keeping
#---------------------

	$sf        = param('tmp_suf');			        #--- suffix for temp file written in $temp_dir
								                    #--- this avoids to over write other user's file
								                    #--- see "submit_entry"
#
#--- tell you how many parameters are modified
#
	$cnt_modified  = param('cnt_modified');

#----------------------
#------- general cases
#----------------------

	foreach $ent (@paramarray){				        #--- paramarray has all parameter's names
#
#--- time order, roll order, and window space order must be checked
#
        if($time_ordr_special =~ /yes/i){
            if($ent =~ /TIME_ORDR/i){
                $time_ordr_special = 'no';

            }else{
                $new_entry    = lc ($ent);
                ${$new_entry} = param("$ent");
            }

        }elsif($roll_ordr_special =~ /yes/i){
            if($ent =~ /ROLL_ORDR/i){
                $roll_ordr_special = 'no';

            }else{
                $new_entry    = lc ($ent);
                ${$new_entry} = param("$ent");
            }

        }elsif($ordr_special =~/yes/i){
            if($ent  =~ /ACISWIN_ID/i){
                $ordr_special = 'no';

            }else{
                $new_entry    = lc ($ent);
                ${$new_entry} = param("$ent");
            }
#
#--- all other cases
#
        }else{
			$new_entry    = lc ($ent);
			${$new_entry} = param("$ent");
		}
	}

#-----------------------------------------------------------------------------------
#-------- time constarint case: there could be more than 1 order of data sets
#-------- (also roll and window constraints)
#-----------------------------------------------------------------------------------

	$time_ordr_add = param("TIME_ORDR_ADD");		#--- if window constraint is addred later, this will be 1
	for($j = 1; $j <= $time_ordr; $j++){
#
#---- if window constraint is set to Null, set tstart and stop to Null, too
#
		$name = 'WINDOW_CONSTRAINT'."$j";
		$window_constraint[$j] = param("$name");
		$null_ind = 0;
		if($window_constraint[$j] eq 'NO'
		    || $window_constraint[$j] eq 'NULL'
		    || $window_constraint[$j] eq 'NONE'
		    || $window_constraint[$j] eq ''
		    || $window_constraint[$j] eq 'N'){
			$null_ind = 1;
		}

		foreach $ent ('START_DATE', 'START_MONTH', 'START_YEAR', 'START_TIME',
			          'END_DATE',   'END_MONTH',   'END_YEAR',   'END_TIME',
			          'TSTART',     'TSTOP'){
			$name  = "$ent"."$j";
			$val   = param("$name");
			$lname = lc($ent);

			if($null_ind == 0){
				${$lname}[$j] = $val;
			}else{
				${$lname}[$j] = '';
			}
		}

		$tstart_new[$j] = '';					    #--- recombine tstart and tstop
		if($start_month[$j] ne 'NULL'){
            if($start_month[$j] =~/\D/){
                $out             = change_lmon_to_nmon($start_month[$j]);
                $start_month[$j] = adjust_digit($out);
            }
            $start_month[$j] = adjust_digit($start_month[$j]);
		}

		if($start_date[$j] =~ /\d/ && $start_month[$j] =~ /\d/ && $start_year[$j] =~ /\d/ ){
            if($start_time[$j] eq ''){
                $start_time[$j] = '00:00';
                $tind = 0;
            }else{
			    @ttemp   = split(/:/, $start_time[$j]);
			    $tind    = 0;
			    $time_ck = 0;
    
			    foreach $tent (@ttemp){
				    if($tent =~ /\D/ || $tind eq ''){
					    $tind++;
				    }else{
					    $time_ck = "$time_ck"."$tent";
				    }
			    }
            }

			if($tind == 0){
				$tstart_new  = "$start_month[$j]:$start_date[$j]:$start_year[$j]:$start_time[$j]";
				$chk_start   = -9999;

				if($tstart_new =~ /\s+/ || $tstart_new == ''){
                    #
                    #--- do nothing
                    #
				}else{
					$tstart[$j] = $tstart_new;
				}
			}
		}
		
		$tstop_new[$j] = '';
		if($end_month[$j] ne 'NULL'){
            if($end_month[$j] =~/\D/){
                $out           = change_lmon_to_nmon($end_month[$j]);
                $end_month[$j] = adjust_digit($out);
            }
            $end_month[$j] = adjust_digit($end_month[$j]);
		}
		if($end_date[$j] =~ /\d/ && $end_month[$j] =~ /\d/ && $end_year[$j] =~ /\d/ ){
            if($end_time[$j] eq ''){
                $end_time[$j] = '00:00';
                $tind = 0;
            }else{
			    @ttemp   = split(/:/, $end_time[$j]);
			    $tind    = 0;
			    $time_ck = 0;
    
			    foreach $tent (@ttemp){
				    if($tent =~ /\D/ || $tind eq ''){
					    $tind++;
				    }else{
					    $time_ck = "$time_ck"."$tent";
				    }
			    }
            }

			if($tind == 0){
				$tstop_new = "$end_month[$j]:$end_date[$j]:$end_year[$j]:$end_time[$j]";
				$chk_end = -9999;
				if($tstop_new =~ /\s+/ || $tstop_new == ''){
				}else{
					$tstop[$j] = $tstop_new;
				}
			}
		}

		if($window_constraint[$j]    eq 'Y')         {$dwindow_constraint[$j] = 'CONSTRAINT'}
		elsif($window_constraint[$j] eq 'CONSTRAINT'){$dwindow_constraint[$j] = 'CONSTRAINT'}
		elsif($window_constraint[$j] eq 'P')         {$dwindow_constraint[$j] = 'PREFERENCE'}
		elsif($window_constraint[$j] eq 'PREFERENCE'){$dwindow_constraint[$j] = 'PREFERENCE'}
        else{$window_constraint[$j] = 'NULL'; $dwindow_constraint[$j] = 'NULL'}
	}

	if($check eq 'Remove Null Time Entry '){
		if($time_ordr > 1){
			$new_ordr = $time_ordr;
			for($j = 1; $j <= $time_ordr; $j++){
				if($window_constraint[$j] =~ /Y/i 
                    || $window_constraint[$j] =~ /CONST/i || $window_constraint[$j] =~ /P/i){
					next;
				}
				for($k = $j; $k <= $time_ordr; $k++){
                    $jj = $k + 1;
					if($window_constraint[$jj] =~ /Y/i 
                        || $window_constraint[$jj] =~ /CONST/i || $window_constraint[$jj] =~ /P/i){

						$window_constraint[$k]  = $window_constraint[$jj];
						$dwindow_constraint[$k] = $dwindow_constraint[$jj];

						$start_month[$k]        = $start_month[$jj];
						$start_date[$k]         = $start_date[$jj];
						$start_year[$k]         = $start_year[$jj];
						$start_time[$k]         = $start_time[$jj];
						$end_month[$k]          = $end_month[$jj];
						$end_date[$k]           = $end_date[$jj];
						$end_year[$k]		    = $end_year[$jj];
						$end_time[$k]           = $end_time[$jj];

						$tstart[$k]             = $tstart[$jj];
						$tstop[$k]              = $tstop[$jj];
                    }else{
						$start_month[$k]        =  '';
						$start_date[$k]         =  '';
						$start_year[$k]         =  '';
						$start_time[$k]         =  '';
						$end_month[$k]          =  '';
						$end_date[$k]           =  '';
						$end_year[$k] 		    =  '';
						$end_time[$k]           =  '';

						$tstart[$k]             =  '';
						$tstop[$k]              =  '';
                    }
                }
                $new_ordr--;
			}
			$time_ordr = $new_ordr;
            if($time_ordr == 1 && $window_constraint[1] =~ /NULL/i){
                $window_flag = 'N';
            }
		}else{
            if($window_constraint[1] =~ /NULL/i){
			    $start_month[1]         =  '';
			    $start_date[1]          =  '';
			    $start_year[1]          =  '';
			    $start_time[1]          =  '';
			    $end_month[1]           =  '';
			    $end_date[1]            =  '';
			    $end_year[1]  		    =  '';
			    $end_time[1]            =  '';
    
			    $tstart[1]              =  '';
			    $tstop[1]               =  '';
             
                $time_ordr              = 1;
                $window_flag            = 'N';
            }
        }
		$check = '';
	}

    if($window_constraint[0] =~ /Y/ || $window_constraint[0] =~ /C/i || $window_constraint[0] =~ /P/i){
        $window_flag = 'Y';
    }

#------------------------------
#-------- roll constraint case
#------------------------------
#
#---if roll constraint add is requested later, this will be 1
#
	$roll_ordr_add = param("ROLL_ORDR_ADD");

	for($j = 1; $j <= $roll_ordr; $j++){
		foreach $ent ('ROLL_CONSTRAINT','ROLL_180','ROLL','ROLL_TOLERANCE'){
			$name     = "$ent"."$j";
			$val      =  param("$name");
			$lname    = lc($ent);
			${$lname}[$j] = $val;
		}
		if($roll_constraint[$j]    eq 'Y')         {$droll_constraint[$j] = 'CONSTRAINT'}
		if($roll_constraint[$j]    eq 'CONSTRAINT'){$droll_constraint[$j] = 'CONSTRAINT'}
		elsif($roll_constraint[$j] eq 'P')         {$droll_constraint[$j] = 'PREFERENCE'}
		elsif($roll_constraint[$j] eq 'PREFERENCE'){$droll_constraint[$j] = 'PREFERENCE'}
        else{$droll_constraint[$j] = 'NULL'}

        $droll_180[$j] = assign_dval($roll_180[$j]);
	}
#
#--- remove null roll entry
#
	if($check eq 'Remove Null Roll Entry '){
		if($roll_ordr > 1){
			$new_ordr = $roll_ordr;
			for($j = 1; $j <= $roll_ordr; $j++){
				if($roll_constraint[$j] =~ /Y/i || $roll_constraint[$j] =~ /CONST/i 
                    || $roll_constraint[$j] =~ /P/i){
					next;
				}
				for($k = $j; $k <= $roll_ordr; $k++){
                    $jj = $k + 1;
					if($roll_constraint[$jj] =~ /Y/i || $roll_constraint[$jj] =~ /CONST/i 
                        || $roll_constraint[$jj] =~ /P/i){

						$roll_constraint[$k]   = $roll_constraint[$jj];
						$droll_constraint[$k]  = $droll_constraint[$jj];
						$roll_180[$k]          = $roll_180[$jj];
						$droll_180[$k]         = $droll_180[$jj];
						$roll[$k]              = $roll[$jj];
						$roll_tolerance[$k]    = $roll_tolerance[$jj];
                    }else{

                        $roll_constraint[$k]   = 'NULL';
                        $droll_constraint[$k]  = 'NULL';
						$roll_180[$k]          = 'NULL';
						$droll_180[$k]         = 'NULL';
						$roll[$k]              = '';
						$roll_tolerance[$k]    = '';
                    }
					$new_ordr--;
                }
            }
            $roll_ordr = $new_ordr;
            if($roll_rodr == 1 && $roll_constraint[1] =~ /NULL/i){
                $roll_flag = 'N';
            }
	    }else{
            if($roll_constraint[1] =~ /NULL/i){
                $roll_constraint[1]    = 'NULL';
                $droll_constraint[1]   = 'NULL';
			    $roll_180[1]           = 'NULL';
			    $droll_180[1]          = 'NULL';
			    $roll[1]               = '';
			    $roll_tolerance[1]     = '';
    
                $roll_ordr             = 1;
                $roll_flag             = 'N';
            }
        }
		$check = '';
	}
#--------------------------
#-------- acis window case
#--------------------------

	if($spwindow =~ /Y/i){
        if($orig_aciswin_no == 0 && $aciswin_no == 0){
            $aciswin_no = 1;
		    $aciswin_id[0]      = 1;
		    $ordr[0]            = 1;
            $chip[0]            = 1;
            $dinclude_flag[0]   = 'INCLUDE';
            $include_flag[0]    = 'I';
            $start_row[0]       = '';
            $start_column[0]    = '';
            $height[0]          = '';
            $width[0]           = '';
            $lower_threshold[0] = '';
            $pha_range[0]       = '';
            $sample[0]          = '';
        }
		for($j = 0; $j < $aciswin_no; $j++){
			foreach $ent ('ACISWIN_ID', 'ORDR', 'CHIP',
					      'START_ROW','START_COLUMN','HEIGHT','WIDTH',
					      'LOWER_THRESHOLD','PHA_RANGE','SAMPLE'){
				$name     = "$ent"."$j";
				$val      =  param("$name");

                if($name =~ /LOWER_THRESHOLD/i && $val !~ /\d/){
                    $val  = 0.08;
                }elsif($name =~ /PHA_RANGE/i && $val !~ /\d/){
                    $val  = 13.0;
                }

				$lname    = lc($ent);
				${$lname}[$j] = $val;
			}

			$include_flag[$j]  = 'E';
			$dinclude_flag[$j] = 'EXCLUDE';
		}
	}elsif($spwindow =~ /N/i){
#
#---- if window filter is set to Null or No, set everything to a Null setting
#
		$aciswin_id[0]      = '';
		$ordr[0]            = '';
        $chip[0]            = 'NULL';
        $dinclude_flag[0]   = 'INCLUDE';
        $include_flag[0]    = 'I';
        $start_row[0]       = '';
        $start_column[0]    = '';
        $height[0]          = '';
        $width[0]           = '';
        $lower_threshold[0] = '';
        $pha_range[0]       = '';
        $sample[0]          = '';
	}

#----------------
#-------- others
#----------------

	$asis       = param("ASIS");
	$clone      = param("CLONE");
	$submitter  = param("USER");
	$dutysci    = param("USER");
	$acistag    = param("ACISTAG");
	$generaltag = param("GENERALTAG");
	$sitag      = param("SITAG");
	$instrument = param("INSTRUMENT");

    if($instrument =~ /HRC/i){
        $si_mode = param('HRC_SI_MODE');
    }else{
        $si_mode = param("SI_MODE");
    }
 
#---------------------------------------------------------------------------------
#------ here are the cases which database values and display values are different.
#---------------------------------------------------------------------------------

	if($multitelescope eq ''){$multitelescope = 'N'}

	if($proposal_joint eq ''){
		$proposal_joint     = 'N/A';
	}
	if($proposal_hst eq ''){
		$proposal_hst       = 'N/A';
	}
	if($proposal_noao eq ''){
		$proposal_noao      = 'N/A';
	}
	if($proposal_xmm eq ''){
		$proposal_xmm       = 'N/A';
	}
	if($rxte_approved_time eq ''){
		$rxte_approved_time = 'N/A';
	}
	if($vla_approved_time eq ''){
		$vla_approved_time  = 'N/A';
	}
	if($vlba_approved_time eq ''){
		$vlba_approved_time = 'N/A';
	}
	
    $dwindow_flag            = assign_dval($window_flag);
    if($window_flag eq '')          {$window_flag = 'NULL';}    

    $droll_flag             = assign_dval($roll_flag);
    if($roll_flag eq '')            {$roll_flag = 'NULL';}

    $ddither_flag           = assign_dval($dither_flag);
    if($dither_flag eq '')          {$dither_flag = 'NULL';}

    $duninterrupt           = assign_dval($uninterrupt);
    if($uninterrupt eq '')          {$uninterrupt = 'NULL';}

    $dphotometry_flag       = assign_dval($photometry_flag);

    $dconstr_in_remarks     = assign_dval($constr_in_remarks);

    $dphase_constraint_flag = assign_dval($phase_constraint_flag);
    if($phase_constraint_flag eq 'CONSTRAINT'){$dphase_constraint_flag = 'CONSTRAINT'}

    $dmonitor_flag          = assign_dval($monitor_flag);
    if($monitor_flag eq 'YES')      {$monitor_flag = 'Y'} 
    elsif($monitor_flag eq 'NO')    {$monitor_flag = 'N'}
#
#---- if phase constraint flag is set for Null, set all phase constraint params to Null
#
	if($phase_constraint_flag =~ /N/i 
		&& $phase_constraint_flag !~ /CONSTRAINT/i 
		&& $phase_constraint_flag !~ /PREFERENCE/i){
		$phase_epoch        = '';
		$phase_period       = '';
		$phase_start        = '';
		$phase_start_margin = '';
		$phase_end          = '';
		$phase_end_margin   = '';
	}

    $dmultitelescope  = assign_dval($multitelescope);
    $dhrc_zero_block  = assign_dval($hrc_zero_block);
	if($hrc_zero_block eq '')   {$hrc_zero_block = 'N';}
    $dmost_efficient  = assign_dval($most_efficient);
#
#--- New 02-04-21
#
    $dpointing_constraint   = assign_dval($pointing_constraint);

    ($dccdi0_on, $ccdi0_on) = ccd_on_check($ccdi0_on);
    ($dccdi1_on, $ccdi1_on) = ccd_on_check($ccdi1_on);
    ($dccdi2_on, $ccdi2_on) = ccd_on_check($ccdi2_on);
    ($dccdi3_on, $ccdi3_on) = ccd_on_check($ccdi3_on);

    ($dccds0_on, $ccds0_on) = ccd_on_check($ccds0_on);
    ($dccds1_on, $ccds1_on) = ccd_on_check($ccds1_on);
    ($dccds2_on, $ccds2_on) = ccd_on_check($ccds2_on);
    ($dccds3_on, $ccds3_on) = ccd_on_check($ccds3_on);
    ($dccds4_on, $ccds4_on) = ccd_on_check($ccds4_on);
    ($dccds5_on, $ccds5_on) = ccd_on_check($ccds5_on);
	
	$count_ccd_on = 0;
    foreach $tccd ($ccdi0_on, $ccdi1_on, $ccdi2_on, $ccdi3_on,
                   $ccds0_on, $ccds1_on, $ccds2_on, $ccds3_on, $ccds4_on, $ccds5_on){
        if($tccd =~ /Y/i) {$count_ccd_on++}
        if($tccd =~ /0/i) {$count_ccd_on++}
    }
	
    $dduty_cycle              = assign_dval($duty_cycle);
    $donchip_sum              = assign_dval($onchip_sum);
    $deventfilter             = assign_dval($eventfilter);
    $dmultiple_spectral_lines = assign_dval($multiple_spectral_lines);
    $dspwindow                = assign_dval($spwindow);
    $dextended_src            = assign_dval($extended_src);

    $dsubarray                = assign_dval($subarray);
    if($subarray eq 'N')         {$subarray  = 'NONE'}
    elsif($subarray eq 'NO')     {$subarray  = 'NONE'}
    elsif($subarray eq 'YES')    {$subarray  = 'CUSTOM'}
    elsif($subarray eq 'CUSTOM') {$dsubarray = 'YES'}


	if($hrc_timing_mode eq 'N'){
		$dhrc_timing_mode = 'NO'

	}elsif($hrc_timing_mode eq 'Y'){
		$dhrc_timing_mode = 'YES'
	}
#
#--- coordindate format check
#
	if($ra =~ /;/){					            #--- if someone mis-typed ":" for ";"
		if($ra =~ /:/){
			$ra =~ s/;/:/g;
		}else{
			$ra =~ s/;/ /g;
		}
	}
	if($ra =~ /:/){					            #--- if ra is in HH:MM:SS form, change it into dra
		$ra =~s/\s+//g;
		@rtemp = split(/:/,$ra);
		$ra    = 15.0*($rtemp[0] + $rtemp[1]/60 + $rtemp[2]/3600);
		$ra    = sprintf "%3.6f",$ra;
	}else{
		@rtemp = split(/\s+/, $ra);		        #---if ra is in HH MM SS form, change it into dra
		if($rtemp[0] eq ''){
			$rtemp[0] = $rtemp[1];
			$rtemp[1] = $rtemp[2];
			$rtemp[2] = $rtemp[3];
		}

		if($rtemp[0] =~ /\d/ && $rtemp[1] =~ /\d/ && $rtemp[2] =~ /\d/){
			$ra = 15.0*($rtemp[0] + $rtemp[1]/60 + $rtemp[2]/3600);
			$ra = sprintf "%3.6f",$ra;
		}
	}

	if($dec =~ /;/){				            #--- if someone mis-typed ";" for ":"
		if($dec =~ /:/){
			$dec =~ s/;/:/g;
		}else{
			$dec =~ s/;/ /g;
		}
	}
	if($dec =~ /:/){				            #--- if dec is in DDD:MM:SS form, change it into ddec
		$dec =~ s/\s+//g;
		@dtemp = split(/:/, $dec);
		$zzz   = abs ($dtemp[2]);
		if($zzz =~ /\d/){
			$sign  = 1;
			@etemp = split(//, $dec);
			if($etemp[0] eq '-'){
				$sign = -1;
			}
			$dec = $sign * (abs($dtemp[0]) + $dtemp[1]/60 + $dtemp[2]/3600);
			$dec = sprintf "%3.6f",$dec;
		}
	}else{
		@dtemp = split(/\s+/, $dec);		   #--- if dec is in DDD MM SS form, change it into ddec
		if($dtemp[0] eq ''){
			if($dtemp[1] eq '-' || $dtemp[1] eq '+'){
				$dtemp[0] = "$dtemp[1]$dtemp[2]";
				$dtemp[1] = $dtemp[3];
				$dtemp[2] = $dtemp[4];
			}else{
				$dtemp[0] = $dtemp[1];
				$dtemp[1] = $dtemp[2];
				$dtemp[2] = $dtemp[3];
			}
		}elsif($dtemp[0] eq '-' || $detemp[0] eq '+'){
				$dtemp[0] = "$dtemp[0]$dtemp[1]";
				$dtemp[1] = $dtemp[2];
				$dtemp[2] = $dtemp[3];
		}
			

		if($dtemp[0] =~ /\d/ && $dtemp[1] =~ /\d/ && $dtemp[2] =~ /\d/){
			$zzz = abs ($dtemp[2]);
			if($zzz =~ /\d/){
				$sign  = 1;
				if($dtemp[0] < 0){
					$sign = -1;
				}
				$dec = $sign * (abs($dtemp[0]) + $dtemp[1]/60 + $dtemp[2]/3600);
				$dec = sprintf "%3.6f",$dec;
			}
		}
	}
	$dra  = $ra;
	if($ddec == 0 && $ddec =~ /-/){
		$ddec = 0.000000;
	}
	$ddec = $dec;
#
#----- check whether ACIS Window Constraints Lowest Energy exceeds 0.5 keV limit.
#
	for($j = 0; $j < $aciswin_no; $j++){
		if($chip[$j] =~ /N/i){
			$lower_threshold[$j] = '';
			$pha_range[$j]       = '';
			$sample[$j]      = '';
		}elsif($lower_threshold[$j] > 0.5){
			$awc_l_th = 1;
		}
	}
#
#----- dether params
#
	if($y_amp =~ /\d/ || $y_amp_asec =~ /\d/){
    	$y_amp   = $y_amp_asec/3600;
	}

	if($z_amp =~ /\d/ || $z_amp_asec =~ /\d/){
    	$z_amp   = $z_amp_asec/3600;
	}

	if($y_freq =~ /\d/ || $y_freq_asec =~ /\d/){
    	$y_freq   = $y_freq_asec/3600;
	}

	if($z_freq =~ /\d/ || $z_freq_asec =~ /\d/){
    	$z_freq   = $z_freq_asec/3600;
	}
#
#--- hrc si mode change only notification
#
    $hrc_si_select = param('hrc_si_select');
#
#--- extra split_obsid list
#
    $split_list    = param('split_list');

}

################################################################################
################################################################################
################################################################################

sub ccd_on_check{
    (my $ccd_on) = @_;
    my $dccd_on  = 'NULL';
	
	if($ccd_on    eq 'NULL')        {$dccd_on = 'NULL'}
	elsif($ccd_on eq 'Y')           {$dccd_on = 'YES'}
	elsif($ccd_on eq 'YES')         {$dccd_on = 'YES'}
	elsif($ccd_on eq 'N')           {$dccd_on = 'NO'}
	elsif($ccd_on eq 'NO')          {$dccd_on = 'NO'}
	elsif($ccd_on eq 'OPT1')        {$dccd_on = 'OPT1'}
	elsif($ccd_on eq 'OPT2')        {$dccd_on = 'OPT2'}
	elsif($ccd_on eq 'OPT3')        {$dccd_on = 'OPT3'}
	elsif($ccd_on eq 'OPT4')        {$dccd_on = 'OPT4'}
	elsif($ccd_on eq 'OPT5')        {$dccd_on = 'OPT5'}

	if($ccd_on    eq 'OPT1')        {$ccd_on  = 'O1'}
	elsif($ccd_on eq 'OPT2')        {$ccd_on  = 'O2'}
	elsif($ccd_on eq 'OPT3')        {$ccd_on  = 'O3'}
	elsif($ccd_on eq 'OPT4')        {$ccd_on  = 'O4'}
	elsif($ccd_on eq 'OPT5')        {$ccd_on  = 'O5'}
    
    return ($dccd_on, $ccd_on);
}	

################################################################################
################################################################################
################################################################################
	
sub assign_dval{

    (my $val) = @_;
    my $dval  = 'NULL';

    if($val    eq '')    {$val  = 'NULL'}

	if($val    eq 'NULL'){$dval = 'NULL'}
	elsif($val eq 'Y')	 {$dval = 'YES'}
	elsif($val eq 'YES') {$dval = 'YES'}
	elsif($val eq 'N')	 {$dval = 'NO'}
	elsif($val eq 'NO')	 {$dval = 'NO'}

    elsif($val eq 'P')          {$dval = 'PREFERENCE'}
    elsif($val eq 'PREFERENCE') {$dval = 'PREFERENCE'}


    return $dval;
}

################################################################################
### sub read_databases: read out values from databases                       ###
################################################################################

sub read_databases{
    (my $obsid, my $rep_ind) = @_;
    $rep_ind //= 0;

#------------------------------------------------
#-------  database username, password, and server
#------------------------------------------------

    $web = $ENV{'HTTP_REFERER'};
    if($web =~ /icxc/){
        $db_user   = "mtaops_internal_web";
	    $db_passwd =`cat $pass_dir/.targpass_internal`;
    }else{
        $db_user = "mtaops_public_web";
	    $db_passwd =`cat $pass_dir/.targpass_public`;
    }
	$server    = "ocatsqlsrv";

	chop $db_passwd;

#--------------------------------------
#-------- open connection to sql server
#--------------------------------------

	my $db = "server=$server;database=axafocat";
	$dsn1  = "DBI:Sybase:$db";
	$dbh1  = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});

#-------------------------------------------
#-----------  get remarks from target table
#-------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select remarks  from target where obsid=$obsid));
	$sqlh1->execute();
	($remarks) = $sqlh1->fetchrow_array;
	$sqlh1->finish;

#---------------------------------------------
#----------  get mp remarks from target table
#---------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select mp_remarks  from target where obsid=$obsid));
	$sqlh1->execute();
  	($mp_remarks) = $sqlh1->fetchrow_array;
	$sqlh1->finish;

#------------------------------------------------------
#---------------  get stuff from target table, clean up
#------------------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select 
		obsid,targid,seq_nbr,targname,obj_flag,object,si_mode,photometry_flag, 
		vmagnitude,ra,dec,est_cnt_rate,forder_cnt_rate,y_det_offset,z_det_offset, 
		raster_scan,dither_flag,approved_exposure_time,pre_min_lead,pre_max_lead, 
		pre_id,seg_max_num,aca_mode,phase_constraint_flag,ocat_propid,acisid, 
		hrcid,grating,instrument,rem_exp_time,soe_st_sched_date,type,lts_lt_plan, 
		mpcat_star_fidlight_file,status,data_rights,tooid,description,
		total_fld_cnt_rate, extended_src,uninterrupt, multitelescope,observatories,
		tooid, constr_in_remarks, group_id, obs_ao_str, roll_flag, window_flag, spwindow_flag,
        multitelescope_interval,
        pointing_constraint
	from target where obsid=$obsid));
	$sqlh1->execute();
    	@targetdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

#--------------------------------------------------------------------------
#------- fill values from target table
#------- doing this the long way so I can see what I'm doing and make sure
#------- everything is accounted for
#--------------------------------------------------------------------------

	$targid		 		     = $targetdata[1];
	$seq_nbr		 	     = $targetdata[2];
	$targname		 	     = $targetdata[3];
	$obj_flag		 	     = $targetdata[4];
	$object		 		     = $targetdata[5];
	$si_mode		 	     = $targetdata[6];
	$photometry_flag	     = $targetdata[7];
	$vmagnitude		 	     = $targetdata[8];
	$ra		 	   	         = $targetdata[9];
	$dec		 		     = $targetdata[10];
	$est_cnt_rate		     = $targetdata[11];
	$forder_cnt_rate	     = $targetdata[12];
	$y_det_offset		     = $targetdata[13];
	$z_det_offset		     = $targetdata[14];
	$raster_scan		     = $targetdata[15];
	$dither_flag		     = $targetdata[16];
	$approved_exposure_time	 = $targetdata[17];
	$pre_min_lead		 	 = $targetdata[18];
	$pre_max_lead 			 = $targetdata[19];
	$pre_id				     = $targetdata[20];
	$seg_max_num		 	 = $targetdata[21];
	$aca_mode		 	     = $targetdata[22];
	$phase_constraint_flag 	 = $targetdata[23];
	$proposal_id		  	 = $targetdata[24];
	$acisid				     = $targetdata[25];
	$hrcid		 		     = $targetdata[26];
	$grating		 	     = $targetdata[27];
	$instrument		 	     = $targetdata[28];
	$rem_exp_time		 	 = $targetdata[29];
	$soe_st_sched_date		 = $targetdata[30];
	$type				     = $targetdata[31];
	$lts_lt_plan		   	 = $targetdata[32];
	$mpcat_star_fidlight_file= $targetdata[33];
	$status		 		     = $targetdata[34];
	$data_rights		 	 = $targetdata[35];
	$tooid 		 		     = $targetdata[36];
	$description 		 	 = $targetdata[37];
	$total_fld_cnt_rate		 = $targetdata[38];
	$extended_src 		 	 = $targetdata[39];
	$uninterrupt 			 = $targetdata[40];
	$multitelescope 		 = $targetdata[41];
	$observatories 		 	 = $targetdata[42];
	$tooid 				     = $targetdata[43];
	$constr_in_remarks		 = $targetdata[44];
	$group_id 			     = $targetdata[45];
	$obs_ao_str 			 = $targetdata[46];
	$roll_flag		 	     = $targetdata[47];
	$window_flag 			 = $targetdata[48];
	$spwindow			     = $targetdata[49];
	$multitelescope_interval = $targetdata[50];
    $pointing_constraint     = $targetdata[51];

#------------------------------------------------
#---- check group_id and find out related obsids
#------------------------------------------------

	$group_id     =~ s/\s+//g;
	$pre_id       =~ s/\s+//g;
	$pre_min_lead =~ s/\s+//g;
	$pre_max_lead =~ s/\s+//g;

	$monitor_flag = "N";
	if ($pre_id){
    	$monitor_flag = "Y";
	}

	$sqlh1 = $dbh1->prepare(qq(select distinct pre_id from target where pre_id=$obsid));	
	$sqlh1->execute();
	$pre_id_match = $sqlh1->fetchrow_array;
	$sqlh1->finish;
	if($pre_id_match){
		$monitor_flag = "Y";
	}

	if ($group_id){
   		$monitor_flag = "N";
	
		$sqlh1 = $dbh1->prepare(qq(select
    		obsid
		from target where group_id = \'$group_id\'));
		$sqlh1->execute();

		while(@group_obsid = $sqlh1->fetchrow_array){
    		$group_obsid = join("<td>", $group_obsid);
			if($usint_on =~ /test/){
                $line  = "<a href=\"$test_http\/ocatdata2html.cgi\?$group_obsid\">$group_obsid<\/a> ";
    			@group = (@group, $line);
			}else{
                $line  = "<a href=\"$usint_http\/ocatdata2html.cgi\?$group_obsid\">$group_obsid<\/a> ";
    			@group = (@group, $line);
			}
		}
#
#---  output formatting
#
   		$group_count = 0;
   		foreach (@group){
       		$group_count ++;
       		if(($group_count % 10) == 0){
	       		@group[$group_count - 1] = "@group[$group_count - 1]<br />";
       		}
   		}
		$group_cnt    = $group_count;
   		$group_count .= " obsids for ";
	}else{
		if($monitor_flag !~ /Y/i){
   			undef $pre_min_lead;
    		undef $pre_max_lead;
  			undef $pre_id;
		}
	}

#------------------------------------------------------------------
#---- if monitoring flag is Y, find which ones are monitoring data
#------------------------------------------------------------------

    if($monitor_flag =~ /Y/i){
        &series_rev($obsid);
        &series_fwd($obsid);
        %seen = ();
        @uniq = ();
        foreach $monitor_elem (@monitor_series) {
            push(@uniq, $monitor_elem) unless $seen{$monitor_elem}++;
        }
        @monitor_series = sort @uniq;
    }

#-------------------------------------------------
#---- updating AO number for the observation
#---- ao value is different from org and current
#-------------------------------------------------

	$proposal_id =~ s/\s+//g;
    $sqlh1 = $dbh1->prepare(qq(select
        ao_str
    from prop_info where ocat_propid=$proposal_id ));

    $sqlh1->execute();
    @updatedata   = $sqlh1->fetchrow_array;
    $sqlh1->finish;
    $obs_ao_str = $updatedata[0];
    $obs_ao_str =~ s/\s+//g;

#-----------------------------------------------------------------------
#------- roll requirement database
#------- first, get roll_ordr to see how many orders are in the database
#-----------------------------------------------------------------------

	$roll_ordr = '';
	OUTER:
	for($incl= 1; $incl < 30; $incl++){
		$sqlh1 = $dbh1->prepare(qq(select ordr from rollreq where ordr=$incl and obsid=$obsid));
		$sqlh1->execute();
    	@rollreq_data = $sqlh1->fetchrow_array;
		$sqlh1->finish;
		if($rollreq_data[0] eq ''){
			next OUTER;
		}
		$roll_ordr = $rollreq_data[0];
		$roll_ordr =~ s/\s+//g;
	}
	if($roll_ordr =~ /\D/ || $roll_ordr eq ''){
		$roll_ordr = 1;
	}

#-----------------------------------------------------------------
#-------- get the rest of the roll requirement data for each order
#-----------------------------------------------------------------

    for ($tordr = 1; $tordr < 30; $tordr++){
		$roll_constraint[$tordr] =  'NULL';
		$roll_180[$tordr]        =  'NULL';
		$roll[$tordr]            =  'NULL';
		$roll_tolerance[$tordr]  =  'NULL';
    }

	for($tordr = 1; $tordr <= $roll_ordr; $tordr++){

		$sqlh1 = $dbh1->prepare(qq(select 
			roll_constraint,roll_180,roll,roll_tolerance 
		from rollreq where ordr = $tordr and obsid=$obsid));
		$sqlh1->execute();
		@rollreq_data = $sqlh1->fetchrow_array;
		$sqlh1->finish;

		$roll_constraint[$tordr] = $rollreq_data[0];
		$roll_180[$tordr]        = $rollreq_data[1];
		$roll[$tordr]            = $rollreq_data[2];
		$roll_tolerance[$tordr]  = $rollreq_data[3];
	}

#-----------------------------------------------------------------------
#------ time requirement database
#------ first, get time_ordr to see how many orders are in the database
#-----------------------------------------------------------------------

	@window_constraint = ();
	@tstart = ();
	@tstop  = ();
	OUTER:
	for($incl= 1; $incl < 30; $incl++){
		$sqlh1 = $dbh1->prepare(qq(select ordr from timereq where ordr=$incl and obsid=$obsid));
		$sqlh1->execute();
		@timereq_data = $sqlh1->fetchrow_array;
		$sqlh1->finish;
		if($timereq_data[0] eq ''){
			next OUTER;
		}
		$time_ordr = $timereq_data[0];				#--- here is time order
		$time_ordr =~ s/\s+//g;
	}
	if($time_ordr =~ /\D/ || $time_ordr eq ''){
		$time_ordr = 1;
	}

#--------------------------------------------------------------
#----- get the rest of the time requirement data for each order
#--------------------------------------------------------------

    for ($tordr = 1; $tordr < 30; $tordr++){
		$window_constraint[$tordr] = 'NULL';
		$tstart[$tordr]            = '';
		$tstop[$tordr]             = '';
	}
	for($tordr = 1; $tordr <= $time_ordr; $tordr++){
		$sqlh1 = $dbh1->prepare(qq(select 
			window_constraint, tstart, tstop  
		from timereq where ordr = $tordr and obsid=$obsid));
		$sqlh1->execute();
		@timereq_data = $sqlh1->fetchrow_array;
		$sqlh1->finish;
#
#--- New 02-04-21 (modified)
#
        $val = $timereq_data[0];
        if($val eq ''){$val = 'NULL'}
		$window_constraint[$tordr] = $val;

		$tstart[$tordr]            = $timereq_data[1];
		$tstop[$tordr]             = $timereq_data[2];
	}

#-----------------------------------------------------------------
#---------- if it's a TOO, get remarks and trigger from TOO table
#-----------------------------------------------------------------

	if ($tooid) {
		$sqlh1 = $dbh1->prepare(qq(select 
			type,trig,start,stop,followup,remarks,tooid 
		from too where tooid=$tooid));
		$sqlh1->execute();
		@toodata = $sqlh1->fetchrow_array;
		$sqlh1->finish;

    		$too_type     = $toodata[0];
    		$too_trig     = $toodata[1];
    		$too_start    = $toodata[2];
    		$too_stop     = $toodata[3];
    		$too_followup = $toodata[4];
    		$too_remarks  = $toodata[5];
    		$too_id       = $toodata[6];
	} else {
    		$too_type     = "NULL";
    		$too_trig     = "NULL";
    		$too_start    = "NULL";
    		$too_stop     = "NULL";
    		$too_followup = "NULL";
    		$too_remarks  = "";
    		$too_id       = "NULL";
	}

#------------------------------------------------------------------------
#------------  if it's an hrc observation, get values from hrcparam table
#------------------------------------------------------------------------

	if ($hrcid){
		$sqlh1 = $dbh1->prepare(qq(select 
			hrc_zero_block,timing_mode,si_mode 
		from hrcparam where hrcid=$hrcid));
		$sqlh1->execute();
		@hrcdata = $sqlh1->fetchrow_array;
		$sqlh1->finish;
        
    	$hrc_zero_block  = $hrcdata[0];
    	$hrc_timing_mode = $hrcdata[1];
		$hrc_si_mode     = $hrcdata[2];
        $si_mode         = $hrc_si_mode;

	} else {
    	$hrc_zero_block  = "N";
    	$hrc_timing_mode = "N";
		$hrc_si_mode	 = "NULL";
	}

#--------------------------------------------------------------------------
#-----------  if it's an acis observation, get values from acisparam table
#--------------------------------------------------------------------------

	if ($acisid){
		$sqlh1 = $dbh1->prepare(qq(select 
			exp_mode,
			ccdi0_on, ccdi1_on, ccdi2_on, ccdi3_on,
			ccds0_on, ccds1_on, ccds2_on, ccds3_on, ccds4_on,ccds5_on,
			bep_pack, onchip_sum, onchip_row_count, onchip_column_count, frame_time,
			subarray, subarray_start_row, subarray_row_count, 
			duty_cycle, secondary_exp_count, primary_exp_time,
			eventfilter, eventfilter_lower, eventfilter_higher,
			most_efficient, dropped_chip_count,
			multiple_spectral_lines,  spectra_max_count

		from acisparam where acisid=$acisid));
		$sqlh1->execute();
		@acisdata = $sqlh1->fetchrow_array;
		$sqlh1->finish;
        
    	$exp_mode 		        = $acisdata[0];
    	$ccdi0_on 		        = $acisdata[1];
    	$ccdi1_on 		        = $acisdata[2];
    	$ccdi2_on 		        = $acisdata[3];
    	$ccdi3_on 		        = $acisdata[4];

    	$ccds0_on 		        = $acisdata[5];
    	$ccds1_on 		        = $acisdata[6];
    	$ccds2_on 		        = $acisdata[7];
    	$ccds3_on 		        = $acisdata[8];
    	$ccds4_on 		        = $acisdata[9];
    	$ccds5_on 		        = $acisdata[10];

    	$bep_pack 		        = $acisdata[11];
    	$onchip_sum      	    = $acisdata[12];
    	$onchip_row_count    	= $acisdata[13];
    	$onchip_column_count 	= $acisdata[14];
    	$frame_time      	    = $acisdata[15];

    	$subarray        	    = $acisdata[16];
    	$subarray_start_row  	= $acisdata[17];
    	$subarray_row_count  	= $acisdata[18];
    	$duty_cycle      	    = $acisdata[19];
    	$secondary_exp_count 	= $acisdata[20];

    	$primary_exp_time    	= $acisdata[21];
    	$eventfilter     	    = $acisdata[22];
    	$eventfilter_lower   	= $acisdata[23];
    	$eventfilter_higher  	= $acisdata[24];
    	$most_efficient      	= $acisdata[25];

		$dropped_chip_count     = $acisdata[26];
		$multiple_spectral_lines= $acisdata[27];
		$spectra_max_count      = $acisdata[28];

	} else {
    	$exp_mode 		        = "NULL";
    	$ccdi0_on 		        = "NULL";
    	$ccdi1_on 		        = "NULL";
    	$ccdi2_on 		        = "NULL";
    	$ccdi3_on 		        = "NULL";
    	$ccds0_on 		        = "NULL";
    	$ccds1_on 		        = "NULL";
    	$ccds2_on 		        = "NULL";
    	$ccds3_on 		        = "NULL";
    	$ccds4_on 		        = "NULL";
    	$ccds5_on 		        = "NULL";
    	$bep_pack 		        = "NULL";
    	$onchip_sum         	= "NULL";
    	$onchip_row_count    	= "NULL";
    	$onchip_column_count 	= "NULL";
    	$frame_time      	    = "NULL";
    	$subarray        	    = "NONE";
    	$subarray_start_row  	= "NULL";
    	$subarray_row_count  	= "NULL";
    	$subarray_frame_time 	= "NULL";
    	$duty_cycle      	    = "NULL";
    	$secondary_exp_count 	= "NULL";
    	$primary_exp_time    	= "";
    	$eventfilter     	    = "NULL";
    	$eventfilter_lower   	= "NULL";
    	$eventfilter_higher  	= "NULL";
    	$spwindow        	    = "NULL";
    	$most_efficient      	= "NULL";
		$dropped_chip_count     = "NULL";
		$multiple_spectral_lines= "NULL";
		$spectra_max_count      = "NULL";
	}

#-------------------------------------------------------------------
#-------  get values from aciswin table
#-------  first, get aciswin_id to see whether there are any aciswin param set
#-------------------------------------------------------------------


    for($j = 0; $j < 30; $j++){
		$ordr[$j]	         = '';
		$start_row[$j]       = '';
		$start_column[$j]    = '';
		$width[$j]	         = '';
		$height[$j]	         = '';
		$lower_threshold[$j] = '';
		$pha_range[$j]       = '';
		$sample[$j]	         = '';
		$chip[$j]	         = '';
		$include_flag[$j]    = '';
		$aciswin_id[$j]      = '';
    }
	$sqlh1 = $dbh1->prepare(qq(select  aciswin_id  from aciswin where  obsid=$obsid));
	$sqlh1->execute();
	@aciswindata = $sqlh1->fetchrow_array;
	$sqlh1->finish;
	$aciswin_id[0] = $aciswindata[0];
	$aciswin_id[0] =~ s/\s+//g;

	if($aciswin_id[0] =~ /\d/){
		$sqlh1 = $dbh1->prepare(qq(select
			ordr, start_row, start_column, width, height, lower_threshold,
			pha_range, sample, chip, include_flag , aciswin_id
		from aciswin where obsid=$obsid));
		$sqlh1->execute();
		$j = 0;
		while(my(@aciswindata) = $sqlh1->fetchrow_array){

			$ordr[$j]	         = $aciswindata[0];
			$start_row[$j]       = $aciswindata[1];
			$start_column[$j]    = $aciswindata[2];
			$width[$j]	         = $aciswindata[3];
			$height[$j]	         = $aciswindata[4];
			$lower_threshold[$j] = $aciswindata[5];

			if($lower_threshold[$j] > 0.5){
				$awc_l_th = 1;
			}

			$pha_range[$j]       = $aciswindata[6];
			$sample[$j]	         = $aciswindata[7];
			$chip[$j]	         = $aciswindata[8];
			$include_flag[$j]    = $aciswindata[9];
			$aciswin_id[$j]      = $aciswindata[10];

			$j++;
		}
		$aciswin_no = $j;
#
#--- reorder the rank with increasing order value sequence (added Jul 14, 2015)
#
        if($aciswin_no > 0){
            @rlist = ();
            for($i = 0; $i < $aciswin_no; $i++){
                push(@rlist, $ordr[$i]);
            }
            @sorted = sort{$a<=>$b} @rlist;
            @tlist = ();
            foreach $ent (@sorted){
                for($i = 0; $i < $aciswin_no; $i++){
                    if($ent == $ordr[$i]){
                        push(@tlist, $i);
                    }
                }
            }
        
            @temp0 = ();
            @temp1 = ();
            @temp2 = ();
            @temp3 = ();
            @temp4 = ();
            @temp5 = ();
            @temp6 = ();
            @temp7 = ();
            @temp8 = ();
            @temp9 = ();
            @temp10= ();
        
            for($i = 0; $i < $aciswin_no; $i++){
                $pos = $tlist[$i];
        
                push(@temp0 , $ordr[$pos]);
                push(@temp1 , $start_row[$pos]);
                push(@temp2 , $start_column[$pos]);
                push(@temp3 , $width[$pos]);
                push(@temp4 , $height[$pos]);
                push(@temp5 , $lower_threshold[$pos]);
                push(@temp6 , $pha_range[$pos]);
                push(@temp7 , $sample[$pos]);
                push(@temp8 , $chip[$pos]);
                push(@temp9 , $include_flag[$pos]);
                push(@temp10, $aciswin_id[$pos]);
            }
            @ordr            = @temp0;
            @start_row       = @temp1;
            @start_column    = @temp2;
            @width           = @temp3;
            @height          = @temp4;
            @lower_threshold = @temp5;
            @pha_range       = @temp6;
            @sample          = @temp7;
            @chip            = @temp8;
            @include_flag    = @temp9;
            @aciswin_id      = @temp10;
        
        }

		$sqlh1->finish;

	}else{

#--------------------------------------------------------
#----    no acis wind constrain parameters are assigned.
#--------------------------------------------------------

		$aciswin_no = 0;
	}

#---------------------------------
#-------  get values from phasereq
#---------------------------------

	$sqlh1 = $dbh1->prepare(qq(select 
		phase_period,phase_epoch,phase_start,phase_end, 
		phase_start_margin, phase_end_margin 
	from phasereq where obsid=$obsid));
	$sqlh1->execute();
	@phasereqdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$phase_period       = $phasereqdata[0];
	$phase_epoch        = $phasereqdata[1];
	$phase_start        = $phasereqdata[2];
	$phase_end          = $phasereqdata[3];
	$phase_start_margin = $phasereqdata[4];
	$phase_end_margin   = $phasereqdata[5];

#------------------------------
#------  get values from dither
#------------------------------

	$sqlh1 = $dbh1->prepare(qq(select 
		y_amp,y_freq,y_phase,z_amp,z_freq,z_phase 
	from dither where obsid=$obsid));
	$sqlh1->execute();
	@ditherdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$y_amp   = $ditherdata[0];
	$y_freq  = $ditherdata[1];
	$y_phase = $ditherdata[2];
	$z_amp   = $ditherdata[3];
	$z_freq  = $ditherdata[4];
	$z_phase = $ditherdata[5];

#-----------------------------
#--------  get values from sim
#-----------------------------

	$sqlh1 = $dbh1->prepare(qq(select 
		trans_offset,focus_offset 
	from sim where obsid=$obsid));
	$sqlh1->execute();
	@simdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$trans_offset = $simdata[0];
	$focus_offset = $simdata[1];

#---------------------------
#------  get values from soe
#---------------------------

	$sqlh1 = $dbh1->prepare(qq(select soe_roll from soe where obsid=$obsid and unscheduled='N'));
	$sqlh1->execute();
	@soedata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$roll_obsr = $soedata[0];

#------------------------------------
#-------    get values from prop_info
#------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select 
		prop_num,title,joint from prop_info 
	where ocat_propid=$proposal_id));
	$sqlh1->execute();
	@prop_infodata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$proposal_number = $prop_infodata[0];
	$proposal_title  = $prop_infodata[1];
	$proposal_joint  = $prop_infodata[2];
	$proposal_hst    = $prop_infodata[3];
	$proposal_noao   = $prop_infodata[4];
	$proposal_xmm    = $prop_infodata[5];
	$proposal_rxte   = $prop_infodata[6];
	$proposal_vla    = $prop_infodata[7];
	$proposal_vlba   = $prop_infodata[8];

#---------------------------------------------------
#-----  get proposer's and observer's last names
#---------------------------------------------------

    $sqlh1 = $dbh1->prepare(qq(select  
       last  from view_pi where ocat_propid=$proposal_id));
    $sqlh1->execute();
    $PI_name = $sqlh1->fetchrow_array;
    $sqlh1->finish;
 
    $sqlh1 = $dbh1->prepare(qq(select  
        last  from view_coi where ocat_propid=$proposal_id));
    $sqlh1->execute();
    $Observer = $sqlh1->fetchrow_array;
    $sqlh1->finish;

    if($Observer eq ""){
        $Observer = $PI_name;
    }

#-------------------------------------------------
#---- Disconnect from the server
#-------------------------------------------------

	$dbh1->disconnect();

#-----------------------------------------------------------------
#------ these ~100 lines are to remove the whitespace from most of
#------ the obscat dump entries.  
#-----------------------------------------------------------------
	$targid  		        =~ s/\s+//g; 
	$seq_nbr 		        =~ s/\s+//g; 
	$targname 		        =~ s/\s+//g; 
	$obj_flag 		        =~ s/\s+//g; 
	if($obj_flag 		    =~ /NONE/){
		$obj_flag 	        = "NO";
	}
	$object 		        =~ s/\s+//g; 
	$si_mode 		        =~ s/\s+//g; 
	$photometry_flag 	    =~ s/\s+//g; 
	$vmagnitude 		    =~ s/\s+//g; 
	$ra 			        =~ s/\s+//g; 
	$dec 			        =~ s/\s+//g; 
	$est_cnt_rate 		    =~ s/\s+//g; 
	$forder_cnt_rate 	    =~ s/\s+//g; 
	$y_det_offset 		    =~ s/\s+//g; 
	$z_det_offset 		    =~ s/\s+//g; 
	$raster_scan 		    =~ s/\s+//g; 
	$defocus 		        =~ s/\s+//g; 
	$dither_flag 		    =~ s/\s+//g; 
	$roll 			        =~ s/\s+//g; 
	$roll_tolerance 	    =~ s/\s+//g; 
	$approved_exposure_time =~ s/\s+//g; 
	$pre_min_lead 		    =~ s/\s+//g; 
	$pre_max_lead 		    =~ s/\s+//g; 
	$pre_id 		        =~ s/\s+//g; 
	$seg_max_num 		    =~ s/\s+//g; 
	$aca_mode 		        =~ s/\s+//g; 
	$phase_constraint_flag 	=~ s/\s+//g; 
	$proposal_id 		    =~ s/\s+//g; 
	$acisid 		        =~ s/\s+//g; 
	$hrcid 			        =~ s/\s+//g; 
	$grating 		        =~ s/\s+//g; 
	$instrument 		    =~ s/\s+//g; 
	$rem_exp_time 		    =~ s/\s+//g; 
	$type 			        =~ s/\s+//g; 
	$mpcat_star_fidlight_file =~ s/\s+//g; 
	$status 		        =~ s/\s+//g; 
	$data_rights 		    =~ s/\s+//g; 
	$server_name 		    =~ s/\s+//g; 
	$hrc_zero_block 	    =~ s/\s+//g; 
	$hrc_timing_mode 	    =~ s/\s+//g;
	$hrc_si_mode 		    =~ s/\s+//g;
	$exp_mode 		        =~ s/\s+//g; 
	$ccdi0_on 		        =~ s/\s+//g; 
	$ccdi1_on 		        =~ s/\s+//g; 
	$ccdi2_on 		        =~ s/\s+//g; 
	$ccdi3_on 		        =~ s/\s+//g; 
	$ccds0_on 		        =~ s/\s+//g; 
	$ccds1_on 		        =~ s/\s+//g; 
	$ccds2_on 		        =~ s/\s+//g; 
	$ccds3_on 		        =~ s/\s+//g; 
	$ccds4_on 		        =~ s/\s+//g; 
	$ccds5_on 		        =~ s/\s+//g; 
	$bep_pack 		        =~ s/\s+//g; 
	$onchip_sum 		    =~ s/\s+//g; 
	$onchip_row_count 	    =~ s/\s+//g; 
	$onchip_column_count 	=~ s/\s+//g; 
	$frame_time 		    =~ s/\s+//g; 
	$subarray 		        =~ s/\s+//g; 
	$subarray_start_row 	=~ s/\s+//g; 
	$subarray_row_count 	=~ s/\s+//g; 
	$subarray_frame_time 	=~ s/\s+//g; 
	$duty_cycle 		    =~ s/\s+//g; 
	$secondary_exp_count 	=~ s/\s+//g; 
	$primary_exp_time 	    =~ s/\s+//g; 
	$secondary_exp_time 	=~ s/\s+//g; 
	$eventfilter 		    =~ s/\s+//g; 
	$eventfilter_lower 	    =~ s/\s+//g; 
	$eventfilter_higher 	=~ s/\s+//g; 
	$multiple_spectral_lines=~ s/\s+//g;
	$spectra_max_count      =~ s/\s+//g;
	$spwindow 		        =~ s/\s+//g; 
	$multitelescope_interval=~ s/\s+//g;
	$phase_period 		    =~ s/\s+//g; 
	$phase_epoch 		    =~ s/\s+//g; 
	$phase_start 		    =~ s/\s+//g; 
	$phase_end 		        =~ s/\s+//g; 
	$phase_start_margin 	=~ s/\s+//g; 
	$phase_end_margin 	    =~ s/\s+//g; 
	$PI_name 		        =~ s/\s+//g; 
	$proposal_number 	    =~ s/\s+//g; 
	$trans_offset 		    =~ s/\s+//g; 
	$focus_offset 		    =~ s/\s+//g;
	$tooid 			        =~ s/\s+//g;
	$description 		    =~ s/\s+//g;
	$total_fld_cnt_rate 	=~ s/\s+//g;
	$extended_src 		    =~ s/\s+//g;
	$y_amp 			        =~ s/\s+//g;
	$y_freq 		        =~ s/\s+//g;
	$y_phase 		        =~ s/\s+//g;
	$z_amp 			        =~ s/\s+//g;
	$z_freq 		        =~ s/\s+//g;
	$z_phase 		        =~ s/\s+//g;
	$most_efficient 	    =~ s/\s+//g;
	$fep 			        =~ s/\s+//g;
	$dropped_chip_count     =~ s/\s+//g;
	$timing_mode 		    =~ s/\s+//g;
	$uninterrupt 		    =~ s/\s+//g;
	$proposal_joint 	    =~ s/\s+//g;
	$proposal_hst 		    =~ s/\s+//g;
	$proposal_noao 		    =~ s/\s+//g;
	$proposal_xmm 		    =~ s/\s+//g;
	$roll_obsr 		        =~ s/\s+//g;
	$multitelescope 	    =~ s/\s+//g;
	$observatories 		    =~ s/\s+//g;
	$too_type 		        =~ s/\s+//g;
	$too_start 		        =~ s/\s+//g;
	$too_stop 		        =~ s/\s+//g;
	$too_followup 		    =~ s/\s+//g;
	$roll_flag 		        =~ s/\s+//g;
	$window_flag 		    =~ s/\s+//g;
	$constr_in_remarks  	=~ s/\s+//g;
	$group_id  		        =~ s/\s+//g;
	$obs_ao_str  		    =~ s/\s+//g;
#
#--- New 02-04-21
#
    $pointing_constraint    =~ s/\s+//g;

#--------------------------------------------------------------------
#----- roll_ordr, time_ordr, and ordr need extra check for each order
#--------------------------------------------------------------------

	for($k = 1; $k <= $roll_ordr; $k++){
		$roll_constraint[$k] =~ s/\s+//g; 
		$roll_180[$k]        =~ s/\s+//g; 
		$roll[$k]            =~ s/\s+//g;
		$roll_tolerance[$k]  =~ s/\s+//g; 
	}

	for($k = 1; $k <= $time_ordr; $k++){
		$window_constraint[$k] =~ s/\s+//g; 
	}

	for($k = 0; $k < $aciswin_no; $k++){
		$aciswin_id[$k]      =~ s/\s+//g;
		$ordr[$k]            =~ s/\s+//g;
		$chip[$k]            =~ s/\s+//g;
		$include_flag[$k]    =~ s/\s+//g;
		$start_row[$k]       =~ s/\s+//g; 
		$start_column[$k]    =~ s/\s+//g; 
		$width[$k]           =~ s/\s+//g; 
		$height[$k]          =~ s/\s+//g; 
		$lower_threshold[$k] =~ s/\s+//g; 
		$pha_range[$k]       =~ s/\s+//g; 
		$sample[$k]          =~ s/\s+//g; 
	}

#-----------------------------------
#-----------  A FEW EXTRA SETTINGS
#-----------------------------------

	$ra   = sprintf("%3.6f", $ra);		                    #--- setting to 6 digit after a dicimal point
	$dec  = sprintf("%3.6f", $dec);
	$dra  = $ra;
	$ddec = $dec;

#---------------------------------------------------------------------------
#------- time need to be devided into year, month, day, and time for display
#---------------------------------------------------------------------------

	for($k = 1; $k <= $time_ordr; $k++){
		if($tstart[$k] ne ''){
			$input_time      = $tstart[$k];
			mod_time_format();		                        #--- sub mod_time_format changes time format
			$start_year[$k]  = $year;
			$start_month[$k] = $month;
			$start_date[$k]  = $day;
			$start_time[$k]  = $time;
            $amonth          =  adjust_digit($month);
			$tstart[$k]      = "$amonth:$day:$year:$time";
		}
		
		if($tstop[$k] ne ''){
			$input_time      = $tstop[$k];
			mod_time_format();
			$end_year[$k]    = $year;
			$end_month[$k]   = $month;
			$end_date[$k]    = $day;
			$end_time[$k]    = $time;
            $amonth          =  adjust_digit($month);
			$tstop[$k]       = "$amonth:$day:$year:$time";
		}
	}

#---------------------------------------------------------------------------------
#------ here are the cases which database values and display values are different.
#---------------------------------------------------------------------------------

	if($multitelescope eq '')           {$multitelescope = 'N'}
	if($proposal_joint eq '')           {$proposal_joint = 'N/A'}
	if($proposal_hst eq '')             {$proposal_hst = 'N/A'}
	if($proposal_noao eq '')            {$proposal_noao = 'N/A'}
	if($proposal_xmm eq '')             {$proposal_xmm = 'N/A'}
	if($rxte_approved_time eq '')       {$rxte_approved_time = 'N/A'}
	if($vla_approved_time eq '')        {$vla_approved_time = 'N/A'}
	if($vlba_approved_time eq '')       {$vlba_approved_time = 'N/A'}
#
#--- New 02-04-21
#
    if($pointing_constraint eq '')      {$pointing_constraint = 'N'}
	
	if($roll_flag    eq 'NULL')        	{$droll_flag = 'NULL'}
	elsif($roll_flag eq '')	        	{$droll_flag = 'NULL'; 
                                         $roll_flag  = 'NULL';}
	elsif($roll_flag eq 'Y')        	{$droll_flag = 'YES'}
	elsif($roll_flag eq 'N')        	{$droll_flag = 'NO'}
	elsif($roll_flag eq 'P')        	{$droll_flag = 'PREFERENCE'}
	
	if($window_flag    eq 'NULL')    	{$dwindow_flag = 'NULL'}
	elsif($window_flag eq '')	        {$dwindow_flag = 'NULL'; 
                                         $window_flag  = 'NULL';}
	elsif($window_flag eq 'Y')	        {$dwindow_flag = 'YES'}
	elsif($window_flag eq 'N')	        {$dwindow_flag = 'NO'}
	elsif($window_flag eq 'P')	        {$dwindow_flag = 'PREFERENCE'}
	
	if($dither_flag    eq 'NULL')    	{$ddither_flag = 'NULL'}
	elsif($dither_flag eq '')	        {$ddither_flag = 'NULL'; 
                                         $dither_flag  = 'NULL';}
	elsif($dither_flag eq 'Y')	        {$ddither_flag = 'YES'}
	elsif($dither_flag eq 'N')	        {$ddither_flag = 'NO'}
	
	if($uninterrupt    eq 'NULL')    	{$duninterrupt = 'NULL'}
	elsif($uninterrupt eq '')	        {$duninterrupt = 'NULL'; 
                                         $uninterrupt  = 'NULL';}
	elsif($uninterrupt eq 'N')	        {$duninterrupt = 'NO'}
	elsif($uninterrupt eq 'Y')	        {$duninterrupt = 'YES'}
	elsif($uninterrupt eq 'P')	        {$duninterrupt = 'PREFERENCE'}

	if($photometry_flag    eq 'NULL')	{$dphotometry_flag = 'NULL'}
	elsif($photometry_flag eq '') 		{$dphotometry_flag = 'NULL'; 
                                         $photometry_flag  = 'NULL'}
	elsif($photometry_flag eq 'Y')		{$dphotometry_flag = 'YES'}
	elsif($photometry_flag eq 'N')		{$dphotometry_flag = 'NO'}
	
	for($k = 1; $k <= $time_ordr; $k++){
		if($window_constraint[$k]    eq 'Y') {$dwindow_constraint[$k] = 'CONSTRAINT'}
		elsif($window_constraint[$k] eq 'P') {$dwindow_constraint[$k] = 'PREFERENCE'}
	}	
	
	for($k = 1; $k <= $roll_ordr; $k++){
		if($roll_constraint[$k]    eq 'Y')   {$droll_constraint[$k] = 'CONSTRAINT'}
		elsif($roll_constraint[$k] eq 'P')   {$droll_constraint[$k] = 'PREFERENCE'}
		elsif($roll_constraint[$k] eq 'N')   {$droll_constraint[$k] = 'NONE'}

		if($roll_180[$k]    eq 'Y'){$droll_180[$k] = 'YES'}
		elsif($roll_180[$k] eq 'N'){$droll_180[$k] = 'NO'}
		else{$droll_180[$k] = 'NULL'}
	}	

	if($constr_in_remarks eq '')        {$dconstr_in_remarks = 'NO'; 
                                         $constr_in_remarks  = 'N'}
	elsif($constr_in_remarks eq 'N')    {$dconstr_in_remarks = 'NO'}
	elsif($constr_in_remarks eq 'Y')    {$dconstr_in_remarks = 'YES'}
	elsif($constr_in_remarks eq 'P')    {$dconstr_in_remarks = 'PREFERENCE'}

	if($phase_constraint_flag eq 'NULL'){$dphase_constraint_flag = 'NULL'}
	elsif($phase_constraint_flag eq '') {$dphase_constraint_flag = 'NONE'; 
                                         $phase_constraint_flag  = 'NULL'}
	elsif($phase_constraint_flag eq 'N'){$dphase_constraint_flag = 'NONE'}
	elsif($phase_constraint_flag eq 'Y'){$dphase_constraint_flag = 'CONSTRAINT'}
	elsif($phase_constraint_flag eq 'P'){$dphase_constraint_flag = 'PREFERENCE'}

	if($monitor_flag eq 'NULL')   {$dmonitor_flag = 'NULL'}
	elsif($monitor_flag eq '')    {$dmonitor_flag = 'NULL'}
	elsif($monitor_flag eq 'Y')   {$dmonitor_flag = 'YES'}
	elsif($monitor_flag eq 'YES') {$dmonitor_flag = 'YES'}
	elsif($monitor_flag eq 'N')   {$dmonitor_flag = 'NONE'}
	elsif($monitor_flag eq 'NONE'){$dmonitor_flag = 'NONE'}
	elsif($monitor_flag eq 'NO')  {$dmonitor_flag = 'NO'}

	if($multitelescope eq 'Y')    {$dmultitelescope = 'YES'}
	elsif($multitelescope eq 'N') {$dmultitelescope = 'NO'}
	elsif($multitelescope eq 'P') {$dmultitelescope = 'PREFERENCE'}

	if($hrc_zero_block eq 'NULL') {$dhrc_zero_block = 'NULL'}
	elsif($hrc_zero_block eq '')  {$dhrc_zero_block = 'NO'; 
                                   $hrc_zero_block  = 'N';}
	elsif($hrc_zero_block eq 'Y') {$dhrc_zero_block = 'YES'}
	elsif($hrc_zero_block eq 'N') {$dhrc_zero_block = 'NO'}

	if($hrc_timing_mode eq 'NULL'){$dhrc_timing_mode = 'NULL'}
	elsif($hrc_timing_mode eq '') {$dhrc_timing_mode = 'NO'; 
                                   $hrc_timing_mode  = 'N';}
	elsif($hrc_timing_mode eq 'Y'){$dhrc_timing_mode = 'YES'}
	elsif($hrc_timing_mode eq 'N'){$dhrc_timing_mode = 'NO'}

	if($most_efficient eq 'NULL') {$dmost_efficient = 'NULL'}
	elsif($most_efficient eq '')  {$most_efficient  = 'NULL'; 
                                   $dmost_efficient = 'NULL'}
	elsif($most_efficient eq 'Y') {$dmost_efficient = 'YES'}
	elsif($most_efficient eq 'N') {$dmost_efficient = 'NO'}

	if($ccdi0_on eq 'NULL') {$dccdi0_on = 'NULL'}
	elsif($ccdi0_on eq '')  {$dccdi0_on = 'NULL'; $ccdi0_on = 'NULL'}
	elsif($ccdi0_on eq 'Y') {$dccdi0_on = 'YES'}
	elsif($ccdi0_on eq 'N') {$dccdi0_on = 'NO'}
	elsif($ccdi0_on eq 'O1'){$dccdi0_on = 'OPT1'}
	elsif($ccdi0_on eq 'O2'){$dccdi0_on = 'OPT2'}
	elsif($ccdi0_on eq 'O3'){$dccdi0_on = 'OPT3'}
	elsif($ccdi0_on eq 'O4'){$dccdi0_on = 'OPT4'}
	elsif($ccdi0_on eq 'O5'){$dccdi0_on = 'OPT5'}
	
	if($ccdi1_on eq 'NULL') {$dccdi1_on = 'NULL'}
	elsif($ccdi1_on eq '')  {$dccdi1_on = 'NULL'; $ccdi1_on = 'NULL'}
	elsif($ccdi1_on eq 'Y') {$dccdi1_on = 'YES'}
	elsif($ccdi1_on eq 'N') {$dccdi1_on = 'NO'}
	elsif($ccdi1_on eq 'O1'){$dccdi1_on = 'OPT1'}
	elsif($ccdi1_on eq 'O2'){$dccdi1_on = 'OPT2'}
	elsif($ccdi1_on eq 'O3'){$dccdi1_on = 'OPT3'}
	elsif($ccdi1_on eq 'O4'){$dccdi1_on = 'OPT4'}
	elsif($ccdi1_on eq 'O5'){$dccdi1_on = 'OPT5'}
	
	if($ccdi2_on eq 'NULL') {$dccdi2_on = 'NULL'}
	elsif($ccdi2_on eq '')  {$dccdi2_on = 'NULL'; $ccdi2_on = 'NULL'}
	elsif($ccdi2_on eq 'Y') {$dccdi2_on = 'YES'}
	elsif($ccdi2_on eq 'N') {$dccdi2_on = 'NO'}
	elsif($ccdi2_on eq 'O1'){$dccdi2_on = 'OPT1'}
	elsif($ccdi2_on eq 'O2'){$dccdi2_on = 'OPT2'}
	elsif($ccdi2_on eq 'O3'){$dccdi2_on = 'OPT3'}
	elsif($ccdi2_on eq 'O4'){$dccdi2_on = 'OPT4'}
	elsif($ccdi2_on eq 'O5'){$dccdi2_on = 'OPT5'}
	
	if($ccdi3_on eq 'NULL') {$dccdi3_on = 'NULL'}
	elsif($ccdi3_on eq '')  {$dccdi3_on = 'NULL'; $ccdi3_on = 'NULL'}
	elsif($ccdi3_on eq 'Y') {$dccdi3_on = 'YES'}
	elsif($ccdi3_on eq 'N') {$dccdi3_on = 'NO'}
	elsif($ccdi3_on eq 'O1'){$dccdi3_on = 'OPT1'}
	elsif($ccdi3_on eq 'O2'){$dccdi3_on = 'OPT2'}
	elsif($ccdi3_on eq 'O3'){$dccdi3_on = 'OPT3'}
	elsif($ccdi3_on eq 'O4'){$dccdi3_on = 'OPT4'}
	elsif($ccdi3_on eq 'O5'){$dccdi3_on = 'OPT5'}
	
	if($ccds0_on eq 'NULL') {$dccds0_on = 'NULL'}
	elsif($ccds0_on eq '')  {$dccds0_on = 'NULL'; $ccds0_on = 'NULL'}
	elsif($ccds0_on eq 'Y') {$dccds0_on = 'YES'}
	elsif($ccds0_on eq 'N') {$dccds0_on = 'NO'}
	elsif($ccds0_on eq 'O1'){$dccds0_on = 'OPT1'}
	elsif($ccds0_on eq 'O2'){$dccds0_on = 'OPT2'}
	elsif($ccds0_on eq 'O3'){$dccds0_on = 'OPT3'}
	elsif($ccds0_on eq 'O4'){$dccds0_on = 'OPT4'}
	elsif($ccds0_on eq 'O5'){$dccds0_on = 'OPT5'}
	
	if($ccds1_on eq 'NULL') {$dccds1_on = 'NULL'}
	elsif($ccds1_on eq '')  {$dccds1_on = 'NULL'; $ccds1_on = 'NULL'}
	elsif($ccds1_on eq 'Y') {$dccds1_on = 'YES'}
	elsif($ccds1_on eq 'N') {$dccds1_on = 'NO'}
	elsif($ccds1_on eq 'O1'){$dccds1_on = 'OPT1'}
	elsif($ccds1_on eq 'O2'){$dccds1_on = 'OPT2'}
	elsif($ccds1_on eq 'O3'){$dccds1_on = 'OPT3'}
	elsif($ccds1_on eq 'O4'){$dccds1_on = 'OPT4'}
	elsif($ccds1_on eq 'O5'){$dccds1_on = 'OPT5'}
	
	if($ccds2_on eq 'NULL') {$dccds2_on = 'NULL'}
	elsif($ccds2_on eq '')  {$dccds2_on = 'NULL'; $ccds2_on = 'NULL'}
	elsif($ccds2_on eq 'Y') {$dccds2_on = 'YES'}
	elsif($ccds2_on eq 'N') {$dccds2_on = 'NO'}
	elsif($ccds2_on eq 'O1'){$dccds2_on = 'OPT1'}
	elsif($ccds2_on eq 'O2'){$dccds2_on = 'OPT2'}
	elsif($ccds2_on eq 'O3'){$dccds2_on = 'OPT3'}
	elsif($ccds2_on eq 'O4'){$dccds2_on = 'OPT4'}
	elsif($ccds2_on eq 'O5'){$dccds2_on = 'OPT5'}
	
	if($ccds3_on eq 'NULL') {$dccds3_on = 'NULL'}
	elsif($ccds3_on eq '')  {$dccds3_on = 'NULL'; $ccds3_on = 'NULL'}
	elsif($ccds3_on eq 'Y') {$dccds3_on = 'YES'}
	elsif($ccds3_on eq 'N') {$dccds3_on = 'NO'}
	elsif($ccds3_on eq 'O1'){$dccds3_on = 'OPT1'}
	elsif($ccds3_on eq 'O2'){$dccds3_on = 'OPT2'}
	elsif($ccds3_on eq 'O3'){$dccds3_on = 'OPT3'}
	elsif($ccds3_on eq 'O4'){$dccds3_on = 'OPT4'}
	elsif($ccds3_on eq 'O5'){$dccds3_on = 'OPT5'}

	if($ccds4_on eq 'NULL') {$dccds4_on = 'NULL'}
	elsif($ccds4_on eq '')  {$dccds4_on = 'NULL'; $ccds4_on = 'NULL'}
	elsif($ccds4_on eq 'Y') {$dccds4_on = 'YES'}
	elsif($ccds4_on eq 'N') {$dccds4_on = 'NO'}
	elsif($ccds4_on eq 'O1'){$dccds4_on = 'OPT1'}
	elsif($ccds4_on eq 'O2'){$dccds4_on = 'OPT2'}
	elsif($ccds4_on eq 'O3'){$dccds4_on = 'OPT3'}
	elsif($ccds4_on eq 'O4'){$dccds4_on = 'OPT4'}
	elsif($ccds4_on eq 'O5'){$dccds4_on = 'OPT5'}

	if($ccds5_on eq 'NULL') {$dccds5_on = 'NULL'}
	elsif($ccds5_on eq '')  {$dccds5_on = 'NULL'; $ccds5_on = 'NULL'}
	elsif($ccds5_on eq 'Y') {$dccds5_on = 'YES'}
	elsif($ccds5_on eq 'N') {$dccds5_on = 'NO'}
	elsif($ccds5_on eq 'O1'){$dccds5_on = 'OPT1'}
	elsif($ccds5_on eq 'O2'){$dccds5_on = 'OPT2'}
	elsif($ccds5_on eq 'O3'){$dccds5_on = 'OPT3'}
	elsif($ccds5_on eq 'O4'){$dccds5_on = 'OPT4'}
	elsif($ccds5_on eq 'O5'){$dccds5_on = 'OPT5'}
#
#----  the end of the CCD OPT settings			
#

#
#---- ACIS subarray setting
#
	if($subarray eq '')         {$dsubarray = 'NO'}
	elsif($subarray eq 'N')     {$dsubarray = 'NO'}
	elsif($subarray eq 'NONE')  {$dsubarray = 'NO'}
	elsif($subarray eq 'CUSTOM'){$dsubarray = 'YES'}
	elsif($subarray eq 'Y')     {$dsubarray = 'YES'}


	if($duty_cycle eq 'NULL')  {$dduty_cycle = 'NULL'}
	elsif($duty_cycle eq '')   {$dduty_cycle = 'NULL'; 
                                $duty_cycle  = 'NULL'}
	elsif($duty_cycle eq 'Y')  {$dduty_cycle = 'YES'}
	elsif($duty_cycle eq 'YES'){$dduty_cycle = 'YES'}
	elsif($duty_cycle eq 'N')  {$dduty_cycle = 'NO'}
	elsif($duty_cycle eq 'NO') {$dduty_cycle = 'NO'}

	if($onchip_sum eq 'NULL')  {$donchip_sum = 'NULL'}
	elsif($onchip_sum eq '')   {$donchip_sum = 'NULL'; 
                                $onchip_sum  = 'NULL'}
	elsif($onchip_sum eq 'Y')  {$donchip_sum = 'YES'}
	elsif($onchip_sum eq 'N')  {$donchip_sum = 'NO'}

	if($eventfilter eq 'NULL') {$deventfilter = 'NULL'}
	elsif($eventfilter eq '')  {$deventfilter = 'NULL'; 
                                $eventfilter  = 'NULL'}
	elsif($eventfilter eq 'Y') {$deventfilter = 'YES'}
	elsif($eventfilter eq 'N') {$deventfilter = 'NO'}

    if($multiple_spectral_lines eq 'NULL') {$dmultiple_spectral_lines = 'NULL'}
    if($multiple_spectral_lines eq '')     {$dmultiple_spectral_lines = 'NULL'; 
                                            $multiple_spectral_lines  = 'NULL'}
    elsif($multiple_spectral_lines eq 'Y') {$dmultiple_spectral_lines = 'YES'}
    elsif($multiple_spectral_lines eq 'N') {$dmultiple_spectral_lines = 'NO'}

    if($spwindow eq 'NULL')    {$dspwindow = 'NULL'}
    elsif($spwindow eq '' )    {$dspwindow = 'NULL'; 
                                $spwindow  = 'NULL'}
    elsif($spwindow eq 'Y')    {$dspwindow = 'YES'}
    elsif($spwindow eq 'N')    {$dspwindow = 'NO'}

	if($spwindow eq 'NULL')    {$dspwindow = 'NULL'}
	elsif($spwindow eq '' )    {$dspwindow = 'NULL';  
                                $spwindow  = 'NULL'}
	elsif($spwindow eq 'Y')    {$dspwindow = 'YES'}
	elsif($spwindow eq 'N')    {$dspwindow = 'NO'}

	if($y_amp =~ /\d/){
    	$y_amp_asec  = 3600 * $y_amp;
	}else{
		$y_amp_asec  = $y_amp;
	}
	if($z_amp =~ /\d/){
    	$z_amp_asec  = 3600 * $z_amp;
	}else{
		$z_amp_asec  = $z_amp;
	}

	if($y_freq =~ /\d/){
    	$y_freq_asec = 3600 * $y_freq;
	}else{
		$y_freq_asec = $y_freq;
	}
	if($z_freq =~ /\d/){
    	$z_freq_asec = 3600 * $z_freq;
	}else{
		$z_freq_asec = $z_freq;
	}

	$orig_y_amp_asec  = $y_amp_asec;
	$orig_z_amp_asec  = $z_amp_asec;
	$orig_y_freq_asec = $y_freq_asec;
	$orig_z_freq_asec = $z_freq_asec;

    if($extended_src eq 'NULL') {$dextended_src = 'NO'}
    elsif($extended_src eq '')  {$dextended_src = 'NO'}
    elsif($extended_src eq 'N') {$dextended_src = 'NO'}
    elsif($extended_src eq 'Y') {$dextended_src = 'YES'}
#
#--- Other Constraints  (New 02-04-21)
#
    if($pointing_constraint eq 'NULL') {$dpointing_constraint = 'NULL'}
    elsif($pointing_constraint eq '')  {$dpointing_constraint = 'NULL'}
    elsif($pointing_constraint eq 'N') {$dpointing_constraint = 'NO'}
    elsif($pointing_constraint eq 'Y') {$dpointing_constraint = 'YES'}


#-------------------------------------------------------------
#----- define several arrays of parameter names for later use
#-------------------------------------------------------------

#-------------------------
#----- all the param names
#-------------------------

	@namearray = (
		SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,GROUP_ID,OBS_AO_STR,TARGNAME,
		SI_MODE,INSTRUMENT,GRATING,TYPE,PI_NAME,OBSERVER,APPROVED_EXPOSURE_TIME, REM_EXP_TIME,
		PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
		PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
		RA,DEC,ROLL_OBSR,DRA,DDEC,Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
		RASTER_SCAN,DITHER_FLAG,Y_AMP, Y_FREQ, Y_PHASE, Z_AMP, Z_FREQ, Z_PHASE,
		UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,VMAGNITUDE,EST_CNT_RATE,
		FORDER_CNT_RATE, TIME_ORDR,WINDOW_FLAG, ROLL_ORDR,ROLL_FLAG,
		CONSTR_IN_REMARKS,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,
		PHASE_START,PHASE_START_MARGIN, PHASE_END,PHASE_END_MARGIN,PRE_ID,
		PRE_MIN_LEAD,PRE_MAX_LEAD,MULTITELESCOPE, OBSERVATORIES,
		HRC_ZERO_BLOCK,HRC_TIMING_MODE,HRC_SI_MODE,
		EXP_MODE,BEP_PACK,FRAME_TIME,MOST_EFFICIENT,
		CCDI0_ON, CCDI1_ON, CCDI2_ON, CCDI3_ON, CCDS0_ON, CCDS1_ON, CCDS2_ON, 
		CCDS3_ON,CCDS4_ON, CCDS5_ON,
		SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
		DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
		ONCHIP_SUM,ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,
		EVENTFILTER_HIGHER,SPWINDOW,ACISWIN_NO, ACISWIN_ID,ORDR, FEP,DROPPED_CHIP_COUNT, BIAS_RREQUEST,
		TOO_ID,TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
		REMARKS,COMMENTS, MONITOR_FLAG, MULTITELESCOPE_INTERVAL, EXTENDED_SRC,
        POINTING_CONSTRAINT,
	);

#--------------------------------------------------
#----- all the param names passed between cgi pages
#--------------------------------------------------

	@paramarray = (
		SI_MODE,TARGNAME,
		INSTRUMENT,GRATING,TYPE,PI_NAME,OBSERVER,APPROVED_EXPOSURE_TIME, 
		RA,DEC,ROLL_OBSR,Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
		DITHER_FLAG,Y_AMP, Y_FREQ, Y_PHASE, Z_AMP, Z_FREQ, Z_PHASE,Y_AMP_ASEC, Z_AMP_ASEC,
		Y_FREQ_ASEC, Z_FREQ_ASEC, UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,
		VMAGNITUDE,EST_CNT_RATE, FORDER_CNT_RATE, TIME_ORDR,WINDOW_FLAG, ROLL_ORDR,ROLL_FLAG,
		CONSTR_IN_REMARKS,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,
		PHASE_START,PHASE_START_MARGIN, PHASE_END,PHASE_END_MARGIN,
		PRE_ID,PRE_MIN_LEAD,PRE_MAX_LEAD,MULTITELESCOPE, OBSERVATORIES,
		MULTITELESCOPE_INTERVAL,
        POINTING_CONSTRAINT,
		HRC_CONFIG,HRC_ZERO_BLOCK,HRC_TIMING_MODE,HRC_SI_MODE,
		EXP_MODE,BEP_PACK,FRAME_TIME,MOST_EFFICIENT,
		CCDI0_ON, CCDI1_ON, CCDI2_ON, CCDI3_ON, CCDS0_ON, CCDS1_ON, 
		CCDS2_ON, CCDS3_ON,CCDS4_ON, CCDS5_ON,
		SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
		DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
		ONCHIP_SUM,ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT, EVENTFILTER_HIGHER,SPWINDOW,
        ACISWIN_NO,
        ACISWIN_ID, 
		REMARKS,COMMENTS, ACISTAG,SITAG,GENERALTAG, DROPPED_CHIP_COUNT, GROUP_ID, MONITOR_FLAG,
		EXTENDED_SRC,
	);

#---------------------------------------------------------------
#----- all the param names passed not editable in ocat data page
#---------------------------------------------------------------

	@passarray = (
		SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,GROUP_ID,OBS_AO_STR,
		REM_EXP_TIME,RASTER_SCAN,ACA_MODE,
		PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
		PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
		TOO_ID,TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
		FEP,DROPPED_CHIP_COUNT,
	);

#--------------------------------------
#----- all the param names in acis data
#--------------------------------------
	
    @acisarray=(
        EXP_MODE,BEP_PACK,MOST_EFFICIENT,FRAME_TIME,
		CCDI0_ON,CCDI1_ON,CCDI2_ON,CCDI3_ON,
		CCDS0_ON,CCDS1_ON,CCDS2_ON,CCDS3_ON,CCDS4_ON,CCDS5_ON,
		SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
		DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
		ONCHIP_SUM,
		ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
		EVENTFILTER_HIGHER,DROPPED_CHIP_COUNT,SPWINDOW,
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT
	);

#---------------------------------------
#----- all the param in acis window data
#---------------------------------------

	@aciswinarray=(
        START_ROW,START_COLUMN,HEIGHT,WIDTH,LOWER_THRESHOLD,
	    PHA_RANGE,SAMPLE,ACISWIN_ID,ORDR,CHIP,
	);

#-------------------------------------------
#----- all the param in general data dispaly
#-------------------------------------------

	@genarray=(
        REMARKS,INSTRUMENT,GRATING,TYPE,RA,DEC,APPROVED_EXPOSURE_TIME,
		Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET, FOCUS_OFFSET,DEFOCUS,
		RASTER_SCAN,DITHER_FLAG, Y_AMP, Y_FREQ, Y_PHASE, Z_AMP, Z_FREQ, Z_PHASE,
		UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,VMAGNITUDE,
		EST_CNT_RATE,FORDER_CNT_RATE,ROLL,ROLL_TOLERANCE,TSTART,TSTOP,
		PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD, PHASE_START,
		PHASE_START_MARGIN,PHASE_END,PHASE_END_MARGIN,PRE_MIN_LEAD,
		PRE_MAX_LEAD,PRE_ID,HRC_SI_MODE,HRC_TIMING_MODE,HRC_ZERO_BLOCK,
		TOOID,TARGNAME,DESCRIPTION,SI_MODE,ACA_MODE,EXTENDED_SRC,SEG_MAX_NUM,
		Y_AMP,Y_FREQ,Y_PHASE, Z_AMP,Z_FREQ,Z_PHASE,HRC_CHOP_FRACTION,
		HRC_CHOP_DUTY_CYCLE,HRC_CHOP_DUTY_NO,TIMING_MODE, ROLL_OBSR, 
		MULTITELESCOPE, OBSERVATORIES, MULTITELESCOPE_INTERVAL, ROLL_CONSTRAINT, 
		WINDOW_CONSTRAINT, ROLL_ORDR, TIME_ORDR, ROLL_180,
		CONSTR_IN_REMARKS,ROLL_FLAG,WINDOW_FLAG, MONITOR_FLAG,
        POINTING_CONSTRAINT,
	);

#-------------------------------
#------ save the original values
#-------------------------------

	foreach $ent (@namearray){	
		$lname    = lc ($ent);
#
#---  for the original value, all variable name start from "orig_"
#
		$wname    = 'orig_'."$lname";
		${$wname} = ${$lname};
	}

#-------------------------------------
#------------------	special cases
#-------------------------------------

    if($dwindow_flag =~ /N/i && $orig_time_ordr != 0){
        $orig_time_ordr = 1;
    }
    if($droll_flag =~ /N/i &&  $orig_roll_ordr != 0){
        $orig_roll_ordr = 1;
    }
    if(length($orig_aciswin_no)){
        if($orig_aciswin_no eq '' || $orig_aciswin_no =~ /N/i){
            $orig_aciswin_no = 0;
        }
    }else{
        $orig_aciswin_no = 0;
    }

    if($rep_ind == 0){
        print "<input type='hidden' name='ORIG_TIME_ORDR'  value='$orig_time_ordr'>";
        print "<input type='hidden' name='ORIG_ROLL_ORDR'  value='$orig_roll_ordr'>";
        print "<input type='hidden' name='ORIG_ACISWIN_NO' value='$orig_aciswin_no'>";
    }
	$orig_ra  = $dra;
	$orig_dec = $ddec;

#----------------------------------------------
#------- special treatment for time constraint
#----------------------------------------------

	$ptime_ordr = $time_ordr + 1;
	for($j = $ptime_ordr; $j < 30; $j++){
		$start_date[$j]        = 'NULL';
		$start_month[$j]       = 'NULL';
		$start_year[$j]        = 'NULL';
		$end_date[$j]          = 'NULL';
		$end_month[$j]         = 'NULL';
		$end_year[$j]          = 'NULL';
		$tstart[$j]            = '';
		$tstop[$j]             = '';
		$window_constraint[$j] = 'NULL';
	}
	for($j = 1; $j < 30; $j++){
		$orig_start_date[$j]   = $start_date[$j];
		$orig_start_month[$j]  = $start_month[$j];
		$orig_start_year[$j]   = $start_year[$j];
		$orig_end_date[$j]     = $end_date[$j];
		$orig_end_month[$j]    = $end_month[$j];
		$orig_end_year[$j]     = $end_year[$j];
		$orig_tstart[$j]       = $tstart[$j];
		$orig_tstop[$j]        = $tstop[$j];
		$orig_window_constraint[$j] = $window_constraint[$j];
	}

	$time_ordr_add = 0;			 

#----------------------------------------------
#------ special treatment for roll requirements
#----------------------------------------------

	for($j = 1; $j <= $roll_ordr; $j++){   #--- make sure that all entries have some values for each order
		if($roll_constraint[$j] eq ''){ $roll_constraint[$j] = 'NULL'}
		if($roll_180[$j] eq ''){$roll_180[$j] = 'NULL'}
	}

	$proll_ordr = $roll_ordr + 1;

	for($j = $proll_ordr; $j < 30; $j++){	     #--- set default values up to order < 30, assuming that
		$roll_constraint[$j] = 'NULL';		     #--- we do not get the order larger than 29
		$roll_180[$j]        = 'NULL';
		$roll[$j]            = '';
		$roll_tolerance[$j]  = '';
	}

	for($j = 1; $j < 30; $j++){			         #--- save them as the original values
		$orig_roll_constraint[$j] = $roll_constraint[$j];
		$orig_roll_180[$j]        = $roll_180[$j];
		$orig_roll[$j]            = $roll[$j];
		$orig_roll_tolerance[$j]  = $roll_tolerance[$j];
	}

	$roll_ordr_add = 0;

#--------------------------------------------
#----- special treatment for acis window data
#--------------------------------------------

	for($j = 0; $j < $aciswin_no; $j++){
		if($chip[$j] eq '') {$chip[$j] = 'NULL'}
		if($chip[$j] eq 'N'){$chip[$j] = 'NULL'}
		if($include_flag[$j] eq '') {
			if($spwindow =~ /Y/i){
				$dinclude_flag[$j] = 'EXCLUDE'; 
				$include_flag[$j]  = 'E';
			}else{
				$dinclude_flag[$j] = 'INCLUDE'; 
				$include_flag[$j]  = 'I';
			}
		}
		if($include_flag[$j] eq 'I'){$dinclude_flag[$j] = 'INCLUDE'}
		if($include_flag[$j] eq 'E'){$dinclude_flag[$j] = 'EXCLUDE'}
	}

	for($j = $aciswin_no; $j < 30; $j++){
		$aciswin_id[$i]    = '';
		$ordr[$j]          = '';
		$chip[$j] 	       = 'NULL';
		$include_flag[$j]  = 'E';
		$dinclude_flag[$j] = 'EXCLUDE';
	}

	for($j = 0; $j < 30; $j++){
		$orig_aciswin_id[$j]      = $aciswin_id[$j];
		$orig_ordr[$j]            = $ordr[$j];
		$orig_chip[$j]            = $chip[$j];
		$orig_include_flag[$j]    = $include_flag[$j];
        $orig_start_row[$j]       = $start_row[$j];
        $orig_start_column[$j]    = $start_column[$j];
        $orig_width[$j]           = $width[$j];
        $orig_height[$j]          = $height[$j];
        $orig_lower_threshold[$j] = $lower_threshold[$j];
        $orig_pha_range[$j]       = $pha_range[$j];
        $orig_sample[$j]          = $sample[$j];

	}
#
#--- comment is not in the database; but needs to set orig_comment 
#
    $orig_comments = '';

#--------------------------------------------
#--- check planned roll
#--------------------------------------------

	find_planned_roll();

	$scheduled_roll  = ${planned_roll.$obsid}{planned_roll}[0];
	$scheduled_range = ${planned_roll.$obsid}{planned_range}[0];
}

########################################################################################
### data_input_page: create data input page--- Ocat Data Page                        ###
########################################################################################

sub data_input_page{

    print <<endofhtml;

endofhtml

    print '	<h1>Obscat Data Page</h1>';

    $schk = 0;
    if(length($soe_st_sched_date) > 0){
        $obs_time = $soe_st_sched_date;
        $schk = 1;
    }else{
        $obs_time = $lts_lt_plan;
    }

    ($lchk, $sot_diff) = check_obs_date_coming($obs_time);

    if($mp_check > 0){
	    print "<h2><strong style='color:red'>";
	    print "This observation is currently under review in an active OR list. ";
	    print "You must get a permission from MP to modify entries.";
        if(length($soe_st_sched_date) > 0){
            $obs_time = $soe_st_sched_date;
        }else{
            $obs_time = $lts_lt_plan;
        }
        print "<br><span style='font-size:80%;'>(Scheduled Date: "."$obs_time".'</span>)';
	    print "</strong></h2>";
    }else{
        if($lchk == 1){
	        print "<h2><strong style='color:red'>";
    
            if($sot_diff < 2){
                $ldays = 'day';
            }else{
                $ldays = 'days';
            }
            if($sot_diff < 0){
                if($status !~/schedule/i && $status !~/unobserved/i){
                    $pchk = 0;
                }else{
                    $pchk = 1;
                }
            }
            if($pchk > 0){
                if($schk == 0){
                    print "$sot_diff $ldays  left to LTS date, but the observation is not ";
                    print "scheduled yet.  You may want to check ";
                    print "whether this is still a possible observaiton date with MP.";
                }else{
                    print "$sot_diff $ldays  left to the scheduled date. You must get a permission ";
                    print "from MP to modify entries.";
                }
            }else{
                if($sot_diff == 0){
                    print "This observation is scheduled for today.";
                }
            }
            print '</strong></h2>';
        }
    }
#
#--- if the observation is observed, achived, cancelled, notify it
#
    if($status !~ /scheduled/i && $status !~ /unobserved/i){
	    $cap_status = uc($status);
	    print "<h2>This observation was <span style='color:red'>$cap_status</span>.</h2> ";
#
#--- when the scheduled date is passed but not observed yet...
#
    }elsif ($sot_diff < 0){
        print "<h2><span style='color:red;'>The scheduled (LTS) date of this observation "; 
        print " was already passed</span>.</h2>";
    }
    
    print '<p><b>A brief description of the listed parameters is given in: ';
    print '<a href="javascript:WindowOpener(\'./user_help.html\')">';
    print '<span style="background-color:lime;">Ocat Data Help Page</span></a>';
    print " </b></p>";
    
#----------------------------------------------------------------------
#---- if the observation is alrady in an active OR list, print warning
#----------------------------------------------------------------------

    if($eventfilter_lower > 0.5 || $awc_l_th == 1){
        print '<p style="color:red;padding-top:20px;padding-bottom:10px">';
	    print '<strong>';
	    if($eventfilter_lower > 0.5 && $awc_l_th == 0){
    	    print 'Energy Filter Lowest Energy is larger than 0.5 keV. ';
    
	    }elsif($eventfilter_lower > 0.5 && $awc_l_th == 1){
    	    print 'Energy Filter Lowest Energy and ACIS Window Costraint ';
            print 'Lowest Energy are larger than 0.5 keV. ';
    
	    }elsif($eventfilter_lower <= 0.5 && $awc_l_th == 1){
    	    print 'ACIS Window Costraint Lowest Energy is larger than 0.5 keV. ';
	    }
        print 'Please check all Spatial Window parameters of each CCD.';
	    print '</strong>';
	    print '</p>';
    }

	@ntest = split(//, $obsid);
	$tcnt  = 0;
	foreach(@ntest){
		$tcnt++;
	}
	if($tcnt < 5){
		$add_zero = '';
		for($mt = $tcnt; $mt < 5; $mt++){
			$add_zero = "$add_zero".'0';
		}
		$tobsid = "$add_zero"."$obsid";
	}else{
		$tobsid = $obsid;
	}

    $dss   = "$mp_http/targets/"."$seq_nbr".'/'."$seq_nbr".'.'."$tobsid".'.dss.gif';
    $rosat = "$mp_http/targets/"."$seq_nbr".'/'."$seq_nbr".'.'."$tobsid".'.pspc.gif';
    $rass  = "$mp_http/targets/"."$seq_nbr".'/'."$seq_nbr".'.'."$tobsid".'.rass.gif';

    print '<p align=left>';
    print '<a href="javascript:ImageOpener(\''."$dss".'\')">';
    print "<img align=middle src=\"$mp_http/targets/webgifs/dss.gif\"></a>";

    print '<a href="javascript:ImageOpener(\''."$rosat".'\')">';
    print "<img align=middle src=\"$mp_http/targets/webgifs/ros.gif\"></a>";

    print '<a href="javascript:ImageOpener(\''."$rass".'\')">';
    print "<img align=middle src=\"$mp_http/targets/webgifs/rass.gif\"></a>";
    print "<br>";
    print "<div style='padding-top:1px;'></div>";
    $slink = 'https://cda.cfa.harvard.edu/chaser/startViewer.do?menuItem=sequenceSummary&obsid='."$obsid";
    print '<a href="javascript:WindowOpener(\''."$slink".'\')">';
    print '<span style="background-color:lime;font-size:120%;"><b>';
    #print "<span style='font-size:130%;'>";
    print 'Sequence  # Summary';
    print '</span></b></a> (with Roll/Pitch/Visibility)';

    print '</p>';

	print '<h2>General Parameters';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#general_parameters\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

#------------------------------------------------>
#----- General Parameter dispaly starts here----->
#------------------------------------------------>

	print '<table style="border-width:0px">';
	print '<tr><td>&#160;</td>';
	print "<th>Sequence Number:";
	print "</th><td><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do?";
    print "menuItem=sequenceSummary&obsid=$obsid' target='_blank'>$seq_nbr</a></td>";
	print '<th>Status:';
	print "</th><td>$status</td>";
	print '<th>ObsID #:';
	print "</th><td>$obsid";
	print '<input type="hidden" name="OBSID" value="$obsid">';
	print "</td>";
	print '<th>Proposal Number:</th>';
	print "<td>$proposal_number</td>";
	print '</tr></table>';

	print '<table  style="border-width:0px">';
	print '<tr><td>&#160;</td>';
	print '<th>Proposal Title:</th>';
	print "<td>$proposal_title</td>";
	print '</tr>';
	print ' </table>';
	
	print '<table  style="border-width:0px">';
	print '<tr>';
	print '<td>&#160;</td>';
	print '<th>Obs AO Status:';
	print "</th><td>$obs_ao_str</td>";
	print '</tr></table>';

	print '<table  style="border-width:0px">';
	print '<tr><td>&#160;</td>';
#
#--- changed 03/23/21
#
	#print '<th>Target Name:</th><td>';
	#print "$targname",'</td>';
	
	print '<th>Target Name:</th>';
    print '<td style="text-align:left"><input type="text" name="TARGNAME" value="';
    print "$targname";
    print '" size="20"></td>';
#----------
	print '<th>SI Mode:</th>';

    print '<td>',$si_mode,'</td>';

	print '<th>ACA Mode:</th>';
	print '<td style="text-align:left">',"$aca_mode",'</td>';
	print '</tr></table>';

	print '<table style="border-width:0px">';
	print '<tr><td>&#160;</td>';

	print '<th>Instrument:</th><td>';
	print popup_menu(-name=>'INSTRUMENT', 
                     -value=>['ACIS-I','ACIS-S','HRC-I','HRC-S'],
		 	         -default=>"$instrument",-override=>100000);
	
	print '</td><th>Grating:</th><td>';
	print popup_menu(-name=>'GRATING', 
                     -value=>['NONE','HETG','LETG'],
		 	         -default=>"$grating",-override=>10000);
	
	print '</td><th>Type:</th><td>';
	print popup_menu(-name=>'TYPE', 
                     -value=>['GO','TOO','GTO','CAL','DDT','CAL_ER', 'ARCHIVE', 'CDFS'],
		 	         -default=>"$type",-override=>10000);
	
	print '</td></tr></table>';
	
	print '<table style="border-width:0px">';
	print '<tr>';
	print '<th>PI Name:';
	print "</th><td>$PI_name</td>";
	print '<th>Observer:';
	print "</th><td> $Observer</td></tr>";

	print '<tr><th>Exposure Time:</TH>';
    print "<input type='hidden' name='APPROVED_EXPOSURE_TIME' value='$approved_exposure_time'>";
    print '<td style="text-align:left">';
    print "$approved_exposure_time".' ks</td>';

	print '<th>Remaining Exposure Time:</TH>';
	print "<td>$rem_exp_time ks</td>";
	print '</tr></table>';
	
	print '<table style="border-width:0px">';

	print '<tr><th>Joint Proposal:</th>';
	print "<td>$proposal_joint</td><td>&#160;</td><td>&#160;</td><td>&#160;</td></tr>";

	print "<tr><td>&#160;</td><th>HST Approved Time:</th><td>$proposal_hst</td>";
	print "<th>NOAO Approved Time:</th><td>$proposal_noao</td>";
	print '</tr>';
	print "<tr><td>&#160;</td><th>XMM Approved Time:</th><td>$proposal_xmm</td>";
	print "<th>RXTE Approved Time:</th><td>$rxte_approved_time</td>";
	print '</tr>';
	print "<tr><td>&#160;</td><th>VLA Approved Time:</th><td>$vla_approved_time</td>";
	print "<th>VLBA Approved Time:</th><td>$vlba_approved_time</td>";
	print '</tr>';
	print '</table>';
	
	print '<table style="border-width:0px">';
	print '<tr>';
	print '<th>Schedule Date:</TH>';
	print "<td>$soe_st_sched_date</td>";
	print '<th>LTS Date:';
	print "</TH><td>$lts_lt_plan</td>";
	print '</tr></table>';

#----------------------------------------
#-------- Convert $ra from decimal to hms
#----------------------------------------

	$ra = $dra;
   	$hh = int($ra/15);
   	$mm = 60 * ($ra / 15 - $hh);
   	$ss = 60 * ($mm - int($mm));

   	$tra = sprintf("%02d:%02d:%06.4f", $hh, $mm, $ss);

#-----------------------------------------
#-------- Convert $dec from decimal to dms
#-----------------------------------------

	@dtemp = split(/:/, $dec);
	$dec = $ddec;
   	if ($dec < 0) { 			                    #--- set sign
       	$sign = "-";
     	$dec *= -1;
   	} else {
        $sign = "+";
    }
	
   	$dd = int($dec);
   	$mm = 60 * ($dec - $dd);
   	$ss = 60 * ($mm - int($mm));
   	$secrollover = sprintf("%02f", $ss);
   	if ($secrollover == 60) {
       	$ss = abs($ss - 60);
       	$mm = ($mm +1 );
   	}
   	if ($mm == 60) {
       	$mm = ($mm - 60);
     	$hh = ($dd + 1);
   	}
  	$tdec = sprintf("%.1s%02d:%02d:%06.4f", $sign, $dd, $mm, $ss);

	print '<p style="padding-bottom:10px">You may enter RA and Dec in ';
    print 'either HMS/DMS format (separated by colons, e.g. ';
	print '16:22:04.8  -27:43:04.0), or as decimal degrees.  The original OBSCAT decimal ';
	print ' degree values are provided below the update boxes. ';

    $view_http = "$$usint_http/PSPC_page/plot_pspc.cgi?"."$obsid";
	print 'If you like to see the current viewing orientation, open: ';

	$test = `ls /data/targets/'."$seq_nbr".'/*.gif`;
	if($test =~ /soe/){
        $rass  = 'https://cxc.harvard.edu/targets/'."$seq_nbr/$seq_nbr.$obsid".'.soe.rass.gif';
        $rosat = 'https://cxc.harvard.edu/targets/'."$seq_nbr/$seq_nbr.$obsid".'.soe.pspc.gif';
        $dss   = 'https://cxc.harvard.edu/targets/'."$seq_nbr/$seq_nbr.$obsid".'.soe.dss.gif';
	}else{
        $rass  = 'https://cxc.harvard.edu/targets/'."$seq_nbr/$seq_nbr.$obsid".'.rass.gif';
        $rosat = 'https://cxc.harvard.edu/targets/'."$seq_nbr/$seq_nbr.$obsid".'.pspc.gif';
        $dss   = 'https://cxc.harvard.edu/targets/'."$seq_nbr/$seq_nbr.$obsid".'.dss.gif';
	}

    print '<a href="javascript:ImageOpener(\''."$dss".'\')">DSS</a>, ';
    print '<a href="javascript:ImageOpener(\''."$rosat".'\')">ROSAT</a>, or  ';
    print '<a href="javascript:ImageOpener(\''."$rass".'\')">RASS</a>. ';

	print "(Note: These figures do not always exist.)</p>";

	print '<table style="border-width:0px">';
	print '<tr><td>&#160;</td>';
	print '<th>RA (HMS):</th>';
	print '<td style="text-align:left"><input type="text" name="RA"  value="',"$tra",'"  size="14"></td>';
	print '<th>Dec (DMS):</th>';
	print '<td style="text-align:left"><input type="text" name="DEC" value="',"$tdec",'" size="14"></td>';
#
#---- planned roll updated to give range.
#
    if($scheduled_roll eq '' && $scheduled_range eq ""){
        print '<th>Planned Roll:</th><td>NA</td>';

	}elsif($scheduled_roll <= $scheduled_range){
	    print '<th>Planned Roll:</th><td>',"$scheduled_roll",' -- ', "$scheduled_range",'</td>';

    }else{
	    print '<th>Planned Roll:</th><td>',"$scheduled_range",' -- ', "$scheduled_roll",'</td>';
    }

	print '</tr>';

	print '<tr><td>&#160;</td>';
	print '<th>RA:</TH><td>',"$dra",'</td>';
	print '<th>Dec:</TH><td>',"$ddec",'</td>';

	if($status =~ /^OBSERVED/i || $status =~ /ARCHIVED/i){
        #
        #--- do nothing
        #
	}else{
		$roll_obsr ='';
	}

    print '<th>Roll Observed:</th>';
    print '<td style="text-align:left">',"$roll_obsr";
	print "<input type=\"hidden\" name=\"ROLL_OBSR\" value=\"$roll_obsr\">";
	print '</td>';
	print '</tr></table>';

	print '<table style="border-width:0px">';
	print '<tr>';

	print '<th>Offset: Y:</th>';

	print '<td style="text-align:left"><input type="text" name="Y_DET_OFFSET" value="';
	print "$y_det_offset";
	print '" size="12"> arcmin</td><td></td>';

	print '<th>Z:</th>';

	print '<td style="text-align:left"><input type="text" name="Z_DET_OFFSET" value="';
	print "$z_det_offset";
	print '" size="12"> arcmin</td>';
	print '</tr><tr>';

	print '<th>Z-Sim:</th>';
	print '<td style="text-align:left"><input type="text" name="TRANS_OFFSET" value="';
	print "$trans_offset";
	print '" size="12"> mm<td>';

	print '<th>Sim-Focus:</th>';
	print '<td style="text-align:left"><input type="text" name="FOCUS_OFFSET" value="';
	print "$focus_offset";
	print '" size="12"> mm</td>';

	print '<tr>';

	print '<th>Focus:</th>';
	print '<td style="text-align:left"><input type="text" name="DEFOCUS" ';
    print 'value="',"$defocus", '" size="12"></td>';
	print '<td></td>';

	print '<th>Raster Scan:</th>';
	print "<td style='text-align:left'>$raster_scan</td>";
	print '</tr></table>';

	print '<table style="border-width:0px">';

	print '<tr><th>Uninterrupted Obs:</th><td>';
	print popup_menu(-name=>'UNINTERRUPT', 
                     -value=>['NULL','NO','PREFERENCE','YES'], 
			 	     -default=>"$duninterrupt",-override=>1000);

    print '</td><td>&#160;</td>';
    print '<th>Extended SRC:</th><td>';
    print popup_menu(-name=>'EXTENDED_SRC', 
                     -value=>['NO','YES'],
                     -default=>"$dextended_src",-override=>1000);
    print '</td></tr>';


	print '<tr><th>Solar System Object:</th><td>';
	print popup_menu(-name=>'OBJ_FLAG',
                     -value=>['NO','MT','SS'],
                     -default=>"$obj_flag", -override=>10000);

	print '</td><td>&#160;';
	print '</td><th>Object:</th><td>';
	print popup_menu(-name=>'OBJECT', 
	 		         -value=>['NONE','NEW','COMET','EARTH','JUPITER','MARS','MOON','NEPTUNE',
	      		              'PLUTO','SATURN','URANUS','VENUS'],
	 		         -default=>"$object", -override=>10000);
	print '</tr><tr>';
	
	print '<th>Photometry:</th><td>';
	print popup_menu(-name=>'PHOTOMETRY_FLAG', 
                     -value=>['NULL','YES','NO'], 
			         -default=>"$dphotometry_flag", -override=>100000);
	print '</td>';

	print '<td>&#160;</td>';
	print '<th>V Mag:';
	print "</th><td style='text-align:left'><input type=\"text\" name=\"VMAGNITUDE\" ";
    print "value=\"$vmagnitude\" size=\"12\"></td>";

	print '</tr><tr>';
	print '<th>Count Rate:</th>';
	print '<td style="text-align:left"><input type="text" name="EST_CNT_RATE"';
	print " value=\"$est_cnt_rate\" size=\"12\"></td>";
	print '<td>&#160;</td>';

	print '<th>1st Order Rate:';
	print '</th><td style="text-align:left"><input type="text" name="FORDER_CNT_RATE"';
	print " value=\"$forder_cnt_rate\" size=\"12\"></td>";
	print '</tr></table>';

	print '<hr />';

	print '<h2>Dither';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#dither_flag\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

	print '<table  style="border-width:0px">';
	print '<tr><th>Dither:</th><td>';
	print popup_menu(-name=>'DITHER_FLAG', 
                     -value=>['NULL','YES','NO'], 
		 	         -default=>"$ddither_flag", -override=>100000);

	print '</td><td>&#160;</td><td>&#160;</td><td>&#160;</td><td>&#160;</td><td>&#160;</td></tr>';

	print '<tr><td>&#160;</td><th>y_amp (in arcsec):</th>';
	print '<td style="text-align:left"><input type="text" name="Y_AMP_ASEC" ';
    print 'value="',"$y_amp_asec",'" size="8"></td>';

	print '<th>y_freq (in arcsec/sec):</th>';
	print '<td style="text-align:left"><input type="text" name="Y_FREQ_ASEC" ';
    print 'value="',"$y_freq_asec",'" size="8"></td>';

	print '<th>y_phase:</th>';
	print '<td style="text-align:left"><input type="text" name="Y_PHASE" ';
    print 'value="',"$y_phase",'" size="8"></td>';
	print '</tr>';

    print '<tr><td>&#160;</td><th>y_amp (in degrees):</th>';
    print '<td style="text-align:left">',"$y_amp",'</td>';

    print '<th>y_freq(in degree/sec)</th>';
    print '<td style="text-align:left">',"$y_freq",'</td>';

    print '<th>&#160;</th>';
    print '<td style="text-align:left">&#160;</td>';
    print '</tr>';

	print '<tr><td>&#160;</td><th>z_amp (in arcsec):</th>';
	print '<td style="text-align:left"><input type="text" name="Z_AMP_ASEC" ';
    print 'value="',"$z_amp_asec",'" size="8"></td>';

	print '<th>z_freq (in arcsec/sec):</th>';
	print '<td style="text-align:left"><input type="text" name="Z_FREQ_ASEC" ';
    print ' value="',"$z_freq_asec",'" size="8"></td>';

	print '<th>z_phase:</th>';
	print '<td style="text-align:left"><input type="text" name="Z_PHASE" ';
    print 'value="',"$z_phase",'" size="8"></td>';
	print '</tr>';

    print '<tr><td>&#160;</td><th>z_amp (in degrees):</th>';
    print '<td style="text-align:left">',"$z_amp",'</td>';
 
    print '<th>z_freq(in degree/sec)</th>';
    print '<td style="text-align:left">',"$z_freq",'</td>';
 
    print '<th>&#160;&#160;</th>';
    print '<td>&#160;</td>';
    print '</tr>';

	print '</table>';
	print '<hr />';

#-------------------------------------
#----- time constraint case start here
#-------------------------------------

	print '<h2>Time Constraints';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#time_constraints\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

    print '<p><span style="color:red;">New</span>: "';
    print '<a href="javascript:WindowOpener(\'./ranked_entries.html\')">';
    print 'How To Change The Same Parameter Values In Multiple ObsIDs: Ranked Entries for Constraints';
    print '</a></p>';

	print "<input type=\"hidden\" name=\"TIME_ORDR\" value=\"$time_ordr\">";

	if($dwindow_flag =~ /NO/i || $dwindow_flag =~ /NULL/i){
		print "<h3 style='padding-bottom:40px'>There Is No Time Constraints. Do You Need To Add? ";
		print popup_menu(-name=>"WINDOW_FLAG", 
                         -value=>['NO', 'YES'], 
                         -default=>"$dwindow_flag", -override=>100000);
		print '<input type="submit" name="Check" value="Update">';
		print '</h3>';

		print "<input type=\"hidden\" name=\"WINDOW_CONSTRAINT1\" value=\"$dwindow_constraint[1]\">";
		print "<input type=\"hidden\" name=\"START_MONTH1\" value=\"$start_month[1]\">";
		print "<input type=\"hidden\" name=\"START_DATE1\"  value=\"$start_date[1]\">";
		print "<input type=\"hidden\" name=\"START_YEAR1\"  value=\"$start_year[1]\">";
		print "<input type=\"hidden\" name=\"START_TIME1\"  value=\"$start_time[1]\">";

		print "<input type=\"hidden\" name=\"END_MONTH1\"   value=\"$end_month[1]\">";
		print "<input type=\"hidden\" name=\"END_DATE1\"    value=\"$end_date[1]\">";
		print "<input type=\"hidden\" name=\"END_YEAR1\"    value=\"$end_year[1]\">";
		print "<input type=\"hidden\" name=\"END_TIME1\"    value=\"$end_time[1]\">";

		print "<input type=\"hidden\" name=\"TIME_ORDR_ADD\" value=\"1\">";

	}else{
		print "<input type=\"hidden\" name=\"WINDOW_FLAG\"   value=\"$dwindow_flag\">";
		print "<input type=\"hidden\" name=\"TIME_ORDR_ADD\" value=\"$time_ordr_add\">";

		if($time_ordr_add == 0 || $window_flag =~ /Y/i){
			print '<p style="padding-bottom:20px">';
			print 'If you want to add ranks, press "Add Time Rank." ';
            print 'If you want to remove null entries, press "Remove Null Time Entry."';
			print '</p>';
			print '<strong>Rank</strong>: ';
			print '<spacer type=horizontal size=30>';
	
			print '<spacer type=horizontal size=50>';
			print submit(-name=>'Check',-value=>'     Add Time Rank     ')	;
			print submit(-name=>'Check',-value=>'Remove Null Time Entry ')	;
		}

		print '<table style="border-width:0px">';
		print '<tr><th>Rank</th>
			<th>Window Constraint<th>
			<th>Month</th><th>Date</th><th>Year</th><th>Time (24hr system)</th></tr>';

        $chk = find_rank(@t_const);
        if($chk > 0){
            $window_flag  = 'Y';
            $dwindow_flag = 'YES';
        }
	
		for($k = 1; $k <= $time_ordr; $k++){
			if($start_month[$k] =~/\d/){
				if($start_month[$k]    == 1) {$wstart_month = 'Jan'}
				elsif($start_month[$k] == 2) {$wstart_month = 'Feb'}
				elsif($start_month[$k] == 3) {$wstart_month = 'Mar'}
				elsif($start_month[$k] == 4) {$wstart_month = 'Apr'}
				elsif($start_month[$k] == 5) {$wstart_month = 'May'}
				elsif($start_month[$k] == 6) {$wstart_month = 'Jun'}
				elsif($start_month[$k] == 7) {$wstart_month = 'Jul'}
				elsif($start_month[$k] == 8) {$wstart_month = 'Aug'}
				elsif($start_month[$k] == 9) {$wstart_month = 'Sep'}
				elsif($start_month[$k] == 10){$wstart_month = 'Oct'}
				elsif($start_month[$k] == 11){$wstart_month = 'Nov'}
				elsif($start_month[$k] == 12){$wstart_month = 'Dec'}
				else{$wstart_month = 'NULL'}
				$start_month[$k]   = $wstart_month;
			}
		
			if($end_month[$k] =~ /\d/){
				if($end_month[$k]    == 1) {$wend_month = 'Jan'}
				elsif($end_month[$k] == 2) {$wend_month = 'Feb'}
				elsif($end_month[$k] == 3) {$wend_month = 'Mar'}
				elsif($end_month[$k] == 4) {$wend_month = 'Apr'}
				elsif($end_month[$k] == 5) {$wend_month = 'May'}
				elsif($end_month[$k] == 6) {$wend_month = 'Jun'}
				elsif($end_month[$k] == 7) {$wend_month = 'Jul'}
				elsif($end_month[$k] == 8) {$wend_month = 'Aug'}
				elsif($end_month[$k] == 9) {$wend_month = 'Sep'}
				elsif($end_month[$k] == 10){$wend_month = 'Oct'}
				elsif($end_month[$k] == 11){$wend_month = 'Nov'}
				elsif($end_month[$k] == 12){$wend_month = 'Dec'}
				else{$wend_month = 'NULL'}
				$end_month[$k]   = $wend_month;
			}
	
			print '<tr><td style="text-align:center"><strong>';
			print "$k";
			print '</strong></td><td>';
	
			$twindow_constraint = 'WINDOW_CONSTRAINT'."$k";
	
			if($sp_user eq'yes' || $dwindow_constraint[$k] =~ /CONSTRAINT/i){
				print popup_menu(-name=>"$twindow_constraint", 
                                 -value=>['CONSTRAINT','PREFERENCE', 'NULL'],
			 		             -default=>"$dwindow_constraint[$k]", -override=>100000);
			}else{
				print popup_menu(-name=>"$twindow_constraint", 
                                 -value=>['PREFERENCE'],
			 		             -default=>"$dwindow_constraint[$k]", -override=>100000);
			}
			print '</td><th>Start</th><td>';
	
			$tstart_month = 'START_MONTH'."$k";
	
			print popup_menu(-name=>"$tstart_month",
        				     -value=>['NULL','Jan', 'Feb', 'Mar','Apr','May','Jun',
                                             'Jul', 'Aug', 'Sep','Oct','Nov','Dec'],
        				     -default=>"$start_month[$k]",-override=>100000);
			print '</td><td>';
			
			$tstart_date = 'START_DATE'."$k";
	
			print popup_menu(-name=>"$tstart_date",
        				     -value=>['NULL','01','02','03','04','05','06','07','08','09','10',
                				     '11','12','13','14','15','16','17','18','19','20',
                				     '21','22','23','24','25','26','27','28','29','30', '31'],
        				     -default=>"$start_date[$k]", -override=>10000);
			print '</td><td>';
	
			$tstart_year = 'START_YEAR'."$k";
#
#--- create a year list starting the last year
#
            @y_list = create_year_list($start_year[$k]);

			print popup_menu(-name=>"$tstart_year",
        				     -value=>[@y_list],
        				     -default=>"$start_year[$k]",-override=>1000000);
			print '</td><td>';

			$tstart_time = 'START_TIME'."$k";
	
			print textfield(-name=>"$tstart_time", 
                            -size=>'8', 
                            -default =>"$start_time[$k]", ,-override=>1000000);
	
			print '</td></tr><tr><td>&#160;</td><td>&#160;</td>';
	
			print '</td><th>End</th><td>';
	
			$tend_month = 'END_MONTH'."$k";
	
			print popup_menu(-name=>"$tend_month",
        				     -value=>['NULL','Jan', 'Feb', 'Mar','Apr','May','Jun',
                                             'Jul', 'Aug','Sep','Oct','Nov','Dec'],
        				     -default=>"$end_month[$k]",-override=>10000);
			print '</td><td>';
	
			$tend_date = 'END_DATE'."$k";
	
			print popup_menu(-name=>"$tend_date",
        				     -value=>['NULL','01','02','03','04','05','06','07','08','09','10',
                			     	 '11','12','13','14','15','16','17','18','19','20',
                				     '21','22','23','24','25','26','27','28','29','30', '31'],
        				     -default=>"$end_date[$k]",-override=>1000000);
			print '</td><td>';
	
			$tend_year = 'END_YEAR'."$k";
	
			print popup_menu(-name=>"$tend_year",
        				     -value=>[@y_list],
        				     -default=>"$end_year[$k]", -override=>100000);
			print '</td><td>';
	
			$tend_time = 'END_TIME'."$k";
	
			print textfield(-name=>"$tend_time", -size=>'8', 
                            -default =>"$end_time[$k]",-override=>1000000);
			print '</td></tr>';
		}
		print '</table>';
	}	
	print '<hr />';

#-------------------------------------
#---- Roll Constraint Case starts here
#-------------------------------------

    print '<h2>Roll Constraints';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#roll_constraints\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print ' </h2>';

    print '<p><span style="color:red;">New</span>: "';
    print '<a href="javascript:WindowOpener(\'./ranked_entries.html\')">';
    print 'How To Change The Same Parameter Values In Multiple ObsIDs: Ranked Entries for Constraints';
    print '</a></p>';

	
    $target_http = "$mp_http/targets/"."$seq_nbr".'/'."$seq_nbr".'.rollvis.gif';
	
	print "<input type=\"hidden\" name=\"ROLL_ORDR\" value=\"$roll_ordr\">";

	if($droll_flag =~ /NO/i || $droll_flag =~ /NULL/i){
		print '<h3 style="padding-bottom:40px">There Is No Roll Constraint. Do You Need To Add? ';
		print popup_menu(-name=>"ROLL_FLAG", 
                         -value=>['NO', 'YES'], 
                         -default=>"$droll_flag", -override=>100000);

		print '<input type="submit" name="Check" value="Update">';
		print '</h3>';

		print "<input type=\"hidden\" name=\"ROLL_CONSTRAINT1\" value=\"$droll_constraint[1]\">";
		print "<input type=\"hidden\" name=\"ROLL_1801\"        value=\"$droll_180[1]\">";
		print "<input type=\"hidden\" name=\"ROLL1\"            value=\"$droll[1]\">";
		print "<input type=\"hidden\" name=\"ROLL_TOLERANCE1\"  value=\"$droll_tolerance[1]\">";

		print "<input type=\"hidden\" name=\"ROLL_ORDR_ADD\"    value=\"1\">";
	}else{
		print "<input type=\"hidden\" name=\"ROLL_ORDR_ADD\"    value=\"$roll_ordr_add\">";
		print "<input type=\"hidden\" name=\"ROLL_FLAG\"        value=\"$droll_flag\">";

		if($roll_ordr_add == 0 || $roll_flag =~ /Y/i){
			print '<p style="padding-bottom:20px">If you want to add a rank, press "Add Roll Rank". ';
			print 'If you want to remove null entries, press "Remove Null Roll Entry."';
			print '</p>';

			print '<strong>Rank</strong>: ';
			print '<spacer type=horizontal size=30>';
	
			print '<spacer type=horizontal size=50>';
#
#--- from ao cycle 22, only constraint choice is available and only one rank is allowed
#
            if($obs_ao_str < 22){
			    print submit(-name=>'Check',-value=>'     Add Roll Rank     ') ;
            }
			print submit(-name=>'Check',-value=>'Remove Null Roll Entry ') ;
		}

		print '<table style="border-width:0px">';
		print '<tr><th>Rank</th>
			<th>Type of Constraint</th>
			<th>Roll180?</th>
			<th>Roll</th>
			<th>Roll Tolerance</th></tr>';
	
		for($k = 1; $k <= $roll_ordr; $k++){
			print '<tr><td align=center><strong>';
			print "$k";	
			print '</strong></td><td>';
			$troll_constraint = 'ROLL_CONSTRAINT'."$k";
			if($sp_user eq 'yes' || $droll_constraint[$k] =~ /YES/i){
#
#--- ao cycle 22 division
#
                if($obs_ao_str < 22){
				    print popup_menu(-name=>"$troll_constraint", 
                                    -value=>['CONSTRAINT','PREFERENCE', 'NULL'],
			  			            -default=>"$droll_constraint[$k]",  -override=>100000);
                }else{
				    print popup_menu(-name=>"$troll_constraint", 
                                    -value=>['CONSTRAINT', 'NULL'],
			  			            -default=>"$droll_constraint[$k]",  -override=>100000);
                }
			}else{
				print popup_menu(-name=>"$troll_constraint", 
                                 -value=>['PREFERENCE', 'NULL'],
						         -default=>"$droll_constraint[$k]",  -override=>100000);
			}
	
			print '</td><td>';
			$troll_180 = 'ROLL_180'."$k";
			print popup_menu(-name=>"$troll_180", 
                             -value=>['NULL','YES','NO'],
                             -default=>"$droll_180[$k]",-override=>100000);
			print '</td><td>';
			$troll = 'ROLL'."$k";
			print textfield(-name=>"$troll", 
                            -value=>"$roll[$k]", 
                            -size=>'10', -override=>100000);
			print '</td><td>';
			$troll_tolerance = 'ROLL_TOLERANCE'."$k";
			print textfield(-name=>"$troll_tolerance", 
                            -value=>"$roll_tolerance[$k]", 
                            -size=>'10', -override=>100000);
			print '</td></tr>';
		}
		print '</table>';
	}

#----------------------------------------
#----- Other Constraint Case starts here
#----------------------------------------

	print '<hr />';
	print '<h2>Other Constraints'; 
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#other_constraints\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

	print '<table style="border-width:0px">';
	print '<tr>';
	
	print '<th>Constraints in Remarks?:</th><td>';
	print popup_menu(-name=>'CONSTR_IN_REMARKS', 
                     -value=>['YES','PREFERENCE','NO'],
		             -default=>"$dconstr_in_remarks", -override=>100000);
	print ' </td></tr>';
	print '</table>';
#
#--- New 02-04-21
#
    print '<table style="border-width:0px">';
    print '<tr>';
	print '<th>Pointing Update:</th><td>';
	print popup_menu(-name=>'POINTING_CONSTRAINT', 
                     -value=>['NO','YES', 'NULL'],
	 		         -default=>"$dpointing_constraint",-override=>1000000);
#### REMOVE AFTER 04-30-21   #####################
#	print "<span style='color:red;font-size:90%;'>(New Field! ";
#    print "<a href='https://cxc.harvard.edu/mta/CUS/Usint/user_help.html#pointing_constraint'>";
#    print "Description</a>)</span></td>";
##################################################
    print '</tr>';
    print '</table>';

	print '<table style="border-width:0px">';
	print '<tr>';
	print '<th>Phase Constraint:</th>
	<td style="text-align:left">';
	
	print " $dphase_constraint_flag";
    print "<input type=\"hidden\" name=\"PHASE_CONSTRAINT_FLAG\" value=\"$dphase_constraint_flag\">";

	print '</td></tr></table>';

	if($dphase_constraint_flag =~ /NONE/ || $dphase_constraint_flag =~ /NULL/){
			#
			#--- do nothing
			#
	}else{
		print '<table style="border-width:0px">';
		print '<tr><td>&#160;</td>';
		print '<th>Phase Epoch:</th>';
		print '<td style="text-align:left"><input type="text" name="PHASE_EPOCH" value=';
		print "\"$phase_epoch\"",' size="12"></td>';
		print '<th>Phase Period:</th>';
		print '<td style="text-align:left"><input type="text" name="PHASE_PERIOD" value=';
		print "\"$phase_period\"", ' size="12"></td>';
		print '<td>&#160;</td><td>&#160;</td></tr>';
		
		print '<tr><td>&#160;</td>';
		print '<th>Phase Start:</th>';
		print '<td style="text-align:left"><input type="text" name="PHASE_START" value=';
		print "\"$phase_start\"",' size="12"></td>';
		print '<th>Phase Start Margin:</th>';
		print '<td style="text-align:left"><input type="text" name="PHASE_START_MARGIN" value=';
		print "\"$phase_start_margin\"",' size="12"></td>';
		print '</tr><tr>';
		print '<td>&#160;</td>';
		print '<th>Phase End:</th>';
		print '<td style="text-align:left"><input type="text" name="PHASE_END" value=';
		print "\"$phase_end\"",' size="12"></td>';
		print '<th>Phase End Margin:</th>';
		print '<td style="text-align:left"><input type="text" name="PHASE_END_MARGIN" value=';
		print "\"$phase_end_margin\"",' size="12"></td>';
		print '</tr></table>';
	}

   if($monitor_flag =~ /Y/i){
       	%seen = ();
       	@uniq = ();
       	foreach $monitor_elem (@monitor_series) {
            $schk = 0;
            OUTER3:
            foreach $echk (@schdulable_list){
                if($monitor_elem =~ /$echk/){
	                $schk++;
	                last OUTER3;
                }
            }

            if($schk > 0){
                if($usint_on =~ /test/){
                    $line = "<a href=\"$test_http/ocatdata2html.cgi\?";
                    $line = "$line"."$monitor_elem.$pass.$submitter\">$monitor_elem<\/a> ";
              	    push(@uniq, $line) unless $seen{$monitor_elem}++;
                }else{
                    $line = "<a href=\"$usint_http/ocatdata2html.cgi\?";
                    $line = "$line"."$monitor_elem.$pass.$submitter\">$monitor_elem<\/a> ";
              	    push(@uniq, $line) unless $seen{$monitor_elem}++;
                }
            }
        }
        @monitor_series_list  = sort @uniq;
    }

	print '<table style="border-width:0px">';
	print '<tr>';

	print '<th>Group ID:</th>';
	print '<td>';

	if($group_id){
		print "$group_id";
		print "<input type='hidden' name='GROUP_ID' value=\"$group_id\">";
	}else{
		print '  No Group ID  ';
	}
	print '</td>';

	print '<th>Monitoring Observation:  </th>';
	print '<td>';

	if($sp_user eq 'yes' && ($dmonitor_flag =~ /Y/i || $dmonitor_flag == '') 
			     && ($group_id =~ /\s+/ || $group_id eq '')){
		print popup_menu(-name=>'MONITOR_FLAG', 
                         -values=>['NO','YES','NULL'],
               	         -default=>"$dmonitor_flag",-override=>10000);

	}elsif($sp_user eq 'yes' && $dmonitor_flag =~ /Y/i && $group_id =~ /\w/ ){
		print popup_menu(-name=>'MONITOR_FLAG', 
                         -values=>['NO','YES','NULL'],
               	         -default=>"$dmonitor_flag",-override=>10000);
	}
	print '</td>';

	print '<td>';
	print '</td></tr></table>';

	if($group_id){
		print "<br />Observations in the Group: @group<br />";
	}elsif($monitor_flag =~ /Y/i){
		print "<br /> Remaining Observations in the Monitoring: @monitor_series_list<br />";
	}else{
		print "<br />";
	}

	if($group_id =~ /No Group ID/ || $group_id !~ /\d/){
		print '<table style="border-width:0px">';

		print '<tr><th>Follows ObsID#:</th>';
		print '<td style="text-align:left"><input type="text" name="PRE_ID" ';
        print 'value="',"$pre_id",'" size="8"></td>';
		
		print '<th>Min Int<br />(pre_min_lead):</th>';
		print '<td style="text-align:left"><input type="text" name="PRE_MIN_LEAD" ';
        print 'value="',"$pre_min_lead",'" size="8"></td>';
	
		print '<th>Max Int<br />(pre_max_lead):</th>';
		print '<td style="text-align:left"><input type="text" name="PRE_MAX_LEAD" ';
        print 'value="',"$pre_max_lead",'" size="8"></td>';
		print '</tr></table>';
	}else{
      	print '<table style="border-width:0px">';

       	print '<tr><th>Follows ObsID#:</th>';
       	print '<td style="text-align:left">',"$pre_id",'</td>';
	
       	print '<th>Min Int<br />(pre_min_lead):</th>';
       	print '<td style="text-align:left">',"$pre_min_lead",'</td>';
	
       	print '<th>Max Int<br />(pre_max_lead):</th>';
       	print '<td style="text-align:left">',"$pre_max_lead",'</td>';
       	print '</tr></table>';

		print "<input type=\"hidden\" name=\"PRE_ID\"       value=\"$pre_id\"\>";
		print "<input type=\"hidden\" name=\"PRE_MIN_LEAD\" value=\"$pre_min_lead\"\>";
		print "<input type=\"hidden\" name=\"PRE_MAX_LEAD\" value=\"$pre_max_lead\"\>";
	}

	print '<table style="border-width:0px">';
	print '<tr>';
	print '<th>Coordinated Observation:</th><td>';
	print popup_menu(-name=>'MULTITELESCOPE', 
                     -value=>['NO','YES','PREFERENCE'],
	 		         -default=>"$dmultitelescope",-override=>1000000);
	print '</td>';
	#print '<td>&#160;</td>';
	print '<th>Observatories:</th>';
	print '<td style="text-align:left"><input type="text" name="OBSERVATORIES" value=';
	print "\"$observatories\"",' size="12"></td>';
    print '</tr>';

    print '<tr>';
	print '<th>Max Coordination Offset:</th>';
	print '<td style="text-align:left"><input type="text" name="MULTITELESCOPE_INTERVAL" value=';
	print "\"$multitelescope_interval\"",' size="12"></td>';
	print "</td><td>&#160;</td>";


	print '</tr> </table>';

	print '<hr />';

#--------------------
#----- HRC Parameters
#--------------------

	print '<h2>HRC Parameters';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#hrc_parameters\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

	print '<table style="border-width:0px">';
	print '<tr><td></td>';

	print '<th>HRC Timing Mode:</th><td>';
	print popup_menu(-name=>'HRC_TIMING_MODE', 
                     -value=>['NO','YES'], 
		 	         -default=>"$dhrc_timing_mode", -override=>100000);
	print '</td>';
	
	print '<th>Zero Block:</th><td>';
	print popup_menu(-name=>'HRC_ZERO_BLOCK', 
                     -value=>['NO','YES'], 
		 	         -default=>"$dhrc_zero_block", -override=>1000000);
	print '</td><td>';

	if($sp_user eq 'no'){
		print '<th>SI Mode:</th><td style="text-align:left">';
		print "$hrc_si_mode";
		print "<input type=\"hidden\" name=\"HRC_SI_MODE\" value=\"$hrc_si_mode\">";
		print '</td></tr>';
	}else{
		print '<th>SI Mode:</th>
			<td style="text-align:left"><input type="text" name="HRC_SI_MODE" value="';
		print "$hrc_si_mode";
		print '" size="8"></td></tr>';
	}

	print '</table>';
	
	print '<hr />';

#---------------------
#----- ACIS Parameters
#--------------------

	print '<h2>ACIS Parameters';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#acis_parameters\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

	print '<table style="border-width:0px">';
	print '<tr>';
	
	print '<th>ACIS Exposure Mode:</th><td>';
	
	print popup_menu(-name=>'EXP_MODE',     
                     -value=>['NULL','TE','CC'], 
                     -default=>"$exp_mode", -override=>100000);
	
	print '</td><th>Event TM Format:</th><td>';
	
	if($instrument =~ /ACIS/i){
		print popup_menu(-name=>'BEP_PACK', 
                         -value=>['F','VF','F+B','G'], 
		 		         -default=>"$bep_pack", -override=>100000);
	}else{
		print popup_menu(-name=>'BEP_PACK', 
                         -value=>['NULL','F','VF','F+B','G'], 
		 		         -default=>"$bep_pack", -override=>100000);
	}
	print '</td>';

	print '<th>Frame Time:</th>';

	print "<td style='text-align:left'>";
	print textfield(-name=>'FRAME_TIME', 
                    -value=>"$frame_time",
                    -size=>12, -override=>1000);
	print "</td></tr>";

	print '<tr>';
	print '<td>&#160;</td><td>&#160;</td><td>&#160;</td><td>&#160;</td>
		<th>Most Efficient:</th><td>';

	print popup_menu(-name=>'MOST_EFFICIENT', 
                     -value=>['NULL','YES','NO'],
		 	         -default=>"$dmost_efficient", -override=>10000);
	print '</td>';
	print '</tr></table>';
	
	print '<table style="border-width:0px">';
	print '<tr><td></td>';


	print '<th>FEP:</th><td>';
              print "$fep";
	print '</td><td></td><td></td>';
	print '<th>Dropped Chip Count:</th><td>';
	print "$dropped_chip_count";

	print '</td>';
	print '</tr></table>';

	print "<input type=\"hidden\" name=\"FEP\" value=\"$fep\">";
	print "<input type=\"hidden\" name=\"DROPPED_CHIP_COUNT\" value=\"$dropped_chip_count\">";

	print '<table style="border-width:0px">';
	print '<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>';
	

	print '<th>I0:</th>';
	
	print '<td>',popup_menu(-name=>'CCDI0_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccdi0_on",-override=>100000),'</td>';

	print '<th>I1:</th>';
	
	print '<td>',popup_menu(-name=>'CCDI1_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccdi1_on",-override=>1000000),'</td>';
	
	print '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>';
	print '<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td>';
	
	print '<th>I2:</th>';
	
	print '<td>',popup_menu(-name=>'CCDI2_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccdi2_on",-override=>100000),'</td>';

	print '<th>I3:</th>';
	
	print '<td>',popup_menu(-name=>'CCDI3_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccdi3_on",-override=>100000),'</td>';
	
	print '<td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>';
	
	print '<tr>';
	
	print '<th>S0:</th>';
	
	print '<td>',popup_menu(-name=>'CCDS0_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccds0_on",-override=>100000),'</td>';
	
	print '<th>S1:</th>';

	print '<td>',popup_menu(-name=>'CCDS1_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
					        -default=>"$dccds1_on",-override=>100000),'</td>';

	print '<th>S2:</th>';
	
	print '<td>',popup_menu(-name=>'CCDS2_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccds2_on",-override=>10000),'</td>';

	print '<th>S3:</th>';
	
	print '<td>',popup_menu(-name=>'CCDS3_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
                            -default=>"$dccds3_on",-override=>1000000),'</td>';

	print '<th>S4:</th>';
	
	print '<td>',popup_menu(-name=>'CCDS4_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
                            -default=>"$dccds4_on",-override=>100000),'</td>';

	print '<th>S5:</th>';
	
	print '<td>',popup_menu(-name=>'CCDS5_ON', 
                            -value=>['NULL','YES','OPT1','OPT2','OPT3','OPT4','OPT5','NO'],
						    -default=>"$dccds5_on",-override=>100000),'</td>';
	
	print '</tr></table><p>';
	
	print '<table style="border-width:0px">';
	print '<tr>';
	print '<Th>Use Subarray:</Th>';
	print '<td>';
	print popup_menu(-name=>'SUBARRAY', 
                     -value=>['NO', 'YES'],
		 	         -default=>"$dsubarray", -override=>100000);
	print '</td>';
	print '<td colspan=4><strong>Please fill the next two entries, if you select YES.</strong></td>';
	print '</tr>';

	print '<tr>';
	print '<th>Start:</th>';
	print '<td style="text-align:left"><input type="text" name="SUBARRAY_START_ROW" ';
    print 'value="',"$subarray_start_row",'" size="12"></td>';

	print '<th>Rows:</th>';
	print '<td style="text-align:left"><input type="text" name="SUBARRAY_ROW_COUNT" ';
    print 'value="',"$subarray_row_count",'" size="12"></td>';

	print "<td>&#160;</td><td>&#160;</td>";
	print '</tr>';

	print '<tr>';
	print '<th>Duty Cycle:</th>';
	print '<td>';
	print popup_menu(-name=>'DUTY_CYCLE', 
                     -value=>['NULL','YES','NO'], 
		 	         -default=>"$dduty_cycle", -override=>100000);
	print '</td>';
	print '<th colspan=4><strong>If you selected YES, please fill the next two entries</strong></th>';
	print '</tr>';

	print '<tr>';
	print '<th>Number:</th>';
	print '<td style="text-align:left"><input type="text" name="SECONDARY_EXP_COUNT" value=';
	print "\"$secondary_exp_count\"", ' size="12"></td>';

	print '<th>Tprimary:</th>';
	print '<td style="text-align:left"><input type="text" name="PRIMARY_EXP_TIME" value=';
	print "\"$primary_exp_time\"", ' size="12"></td>';
	print "<td>&#160;</td><td>&#160;</td>";
	print '</tr>';

	print ' <tr>';
	print '<th>Onchip Summing:</th><td>';
	print popup_menu(-name=>'ONCHIP_SUM', 
                     -value=>['NULL','YES','NO'], 
		 	         -default=>"$donchip_sum", -override=>100000);
	print '</td>';
	print '<th>Rows:</th>';
	print '<td style="text-align:left"><input type="text" name="ONCHIP_ROW_COUNT" value=';
	print "\"$onchip_row_count\"", ' size="12"></td>';

	print '<th>Columns:</th>';
	print '<td style="text-align:left"><input type="text" name="ONCHIP_COLUMN_COUNT" value=';
	print "\"$onchip_column_count\"", ' size="12"></td>';
	print '</tr>';

	print '<tr>';
	print '<th>Energy Filter:</th><td>';
	print popup_menu(-name=>'EVENTFILTER', 
                     -value=>['NULL','YES','NO'], 
		 	         -default=>"$deventfilter", -override=>100000);
	print '</td>';

	print '<th>Lowest Energy:</th>';
	print '<td style="text-align:left"><input type="text" name="EVENTFILTER_LOWER" value="';
	print "$eventfilter_lower";
	print '" size="12"></td>';

	print '<th>Energy Range:</th>';
	print '<td style="text-align:left"><input type="text" name="EVENTFILTER_HIGHER" value="';
	print "$eventfilter_higher";
	print '" size="12"></td>';
	if($deventfilter =~ /YES/i){
		$high_energy = $eventfilter_lower + $eventfilter_higher;
		print "<td><b> = Highest Energy:</b> $high_energy</td>";
	}
	print '</tr>';

	print '<tr> ';
	print '<th>Multiple Spectral Lines:</th>';
	print '<td style="text-align:left">';
	print popup_menu(-name=>'MULTIPLE_SPECTRAL_LINES', 
                     -value=>['NULL','NO','YES'], 
                     -default=>"$dmultiple_spectral_lines",-override=>10000);
	print '</td>';
	print '<th>Spectra Max Count:</th>';
	print '<td style="text-align:left"><input type="text" name="SPECTRA_MAX_COUNT" value="';
	print "$spectra_max_count";
	print '" size="12"></td>';
	print "<td>&#160;</td><td>&#160;</td>";
	print '</tr> ';

	print '</table>';

#------------------------------------------------
#-------- Acis Window Constraint Case starts here
#------------------------------------------------
#
#--- ACIS window Constraints: some values are linked to eventfilter_lower condition
#
	print '<hr />';
	print '<h2> ACIS Window Constraints';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#acis_window\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';

    print '<p><span style="color:red;">New</span>: "';
    print '<a href="javascript:WindowOpener(\'./ranked_entries.html\')">';
    print 'How To Change The Same Parameter Values In Multiple ObsIDs: Ranked Entries for Constraints';
    print '</a></p>';


    if($instrument =~ /ACIS/i){
	    print '<table style="border-width:0px"><tr><th>';
	    print 'Window Filter:';
	    print '</th><td>';
#
#---awc_l_th: acis window constraint lowest energy indicator: if 1 it is exceeded 0.5 keV
#
	    if($aciswin_no eq ''){
		    $aciswin_no = 0;
	    }
    
	    if($awc_cnt eq ''){
		    $awc_cnt = 1;
	    }
	    if($eventfilter_lower > 0.5 || $awc_l_th == 1){
		    $dspwindow = 'YES';
	    }

	    print popup_menu(-name=>'SPWINDOW', 
                        -value=>['NULL','YES','NO'],
                        -default=>"$dspwindow", -override=>10000);
	    print '<input type="submit" name="Check" value="Update">';
	    print '</td></tr></table>';
    }

	if($dspwindow =~ /YES/i){

		print '<br />';
		$wfill = 0;
#
#--- check which CCDs are ON
#
		@open_ccd = ();				                        #--- a list of ccd abled
		$ocnt     = 0;				                        #--- # of ccd abled
		for($m = 0; $m < 4; $m++){
			$name = 'ccdi'."$m".'_on';
			if(${$name} !~ /N/i && ${$name} !~ /NO/i && ${$name} !~ /NULL/){
				$name2 = 'I'."$m";
				push(@open_ccd, $name2);
				$ocnt++;
			}
		}
		for($m = 0; $m < 6; $m++){
			$name = 'ccds'."$m".'_on';
			if(${$name} !~ /N/i && ${$name} !~ /NO/i && ${$name} !~ /NULL/){
				$name2 = 'S'."$m";
				push(@open_ccd, $name2);
				$ocnt++;
			}
		}
#
#--- if lowest energy is > 0.5 keV check # of CCD abled
#
		OTUER:
		if($eventfilter_lower > 0.5 || $awc_l_th == 1){
			print '<p style="color:red"><strong>';
			if($eventfilter_lower > 0.5 && $awc_l_th == 0){
				print 'Energy Filter Lowest Energy is larger than 0.5 keV. ';

			}elsif($eventfilter_lower > 0.5 && $awc_l_th == 1){
				print 'Energy Filter Lowest Energy and ACIS Window Constraint ';
                print 'Lowest Energy are larger than 0.5 keV. ';

			}elsif($eventfilter_lower <= 0.5 && $awc_l_th == 1){
				print 'ACIS Window Constraint Lowest Energy is larger than 0.5 keV. ';
			}
			print 'Please check all Spatial Window parameters of each CCD.<br />';
			print 'If you want to remove all the window constraints, change Lowest Energy ';
			print 'to less than 0.5keV, and set Window Filter to No or Null, ';
			print 'then Submit the change using the "Submit" button at the bottom of the page.';
			print '</strong><br />';
			print "<a href=\"$usint_http/eventfilter_answer.html\" target='_blank'>Why did this happen?</a>";
			print '</p>';
#
#--- check how many ccds match with opened ccds
#
			@un_opened = ();
			OUTER:
			foreach $ent (@open_ccd){
				for($k = 0; $k < $aciswin_no; $k++){
					if($chip[$k] =~ /NULL/i){
						next OUTER;
					}
					if($ent =~ /$chip[$k]/i){
						next OUTER;
					}
				}
				push(@un_opened, $ent);
				$chip_chk++;
			}
		}

		print '<p>';
		print 'If you want to modify the number of ranks, change Window Filter above to "YES", ';
		print 'then change the rank entry below, and press "Add Window Rank"';
		print '</p>';
		print '<strong>Rank</strong>: ';
		print '<spacer type=horizontal size=30>';
	
		print '<spacer type=horizontal size=50>';
		print submit(-name=>'Check',-value=>'     Add Window Rank     ') ;
		
		print '<p style="padding-top:5px;padding-bottom:20px">';
        print 'If you are changing any of following entries, make sure ';
		print 'Window Filter above is set to "YES".<br />';
		print 'Otherwise, all changes are automatically nullified ';
		print 'when you submit the changes.';
		print "<br /><br />";
        print 'Note: By default: the sample rate is 0 and the window ';
        print 'specified is an <b>EXCLUSION</b> area. ';
        print 'To set as INCLUSION, set the sample rate to 1 in the desired ';
        print 'window and then  an exclusion window ';
        print 'for 1024 x 1024, with a sample value of 0.';
        print '<br /><br />';

		print '</p>';
	
		if($eventfilter_lower > 0.5 || $awc_l_th == 1){
			print '<p>If you change one or more CCD from YES to NO or ';
            print 'the other way around in ACIS Parameters section, ';
			print '<br />';
			print 'this action will affect the ranks below. After changing the CCD status, ';
            print 'please click "Submit" button at the bottom of the page, ';
			print '<br />';
			print ' and then come back to this page ';
			print 'using "PREVIOUS PAGE" button to make the effect to take place.';
			print '</p>';
		}

		$add_extra_line = 0;
		$reduced_ccd_no = 0;
		$org_aciswin_no = $aciswin_no;
#
#--- if eventfilter lower <= 0.5 keV and window filter is set to Null, 
#--- reduce all window constraints to Null state
#

		if($eventfilter_lower > 0.5 || $awc_l_th == 1){
			if($chip[$aciswin_no -1]=~ /N/i){
				$awc_cnt	    = 0;
				$aciswin_no     = $chip_chk;
				$org_aciswin_no = $aciswin_no;
			}else{
				$awc_cnt	    = $aciswin_no;
				$aciswin_no    += $chip_chk;
				$org_aciswin_no = $aciswin_no;
			}
#
#--- if eventfilter_lower > 0.5, lower_threshold must be at least equal to eventfilter_lower
#
			for($k = 0; $k < $aciswin_no; $k++){
				if($lower_threshold[$k] < $eventfilter_lower){
					$lower_threshold[$k] = $eventfilter_lower;
				}
			}

			for($k = 0; $k < $chip_chk; $k++){
				$j = $awc_cnt + $k;
				$aciswin_id[$j]      = $aciswin_id[$j-1] +1;
				$ordr[$j]	         = $j + 1;
				$chip[$j]	         = $un_opened[$k];
				$dinclude_flag[$j]   = 'INCLUDE';
				$start_row[$j]       = 1;
				$start_column[$j]    = 1;
				$height[$j]	         = 1024;
				$width[$j]	         = 1024;
				$lower_threshold[$j] = $eventfilter_lower;
				$pha_range[$j]       = $eventfilter_higher;
				$sample[$j]	         = 1;
				$awc_ind	         = 1;
			}
		}
#
#---- when whidow filter is changed from no to yes, add one empty acis window constraint line
#---- with one of opened CCD (fist in the line)
#
		if($aciswin_no !~ /\d/ || $aciswin_no == 0){
			$aciswin_no = 0;
			$ordr[0] = 1;
			$chip[0] = $open_ccd[0];
		}
#
#--- adding one extra entry (consequence of "Add New Window Entry" pressed)
#
		if($add_window_rank == 1 &&  $ordr[$aciswin_no -1] !~ /\d/){
			$ordr[$aciswin_no -1] = 1;
			$chip[$aciswin_no -1] = $open_ccd[0];
			$add_window_rank = 0;
		}

		print '<table style="border-width:0px">';
		print '<tr><th>Ordr</th>
		<th>Chip</th>
		<th>Start Row</th>
		<th>Start Column</th>
		<th>Height</th>
		<th>Width</th>
		<th>Lowest Energy</th>
		<th>Energy Range</th>
		<th>Sample Rate</th>
		<th>&#160;</th></tr>';

		if($aciswin_no == 0 || $aciswin_no =~ /\D/ ){
			$aciswin_no = 0;
		}
#
#---- if eventfilter_lower > 0.5, you need to keep all CCDs must have acis window constraints entires.
#---- check none of them are accidentally "removed" from the list. If so, put it back with warning.
#
		@chk_list  = ();
		@accd_list = ();
		@dccd_list = ();
		$cn        = 0;
		for($k = 0; $k < $aciswin_no; $k++){
			if($ordr[$k] !~ /\d/){
				push(@chk_list,  $k);
				push(@dccd_list, $chip[$k]);
				$cn++;
			}else{
				push(@accd_list, $chip[$k]);
			}
		}
		if($cn > 0){
			@tccd_list = ();
			@k_list    = ();
			$tn	= 0;
			TOUTER:
			for($k = 0; $k < $cn; $k++){
				foreach $comp (@accd_list){
					if($dccd_list[$k] =~ /$comp/){
						next TOUTER;
					}
				}
				push(@tccd_list, $dccd_list[$k]);
				push(@k_list,    $chk_list[$k]);
				$tn++;
			}

			if($tn > 0){
				for($k = 0; $k < $tn; $k++){
					foreach $comp (@open_ccd){
						if($tccd_list[$k] =~ /$comp/){
							$ordr[$k_list[$k]] = 999;
						}
					}
				}
			}
		}

		$chk_drop = 0;
		OUTER:
		for($k = 0; $k < $aciswin_no; $k++){
#
#---- if the ordr entry is blank, remove the line from the data.
#
			if($ordr[$k] == 999){
				print "<tr><td style='background-color:red'>";
			}else{
				print "<tr><td>";
			}

			if($ordr[$k] !~ /\d/){

				if($orig_ordr[$k] =~ /\d/ && $orig_chip[$k] !~ /N/){
#
#--- this is for the case the entry was there in database
#
					print "<input type=\"hidden\" name=\"$tordr\"            value=\" \">";
					print "<input type=\"hidden\" name=\"$tchip\"            value=\"NULL\">";
					print "<input type=\"hidden\" name=\"$tinclude_flag\"    value=\" \">";
					print "<input type=\"hidden\" name=\"$tstart_row\"       value=\" \">";
					print "<input type=\"hidden\" name=\"$tstart_column\"    value=\" \">";
					print "<input type=\"hidden\" name=\"$theight\"          value=\" \">";
					print "<input type=\"hidden\" name=\"$twidth\"           value=\" \">";
					print "<input type=\"hidden\" name=\"$tlower_threshold\" value=\" \">";
					print "<input type=\"hidden\" name=\"$tpha_range\"       value=\" \">";
					print "<input type=\"hidden\" name=\"$tsample\"          value=\" \">";
				}else{
#
#--- this is for the case the entry was not in database (removing an added row during this session)
#
					$chk_drop++;
				}
				next OUTER;
			}
#
#--- if a ccd which is not opened is accidentaly added, or during this session, 
#--- any of the open ccd is closed remove that ccd from the acis window constraint entries.
#
			$open_chk = 1;
			OUTER2:
			foreach $comp (@open_ccd){
				if($chip[$k] =~ /$comp/){
					$open_chk = 0;
					last OUTER2;
				}
			}

			if($open_chk == 1){
				if($orig_ordr[$k] =~ /\d/ && $orig_chip[$k] !~ /N/){
					print "<input type=\"hidden\" name=\"$tordr\"            value=\" \">";
					print "<input type=\"hidden\" name=\"$tchip\"            value=\"NULL\">";
					print "<input type=\"hidden\" name=\"$tinclude_flag\"    value=\" \">";
					print "<input type=\"hidden\" name=\"$tstart_row\"       value=\" \">";
					print "<input type=\"hidden\" name=\"$tstart_column\"    value=\" \">";
					print "<input type=\"hidden\" name=\"$theight\"          value=\" \">";
					print "<input type=\"hidden\" name=\"$twidth\"           value=\" \">";
					print "<input type=\"hidden\" name=\"$tlower_threshold\" value=\" \">";
					print "<input type=\"hidden\" name=\"$tpha_range\"       value=\" \">";
					print "<input type=\"hidden\" name=\"$tsample\"          value=\" \">";
				}else{
					$chk_drop++;
				}
				next OUTER;
			}
#
#--- readjusting the entry number (for the case any ccd is dropped from the list)
#
			$m = $k - $chk_drop;
			$taciswin_id      = 'ACISWIN_ID'."$m";
			$tordr	          = 'ORDR'."$m";
			$tchip	          = 'CHIP'."$m";
			$tinclude_flag    = 'INCLUDE_FLAG'."$m";
			$tstart_row       = 'START_ROW'."$m";
			$tstart_column    = 'START_COLUMN'."$m";
			$theight	      = 'HEIGHT'."$m";
			$twidth	          = 'WIDTH'."$m";
			$tlower_threshold = 'LOWER_THRESHOLD'."$m";
			$tpha_range       = 'PHA_RANGE'."$m";
			$tsample	      = 'SAMPLE'."$m";

			if($chip[$k] !~ /N/i){
				if($lower_threshold[$k] !~ /\d/){
					$lower_threshold[$k] = $eventfilter_lower;
				}
				if($pha_range[$k] !~ /\d/){
					$pha_range[$k] = $eventfilter_higher;
				}
			}

            if($orig_ordr[$k] =~ /D/ || $orig_ordr[$k] eq ''){
                    $orig_ordr[$k] = 0;
                    $ordr[$k] = $k +1;
            }
			print textfield(-name=>"$tordr", 
                            -value=>"$ordr[$k]", 
                            -override=>10000, -size=>'2');
			print " </td><td>";
			print popup_menu(-name=>"$tchip",
                             -value=>['NULL','I0','I1','I2','I3','S0','S1','S2','S3','S4','S5'],
					         -default=>"$chip[$k]", -override=>10000);
			print "</td><td>";

			print textfield(-name=>"$tstart_row", 
                            -value=>"$start_row[$k]",
                            -override=>10000, -size=>'8');
			print "</td><td>";
			print textfield(-name=>"$tstart_column", 
                            -value=>"$start_column[$k]", 
                            -override=>10000, -size=>'8');

			print "</td><td>";
			print textfield(-name=>"$theight", 
                            -value=>"$height[$k]",
                            -override=>10000,  -size=>'8');
			print "</td><td>";
			print textfield(-name=>"$twidth", 
                            -value=>"$width[$k]",
                            -override=>10000,  -size=>'8');
			print "</td><td>";
			print textfield(-name=>"$tlower_threshold", 
                            -value=>"$lower_threshold[$k]",
                            -override=>10000, -size=>'8');

			print "</td><td align=middle>";
			print textfield(-name=>"$tpha_range", 
                            -value=>"$pha_range[$k]",
                            -override=>10000, -size=>'8');
			print '</td><td>';
			print textfield(-name=>"$tsample", 
                            -value=>"$sample[$k]",
                            -override=>10000, -size=>'8');
			print "</td><td>";
			if($ordr[$k] == 999){
				print "<em style='color:red'>You Cannot Remove This Entry</em>";
			}
			print "<input type=\"hidden\" name=\"$taciswin_id\" value=\"$aciswin_id[$k]\"\>";

			print '</td></tr>';
		}
		print '</table>';
#
#--- adjust total # of ccds (subtract # of dropped ccds)
#
		$aciswin_no -= $chk_drop;

		print '<p>* If you need to remove any window constraint entries, make "Ordr" a blank, then push: ';
		print '<input type="submit" name="Check" value="Update">';
		print '</p>';
		print "<input type=\"hidden\" name=\"SPWINDOW\"   value=\"$spwindow\">";
		print "<input type=\"hidden\" name=\"ACISWIN_NO\" value=\"$aciswin_no\">";
		print "<input type=\"hidden\" name=\"awc_cnt\"    value=\"$awc_cnt\">";
		print "<input type=\"hidden\" name=\"awc_ind\"    value=\"$awc_ind\">";

	}else{
		print "<h3>No ACIS Window Constraints</h3>";
        for($k = 0; $k <= $aciswin_no; $k++){

			$taciswin_id      = 'ACISWIN_ID'."$k";
			$tordr	          = 'ORDR'."$k";
			$tchip	          = 'CHIP'."$k";
			$tstart_row       = 'START_ROW'."$k";
			$tstart_column    = 'START_COLUMN'."$k";
			$theight	      = 'HEIGHT'."$k";
			$twidth	          = 'WIDTH'."$k";
			$tlower_threshold = 'LOWER_THRESHOLD'."$k";
			$tpha_range       = 'PHA_RANGE'."$k";
			$tsample	      = 'SAMPLE'."$k";

			print "<input type=\"hidden\" name=\"$taciswin_id\"   value=\"$aciswin_id[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tordr\"         value=\"$ordr[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tchip\"         value=\"$chip[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tinclude_flag\" value=\"$dinclude_flag[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tstart_row\"    value=\"$start_row[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tstart_column\" value=\"$start_column[$k]\"\>";
			print "<input type=\"hidden\" name=\"$theight\"       value=\"$height[$k]\"\>";
			print "<input type=\"hidden\" name=\"$twidth\"        value=\"$width[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tpha_range\"    value=\"$pha_range[$k]\"\>";
			print "<input type=\"hidden\" name=\"$tsample\"       value=\"$sample[$k]\"\>";
		}
		print "<input type=\"hidden\" name=\"ACISWIN_NO\" value=\"$aciswin_no\"\>";

	}

#-----------------------------------
#----- TOO Parameter Case start here
#-----------------------------------

	print '<hr />';
	print '<h2>TOO Parameters';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#too_parameters\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';
	
	print '<table style="border-width:0px">';
	print '<tr>';
	print '<th style="verticla-align:top">TOO ID:';
	print '</th><td>';
	print "$too_id",'</td>';
	print '</tr>';
	
	print '<tr>';
	print '<th style="verticla-align:top;white-space:nowrap">TOO Trigger:';
	print '</th><td>',"$too_trig",'</td>';
	print '</tr>';

    print '<tr>';
	print '<th>TOO Type:</th><td>';
	print "$too_type";
	print '</td></tr></table>';

	print '<table style="border-width:0px">';
	print '<tr>';
	print '<th>Exact response window (days):</th>';
	print '<td>&#160;</td><td>&#160;</td>';
	print '<td>&#160;</td>';
	print '</tr>';

	print '<tr>';
	print '<th>Start:</th><td>';
	print "$too_start";
	print '</td>';

	print '<th>Stop:</th><td>';
	print "$too_stop";
	print '</td>';
	print '</tr>';

	print '<tr>';
	print '<th>';
	print '# of Follow-up Observations:</th><td>';
	print "$too_followup";
	print '</td>';

	print '<td>&#160;</td><td>&#160;</td>';
	print '</tr></table>';

	print '<table style="border-width:0px">';
	print '<tr><td>&#160;</td>';
	print '<th style="vertical-align:top">';
	print 'TOO Remarks:</th><td>';
	print "$too_remarks";
	print '</td></tr></table>';
	
#---------------------------------->
#---- Comment and Remarks  -------->
#---------------------------------->
	
	print '<hr />';
	print '<h2>Comments and Remarks';
    print "<span style='font-size:65%;'>";
    print '<a href="javascript:WindowOpener(\'./user_help.html#comments\')">';
    print '<span style="background-color:lime;"> (Open Help Page)</span></a>';
    print " </span>";
    print '</h2>';
	print '<p style="padding-bottom:20px"><strong>The remarks area below ';
    print 'is reserved for remarks related to constraints, ';
	print 'actions/considerations that apply to the observation. ';
	print 'Please put all other remarks/comments into the comment area below. ';
	print '</strong></p>';
	

#---------------------------------------------------------------------------------------
#------- Some remarks and/or comments contains " in the sentences. Since html page has 
#------- a problem with it, replacing " to ' so that html can behave normally.
#---------------------------------------------------------------------------------------

	@rtemp = split(//,$remarks);
	$temp = '';
	foreach $ent (@rtemp){
		if($ent eq "\""){
			$temp = "$temp"."'";
		}else{
			$temp = "$temp"."$ent";
		}
	}
	$remarks = $temp;
	
	@rtemp = split(//,$mp_remarks);
	$temp = '';
	foreach $ent (@rtemp){
		if($ent eq "\""){
			$temp = "$temp"."'";
		}else{
			$temp = "$temp"."$ent";
		}
	}
	$mp_remarks = $temp;
	
	@rtemp = split(//,$comments);
	$temp = '';
	foreach $ent (@rtemp){
		if($ent eq "\""){
			$temp = "$temp"."'";
		}else{
			$temp = "$temp"."$ent";
		}
	}
		
	$comments = $temp;

	print '<table style="border-width:0px">';

	print '<tr><th style="vertical-align:top">Remarks:</th>';
	print '<td><textarea name="REMARKS" ROWS="10" COLS="60">';
	print "$remarks";
	print '</textarea></td><td>&#160;</td></tr>';


	if($remark_cont ne ''){
		print '<tr><th style="vertical-align:top">Other Remark:</th><td>',"$remark_cont",'</td></tr>',"\n";
	}

	print "<tr><td colspan=3>";
	print "<strong> Comments are kept as a record of why a change was made.<br />";
	print "If a CDO approval is required, or if you have a special instruction for ARCOPS, ";
	print "add the comment in this area.</strong>";
	print "</td></tr>";
	print "<tr>";
	print "<th  style='vertical-align:top'>Comments:</th>";
	print "<td><textarea name='COMMENTS' ROWS='3' COLS='60'>";
    print "$comments";
    print "</textarea></td><td>&#160;</td></tr>";

	print "</table>";
	print "<hr />";
	
#------------------------------------->
#---- here is submitting options ----->
#------------------------------------->

	if($mp_check > 0){
		print "<h2><strong style='color:red;padding-bottom:10px'>";

		print "Currently under review in an active OR list.";
		print "</strong></h2>";
	}

	print '<strong>OPTIONS</strong>';
	print '<table style="border-width:0px"><tr><td>';
	print '<strong>Normal Change </strong> ';
	print '</td><td>';
	print 'Any changes other than APPROVAL status';
	print '</td></tr><tr><td>';
	print '<strong>Observation is Approved for flight </strong>';
	print '</td><td>';
	print 'Adds ObsID to the Approved File - nothing else<br />';
	print '</td></tr><tr><td>';
	print '<strong>ObsID no longer ready to go </strong> ';
	print '</td><td>';
	print 'REMOVES ObsID from the Approved File - nothing else<br />';
	print '</td></tr>';

	print '<tr><td>';
	print '<strong>Split this ObsID </strong> ';
	print '</td> <td> ';
	print '	<span style="color:fuchsia"> Please add an explanation why you need<br /> ';
    print 'to split this observation in the comment area.</span>';
	print '</td></tr>';

	print '</table>';
		
	print '<div style="text-align:center;margin-left:auto;margin-right:auto;padding-bottom:20px">';
	print '<table style="border-width:0px">';
	print '<tr>';
	
	if($asis eq 'NORM' || $asis eq ''){
		print '<td><input type="RADIO" name="ASIS" value="NORM" CHECKED><strong> Normal Change</strong>';
	}else{
		print '<td><input type="RADIO" name="ASIS" value="NORM"><strong> Normal Change</strong>';
	}
	
	if($asis eq 'ASIS'){
		print '<td><input type="RADIO" name="ASIS" value="ASIS" CHECKED><strong> ';
        print 'Observation is Approved for flight</strong>';
	}else{
		print '<td><input type="RADIO" name="ASIS" value="ASIS"><strong> ';
        print 'Observation is Approved for flight</strong>';
	}
	
	if($asis eq 'REMOVE'){
		print '<td><input type="RADIO" name="ASIS" value="REMOVE" CHECKED> ';
        print '<strong>ObsID no longer ready to go</strong>';
	}else{
		print '<td><input type="RADIO" name="ASIS" value="REMOVE"> <strong> ';
        print 'ObsID no longer ready to go</strong>';
	}

	if($asis eq 'CLONE'){
		print '<td><input type="RADIO" name="ASIS" value="CLONE" CHECKED><strong> Split this ObsID</strong>';
	}else{
		print '<td><input type="RADIO" name="ASIS" value="CLONE"><strong> Split this ObsID</strong>';
	}
	
	print '</tr></table>';

    print '<input type="hidden" name="OBSID"        '," value=\"$orig_obsid\">";
    print '<input type="hidden" name="ACISID"       '," value=\"$orig_acisid\">";
    print '<input type="hidden" name="HRCID"        '," value=\"$orig_hrcid\">";
    print '<input type="hidden" name="SI_MODE"      '," value=\"$si_mode\">";
    print '<input type="hidden" name="access_ok"    '," value=\"yes\">";
    print '<input type="hidden" name="pass"         '," value=\"$pass\">";
    print '<input type="hidden" name="sp_user"      '," value=\"$sp_user\">";
    print '<input type="hidden" name="email_address"'," value=\"$email_address\">";

    print '<input type="hidden" name="USER"         '," value=\"$submitter\">";
    print '<input type="hidden" name="SUBMITTER"    '," value=\"$submitter\">";

    print '<p style="text-align:left;"><b>';

    print "<span style='color:red;'>NEW!!</span><br />";
    print "If you want to apply the same changes to other obsids, please list ";
    print "them below.<br> ";
    print 'Please read: ';
    print '<a href="javascript:WindowOpener(\'./multi_obsids.html\')">';
    print 'how to use multiple obsid editing</a> for more details.<br><br>';

    print textfield(-name=>'split_list', 
                    -value=>"$split_list", 
                    -override=>10000, -size=>'80');
    print "</p>";

    print '<table style="border-width:0px">';
    print '<tr>';
    print '<td style="text-align:left;">';

    if($status !~ /scheduled/i && $status !~ /unobserved/i){
        print "<b style='text-align:left;'>This observation was ";
        print "<span style='color:red;'>$status</span>: ";
        print "You may not want to submit parameter changes.</b><br>";
    }

    print '<input type="submit" name="Check"  value="Submit">';
    print '</td>';
    print '</tr>';
    print '</table>';
    print '</div>';

    print '<hr>';

	print '<p style="padding-bottom:20px;">';
    print '<span style="font-size:110%;">Link to:</span><br> ';

	if($usint_on =~ /test/){
		print "<a href='$test_http/express_signoff.cgi'>";
	}elsif($usint_on =~ /yes/){
		print "<a href='$usint_http/express_signoff.cgi'>";
    }
	print "Express Approval Page</a>";
	print "</strong>";
    print "<br>";

	print "<a href=\"$cdo_http/review_report/disp_report.cgi?";
	print "$proposal_number";
	print '">Peer Review Report And Proposal</a>';
    print "<br>";

    print '<a href="https://cda.cfa.harvard.edu/chaser/startViewer.do?';
    print 'menuItem=sequenceSummary&obsid='."$obsid".'">ChaSeR Sequence Summary (with Roll/Pitch/Visibility, etc.)</a>';
    print '<br>';

	print "<a href='https://cxc.cfa.harvard.edu/cgi-bin/target_search/search.html'>";
	print 'Chandra User Observation Search Page</A><p>  ';
    print '</p>';

    print '<hr>';
    print '<p style="padding-top:5px; padding-bottom:20px;">';
    print 'If you have any questions, please contact: ';
    print '<a href="mailto:bwargelin@head.cfa.harvard.edu">bwargelin@head.cfa.harvard.edu</a>.';
    print '<br>';
    print '<em>Last Update: Oct 29, 2020</em>';
    print '</p>';

}           #---- end of sub "data_input_page"

##################################################################################
### prep_submit: preparing the data for submission                             ###
##################################################################################

sub prep_submit{

#----------------------
#----- time order cases
#----------------------
#
#--- if no_time_update > 0, skip converting day month year into tstart/tstop string
#
    (my $no_time_update) = @_;

	for($j = 1; $j <= $time_ordr; $j++){
		$tstart_new[$j] = '';					#--- recombine tstart and tstop

		if($start_month[$j] ne 'NULL'){
            if($start_month[$j] =~ /D/){
                $start_month[$j] = change_lmon_to_nmon($end_month[$j]);
            }
            $start_month[$j] = adjust_digit($start_month[$j]);
		}

		if($start_date[$j] =~ /\d/ && $start_month[$j] =~ /\d/ && $start_year[$j] =~ /\d/ ){
			@ttemp   = split(/:/, $start_time[$j]);
			$tind    = 0;
			$time_ck = 0;

			foreach $tent (@ttemp){
				if($tent =~ /\D/ || $tind eq ''){
					$tind++;
				}else{
					$time_ck = "$time_ck"."$tent";
				}
			}

            if($no_time_update == 0){
			    if($tind == 0){
				    $tstart_new = "$start_month[$j]:$start_date[$j]:$start_year[$j]:$start_time[$j]";
				    $chk_start  = -9999;
				    if($tstart_new =~ /\s+/ || $tstart_new == ''){
				    }else{
					    $tstart[$j] = $tstart_new;
					    $chk_start  = "$start_year[$j]$start_month[$j]$start_date[$j]$time_ck";
				    }
			    }
            }
		}
		
		$tstop_new[$j] = '';

		if($end_month[$j] ne 'NULL'){
            if($end_month[$j] =~ /D/){
                $end_month[$j] = change_lmon_to_nmon($end_month[$j]);
            }
            $end_month[$j] = adjust_digit($end_month[$j]);
		}

		if($end_date[$j] =~ /\d/ && $end_month[$j] =~ /\d/ && $end_year[$j] =~ /\d/ ){
			@ttemp   = split(/:/, $end_time[$j]);
			$tind    = 0;
			$time_ck = 0;
			foreach $tent (@ttemp){
				if($tent =~ /\D/ || $tind eq ''){
					$tind++;
				}else{
					$time_ck = "$time_ck"."$tent";
				}
			}

            if($no_time_update == 0){
			    if($tind == 0){
				    $tstop_new = "$end_month[$j]:$end_date[$j]:$end_year[$j]:$end_time[$j]";
				    $chk_end = -9999;
				    if($tstop_new =~ /\s+/ || $tstop_new == ''){
                        #
                        #--- do nothing
                        #
				    }else{
					    $tstop[$j] = $tstop_new;
					    $chk_end   = "$end_year[$j]$end_month[$j]$end_date[$j]$time_ck";
				    }
                }
			}
		}
		
		$time_ok[$j] = 0;

		if($chk_start != -9999 && $chk_end != -9999){			#--- check tstop > tstart
			$time_ok[$j] = 1;
			if($chk_end >= $chk_start){
				$time_ok[$j] = 2;
			}
		}

		if($window_constraint[$j]    eq 'NONE')      {$window_constraint[$j] = 'N'}
		elsif($window_constraint[$j] eq 'NULL')      {$window_constraint[$j] = 'NULL'}
		elsif($window_constraint[$j] eq 'CONSTRAINT'){$window_constraint[$j] = 'Y'}
		elsif($window_constraint[$j] eq 'PREFERENCE'){$window_constraint[$j] = 'P'}
	}

#----------------------
#---- roll order cases
#----------------------

	for($j = 1; $j <= $roll_ordr; $j++){

		if($roll_constraint[$j]    eq 'NONE')      {$roll_constraint[$j] = 'N'}
		elsif($roll_constraint[$j] eq 'NULL')      {$roll_constraint[$j] = 'NULL'}
		elsif($roll_constraint[$j] eq 'CONSTRAINT'){$roll_constraint[$j] = 'Y'}
		elsif($roll_constraint[$j] eq 'PREFERENCE'){$roll_constraint[$j] = 'P'}
		elsif($roll_constraint[$j] eq '')          {$roll_constraint[$j] = 'NULL'}

		if($roll_180[$j]    eq 'NULL'){$roll_180[$j] = 'NULL'}
		elsif($roll_180[$j] eq 'NO')  {$roll_180[$j] = 'N'}
		elsif($roll_180[$j] eq 'YES') {$roll_180[$j] = 'Y'}
		elsif($roll_180[$j] eq '')    {$roll_180[$j] = 'NULL'}
	}
#-------------------
#--- aciswin cases
#-------------------

	for($j = 0; $j < $aciswin_no; $j++){
		if($include_flag[$j] eq 'INCLUDE')   {$include_flag[$j] = 'I'}
		elsif($include_flag[$j] eq 'EXCLUDE'){$include_flag[$j] = 'E'}
	}
#
#--- reorder the rank with increasing order value sequence 
#
        if($aciswin_no > 0){
            @rlist = ();
            for($i = 0; $i < $aciswin_no; $i++){
                push(@rlist, $ordr[$i]);
            }
            @sorted = sort{$a<=>$b} @rlist;
            @tlist = ();
            foreach $ent (@sorted){
                if ($ent == 0){
                    next;
                }
                for($i = 0; $i < $aciswin_no; $i++){
                    if($ent == $ordr[$i]){
                        push(@tlist, $i);
                    }
                }
            }
        
            @temp0 = ();
            @temp1 = ();
            @temp2 = ();
            @temp3 = ();
            @temp4 = ();
            @temp5 = ();
            @temp6 = ();
            @temp7 = ();
            @temp8 = ();
            @temp9 = ();
            @temp10= ();
        
            for($i = 0; $i < $aciswin_no; $i++){
                $pos = $tlist[$i];
                push(@temp0 , $ordr[$pos]);
                push(@temp1 , $start_row[$pos]);
                push(@temp2 , $start_column[$pos]);
                push(@temp3 , $width[$pos]);
                push(@temp4 , $height[$pos]);
                push(@temp5 , $lower_threshold[$pos]);
                push(@temp6 , $pha_range[$pos]);
                push(@temp7 , $sample[$pos]);
                push(@temp8 , $chip[$pos]);
                push(@temp9 , $include_flag[$pos]);
                push(@temp10, $aciswin_id[$pos]);
            }
            @ordr            = @temp0;
            @start_row       = @temp1;
            @start_column    = @temp2;
            @width           = @temp3;
            @height          = @temp4;
            @lower_threshold = @temp5;
            @pha_range       = @temp6;
            @sample          = @temp7;
            @chip            = @temp8;
            @include_flag    = @temp9;
            @aciswin_id      = @temp10;
        
        }

#----------------------------------------------------------------
#----------- these have different values shown in Ocat Data Page
#----------- find database values for them
#----------------------------------------------------------------
	
    @dname_list = ('proposal_joint', 'roll_flag', 'window_flag', 'dither_flag', 
                   'uninterrupt', 'photometry_flag', 'multitelescope', 'hrc_zero_block',
                   'hrc_timing_mode', 'most_efficient', 'onchip_sum', 'duty_cycle', 
                   'eventfilter', 'multiple_spectral_lines', 'spwindow', 'extended_src', 
                   'phase_constraint_flag', 'window_constrint', 'constr_in_remarks', 
                   'ccdi0_on', 'ccdi1_on', 'ccdi2_on', 'ccdi3_on', 'ccds0_on', 'ccds1_on', 
                   'ccds2_on', 'ccds3_on', 'ccds4_on', 'ccds5_on',
#
#--- New 02-04-21
#
                   'window_constraint', 'pointing_constraint');

    foreach $d_name (@dname_list){
        adjust_o_values();
    }

	read_user_name();					            #--- read registered user name
	
	$usr_ind      = 0;
	$usr_cnt      = 0;

	@list_of_user = @special_user;

	OUTER:
	foreach $usr_nm (@list_of_user){				#--- checking the user name 
		$luser = lc ($submitter);
		$luser =~ s/\s+//g;

		if($luser eq $usr_nm){
			$usr_ind++;
			if($usint_on =~ /yes/){
				$email_address = $special_email[$usr_cnt];
			}
			last OUTER;
		}
		$usr_cnt++;
	}
	if($submitter eq 'mtadude'){
		$usr_ind++;
	}
}

########################################################################################
### chk_entry: calling entry_test to check input value range and restrictions        ###
########################################################################################

sub chk_entry{

#------------------------------
#----- read condition database
#------------------------------

	read_range();					                #--- sub to read the range database

	$header_chk  = 0;
	$range_ind   = 0;
	$error_ind   = 0;
	@out_range   = ();

	@cdo_warning = ();
	$cdo_w_cnt   = 0;

	@pwarning_name_list = ();
	@pwarning_orig_val  = ();
	@pwarning_new_val   = ();
	$pwarning_cnt       = 0;

    $cdo_notes          = '';
    $mp_notes           = '';

#-------------------
#----- general cases
#-------------------

	foreach $name (@paramarray){
		if($name =~ /WINDOW_FLAG/i || $name =~ /ROLL_FLAG/i || $name =~ /SPWINDOW/i 
                    || $name =~ /MONITOR_FLAG/i || $name =~ /GROUP_ID/i 
                    || $name =~ /MONITOR_FLAG/i || $name =~/PRE_MIN_LEAD/i
			        || $name =~ /PRE_MAX_LEAD/i
		){
                #
                #--- do nothing
                #
		}else{

#-----------------------------------------------
#----- check input value range and restrictions
#-----------------------------------------------

			entry_test();
		}
	}

	if($range_ind > 0){
		if($header_chk == 0){
			$header_chk++;
			print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range. </h2>";
		}
	
		print '<table border=1>';
		print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
		foreach $ent (@out_range){
			@atemp = split(/<->/,$ent);
			$db_name = $atemp[0];

			find_name();

			print "<tr><th>$web_name ($atemp[0])</th>";
			print "<td style='color:red;text-align:center'>$atemp[1]</td>";
			print "<td style='color:green'>$atemp[2]</td></tr>";
		}
		print "</table>";
	}
	$range_ind = 0;
	@out_range = ();

#-----------------------------------------
#---- print a html page about the bad news
#-----------------------------------------

#------------------
#---- ccd cases
#------------------

	if($instrument =~ /ACIS/i){
		if($count_ccd_on > 6){
			$range_ind++;
		}

		if($range_ind > 0){
			$error_ind += $range_ind;
			if($header_chk == 0){
				$header_chk++;
				print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
			}
		
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			foreach $ent (@out_range){
				@atemp = split(/<->/,$ent);
				$db_name = $atemp[0];

				find_name();

				print "<tr><th>$web_name ($atemp[0])</th>";
				print "<td style='color:'red;text-align:center'>$atemp[1]</td>";
				print "<td style='green'>$atemp[2]</td></tr>";
			}
	
			if($count_ccd_on > 6){
				print "<tr><th># of CCD On</th>";
				print "<td style='color:red'>$count_ccd_on</td>";
				print "<td style='color:green'>must be less than or equal to 6</td></tr>";
			}
			print '</table>';
		}
	
		$o_cnt1 = 0;
		$o_cnt2 = 0;
		$o_cnt3 = 0;
		$o_cnt4 = 0;
		$o_cnt5 = 0;
		$o_cnt  = 0;
		$no_yes = 0;
		$no_no  = 0;
		foreach $ent ($ccdi0_on, $ccdi1_on, $ccdi2_on, $ccdi3_on, $ccds0_on, $ccds1_on, $ccds2_on,
					  $ccds3_on, $ccds4_on, $ccds5_on){
			if($ent =~ /O1/i){$o_cnt1++};
			if($ent =~ /O2/i){$o_cnt2++};
			if($ent =~ /O3/i){$o_cnt3++};
			if($ent =~ /O4/i){$o_cnt4++};
			if($ent =~ /O5/i){$o_cnt5++};
			if($ent =~ /^O/i){$o_cnt++};
			if($ent =~ /Y/i) {$no_yes++};
			if($ent =~ /N/i) {$no_no++};
		}
		$ccd_warning = 0;
		if($o_cnt1 > 1 || $o_cnt2 > 1 || $o_cnt3 > 1 || $o_cnt4 > 1 || $o_cnt5 > 1){
				$line = 'You cannot assign the same OPT# on multiple CCDs. ';
				$ccd_warning = 1;
		}else{
			if($o_cnt5 > 0 && ($o_cnt1 == 0  || $o_cnt2 == 0  || $o_cnt3 == 0  || $o_cnt4 == 0)){
				$line = 'Please do not skip OPT#: Use 1, 2, 3, 4, and 5 in order. ';	
				$ccd_warning = 1;

			}elsif($o_cnt4 > 0 && ($o_cnt1 == 0  || $o_cnt2 == 0  || $o_cnt3 == 0)){
				$line = 'Please do not skip OPT#: Use 1, 2, 3, and  4 in order. ';	
				$ccd_warning = 1;

			}elsif($o_cnt3 > 0 && ($o_cnt1 == 0  || $o_cnt2 == 0)){
				$line = 'Please do not skip OPT#: Use 1, 2, and 3 in order. ';	
				$ccd_warning = 1;

			}elsif($o_cnt2 > 0 && $o_cnt1 == 0 ){
				$line = 'Please do not skip OPT#: Use 1  nd 2 in order. ';	
				$ccd_warning = 1;
			}
		}
	
		if($no_yes == 0){
			$ccd_warning = 1;
			if($line eq ''){
				$line = 'There must be at least one CCD with YES. ';
			}else{	
				$line = "$line<br />".' There must be at least one CCD with YES. ';
			}
		}

    	if($ccd_warning == 1){
			if($header_chk == 0){
        		print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
			}
        	print '<table border=1>';
        	print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
        	print "<tr><th>CCD Option Selection</th>";
        	print "<td style='color:red;text-align:center'>";
			
			$chk = $o_cnt + $no_yes;
			if($chk == 0){
				print "CCD# = NO";
			}else{
				foreach $ent ('ccdi0_on', 'ccdi1_on', 'ccdi2_on', 'ccdi3_on', 'ccds0_on', 
                              'ccds1_on', 'ccds2_on', 'ccds3_on', 'ccds4_on', 'ccds5_on'){
					$e_val = ${$ent};
					if($e_val =~ /^O/i){
						@atemp   = split(/_on/, $ent);
						$ccd_ind = uc ($atemp[0]);
						print "$ccd_ind: $e_val<br />";
					}
				}
			}
			print "</td>";
        	print "<td style='color:green'>$line</td></tr>";
        	print '</table>';
    	}
	}

#-----------------------
#------ time order cases
#-----------------------

	for($j = 1; $j <= $time_ordr; $j++){
		$range_ind = 0;
		@out_range = ();
		foreach $in_name ('TSTART', 'TSTOP', 'WINDOW_CONSTRAINT'){
			$name      = "$in_name".'.N';
			$lname     = lc ($name);
			$lname2    = lc ($in_name);
			${$lname}  = ${$lname2}[$j];

			$oin_name  = 'orig_'."$in_name";
			$oname     = "$oin_name".'.N';
			$olname    = lc ($oname);
			$olname2   = lc ($oin_name);
			${$olname} = ${$olname2}[$j];
		}

		$time_okn = $time_ok[$j];

		foreach $name ('WINDOW_FLAG', 'TSTART.N', 'TSTOP.N', 'WINDOW_CONSTRAINT.N'){
			entry_test();			                    #--- check the condition
		}

		if($range_ind > 0){			                    #--- write html page about bad news
			$error_ind += $range_ind;
			if($header_chk == 0){
				print "<h2 style='color:red'> Following values are out of range.</h2>";
			}
			$header_chk++;

			print '<strong style="padding-top:10px; padding-bottom:20px">Time Order: ',"$j",'</strong>';
		
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			foreach $ent (@out_range){
				@atemp   = split(/<->/,$ent);
				$db_name = $atemp[0];

				find_name();

				print "<tr><th>$web_name ($atemp[0])</th>";
				print "<td style='color:red;text-align:center'>$atemp[1]</th>";
				print "<td style='color:green'>$atemp[2]</th></tr>";
			}
			print '</table>';
		}
#
#--- preference/constraints change check
#
		foreach $aname ('WINDOW_FLAG', 'TSTART.N', 'TSTOP.N', 'WINDOW_CONSTRAINT.N'){
			$vname     = lc($aname);
			$new_val   = ${$vname};
			$orig_name = 'orig_'."$vname";
			$orig_val  = ${$orig_name};

			compare_to_original_val($vname, $new_val, $orig_val);
		}
	}

#-------------------------
#------- roll order cases
#-------------------------

	for($j = 1; $j <= $roll_ordr; $j++){
		$range_ind = 0;
		@out_range = ();

		$isdigit = 1;
		$rline   = '';
		foreach $in_name ('ROLL_CONSTRAINT','ROLL_180','ROLL','ROLL_TOLERANCE'){
			$name      = "$in_name".'.N';
			$lname     = lc ($name);
			$lname2    = lc ($in_name);
			${$lname}  = ${$lname2}[$j];

			$oin_name  = 'orig_'."$in_name";                                         
			$oname     = "$oin_name".'.N';                                                                      
			$olname    = lc ($oname);
			$olname2   = lc ($oin_name);
			${$olname} = ${$olname2}[$j];

			if(($in_name eq 'ROLL') || ($in_name eq 'ROLL_TOLERANCE')){
				@ctemp = split(//, ${$lname});
				foreach $etest (@ctemp){
					if($etest =~ /\d/ || $etest =~ /\./){
						#
						#--- do nothing;
						#
					}else{
						$isdigit = 0;
						break;
					}
				}
				if(${$lname} eq ''){
					$isdigit = 1;
				}
				if($isdigit == 0){
					$rline = "$rline".'<table border=1>';
					$rline = "$rline".'<tr><th>Parameter</th><th>Requested Value</th>';
                    $rline = "$rline".'<th>Possible Values</th></tr>';
					$rline = "$rline"."<tr><th>$in_name</th>";
					$rline = "$rline"."<th style='color:red;text-align:center'>${$lname}</th>";
					$rline = "$rline"."<th style='color:green'>number (digit & '.')</th></tr>";
					$rline = "$rline"."</table><br />";
				}
			}
		}

		foreach $name ('ROLL_FLAG','ROLL_CONSTRAINT.N','ROLL_180.N','ROLL.N','ROLL_TOLERANCE.N'){
			entry_test();			                    #--- check the condition
		}

		if($range_ind > 0 || $isdigit == 0){			#--- write html page about bad news

			$error_ind += $range_ind;
			print '<br />';
			print '<strong>Roll Order: ',"$j",'</strong><br />';
			if($header_chk == 0){
				print "<h2 style='color:red'> Following values are out of range.</h2>";
				print '<br />';
			}
			$header_chk++;

			if($isdigit == 0){
				print $rline;
			}
		
			if($range_ind > 0){
				print '<table border=1>';
				print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
				foreach $ent (@out_range){
					@atemp = split(/<->/,$ent);
					$db_name = $atemp[0];

					find_name();

					print "<tr><th>$web_name ($atemp[0])</th>";
					print "<td style='color:red;text-align:center'>$atemp[1]</th>";
					print "<td style='color:green'>$atemp[2]</th></tr>";
				}
				print '</table>';
			}
		}
#
#--- preference/constraints change check
#
		foreach $aname ('ROLL_FLAG','ROLL_CONSTRAINT.N','ROLL_180.N','ROLL.N','ROLL_TOLERANCE.N'){
			$vname     = lc($aname);
			$new_val   = ${$vname};
			$orig_name = 'orig_'."$vname";
			$orig_val  = ${$orig_name};
			
			compare_to_original_val($vname, $new_val, $orig_val);
		}
	}

#-----------------------
#--- acis i<-->s change in ACIS Paratmer
#-----------------------

	if(($orig_instrument !~ /ACIS-I/i && $instrument =~ /ACIS-I/i && $grating =~ /N/i)
			|| ($orig_instrument =~ /ACIS-I/i && $orig_grating !~ /N/ 
                  && $instrument =~ /ACIS-I/i && $grating =~ /N/i)) {


		if($multiple_spectral_lines =~ /n/i || $spectra_max_count =~ /n/i || $spectra_max_count eq ''){

			if($header_chk == 0){
				 print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
			}

			$header_chk++;
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			if($multiple_spectral_lines =~ /n/i){
				print '<tr><th>Multiple Spectral Lines</th>';
				print "<td style='color:red;text-align:center'>$multiple_spectral_lines</td>";
				print '<td style="color:green">YES</td>';
				print '</tr>';
			}
			if($spectra_max_count =~ /n/i || $spectra_max_count eq ''){
				print '<tr><th>Spectral Max Count</th>';
				print "<td style='color:red'>$spectra_max_count</td>";
				print '<td style="color:green">1-1000000</td>';
				print '</tr>';
			}
			print '<tr>';
			print '<td colspan=3 style="color:red">You can find these requirements in the RPS forms.</td>';
			print '</tr>';
			print '</table>';
		}
	}

#-----------------------
#----- acis window cases
#-----------------------

	if($instrument =~ /ACIS/){

		$wcnt = 0;
		for($j = 0; $j < $aciswin_no; $j++){
			$jj = $j + 1;
			$range_ind       = 0;
			$acis_order_head = 0;
			@out_range       = ();

			$chk_pha_range   = 0;

			foreach $in_name ('ORDR', 'CHIP','INCDLUDE_FLAG','START_ROW','START_COLUMN',
                              'HEIGHT','WIDTH', 'LOWER_THRESHOLD','PHA_RANGE','SAMPLE'){
				$name      = "$in_name".'.N';
				$lname     = lc ($name);
				$lname2    = lc ($in_name);
				${$lname}  = ${$lname2}[$j];

				$oin_name  = 'orig_'."$in_name";                                         
				$oname     = "$oin_name".'.N';                                                                      
				$olname    = lc ($oname);
				$olname2   = lc ($oin_name); 
				${$olname} = ${$olname2}[$j];


                if($name =~ /PHA_RANGE/i && ${$lname} > 13){
                    $chk_pha_range++;
                }

			}
	
			$name      = 'instrument'.'.n';
			${$name}   = $instrument;
			$test_inst = 'aciswin';			        #--- this one will be used if the instrument is changed
	
#
#---- if the entry is removed from the acis window constrints, skip the test.
#

			if($lname2 =~ /ordr/i && ${$lname} =~ /\d/){
				foreach $name ('INSTRUMENT.N','SPWINDOW','ORDR.N', 'CHIP.N','INCDLUDE_FLAG.N',
                               'START_ROW.N','START_COLUMN.N', 'HEIGHT.N','WIDTH.N', 
                               'LOWER_THRESHOLD.N','PHA_RANGE.N','SAMPLE.N'){

					entry_test();			        #--- check the condition
				}
#
#--- preference/constraints change check
#
				foreach $aname ('INSTRUMENT.N','SPWINDOW','ORDR.N', 'CHIP.N','INCDLUDE_FLAG.N',
                                'START_ROW.N','START_COLUMN.N', 'HEIGHT.N','WIDTH.N', 
                                'LOWER_THRESHOLD.N','PHA_RANGE.N','SAMPLE.N'){
					$vname     = lc($aname);
					$new_val   = ${$vname};
					$orig_name = 'orig_'."$vname";
					$orig_val  = ${$orig_name};
					
					compare_to_original_val($vname, $new_val, $orig_val);
				}

			}


            if($chk_pha_range > 0){
		        if($wcnt == 0){
                    print "<h3 style='color:fuchsia;padding-bottom:10px'> Warning: PHA_RANGE > 13:<br />";
                    print "In many configurations, an Energy Range above 13 keV will ";
                    print "risk telemetry saturation.</h3>";
			        $wcnt++;
		        }
            }

			if($range_ind > 0){			            #--- write html page about bad news
				$error_ind += $range_ind;
				if($header_chk == 0){
					print "<h2 style='color:red;padding-bottom:10px'> ";
                    print "Following values are out of range.</h2>";
				}
				$header_chk++;

				print '<strong style="padding-top:10px;padding-bottom:10px">';
                print 'Acis Window Entry: ',"$jj",'</strong>';
				$acis_order_head++;
			
				print '<table border=1>';
				print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
				foreach $ent (@out_range){
					@atemp = split(/<->/,$ent);
					$db_name = $atemp[0];

					find_name();

					print "<tr><th>$web_name ($atemp[0])</th>";
					print "<td style='color:red;text-align:center'>$atemp[1]</td>";
					print "<td style='color:green'>$atemp[2]/td></tr>";
				}
				print '</table>';

            }elsif($eventfilter_lower  > 0.5 || $awc_l_th == 1){

#------------------------------------------------------------------------------------
#--- this is a special case that ACIS energy fileter lowest energy is set > 0.5 keV.
#--- in this case, you need to fill ACIS window constraints
#------------------------------------------------------------------------------------

                $ocnt = 0;
                for($m = 0; $m < 4; $m++){
                    $name = 'ccdi'."$m".'_on';
                    if(${$name} =~ /Y/i || ${$name} =~ /OPT/i){
                        $ocnt++;
                    }
                }
                for($m = 0; $m < 6; $m++){
                    $name = 'ccds'."$m".'_on';
                    if(${$name} =~ /Y/i || ${$name} =~ /OPT/i){
                        $ocnt++;
                    }
                }
                if($ocnt > $aciswin_no){
                    if($header_chk == 0){
                        print "<h2 style='color:red;padding-bottom:10px'> ";
                        print "Following values are out of range.</h2>";
                    }
                    $header_chk++;

					if($do_not_repeat != 1){
                    	print '<table border=1>';
                    	print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
                    	print "<tr><th>Energy Filter Lowest Energy</th>";
                    	print "<td style='color:red;text-align:center'>0.5 keV </td>";
                    	print "<td style='color:green'>Spatial Window param  must be filled";
                    	print "<br />(just click PREVIOUS PAGE)</td>";
                    	print '</table>';
						$do_not_repeat = 1;
					}
                }
            }

			if(($lower_threshold[$j] < $eventfilter_lower) && ($lower_threshold[$j] ne '')){
				if($header_chk == 0){
					print "<h2 style='color:red;padding-bottom:10px'> ";
                    print "Following values are out of range.</h2>";
				}
				$header_chk++;

				if($acis_order_head == 0){
					print '<strong style="padding-top:10px;padding-bottom:10px">';
                    print 'Acis Window Entry: ',"$jj",'</strong>';
					$acis_order_head++;
				}

				print '<table border=1>';
				print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
				print "<tr><th>ACIS Lowest Threshold</th><td style='color:red;text-align:center'>";
                print "$lower_threshold[$j]</th>";
				print "<td style='olor:green'>lower_threshold must be larger than ";
                print "or equal to eventfilter_lower ";
                print "($eventfilter_lower)</td></tr>";
				print '</table>';
			}
			if($pha_range[$j] > $eventfilter_higher && $pha_range[$j] ne ''){
				if($header_chk == 0){
					print "<h2 style='color:red;padding-bottom:10px'> ";
                    print "Following values are out of range.</h2>";
				}
				$header_chk++;

				if($acis_order_head == 0){
					print '<strong style="padding-top:10px;padding-bottom:10px">';
                    print 'Acis Window Entry: ',"$jj",'</strong> ';
					$acis_order_head++;
				}

				print '<table border1>';
				print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
				print "<tr><th>ACIS Energy Range</th><td style='color:red;text-align:center'>";
                print "$pha_range[$j]</th>";
				print "<td style='color:green'>energy_range must be smaller than ";
                print "or equal to eventfilter_higher ";
                print "($eventfilter_higher)</td></tr>";
				print '</table>';
			}
		}
	}

#--------------------------------
#--- group_id/monitor_flag case
#--------------------------------

	if($monitor_flag =~ /Y/i){

		if($group_id){
			if($header_chk == 0){
				print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
			}
			$header_chk++;
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			print "<tr><th>Monitor Flag</th><td style='color:red;text-align:center'>$monitor_flag</th>";
			print "<td style='color:green'>A monitor_flag must be NULL or change group_id</td></tr>";
			print '</table>';

		}elsif($pre_min_lead eq '' || $pre_max_lead eq ''){
			if($header_chk == 0){
				print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
			}
			$header_chk++;
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			print "<tr><th>Monitor Flag</th><td style='color:red;text-align:center'>$monitor_flag</th>";
			print "<td style='color:green'>A monitor_flag must be NULL or ";
            print "add pre_min_lead and pre_max_lead</td></tr>";
			print '</table>';
		}
	}

	if($group_id){

		if($monitor_flag =~ /Y/i){
			if($header_chk == 0){
				print "<h2 style='color:red;padding-bottom:10px'>Following values are out of range.</h2>";
			}
			$header_chk++;
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			print "<tr><th>Group ID</th><td style='color:red;text-align:center'>$group_id</th>";
			print "<td style='color:green'>A group id must be NULL or change monitor_flag</td></tr>";
			print '</table>';

		}elsif($pre_min_lead eq '' || $pre_max_lead eq ''){
			if($header_chk == 0){
				print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
			}
			$header_chk++;
			print '<table border=1>';
			print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
			print "<tr><th>Group ID</th><td style='color:red;text-align:center'>$group_id</th>";
			print "<td style='color:green'>A group_id must be NULL or add pre_min_lead ";
            print "and pre_max_lead</td></tr>";
			print '</table>';
		}
	}

	if($pre_id == $obsid){

		if($header_chk == 0){
			print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
		}
		$header_chk++;
		print '<table border=1>';
		print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
		print "<tr><th>Follows ObsID#</th><td style='color=:red;text-align:center'>$pre_id</th>";
		print "<td style='color:green'>pre_id must be different from the ObsID ";
        print "of this observation ($obsid) </td></tr>";
		print '</table>';
	}

	if($pre_min_lead > $pre_max_lead){

		if($header_chk == 0){
			print "<h2 style='color:red;padding-bottom:10px'> Following values are out of range.</h2>";
		}
		$header_chk++;
		print '<table border=1>';
		print '<tr><th>Parameter</th><th>Requested Value</th><th>Possible Values</th></tr>';
		print "<tr><th>Min Int</th><td style='color:red;text-align:center'>$pre_min_lead</th>";
		print "<td style='color:green'>pre_min_lead must be smaller than ";
        print "pre_max_lead ($pre_max_lead)</td></tr>";
		print '</table>';
	}
#
#--- preference/constraints change check
#
	foreach $name ('CONSTR_IN_REMARKS', 'PHASE_CONSTRAINT_FLAG', 'PHASE_EPOCH', 'PHASE_PERIOD', 
                   'PHASE_START', 'PHASE_START_MARGIN', 'PHASE_END', 'PHASE_END_MARGIN',
				   'GROUP_ID', 'MONITOR_FLAG', 'PRE_ID', 'PRE_MIN_LEAD', 'PRE_MAX_LEAD', 
                   'MULTITELESCOPE', 'OBSERVATORIES', 'MULTITELESCOPE_INTERVAL', 'POINTING_CONSTRAINT'){
		$lname    = lc($name);
		$new_val  = ${$lname};
		$oin_name = 'orig_'."$lname";
		$orig_val = ${$oin_name};
		compare_to_original_val($lname, $new_val, $orig_val);
	}
#
#--- print preference/constraint change warning 
#	
	if($pwarning_cnt > 0){
		print_pwarning();
	}
		
	print '<br /><br />';
#
#--- if cdo/mp warning is logged, pass it as param. make sure that there is no space etc.
#
    if(length($cdo_notes) > 1){
        $cdo_notes =~ s/\n/##/g;
        $cdo_notes =~ s/\s/#/g;
    }else{
        $cdo_notes = '';
    }
    if(length($mp_notes) > 1){
        $mp_notes =~ s/\n/##/g;
        $mp_notes =~ s/\s/#/g;
    }else{
        $mp_notes = '';
    }
    print "<input type='hidden' name='cdo_notes' value=$cdo_notes>";
    print "<input type='hidden' name='mp_notes'  value=$mp_notes>";

#---------------------------------------------------------------
#----- print all paramter entries so that a user verifies input
#---------------------------------------------------------------

	submit_entry(1, $obsid, $sf);
}

###############################################################################################
### compare_to_original_val: sending a warning if there is preference/costraint changes    ####
###############################################################################################

sub compare_to_original_val{

	my $vname, $new_val, $orig_val;
	($vname, $new_val, $orig_val) = @_;

	if($vname =~ /\.n/){
		$vname =~ s/\.n//g;
	}

	if($new_val ne '' || $orig_val ne ''){
		if($new_val !~ /$orig_val/i){
			if( $orig_val eq ''){
				$orig_val = "' '";
			}
			push(@pwarning_name_list, $vname);
			push(@pwarning_orig_val,  $orig_val);
			push(@pwarning_new_val,   $new_val);	
			$pwarning_cnt++;
		}
	}
}

###############################################################################################
### print_pwarning: print out preference/constrain change warning                          ####
###############################################################################################

sub print_pwarning{
	print '<div style="padding-top:30px;padding-bottom:20px">';
	print '<table border=1 style="width:80%">';

	if($pwarning_cnt > 1){
		print '<tr><th colspan=3  style="color:red">The following changes impact ';
        print 'constraints or preferences.<br /> ';
		print 'Verify you have indicated CDO approval in the comments.</th></tr>';
	}else{
		print '<tr><th colspan=3 style="color:red">The following change impacts ';
        print 'a constraint or preference.<br /> ';
		print 'Verify you have indicated CDO approval in the comments.</td></tr>';
	}
	print '<tr><th>Parameter</th><th>Original Value</th><th>New Value</th></tr>';
	for($i = 0; $i < $pwarning_cnt; $i++){
		$vname = $pwarning_name_list[$i];
		$o_val = $pwarning_orig_val[$i];
		$n_val = $pwarning_new_val[$i];

		$db_name = $vname;
        find_name();
		$uvname = uc($vname);

		if($web_name eq ''){
			print "<tr><td style='text-align:center'><b>$uvname</b></td>";
		}else{
			print "<tr><td style='text-align:center'><b>$web_name ($uvname)</b></td>";
		}
		$eo_val = $o_val;
		if($o_val =~ /\'/){
			$eo_val = $blank;
		}
		print "<td style='text-align:center'>$eo_val</td>";
		print "<td style='text-align:center'>$n_val</td></tr>";
	}
	print '</tr></table>';
	print '</div>';
}

###############################################################################################
### entry_test: check input value range and restrictions                                   ####
###############################################################################################

sub entry_test{

	$uname = lc ($name);		                    #--- $name is a parameter name
	
#---------------------------------------------
#----- check whether the entry is digit or not
#---------------------------------------------

	$digit = 0;

	@ctemp = split(//, ${$uname});			
	OUTER:
	foreach $comp (@ctemp){
		if($comp eq '+' || $comp eq '-' || $comp =~/\d/ || $comp =~ /\./){
			$digit = 1;
		}else{
			$digit = 0;
			last OUTER;
		}
	}

#--------------------------------------------------------------
#----- if there any conditions, procceed to check the condtion
#--------------------------------------------------------------

	unless(${condition.$name}[0]  =~ /OPEN/i){
		$rchk = 0;				                    #--- comparing the data to the value range

#--------------------------------------------
#----- for the case that the condition is CDO
#--------------------------------------------

		if(${condition.$name}[0] eq 'CDO'){
			$original = "orig_$uname";
			if(${$original} ne ${$uname}){
				@{same.$name} = @{condition.$name};
				shift @{condition.$name};
				push(@{condition.$name},'<span style="color:red">Has CDO approved this change?</span>');
				$rchk++;

                $cdo_notes = "$cdo_notes"."$uname: ${$original} to ${$uname} \n";
#
#--- keep CDO warning
#
				if($original =~ /\s+/ || $original eq ''){
					$wline = "$uname is changed from $blank} to  ${$uname}";
				}else{
					$wline = "$uname is changed from $original} to  ${$uname}";
				}
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;
			}
		}

		OUTER:
		foreach $ent (@{condition.$name}){

#---------------------------------------------
#---- check whether condition is value ranges
#---------------------------------------------

			@atemp = split(/\(/,$ent);	            #--- the range is numbers

			if($ent =~ /NULL/i && (${$uname} eq '' || ${$uname}=~ /\s+/)){
				$rchk = 0;
				last OUTER;
			}

			if($ent eq 'NULL' || $ent eq 'CDO' || $ent eq 'DEFAULT'){
				if(${$uname} eq $ent){
					$rchk = 0;
					last OUTER;
				}
			}elsif($ent =~  /MUST/i){
				if(${$uname} eq '' || ${$uname} =~ /NULL/i || ${$uname} =~ /\s+/){
					$rchk++;
				}else{
					 $rchk =0;
				}
				last OUTER;
			}elsif($atemp[1] eq '+' || $atemp[1] eq '-' || $atemp[1] =~ /\d/){
				@btemp = split(/\)/, $atemp[1]);
				@data  = split(/<>/, $btemp[0]);
				if($digit == 0){
					$digit = 1;
					$rchk++;
					last OUTER;
				}
				if($digit == 1 && (${$uname} <  $data[0] || ${$uname} > $data[1])){
					$rchk++;
					last OUTER;
				}

#--------------------------------------------------
#---- check whether there is a special restriction
#--------------------------------------------------

			}elsif(($ent =~ /REST/i) && ( ${$uname} ne '' || ${$uname} !~/\s/)){	
                                                    #--- it has a special restriction
					$rchk = 0;
					last OUTER;
			}else{

#----------------------------------------------
#---- check the case that the condition is word
#----------------------------------------------

				if($digit == 0 && ${$uname} ne '' && ${$uname} !~/\s+/){	        
                                                    #--- the condition is in words
					$rchk++;
					if(${$uname} eq $ent){
						$rchk = 0;
						last OUTER;
					}
				}
			}
		}
	
#-----------------------------------------------------------------
#------- special case: if tstart and tstop is out of order, say so
#-----------------------------------------------------------------

		if($uname =~/^TSTART/i || $uname =~/^TSTOP/i){
			if($time_okn == 1){
				@{same.$name}      = @{condition.$name};
				@{condition.$name} = ("Out of Order");
				$digit = 0;
				$rchk++;
			}
		}

#--------------------------------------------------------------------
#----- if the value is out of range, start writing it into @out_range
#--------------------------------------------------------------------

		if($rchk > 0){				
			$range_ind++;			
			if($digit == 0){
				$line = "$name<->${$uname}<->@{condition.$name}";
				$sind = 0;
				if(${condition.$name}[0] =~ /MUST/){
					$line = "$name<->${$uname}<-> 'Must Have a Value'";
				}
				@{same.$name}      = @{condition.$name};

#-----------------------------------------------------------------
#---- extra restriction check, if there is violation, add comment
#-----------------------------------------------------------------

				restriction_check();	#----- sub to check an extra restriction

				if($sind > 0){		
					$line = "$line<br />"."$add";
				}
			 	push(@out_range,$line);
				@{condition.$name}= @{same.$name};
			}else{
				@{same.$name}      = @{condition.$name};
				if(${condition.$name}[0] eq 'NULL'){
					$add = 'NULL '."$data[0]<-->$data[1]";
				}else{
					$add = "$data[0]<---->$data[1]";
				}
				$line = "$name<->${$uname}<->$add";
				$sind = 0;
				restriction_check();
				if($sind >  0){
					$line = "$line<br />"."$add";
				}
			 	push(@out_range,$line);
				@{condition.$name}= @{same.$name};
			}
		}else{					

#--------------------------------------------------------------------
#---- the value is in the range, but still want to check restrictions
#--------------------------------------------------------------------

			if( ${$uname} ne '' && ${$uname} !~/\s+/){
				$sind = 0;			
				restriction_check();		        #--- sub to check an extra restriction
				if($sind >  0){
					$range_ind++;
					$line = "$name<->${$uname}<->$add";
					push(@out_range,$line);
					@{condition.$name}= @{same.$name};
				}
			}
		}

#-----------------------------------------------
#-----we need to check hrc<---> acis change here
#-----------------------------------------------

		if($uname =~ /^INSTRUMENT/i){

			@acis_param_need = ();	            #--- these two will be used to check hrc to acis change
			$apram_cnt       = 0;
			$inst_change     = 0;

#---------------------------------------------
#-------- ACIS <---> HRC INSTRUMENT CHANGE!!!
#---------------------------------------------

#--------------------------------------------------------------------------------
#---acis to hrc change saying changed from acis to hrc set all acis param to null
#--------------------------------------------------------------------------------

			if($orig_instrument =~ /^ACIS/i && $instrument =~ /^HRC/i){
				$inst_change             = 1;				
				$exp_mode                = 'NULL';				
				$bep_pack                = 'NULL';
				$frame_time              = '';
				$most_efficient          = 'NULL';
				$ccdi0_on                = 'NULL';
				$ccdi1_on                = 'NULL';
				$ccdi2_on                = 'NULL';
				$ccdi3_on                = 'NULL';
				$ccds0_on                = 'NULL';
				$ccds1_on                = 'NULL';
				$ccds2_on                = 'NULL';
				$ccds3_on                = 'NULL';
				$ccds4_on                = 'NULL';
				$ccds5_on                = 'NULL';
				$subarray                = 'NO';
				$subarray_start_row      = '';
				$subarray_row_count      = '';
				$subarray_frame_time     = '';
				$duty_cycle              = 'NULL';
				$secondary_exp_count     = '';
				$primary_exp_time        = '';
				$secondary_exp_time      = '';
				$onchip_sum              = 'NULL';
				$onchip_row_count        = '';
				$onchip_column_count     = '';
				$eventfilter             = 'NULL';
				$eventfilter_lower       = '';
				$eventfilter_higher      = '';
				$multiple_spectral_lines = '';
				$spectra_max_count       = '';	
				$bias                    = '';
				$frequency               = '';
				$bias_after              = '';
				$spwindow                = 'NULL';

				for($n = 0; $n <= $aciswin_no; $n++){
					$aciswin_id[$n]      = '';
					$ordr[$n]            = '';
					$chip[$n]            = 'NULL';
					$include_flag[$n]    = 'I';
					$start_row[$n]       = '';
					$start_column[$n]    = '';
					$height[$n]          = '';
					$width[$n]           = '';
					$lower_threshold[$n] = '';
					$pha_range[$n]       = '';
					$sample[$n]          = '';
				}
#---------------------------
#---- set aciswin_no to 0
#---------------------------
				$aciswin_no = '0';;
				if($test_inst ne 'aciswin'){
					$warning_line = '';

					if($hrc_si_mode eq '' || $hrc_si_mode =~ /NULL/){
						$warning_line = 'The value for <strong>HRC_SI_MODE</strong> must be provided ';
					}

					@{same.$name} = @{condition.$name};
                    $line              = "<span style='color:red'>Has CDO approved this instrument change?";
                    $line              = "$line"."(all ACIS params are NULLed) <br />$warning_line </span>";
					@{condition.$name} =($line);
					$line              = "$name<->${$uname}<->@{condition.$name}";
					push(@out_range,$line);
					@{condition.$name} = @{same.$name};
#
#--- CDO warning
#
					$wline = "$name<->${$uname}";
					push(@cdo_warning, $wline);
					$cdo_w_cnt++;

                    $cdo_notes = "$cdo_notes"."$uname: $orig_instrument to $instrument \n";
				}
				$rchk++;

#-----------------------------------------------------------------------
#----- hrc to acis change:saying hrc to acis change set hrc parm to null
#-----------------------------------------------------------------------

			}elsif($orig_instrument =~ /^HRC/i && $instrument =~ /ACIS/i){
				$inst_change     = 2;				
				$hrc_config      = 'NULL';			
				$hrc_zero_block  = 'N';
				$hrc_si_mode     = '';
				$hrc_timing_mode = 'N';
				$warning_line    = '';

				if($test_inst eq 'aciswin'){

					if($spwindow  eq '' || $spwindow  =~ /NULL/){
						$warning_line = 'The value for <strong>ACIS Winodw Filter</strong> must be provided<br />';
					}
					$test_inst = '';
				}else{
					foreach $test ('EXP_MODE','BEP_PACK','MOST_EFFICIENT','CCDI0_ON','CCDI1_ON',
							       'CCDI2_ON','CCDI3_ON','CCDS0_ON','CCDS1_ON','CCDS2_ON','CCDS3_ON',
                                   'CCDS4_ON','CCDS5_ON','SUBARRAY','DUTY_CYCLE'){
						$ltest = lc($test);

						if(${$ltest} eq '' || ${$ltest} =~ /NULL/){
							$warning_line = "$warning_line"."The value for <strong>$test</strong> must be provided<br />";
						}
					}
				}

				@{same.$name}      = @{condition.$name};
                $line              = "<span style='color:red'>Has CDO approved this instrument change? ";
                $line              = "$line"."(All HRC params are NULLed)<br />$warning_line</span>";
				@{condition.$name} = ($line);
				$line              = "$name<->${$uname}<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name} = @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->${$uname}";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $orig_instrument to $instrument \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}

#-----------------------
#------ target name: MP 
#-----------------------

        if($uname =~/TARGNAME/i){

			if($orig_targname ne $targname){
                @{same.$name}      = @{condition.$name};
                @{condition.$name} = ("<span style='color:red'>MP will be notified this change.</span>");
                $line              = "$name<->${$uname}<->@{condition.$name}";
                push(@out_range,$line);
                @{condition.$name} = @{same.$name};
                $rchk++;
#
#---MP warning
#
                $mp_notes = "$cdo_notes"."$uname: $orig_targname to $targname \n";
            }
            if($rchk > 0){
                $range_ind++;
            }
        }

#-----------------------
#----- grating case: CDO
#-----------------------

		if($uname =~ /^GRATING/i){

			if($orig_grating ne $grating){
				@{same.$name}      = @{condition.$name};
				@{condition.$name} = ("<span style='color:red'>CDO approval is required </span>");
				$line              = "$name<->${$uname}<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name} = @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->${$uname}";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $orig_grating to $grating \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}

#------------------
#---- obj_flag case
#------------------

		if($uname =~ /^OBJ_FLAG/i){

			if($orig_obj_flag ne $obj_flag){
				@{same.$name}      = @{condition.$name};
				@{condition.$name} = ("<span style='color:red'>CDO approval is required </span>");
				$line              = "$name<->${$uname}<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name} = @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->${$uname}";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $orig_obj_flag to $obj_flag \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}

#---------------------------------------------------------------------
#----ra/dec case:  a new and old positional difference must be in 0.5
#---------------------------------------------------------------------

		if($uname =~ /^DEC/i){
			$rtemp = split(/:/,$ra);

			if($rtemp[1] =~ /\d/){
				$tra   = 15.0 * ( $rtemp[0] + $rtemp[1]/60 + $rtemp[2]/3600);
			}else{
				$tra  = $ra;
			}

			$dtemp = split(/:/,$dec);
			if($dtemp[1] =~ /\d/){
				$frac  = $dtemp[1]/60  + $dtemp[2]/3600;

				if($dtemp[0] < 0 || $dtemp[0] =~ /-/){
					$tdec = $dtemp[0] - $frac;
				}else{	
					$tdec = $dtemp[0] + $frac;
				}
			}else{
				$tdec = $dec;
			}

			$diff_ra  = abs($orig_ra - $tra) * cos(abs(0.5 * ($orig_dec + $tdec)/57.2958));
			$diff_dec = abs($orig_dec - $tdec);
			$diff     = sqrt($diff_ra * $diff_ra + $diff_dec * $diff_dec);


			if($diff > 0.1333){
				@{same.$name} = @{condition.$name};
				$wline = '1) No changes can be requested until the out of range is corrected. ';
				$wline = "$wline".'please use the back button to correct out of range requests.<br />';

				$wline = "$wline".'2) If you desire CDO approval please use the Helpdesk (link) and select ';
				$wline = "$wline".'obscat changes.';

				@{condition.$name} = ("<span style='olor:red'>$wline<\/span>");

				$line = "$name<->RA+DEC > 8 arcmin<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name}= @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->RA+DEC > 8 arcmin";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $wline \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}

#---------------------------------------------------------------------
#-- y/z det offset: change must be less than equal to 10 arc min  ----
#---------------------------------------------------------------------

        if($uname =~/y_det_offset/i){
            $ydiff = $orig_y_det_offset - $y_det_offset;
            $zdiff = $orig_z_det_offset - $z_det_offset;
        
            $diff = sqrt($ydiff * $ydiff + $zdiff * $zdiff);
        
        
            if($diff >= 10){
                @{same.$name} = @{condition.$name};
                $wline = '1) No changes can be requested until the out of range is corrected. ';
                $wline = "$wline".'please use the back button to correct out of range requests.<br />';
        
                $wline = "$wline".'2) If you desire CDO approval please use the Helpdesk (link) and select ';
                $wline = "$wline".'obscat changes.';
        
                @{condition.$name} = ("<span style='olor:red'>$wline<\/span>");
        
        
                $line = "y/z_offset<->Y/Z Offset > 10 arcmin<->@{condition.$name}";
                push(@out_range,$line);
                @{condition.$name}= @{same.$name};
                $rchk++;
#
#---CDO warning
#
                $wline = "y/z_offset<->Y/Z Offset >= 10 arcmin";
                push(@cdo_warning, $wline);
                $cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $wline \n";
            }
            if($rchk > 0){
                $range_ind++;
            }
        }

#-------------------------
#----- multitelescope case
#-------------------------

		if($uname =~ /^MULTITELESCOPE/i){

			if($orig_multitelescope ne $multitelescope){
				@{same.$name}      = @{condition.$name};
				@{condition.$name} = ("<span style='color:red'>CDO approval is required </span>");
				$line              = "$name<->${$uname}<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name} = @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->${$uname}";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $orig_multitelescope to $multitelescope \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}

#------------------------
#----- observatories case
#------------------------

		if($uname =~ /^OBSERVATORIES/i){

			if($orig_observatories ne $observatories){
				@{same.$name}      = @{condition.$name};
				@{condition.$name} = ("<span style='color:red'>CDO approval is required </span>");
				$line              = "$name<->${$uname}<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name} = @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->${$uname}";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $orig_observatories to $observatories \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}

#---------------------
#-- pinting constraint          --- New 02-04-21
#---------------------

		if($uname =~ /^POINTING_CONSTRAINT/i){

			if($orig_pointing_constraint ne $pointing_constraint){
				@{same.$name}      = @{condition.$name};
				@{condition.$name} = ("<span style='color:red'>CDO approval is required </span>");
				$line              = "$name<->${$uname}<->@{condition.$name}";
				push(@out_range,$line);
				@{condition.$name} = @{same.$name};
				$rchk++;
#
#---CDO warning
#
				$wline = "$name<->${$uname}";
				push(@cdo_warning, $wline);
				$cdo_w_cnt++;

                $cdo_notes = "$cdo_notes"."$uname: $orig_pointing_constraint to $pointing_constraint \n";
			}
			if($rchk > 0){
				$range_ind++;
			}
		}
	}
}  

###################################################################
###  restriction_check: check special restrictions for input   ####
###################################################################

sub restriction_check{

	$add = '';
	for($m = 0; $m < ${restcnt.$name}; $m++){       #--- loop around # of restriction entries
		$chname = lc (${rest.$m.$name});	        #--- name of params which need to be checked

		if($chname ne 'NONE'){			            #--- if it is none, we do not need to worry
			$cnt = 0;
			$rest_ind = 0;
			OUTER:
			foreach $ent (@{condition.$name}){
				@atemp = split(//,$ent);
				if($ent eq 'REST'){
					$rest_ind++;
					last OUTER;

#-------------------------------
#------ digit value range check
#-------------------------------

				}elsif($digit == 1 && ($atemp[1] eq '+' || $atemp[1] eq '-' || $atemp[1] =~ /\d/)){
					@btemp = split(/\(/, $ent);
					@ctemp = split(/\)/, $btemp[1]);
					@dat   = split(/<>/, $ctemp[0]);

					if(${$uname} >= $dat[0] && ${$uname} <= $dat[1]){
						last OUTER;
					}else{
						$cnt++;
					}
				}elsif(${$uname} eq $ent){
					last OUTER;
				}else{
					$cnt++;
				}
			}


			@atemp = split(/\(/, ${restcnd.$m.$name}[$cnt]);
			@btemp = split(/\)/, $atemp[1]);

			$comp_val = ${$chname};
			if(${$chname} eq ''){
				$comp_val ='NULL';
			}
			$db_name   = $chname;
			find_name();
			$web_name1 = $web_name;

#--------------------------
#------ restriction check
#--------------------------

			if($rest_ind > 0){
				if($btemp[0] eq 'MUST'){
					if($comp_val eq 'NULL'){
						$add =  "$add"."A value for <em><strong>$web_name1 ($chname)</strong></em> is required.<br />";
						$sind++;
					}
				}elsif($btemp[0] eq 'NULL'){
					if($comp_val ne 'NULL'){
						$db_name = $name;
						find_name();
						$add = "$add"."A value for <em><strong>$web_name1 ($chname)</strong></em> must be ";
						$add = "$add"."<span style='color:magenta'>NULL</span>,<br />";
						$add = "$add"."or change the value for <em><strong>$web_name ($name)</strong></em><br />";
						$sind++;
					}
				}elsif($btemp[0] =~ /^N/i){
					if($comp_val ne 'N' && $comp_val ne 'NULL' && $comp_val ne 'NONE' && $comp_val ne 'NO'){
						$db_name = $name;
						find_name();
						$add = "$add"."A value for <em><strong>$web_name1 ($chname)</strong></em> must be ";
						$add = "$add"."<span style='color:magenta'>NULL or NO</span>,<br />";
						$add = "$add"."or change the value for <em><strong>$web_name ($name)</strong></em><br />";
						$sind++;
					}
				}else{
					if($comp_val ne $btemp[0] && $btemp[0] ne 'OPEN' && $btemp[0] ne ''){
						$db_name = $name;
						find_name();
						$add = "$add"."A value for <em><strong>$web_name1 ($chname)</strong></em> must be ";
						$add = "$add"."<span style='color:magenta'>$btemp[0]</span>,<br />";
						$add = "$add"."or change the value for <em><strong>$web_name ($name)</strong></em><br />";
						$sind++;
					}
				}
			}elsif((${restcnd.$m.$name}[$cnt] ne '')  && ($comp_val ne $btemp[0])){
				if(($comp_val eq 'NULL') && ($btemp[0] eq 'OPEN')){
				}else{
					$db_name = ${rest.$m.$name};
					find_name();
					$web_name2 = $web_name;

					if($btemp[0] eq 'OPEN'){
					}elsif($btemp[0] eq 'MUST'){
						if($comp_val eq '' || $comp_val eq 'NONE' || $comp_val eq 'NULL'){
							$add = "$add"."A value for <em><strong>$web_name2 (${rest.$m.$name})</strong></em> ";
							$add = "$add"."is required.<br />";
						$sind++;
						}
					}elsif($btemp[0] =~  /^N/i){
						if($comp_val ne 'N' && $comp_val ne 'NULL' &&  $comp_val ne 'NONE'){
							$db_name = $name;
							find_name();
							$add = "$add"."A value for <em><strong>$web_name1 ($chname)</strong></em> must be ";
							$add = "$add"."<span style='color:magenta'>NULL or NO</span>,<br />";
							$add = "$add"."or change the value for <em><strong>$web_name ($name)</strong></em><br />";
							$sind++;
						}
					}else{
						$add = "$add"."A value for <em><strong>$web_name2 (${rest.$m.$name})</strong></em> ";
						$add = "$add"."must be <span style='color:magenta'>$btemp[0]</span>,<br />";
						$sind++;
					}
				}
			}
		}
	}
}

###################################################################
### read_range: read conditions                                ####
###################################################################

sub read_range{

	@name_array = ();

#-------------------------------------------------------------
#---- the conditions/restrictions are in the file "ocat_values
#-------------------------------------------------------------

	open(FH,"$data_dir/ocat_values");
	OUTER:
	while(<FH>){
		chomp $_;
		@atemp = split(/\t+/,$_);
		@btemp = split(//,$_);

		if($btemp[0] eq '#'){		   		        #--- pass comment lines
			next OUTER;
		}
		if($instrument     =~ /HRC/i  && $atemp[0] =~ /A/i){
			next OUTER;
		}elsif($instrument =~ /ACIS/i && $atemp[0] =~ /H/i){
			next OUTER;
		}

		@line = ();
		shift(@atemp);

		foreach $ent (@atemp){		  		        #--- pick up only real entries

			$ent = uc ($ent);
			push(@line,$ent);
		}

		push(@name_array, $line[1]);	    		#--- name of the value

		${cndno.$line[1]} = 0;

		if($line[2] eq 'OPEN'){		 		        #--- value range, if it is Open, just say so
			@{condition.$line[1]} = ('OPEN');
			${cndno.$line[1]}++;

		}elsif($line[2] eq 'REST'){	     		    #--- the case which restriction attached
			@{condition.$line[1]} = ('REST');
			${cndno.$line[1]}++;

		}elsif($line[2] eq 'MUST'){
			@{condition.$line[1]} = ('MUST');
			${cndno.$line[1]}++;

		}else{				  		                #--- check the range of the value
			@{condition.$line[1]} = split(/\,/, $line[2]);
			foreach(@{condition.$line[1]}){
				${cndno.$line[1]}++     	        #--- no of possible condtions
			}
		}

		if($line[3] eq 'NONE'){		 		        #--- restriction checking starts here
			$zero = 0;		      		            #--- here is a no restriction case
			@{rest.$zero.$line[1]} = ('NONE');
			${restcnt.$line[1]} = 1;
		}else{
			@btemp = split(/\;/, $line[3]);
			$ent_cnt = 0;
			foreach(@btemp){
				$ent_cnt++;
			}
			${restcnt.$line[1]} = $ent_cnt;

			for($i = 0; $i < $ent_cnt; $i++){
				@atemp = split(/=/, $btemp[$i]);
				${rest.$i.$line[1]}    = $atemp[0];
				@{restcnd.$i.$line[1]} = split(/\,/, $atemp[1]);
			}
		}
	}
	close(FH);
}

####################################################################################
### read_user_name: reading authorized user names                                ###
####################################################################################

sub read_user_name{
	open(FH, "<$pass_dir/.htgroup");
    while(<FH>){
        chomp $_;
        @user_name = split(/\s/,$_);
    }
    shift(@user_name);
}

###################################################################################
### user_warning: warning a user, a user name mistake                           ###
###################################################################################

sub user_warning {

	print "<div style='padding-top:20px;padding-bottom:20px'>";
	if($submitter eq ''){
		print "<strong>No user name is typed in. </strong>";
	}else{
    	print "<strong> The user: <span style='color:magenta'>$submitter</span> ";
        print "is not in our database. </strong>";
	}
	print "<strong> Please go back and enter a correct one (use the Back button on the browser). </strong>";
	print "</div>";
}

###################################################################################
### submit_entry: check and submitting the modified input values                ###
###################################################################################

sub submit_entry{
    (my $wait, my $obsid, $sf) = @_;
#
#--- counters
#
	$k = 0;						            #--- acisarray counter
	$l = 0; 					            #--- aciswin array counter
	$m = 0;						            #--- generalarray counter

#-----------------------------
#--------- pass the parameters
#-----------------------------

    $pline = '';
	foreach $ent (@paramarray){
           $new_entry = lc ($ent);
           $new_value = ${$new_entry};

		unless($ent =~ /TSTART/ || $ent =~ /TSTOP/ || $ent =~ /WINDOW_CONSTRAINT/
			  || $ent =~ /ACISTAG/ || $ent =~ /ACISWINTAG/ 
              || $ent =~ /SITAG/ || $ent =~ /GENERALTAG/
			){
			$pline = "$pline"."<input type=\"hidden\" name=\"$ent\" value=\"$new_value\">";
		}
	}

#-------------------------
#------ hidden values here
#-------------------------

	$pline = "$pline"."<input type=\"hidden\" name=\"ASIS\"          value=\"$asis\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"CLONE\"         value=\"$clone\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"SUBMITTER\"     value=\"$submitter\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"USER\"          value=\"$submitter\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"SI_MODE\"       value=\"$si_mode\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"email_address\" value=\"$email_address\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"awc_cnt\"       value=\"$awc_cnt\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"awc_ind\"       value=\"$awc_ind\">";

#----------------------------
#------ time constraint cases
#----------------------------

	$pline = "$pline"."<input type=\"hidden\" name=\"TIME_ORDR\"     value=\"$time_ordr\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"TIME_ORDR_ADD\" value=\"$time_ordr_add\">";

	for($j = 1; $j <= $time_ordr; $j++){
		foreach $ent ('START_DATE', 'START_MONTH', 'START_YEAR', 'START_TIME',
			          'END_DATE',  'END_MONTH',   'END_YEAR',   'END_TIME',
			          'WINDOW_CONSTRAINT'){
			$name  = "$ent"."$j";
			$lname = lc ($ent);
			$val   = ${$lname}[$j];
			$pline = "$pline"."<input type=\"hidden\" name=\"$name\" value=\"$val\">";
		}
	}

#-----------------------------
#------ roll constraint cases
#-----------------------------

	$pline = "$pline"."<input type=\"hidden\" name=\"ROLL_ORDR\"     value=\"$roll_ordr\">";print 
	$pline = "$pline"."<input type=\"hidden\" name=\"ROLL_ORDR_ADD\" value=\"$roll_ordr_add\">";

	for($j = 1; $j <= $roll_ordr; $j++){
		foreach $ent('ROLL_CONSTRAINT','ROLL_180','ROLL','ROLL_TOLERANCE'){
			$name  = "$ent"."$j";
			$lname = lc ($ent);
			$val   = ${$lname}[$j];
			$pline = "$pline"."<input type=\"hidden\" name=\"$name\" value=\"$val\">";
		}
	}

#-------------------------
#------- acis window cases
#-------------------------

	$pline = "$pline"."<input type=\"hidden\" name=\"ACISWIN_NO\" value=\"$aciswin_no\">";

	for($j = 0; $j < $aciswin_no; $j++){
		foreach $ent ('ORDR', 'CHIP', #'INCLUDE_FLAG',
			          'START_ROW','START_COLUMN','HEIGHT','WIDTH',
				      'LOWER_THRESHOLD','PHA_RANGE','SAMPLE'){
			$name  = "$ent"."$j";
			$lname = lc ($ent);
			$val   = ${$lname}[$j];
			$pline = "$pline"."<input type=\"hidden\" name=\"$name\" value=\"$val\">";
		}
	}

#---------------------------------------------------------------------------------------
#--- to avoid write over other user's entry, generate different a sufix for the temp file
#---------------------------------------------------------------------------------------

	$tnum = rand();
	$sf = int(10000 * $tnum);
	if($tval < 10){
		$sf = '000'."$sf";
	}elsif($sf < 100){
		$sf = '00'."$sf";
	}elsif($sf < 1000){
		$sf = '0'."$sf";
	}

	$pline = "$pline"."<input type=\"hidden\" name=\"tmp_suf\" value=\"$sf\">";


#-------------------------------------------#
#-------------------------------------------#
#-------- ASIS and REMOVE case starts ------#
#-------------------------------------------#
#-------------------------------------------#

   if ($asis eq "ASIS" || $asis eq "REMOVE"){

#------------------------------------------------------
#---- start writing email to the user about the changes
#------------------------------------------------------

    	open (FILE, ">$temp_dir/$obsid.$sf");		    #--- a temp file which email to a user written in.

    	print FILE "OBSID     = $obsid\n";
    	print FILE "SEQNUM    = $seq_nbr\n";
    	print FILE "TARGET    = $targname\n";
    	print FILE "USER NAME = $submitter\n";
    	if($asis eq "ASIS"){
    		print FILE "VERIFIED OK AS IS\n";
    	}elsif($asis eq "REMOVE") {
    	    print FILE "VERIFIED  REMOVED\n";
    	}

    	print FILE "\n------------------------------------------------------------------------------------------\n";
    	print FILE "Below is a full listing of obscat parameter values at the time of submission,\nas well as new";
	    print FILE " values submitted from the form.  If there is no value in column 3,\nthen this is an unchangable";
	    print FILE " parameter on the form.\nNote that new RA and Dec will be slightly off due to rounding errors in";
	    print FILE " double conversion.\n\n";
    	print FILE "PARAM NAME          ORIGINAL VALUE        REQUESTED VALUE         ";
    	print FILE "\n------------------------------------------------------------------------------------------\n";
	
	    foreach $nameagain (@paramarray){

		    $lc_name   = lc ($nameagain);
		    $old_name  = 'orig_'."$lc_name";
		    $old_value = ${$old_name};

    		#unless (($lc_name =~/TARGNAME/i) || ($lc_name =~/TITLE/i)
    		unless (($lc_name =~/TITLE/i)
			    ||  ($lc_name =~/^WINDOW_CONSTRAINT/i) || ($lc_name =~ /^TSTART/i) || ($lc_name =~/^TSTOP/i) 
			    ||  ($lc_name =~/^ROLL_CONSTRAINT/i) || ($lc_name =~ /^ROLL_180/i)
			    ||  ($lc_name =~/^CHIP/i) || ($lc_name =~ /^INCLUDE_FLAG/i) || ($lc_name =~ /^START_ROW/i)
			    ||  ($lc_name =~/^START_COLUMN/i) || ($lc_name =~/^HEIGHT/i) || ($lc_name =~ /^WIDTH/i)
			    ||  ($lc_name =~/^LOWER_THRESHOLD/i) || ($lc_name =~ /^PHA_RANGE/i) || ($lc_name =~ /^SAMPLE/i)
			    ||  ($lc_name =~/^SITAG/i) || ($lc_name =~ /^ACISTAG/i) || ($lc_name =~ /^GENERALTAG/i)
			    ||  ($lc_name =~/ASIS/i) 
			    ){  

#---------------------
#---- time order case
#---------------------

			    if($lc_name =~ /TIME_ORDR/){
				    $current_entry = $oring_time_ordr;
				    print_param_line();
				    for($j = 1; $j <= $orig_time_ordr; $j++){
    
					    $nameagain     = 'WINDOW_CONSTRAINT'."$j";
					    $current_entry = $window_constraint[$j];
					    $old_value     = $orig_window_constraint[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'TSTART'."$j";
					    $current_entry = $tstart[$j];
					    $old_value     = $orig_tstart[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'TSTOP'."$j";
					    $current_entry = $tstop[$j];
					    $old_value     = $orig_tstop[$j];
					    check_blank_entry();
					    print_param_line();
				    }

#--------------------
#--- roll order case
#--------------------

			    }elsif ($lc_name =~ /ROLL_ORDR/){
				    $current_entry = $orig_roll_ordr;
				    print_param_line();
				    for($j = 1; $j <= $orig_roll_ordr; $j++){
    
					    $nameagain     = 'ROLL_CONSTRAINT'."$j";
					    $current_entry = $roll_constraint[$j];
					    $old_value     = $orig_roll_constraint[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'ROLL_180'."$j";
					    $current_entry = $roll_180[$j];
					    $old_value     = $orig_roll_180[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'ROLL'."$j";
					    $current_entry = $roll[$j];
					    $old_value     = $orig_roll[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'ROLL_TOLERANCE'."$j";
					    $current_entry = $roll_tolerance[$j];
					    $old_value     = $orig_roll_tolerance[$j];
					    check_blank_entry();
					    print_param_line();
				    }

#--------------------------
#--- acis window order case
#--------------------------

			    }elsif ($lc_name eq 'ACISWIN_ID'){
				    for($j = 0; $j < $aciswin_no; $j++){
					    $jj = $j + 1;
					    $nameagain     = 'ORDR'."$jj";
					    $current_entry = $ordr[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'CHIP'."$jj";
					    $current_entry = $chip[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'INCLUDE_FLAG'."$jj";
					    $current_entry = $include_flag[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'START_ROW'."$jj";
					    $current_entry = $start_row[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'START_COLUMN'."$jj";
					    $current_entry = $start_column[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'HEIGHT'."$jj";
					    $current_entry = $height[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'WIDTH'."$jj";
					    $current_entry = $width[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'LOWER_THRESHOLD'."$jj";
					    $current_entry = $lower_threshold[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'PHA_RANGE'."$jj";
					    $current_entry = $pha_range[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'SAMPLE'."$jj";
					    $current_entry = $sample[$j];
					    check_blank_entry();
					    print_param_line();
				    }
    		    }else{
        		    $current_entry = ${$old_name};
    			    print_param_line();
    		    }
    	    }
	    }
	    close FILE;

#-----------------------------------------------------------
#-------  start writing a html page for asis and remvoe case
#-----------------------------------------------------------

        $schk = sp_list_test($split_list);
	    if($asis eq "ASIS"){
	        $wrong_si = 0;
    	    if($si_mode =~ /blank/i || $si_mode =~ /NULL/i || $si_mode eq '' || $si_mode =~ /\s+/){
        	    $wrong_si = 9999;
        	    $pline = "$pline"."<p><strong style='color:red;padding-bottom:20px'>";
        	    $pline = "$pline"."Warning, an obsid, may not be approved without an SI_mode.";
        	    $pline = "$pline".'Please contact "acisdude" or and HRC contact as appropriate';
        	    $pline = "$pline"."and request they enter an SI-mode befor proceding.";
        	    "</strong></p>";
                if($schk == 1){
                    $rline = make_obsid_list($split_list, 2);
                    $pline = "$pline"."$rline";
                }
    	    }else{
    		    $pline = "$pline"."<p><strong>You have checked that this Obsid ($obsid) is ready for flight.";
			    $pline = "$pline"."  Any parameter changes you made will not be submitted with this request.</strong></p>";
                if($schk == 1){
                    $rline = make_obsid_list($split_list, 2);
                    $pline = "$pline"."$rline";
                }
		    }
	    }elsif($asis eq "REMOVE") {
    	    $pline = "$pline"."<p><strong>You have requested this Obsid ($obsid) ";
            $pline = "$pline"."to be removed from the \"ready to go\" list.";
 		    $pline = "$pline"." Any parameter changes you made will not be submitted with this request.</strong></p>";
            if($schk == 1){
                $rline = make_obsid_list($split_list, 2);
                $pline = "$pline"."$rline";
            }
   	    }

   	    if($asis eq "ASIS"){
   	        $pline = "$pline"."<input type=\"hidden\" name=\"ASIS\" value=\"ASIS\">";
   	    }elsif($asis eq "REMOVE") {
   	        $pline = "$pline"."<input type=\"hidden\" name=\"ASIS\" value=\"REMOVE\">";
   	    }

        $pline = "$pline"."<input type=\"hidden\" name=\"access_ok\"     value=\"yes\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"pass\"          value=\"$pass\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"sp_user\"       value=\"$sp_user\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"email_address\" value=\"$email_address\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"split_list\"    value=\"$split_list\">";
    
        $pline = "$pline".'<br />';

#
#--- check whether one of obsids are on active OR list
#
        ($tchk, @mp_w_list)             = check_spl_obs_on_mp_list($split_list);
#
#--- check any of the obsids are scheduled in less than 10 days
#
        ($uchk, $usot_diff, @sobs_list) = split_obs_date_check($split_list, $sot_diff, $obsid);
#
#--- check any of the obsids are not in the database
#
        ($nchk, @nobs_list)             = check_obsid_in_database($split_list, $obsid);

        if($nchk > 0){
            if($nchk == 1){
                $pline = "$pline"."<p><i  style='color:red;'>Warning: Obsid: ";
                $pline = "$pline"."@nobs_list is not in the database!</i></p>";
            }else{
                $pline = "$pline"."<p><i  style='color:red;'>Warning: Obsids: ";
                $pline = "$pline"."@nobs_list are not in the database!</i></p>";
            }
        }

        if ($tchk > 0){
            if($tchk == 1){
                $pline = "$pline"."<p><i style='color:red;'>Obsid: ";
                $pline = "$pline"."@mp_w_list  is already in OR list. ";
            }else{
                $pline = "$pline"."<p><i style='color:red;'>Obsids: ";
                $pline = "$pline"."@mp_w_list  are already in OR list. ";
            }

            $pline = "$pline"."Are you sure to submit the changes?</i></p>";

        }elsif($uchk > 0){
            if($uchk  == 1){
                $pline = "$pline"."<p><i style='color:red;'><i>Obsid: ";
                $pline = "$pline"."@sobs_list is scheduled in less than 10 days. ";
            }else{
                $pline = "$pline"."<p><i style='color:red;'>Obsids: ";
                $pline = "$pline"."@sobs_list are scheduled in less than 10 days. ";
            }
    
            $pline = "$pline"."Are you sure to submit the changes?</i></p>";
        }


        if($error_ind ==  0 || $usint_on =~ /yes/){
	        if($wrong_si == 0){
		        $pline = "$pline"."<input type=\"SUBMIT\"  name = \"Check\"  value=\"FINALIZE\">";
	        }
        }
        $pline = "$pline"."<input type=\"SUBMIT\"  name = \"Check\"  value=\"PREVIOUS PAGE\">";
        print "$pline";
   }

#--------------------------------------------#
#--------------------------------------------#
#-------- begin clone stuff  here -----------#
#--------------------------------------------#
#--------------------------------------------#

   if ($asis eq "CLONE"){           #--- this condition goes to line 7181

#--------------------------------
#-------- print email to the user
#--------------------------------

    	open (FILE, ">$temp_dir/$obsid.$sf");

    	print FILE "OBSID     = $obsid\n";
    	print FILE "SEQNUM    = $orig_seq_nbr\n";
    	print FILE "TARGET    = $orig_tragname\n";
    	print FILE "USER NAME =  $submitter\n";
    	print FILE "CLONE\n";
#----------
    	print FILE "PAST COMMENTS = \n $orig_comments\n\n";
    	print FILE "NEW COMMENTS  = \n $comments\n\n";
    	print FILE "PAST REMARKS  = \n $orig_remarks\n\n";
    	print FILE "NEW REMARKS   = \n $remarks\n\n";
#----------

    	print FILE "\n------------------------------------------------------------------------------------------\n";
    	print FILE "Below is a full listing of obscat parameter values at the time of submission,\nas well as new";
	    print FILE " values submitted from the form.  If there is no value in column 3,\nthen this is an unchangable";
	    print FILE " parameter on the form.\nNote that new RA and Dec will be slightly off due to rounding errors in";
	    print FILE " double conversion.\n\n";
    	print FILE "PARAM NAME          ORIGINAL VALUE        REQUESTED VALUE         ";
    	print FILE "\n------------------------------------------------------------------------------------------\n";
	
	    foreach $nameagain (@paramarray){
		    $lc_name = lc ($nameagain);
		    $old_name = 'orig_'."$lc_name";
		    $old_value = ${$old_name};
    		unless (($lc_name =~/TARGNAME/i) || ($lc_name =~/TITLE/i)
			|| ($lc_name =~ /^WINDOW_CONSTRAINT/i) || ($lc_name =~ /^TSTART/i) || ($lc_name =~/^TSTOP/i) 
			|| ($lc_name =~ /^ROLL_CONSTRAINT/i) || ($lc_name =~ /^ROLL_180/i)
			|| ($lc_name =~/^CHIP/i) || ($lc_name =~ /^INCLUDE_FLAG/i) || ($lc_name =~ /^START_ROW/i)
			|| ($lc_name =~/^START_COLUMN/i) || ($lc_name =~/^HEIGHT/i) || ($lc_name =~ /^WIDTH/i)
			|| ($lc_name =~/^LOWER_THRESHOLD/i) || ($lc_name =~ /^PHA_RANGE/i) || ($lc_name =~ /^SAMPLE/i)
			|| ($lc_name =~/^SITAG/i) || ($lc_name =~ /^ACISTAG/i) || ($lc_name =~ /^GENERALTAG/i)
			|| ($lc_name =~/ASIS/i) 
			){

#---------------------
#----- time order case
#---------------------
			    if($lc_name =~ /TIME_ORDR/){
				    $current_entry = ${$lc_name};
				    print_param_line();
				    for($j = 1; $j <= $time_ordr; $j++){
					    $nameagain     = 'WINDOW_CONSTRAINT'."$j";
					    $current_entry = $window_constraint[$j];
					    $old_value     = $orig_window_constraint[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'TSTART'."$j";
					    $current_entry = $tstart[$j];
					    $old_value     = $orig_tstart[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'TSTOP'."$j";
					    $current_entry = $tstop[$j];
					    $old_value     = $orig_tstop[$j];
					    check_blank_entry();
					    print_param_line();
				    }

#--------------------
#---- roll order case
#--------------------

			    }elsif ($lc_name =~ /ROLL_ORDR/){
				    $current_entry = ${$lc_name};
				    print_param_line();
				    for($j = 1; $j <= $roll_ordr; $j++){
					    $nameagain     = 'ROLL_CONSTRAINT'."$j";
					    $current_entry = $roll_constraint[$j];
					    $old_value     = $orig_roll_constraint[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'ROLL_180'."$j";
					    $current_entry = $roll_180[$j];
					    $old_value     = $orig_roll_180[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'ROLL'."$j";
					    $current_entry = $roll[$j];
					    $old_value     = $orig_roll[$j];
					    check_blank_entry();
					    print_param_line();
    
					    $nameagain     = 'ROLL_TOLERANCE'."$j";
					    $current_entry = $roll_tolerance[$j];
					    $old_value     = $orig_roll_tolerance[$j];
					    check_blank_entry();
					    print_param_line();
				    }

#---------------------
#--- acis window case
#---------------------

			    }elsif ($lc_name eq 'ACISWIN_ID'){
				    for($j = 0; $j < $aciswin_no; $j++){
					    $jj = $j + 1;
					    $nameagain     = 'ORDR'."$jj";
					    $current_entry = $ordr[$j];
					    print_param_line();
    
					    $nameagain     = 'CHIP'."$jj";
					    $current_entry = $chip[$j];
					    print_param_line();
    
					    $nameagain     = 'INCLUDE_FLAG'."$jj";
					    $current_entry = $include_flag[$j];
					    print_param_line();
    
					    $nameagain     = 'START_ROW'."$jj";
					    $current_entry = $start_row[$j];
					    print_param_line();
    
					    $nameagain     = 'START_COLUMN'."$jj";
					    $current_entry = $start_column[$j];
					    print_param_line();
    
					    $nameagain     = 'HEIGHT'."$jj";
					    $current_entry = $height[$j];
					    print_param_line();
    
					    $nameagain     = 'WIDTH'."$jj";
					    $current_entry = $width[$j];
					    print_param_line();
    
					    $nameagain     = 'LOWER_THRESHOLD'."$jj";
					    $current_entry = $lower_threshold[$j];
					    print_param_line();
    
					    $nameagain     = 'PHA_RANGE'."$jj";
					    $current_entry = $pha_range[$j];
					    print_param_line();
    
					    $nameagain     = 'SAMPLE'."$jj";
					    $current_entry = $sample[$j];
					    print_param_line();
				    }
    		    }elsif(${$lc_name} ne ''){
        		    $current_entry = ${$lc_name};
    			    print_param_line();
    		    }else{
        		    $current_entry = ${$old_name};
    			    print_param_line();
    		    }
    	    }
	    }
	    close FILE;

#----------------------------------------
#--------- print html page for clone case
#----------------------------------------

        $pline = "$pline"."Username = $submitter<p>";
        $pline = "$pline"."<p><strong>You have submitted a request for splitting obsid $obsid.  ";
        $pline = "$pline"."No parameter changes will be submitted with this request.</strong></p>";
    
	    if($comments eq $orig_comments){
		    $pline = "$pline".'<p style="padding-bottom:10px"><strong style="color:red">';
            $pline = "$pline".'You need to explain why you need to split this observation. ';
		    $pline = "$pline".'Plese go back and add the explanation in the comment area</strong></p>';
	    }else{
		    $pline = "$pline".'<table style="border-width:0px"><tr><th>Reasons for cloning:</th><td> ';
		    $pline = "$pline"."$comments",'</td></tr></table>';
	    }
    	
	    $pline = "$pline"."<input type=\"hidden\" name=\"CLONE\"         value=\"CLONE\">";
	    $pline = "$pline".'<br />';
    
        $pline = "$pline"."<input type=\"hidden\" name=\"access_ok\"     value=\"yes\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"pass\"          value=\"$pass\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"sp_user\"       value=\"$sp_user\">";
	    $pline = "$pline"."<input type=\"hidden\" name=\"email_address\" value=\"$email_address\">";
	    $pline = "$pline"."<input type=\"hidden\" name=\"asis\"          value=\"ARCOPS\">";
        $pline = "$pline"."<input type=\"hidden\" name=\"split_list\"    value=\"$split_list\">";
    
	    if($error_ind ==  0 || $usint_on =~ /yes/){
		    $pline = "$pline"."<input type=\"SUBMIT\"  name = \"Check\"  value=\"FINALIZE\">";
	    }
	    $pline = "$pline"."<input type=\"SUBMIT\"  name = \"Check\"  value=\"PREVIOUS PAGE\">";
        
        print "$pline";

    }       #--- closing "asis eq clone" condition from line 6985
#
#---  !!!! this if statement goes all the way to: line around 8778 (and not indeted correctly)!!!!
#
    if ($asis ne "ASIS" && $asis ne "REMOVE" && $asis ne "CLONE"){

#------------------------------------------#
#------------------------------------------#
#------ begin general changes here --------#
#------------------------------------------#
#------------------------------------------#

#--------------------------------------------
# acisarray triggers acis box in orupdate.cgi
# genarray triggers general box in orupdate.cgi
#--------------------------------------------

#------------------------------------
#----  perform RA and DEC correction
#------------------------------------

	$racnt     = 0;
	if (($ra =~/:/) && ($dec =~/:/)){
		@dec= split (":", $dec);
		if ($dec[0] =~/-/){
			$sign ="-";
			$dec[0] *= -1;
		} else {$sign = "+"}

		$newdec = ($dec[0] + ($dec[1]/60) + ($dec[2]/3600));
		$dec    = sprintf("%1s%3.6f", $sign, $newdec);
		@ra     = split (":", $ra);
		$newra  = (15 * ($ra[0] + ($ra[1]/60) + ($ra[2]/3600)));
		$ra     = sprintf("%3.6f", $newra);
		$racnt++;
	}else{
		$dec    = sprintf("%3.6f", $dec);
		$ra     = sprintf("%3.6f", $ra);
	}

#------------------------------------
#----- print the verification webpage
#------------------------------------

	$pline = "$pline"."<p style='padding-bottom:10'><strong>You have submitted the following ";
    $pline = "$pline"."values for obsid $obsid:</strong> </p>";

    $schk = sp_list_test($split_list);
    if($schk == 1){
        $rline = make_obsid_list($split_list, 1);
        $pline = "$pline"."$rline";

        $pline = "$pline".'<input type="hidden" name="split_list"'," value=\"$split_list\">";
    }

#
#--- check whether one of obsids are on active OR list
#
    ($tchk, @mp_w_list)             = check_spl_obs_on_mp_list($split_list);
#
#--- check any of the obsids are scheduled in less than 10 days
#
    ($uchk, $usot_diff, @sobs_list) = split_obs_date_check($split_list, $sot_diff, $obsid);
#
#--- check any of the obsids are not in the database
#
    ($nchk, @nobs_list)             = check_obsid_in_database($split_list, $obsid);

    if($nchk > 0){
        if($nchk == 1){
            $pline = "$pline"."<p><i  style='color:red;'>Warning: Obsid: ";
            $pline = "$pline"."@nobs_list is not in the database!</i></p>";
        }else{
            $pline = "$pline"."<p><i  style='color:red;'>Warning: Obsids: ";
            $pline = "$pline"."@nobs_list are not in the database!</i></p>";
        }
    }

    if ($tchk > 0){
        if($tchk == 1){
            $pline = "$pline"."<p><i style='color:red;'>Obsid: ";
            $pline = "$pline"."@mp_w_list  is already in OR list. ";
        }else{
            $pline = "$pline"."<p><i style='color:red;'>Obsids: ";
            $pline = "$pline"."@mp_w_list  are already in OR list. ";
        }

        $pline = "$pline"."Are you sure to submit the changes?</i></p>";

    }elsif($uchk > 0){
        if($uchk  == 1){
            $pline = "$pline"."<p><i  style='color:red;'>Obsid: ";
            $pline = "$pline"."@sobs_list is scheduled in less than 10 days. ";
        }else{
            $pline = "$pline"."<p><i style='color:red;'>Obsids: ";
            $pline = "$pline"."@sobs_list are scheduled in less than 10 days. ";
        }

        $pline = "$pline"."Are you sure to submit the changes?</i></p>";
    }
    
    $pline = "$pline"."<input type=\"hidden\" name=\"split_list\"    value=\"$split_list\">";

	if($error_ind == 0 || $usint_on =~ /yes/){
	    $pline = "$pline"."<input type=\"SUBMIT\"  name = \"Check\"  value=\"FINALIZE\">";
	}
	$pline = "$pline"."<input type=\"SUBMIT\"  name = \"Check\"  value=\"PREVIOUS PAGE\">";
	$pline = "$pline"."<p>";
	$pline = "$pline"."Username = $submitter</p>";

	$pline = "$pline"."<p style='padding-bottom:20px'>";
	$pline = "$pline"."If you see a <span style='color:red'>&lt;Blank&gt;</span>  ";
    $pline = "$pline"."in the \"Original Value\" Column below, ";
	$pline = "$pline"."it is because you requested to add a value on a \"Blank\" space. ";
	$pline = "$pline"."The \"Blank\" space in <em>Ocat Data Page</em> could mean \"empty string\", ";
    $pline = "$pline"."\"NULL\", or even \"0\" value in the database. ";
	$pline = "$pline"."If you requested to change any non-\"Blank\" value to a \"Blank\" space, ";
    $pline = "$pline"."<em>arcops</em> will pass it as a \"NULL\" value.";
	$pline = "$pline"."</p>";
#
#---- counter of number of changed paramters
#
	$pline = "$pline"."<table border=1 cellspacing=3>";
	$pline = "$pline"."<th>Parameter</th><th>Original Value</th><th>Requested</th></tr>";
	$cnt_modified = 0;
	
	foreach $name (@paramarray){
		unless (($name =~/ORIG/) || ($name =~/OBSID/) || ($name =~/USER/)
				|| ($name =~ /^REMARKS/) || ($name =~ /^COMMENTS/) || ($name =~ /^MP_REMARKS/)
				|| ($name =~ /^WINDOW_CONSTRAINT/) || ($name =~ /^TSTART/) || ($name =~ /^TSTOP/)
				|| ($name =~ /^ROLL_CONSTRAINT/) || ($name =~/^ROLL_180/) || ($name =~ /^ROLL_TOLERANCE/)
				|| ($name =~/^CHIP/i) || ($name =~ /^INCLUDE_FLAG/i) || ($name =~ /^START_ROW/i)
				|| ($name =~/^START_COLUMN/i) || ($name =~/^HEIGHT/i) || ($name =~ /^WIDTH/i)
				|| ($name =~/^LOWER_THRESHOLD/i) || ($name =~ /^PHA_RANGE/i) || ($name =~ /^SAMPLE/i)
				|| ($name =~/^SITAG/i) || ($name =~ /^ACISTAG/i) || ($name =~ /^GENERALTAG/i)
			){

#------------------------------------------
#------ If it is unchanged print that info
#------------------------------------------

			$new_entry = lc ($name);
			$new_value = ${$new_entry};
			$old_entry = 'orig_'."$new_entry";
			$old_value = ${$old_entry};

#-------------------------------------------------
#----- checking whether the value is digit or not
#-------------------------------------------------

			$chk_digit = 0;
			@dtemp = split(//,$new_value);
			OUTER:
			foreach $comp (@dtemp){
				if($comp =~/\d/ || $comp eq '.' || $comp eq '+' || $comp eq '-'){
					$chk_digit = 1;
				}else{
					$chk_digit = 0;
					last OUTER;
				}
			}
			$match_ok = 0;
			if($new_value eq $old_value){
				$match_ok = 1;
			}elsif($chk_digit > 0 && $new_value == $old_value){
				$match_ok = 1;
			}else{
				$cnt_modified++;
			}
			if($match_ok == 1){

#----------------------------------
#----- checking window order case
#----------------------------------

				if($name =~ /ACISWIN_ID/i){

					for($j = 0; $j < $aciswin_no; $j++){
						$jj = $j + 1;
						$ehead =  "ENTRY $jj: ";

						foreach $tent ('ORDR', 'CHIP', #'INCLUDE_FLAG',
								       'START_ROW','START_COLUMN', 'HEIGHT',
                                       'WIDTH','LOWER_THRESHOLD','PHA_RANGE', 'SAMPLE'){
							$new_entry = lc ($tent);
							$new_value = ${$new_entry}[$j];
							$old_entry = 'orig_'."$new_entry";
							$old_value = ${$old_entry}[$j];
							$chk_digit = 0;
							@dtemp     = split(//,$new_value);

							OUTER:
							foreach $comp (@dtemp){
								if($comp =~/\d/ || $comp eq '.' || $comp eq '+' || $comp eq '-'){
									$chk_digit = 1;
								}else{
									$chk_digit = 0;
									last OUTER;
								}
							}
							$match_ok = 0;

							if($new_value eq $old_value){
								$match_ok = 1;
							}elsif($chk_digit > 0 && $new_value == $old_value){
								$match_ok = 1;
							}

							if($match_ok == 1){
								$tname = "$ehead $tent";
								print_table_row($tname, 'same', $new_value);     
							}else{
								$tname = "$ehead $tent";
								if($old_value =~ /\s+/ || $old_value eq ''){
									print_table_row($tname, $blank, $new_value);
								}else{
									print_table_row($tname, $old_value, $new_value);
								}
								$k++; 		            #--- telling asicwin has modified param!
							}
						}
					}

#-------------------------------
#----- checking time order case
#-------------------------------

				}elsif($name =~ /TIME_ORDR/){
					print_table_row($name, 'same', $new_value);      

					for($j = 1; $j <= $time_ordr; $j++){
						$ehead =  "ORDER $j: ";

						foreach $tent ('WINDOW_CONSTRAINT', 'TSTART', 'TSTOP'){
							$new_entry = lc ($tent);
							$new_value = ${$new_entry}[$j];
							$old_entry = 'orig_'."$new_entry";
							$old_value = ${$old_entry}[$j];
							$chk_digit = 0;
							@dtemp     = split(//,$new_value);

							OUTER:
							foreach $comp (@dtemp){
								if($comp =~/\d/ || $comp eq '.' || $comp eq '+' || $comp eq '-'){
									$chk_digit = 1;
								}else{
									$chk_digit = 0;
									last OUTER;
								}
							}
							$match_ok = 0;

							if($new_value eq $old_value){
								$match_ok = 1;
							}elsif($chk_digit > 0 && $new_value == $old_value){
								$match_ok = 1;
							}

							if($match_ok == 1){
								$tname = "$ehaad $tent";
								print_table_row($tname, 'same', $new_value);      
							}else{
								$tname = "$ehaad $tent";
								if($old_value =~ /\s+/ || $old_value eq ''){
									print_table_row($tname, $blank, $new_value);
								}else{
									print_table_row($tname, $old_value, $new_value);
								}
								$m++;		                        #---- telling general change is ON
							}
						}
					}

#------------------------------
#----- checking roll order case
#------------------------------

				}elsif($name =~ /ROLL_ORDR/){
					print_table_row($name, 'same', $new_value);

					for($j = 1; $j <= $roll_ordr; $j++){
						 $ehead = "ORDER $j ";

						foreach $tent ('ROLL_CONSTRAINT', 'ROLL_180','ROLL', 'ROLL_TOLERANCE'){
							$new_entry = lc ($tent);
							$new_value = ${$new_entry}[$j];
							$old_entry = 'orig_'."$new_entry";
							$old_value = ${$old_entry}[$j];
							$chk_digit = 0;
							@dtemp     = split(//,$new_value);

							OUTER:
							foreach $comp (@dtemp){
								if($comp =~/\d/ || $comp eq '.' || $comp eq '+' || $comp eq '-'){
									$chk_digit = 1;
								}else{
									$chk_digit = 0;
									last OUTER;
								}
							}
							$match_ok = 0;

							if($new_value eq $old_value){
								$match_ok = 1;
							}elsif($chk_digit > 0 && $new_value == $old_value){
								$match_ok = 1;
							}

							if($match_ok == 1){
								$tname = "$ehead $tent";
								print_table_row($tname, 'same', $new_value);
							}else{
								$tname = "$ehead $tent";
								if($old_value =~ /\s+/ || $old_value eq ''){
									print_table_row($tname, $blank, $new_value);
								}else{
									print_table_row($tname, $old_value, $new_value);
								}
								$m++;		                        #---- telling general change is ON
							}
						}
					}

#----------------------
#----- all other cases
#----------------------

				}else{
					print_table_row($name, 'same', $new_value);
				}

#------------------------------------------------
#-------  If it is changed, print from old to new
#------------------------------------------------

			}else{
#-----------------------
#----- window order case
#-----------------------
				if($name eq 'ACISWIN_ID'){
					for($j = 0; $j < $aciswin_no; $j++){
						$jj = $j + 1;
						$ehead = "ENTRY $jj ";

						foreach $tent ('ORDR','CHIP', #	'INCLUDE_FLAG',
								       'START_ROW','START_COLUMN', 'HEIGHT','WIDTH',
                                       'LOWER_THRESHOLD','PHA_RANGE', 'SAMPLE'){
							$new_entry = lc ($tent);
							$new_value = ${$new_entry}[$j];
							$old_entry = 'orig_'."$new_entry";
							$old_value = ${$old_entry}[$j];
							$chk_digit = 0;
							@dtemp     = split(//,$new_value);
							OUTER:
							foreach $comp (@dtemp){
								if($comp =~/\d/ || $comp eq '.' || $comp eq '+' || $comp eq '-'){
									$chk_digit = 1;
								}else{
									$chk_digit = 0;
									last OUTER;
								}
							}
							$match_ok = 0;

							if($new_value eq $old_value){
								$match_ok = 1;
							}elsif($chk_digit > 0 && $new_value == $old_value){
								$match_ok = 1;
							}

							if($match_ok == 1){
								$tname = "$ehead $tent";
								print_table_row($tname, 'same', $new_value);
							}else{
								$tname = "$ehead $tent";
								if($old_value =~ /\s+/ || $old_value eq ''){
									print_table_row($tname, $old_value, $new_value);
								}else{
									print_table_row($tname, $old_value, $new_value);
								}
								$k++;		        #--- telling aciswin param changes
							}
						}
					}

#---------------------
#----- time order case
#---------------------

				}elsif($name =~ /TIME_ORDR/){
					if($old_value =~ /\s+/ || $old_value eq ''){
						print_table_row($name, $blank, $new_value);
					}else{
						print_table_row($name, $old_value, $new_value);
					}

					for($j = 1; $j <= $time_ordr; $j++){
					$ehead = "ORDER $j ";

						foreach $tent ('WINDOW_CONSTRAINT', 'TSTART', 'TSTOP'){
							$new_entry = lc ($tent);
							$new_value = ${$new_entry}[$j];
							$old_entry = 'orig_'."$new_entry";
							$old_value = ${$old_entry}[$j];
							$chk_digit = 0;
							@dtemp     = split(//,$new_value);

							OUTER:
							foreach $comp (@dtemp){
								if($comp =~/\d/ || $comp eq '.' || $comp eq '+' || $comp eq '-'){
									$chk_digit = 1;
								}else{
									$chk_digit = 0;
									last OUTER;
								}
							}
							$match_ok = 0;

							if($new_value eq $old_value){
								$match_ok = 1;
							}elsif($chk_digit > 0 && $new_value == $old_value){
								$match_ok = 1;
							}

							if($match_ok == 1){
								$tname = "$ehead $tent";
								print_table_row($tname, 'same', $new_value);
							}else{
								$tname = "$ehead $tent";
								if($old_value =~ /\s+/ || $old_value eq ''){
									print_table_row($tname, $blank, $new_value);
								}else{
									print_table_row($tname, $old_value, $new_value);
								}
								$m++; 			   #---- telling general change is ON
							}
						}
					}

#---------------------
#----- roll order case
#---------------------

				}elsif($name =~ /ROLL_ORDR/){
					if($old_value =~ /\s+/ || $old_value eq ''){
						print_table_row($name, $blank, $new_value);
					}else{
						print_table_row($name, $old_value, $new_value);
					}

					for($j = 1; $j <= $roll_ordr; $j++){
					$ehead = "ORDER $j ";

						foreach $tent ('ROLL_CONSTRAINT', 'ROLL_180', 'ROLL','ROLL_TOLERANCE'){
							$new_entry = lc ($tent);
							$new_value = ${$new_entry}[$j];
							$old_entry = 'orig_'."$new_entry";
							$old_value = ${$old_entry}[$j];

							if($new_value eq $old_value){
								$tname = "$ehead $tent";
								print_table_row($tname, 'same', $new_value);
							}else{
								$tname = "$ehead $tent";
								if($old_value =~ /\s+/ || $old_value eq ''){
									print_table_row($tname, $blank, $new_value);
								}else{
									print_table_row($tname, $old_value, $new_value);
								}
								$m++;			  #---- telling general change is ON
							}
						}
					}

#----------------------
#----- all other cases
#----------------------

				}else{
					if((($old_value =~ /OPT/) && ($new_value =~ /Y/))
						|| (($old_value =~ /Y/) && ($new_value =~ /OPT/))){
						
						if($old_value =~ /\s+/ || $old_value eq ''){
							print_table_row($name, $blank, $new_value, 'lime');
						}else{
							print_table_row($name, $old_value, $new_value, 'lime');
						}
					}else{
						if($old_value =~ /\s+/ || $old_value eq ''){
							print_table_row($name, $blank, $new_value);
						}else{
							print_table_row($name, $old_value, $new_value);
						}
					}
				}

                if($instrument =~ /ACIS/i){
				    foreach $param (@acisarray){
					    if ($name eq $param){
						    $k++;
					    }
				    }
				    foreach $param (@aciswinarray){
					    if ($name eq $param){
						    $l++;
					    }
				    }
                }
				foreach $param2 (@genarray){
					if ($name eq $param2){
						$m++;
					}
				}
			}
		}
	}
	$pline = "$pline"."</table><br />";

#--------------------------------
#----- check remarks and comment
#--------------------------------

	$tremarks      = $remarks;
	$tremarks      =~ s/\n+//g;
	$tremarks      =~ s/\t+//g;
	$tremarks      =~ s/\s+//g;
	$torig_remarks = $orig_remarks;
	$torig_remarks =~ s/\n+//g;
	$torig_remarks =~ s/\t+//g;
	$torig_remarks =~ s/\s+//g;

	$pline = "$pline"."<h3>REAMARKS and COMMENTS Changes</h3>";
	
	if($tremarks ne $torig_remarks){

		if(($torig_remarks ne '') && ($tremarks eq '')){
			$remarks = "ALL TEXT FROM THE REMRKS HAS BEEN DELETED";	

			$pline = "$pline"."<span style='color:#FF0000'>REMARKS</span> changed from<br /><br />";
			$pline = "$pline"."<span style='color:#FF0000'> $orig_remarks</span><br /> to<br />";
			$pline = "$pline"."<span style='color:#FF0000'><b> $remarks</b></span><br /><br />";
		}elsif($torig_remarks eq ''){
			$pline = "$pline"."<span style='color:#FF0000'>REMARKS</span> changed from<br /><br />";
			$pline = "$pline"."<span style='color:#FF0000'> $blank</span><br /> to<br />";
			$pline = "$pline"."<span style='color:#FF0000'> $remarks</span><br /><br />";
		}else{
			$pline = "$pline"."<span style='color:#FF0000'>REMARKS</span> changed from<br /><br />";
			$pline = "$pline"."<span style='color:#FF0000'> $orig_remarks</span><br /> to<br />";
			$pline = "$pline"."<span style='color:#FF0000'> $remarks</span><br /><br />";
		}
		$m++;			                        #--- remark is a part of general change
		$cnt_modified++;
	} else {
	
		if($tremarks eq ''){
			$pline = "$pline"."REMARKS unchanged and there is no remark.<br /><br />";
		}else{
			$pline = "$pline"."REMARKS unchanged, set to <br /><br /> $remarks<br /><br />";
		}
	}

	$tcomments      = $comments;
	$tcomments      =~ s/\n+//g;
	$tcomments      =~ s/\t+//g;
	$tcomments      =~ s/\s+//g;
	$torig_comments = $orig_comments;
	$torig_comments =~ s/\n+//g;
	$torig_comments =~ s/\t+//g;
	$torig_comments =~ s/\s+//g;

	if ($tcomments ne $torig_comments){
		$cnt_modified++;

		if(($torig_comments ne '') && ($tcomments eq '')){
			$comments = "ALL TEXT FROM THE COMMENTS HAS BEEN DELETED";	

			$pline = "$pline"."<span style='color:#FF0000'>COMMENTS</span> changed from<br /><br /> ";
			$pline = "$pline"."<span style='color:#FF0000'>$orig_comments</span>";
			$pline = "$pline"."<br />to<br />";
			$pline = "$pline"."<span style='color:#FF0000'><b>$comments</b><br /></span>";
		}elsif($torig_comments eq ''){
			$pline = "$pline"."<span style='color:#FF0000'>COMMENTS</span> changed from<br /><br />";
			$pline = "$pline"."<span style='color:#FF0000'> $blank</span>";
			$pline = "$pline"."<br />to<br />";
			$pline = "$pline"."<span style='color:#FF0000'>$comments<br /></span>";
		}else{
			$pline = "$pline"."<span style='color:#FF0000'>COMMENTS</span> changed from<br /><br /> ";
			$pline = "$pline"."<span style='color:#FF0000'>$orig_comments</span>";
			$pline = "$pline"."<br />to<br />";
			$pline = "$pline"."<span style='color:#FF0000'>$comments<br /></span>";
		}

	} else {
		if($tcomments eq ''){
			$pline = "$pline"."COMMENTS unchanged and there is no comment.<br />";
		}else{
			$pline = "$pline"."COMMENTS unchanged, set to <br /><br /> $comments<br />";
		}
	}

	if($wrong_si == 0){
		$pline = "$pline"."<br /><hr />";
		$pline = "$pline"."<p style='padding-top:15px;padding-bottom:5px'>";
		$pline = "$pline"."<strong>If these values are correct, click the FINALIZE button.<br />";
		$pline = "$pline"."Otherwise, use the previous page button to edit.</strong><br />";
		$pline = "$pline"."</p>";
	}
	$j = 0;

#----------------------------------------
#----- turn on and off several indicators
#----------------------------------------

	if ($orig_si_mode eq $si_mode){
		$sitag = "OFF";
	} else {
		$sitag = "ON";
	}

	$sitag = 'OFF';
	if($instrument =~ /ACIS/i){
		if($orig_targname ne $targname){
			if(($orig_ra ne $ra) || ($orig_dec ne $dec)){
				$si_mode = 'NULL';
			}
		}
	}

	if($orig_est_cnt_rate    ne $est_cnt_rate)   {$si_mode = 'NULL'}
	if($orig_forder_cnt_rate ne $forder_cnt_rate){$si_mode = 'NULL'}
	if($orig_raster_scan     ne $raster_scan)    {$si_mode = 'NULL'}
	if($orig_grating	     ne $grating)        {$si_mode = 'NULL'}
	if($orig_instrument      ne $instrument)     {$si_mode = 'NULL'}
	if($orig_dither_flag     ne $dither_flag)    {$si_mode = 'NULL'}

	if($orig_si_mode ne $si_mode){ $sitag = 'ON'}
	if($instrument =~ /HRC/i){
		if($orig_hrc_config ne $hrc_config){$sitag = 'ON'}
		if($orig_hrc_zero_block ne $hrc_zero_block){$sitag = 'ON'}
	}


	if ($k > 0){
		$acistag    = "ON";
	}
	if ($l > 0){
		$aciswintag = "ON";
	}
	if ($m > 0){
		$generaltag = "ON";
	}

	$pline = "$pline"."<input type=\"hidden\" name=\"ACISTAG\"        value=\"$acistag\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"SITAG\"          value=\"$sitag\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"GENERALTAG\"     value=\"$generaltag\">";

	$pline = "$pline"."<input type=\"hidden\" name=\"access_ok\"      value=\"yes\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"pass\"           value=\"$pass\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"sp_user\"        value=\"$sp_user\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"email_address\"  value=\"$email_address\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"cnt_modified\"   value=\"$cnt_modified\">";
	$pline = "$pline"."<input type=\"hidden\" name=\"split_list\"     value=\"$split_listed\">";
#
#--- passing si select only value
#
    $pline = "$pline"."<input type=\"hidden\" name=\"hrc_si_select\"  value=$hrc_si_select>";

	if($error_ind == 0 || $usint_on =~ /yes/){
		if($wrong_si == 0){
			$pline = "$pline"."<input type=\"SUBMIT\" name =\"Check\" value=\"FINALIZE\">";
		}
	}
	$pline = "$pline"."<input type=\"SUBMIT\" name =\"Check\"         value=\"PREVIOUS PAGE\">";
	$pline = "$pline"."<div style='padding-bottom:30px'></div>";

    if($wait == 1){
        print "$pline";
    }

#---------------------------------
#--------------- print email form
#---------------------------------

	open (FILE, ">$temp_dir/$obsid.$sf");
	print FILE "OBSID     = $obsid\n";
	print FILE "SEQNUM    = $orig_seq_nbr\n";
	print FILE "TARGET    = $orig_targname\n";
	print FILE "USER NAME =  $submitter\n";

	if($asis =~ /\w/){
    	print FILE "VERIFIED AS $asis\n";
		if($asis =~ /ARCOPS/i){
			print FILE "Obsid: $obsid will be approved once ARCOPS signs off this submittion.\n";
		}
	}
	print FILE "PAST COMMENTS =\n $orig_comments\n\n";

	if($tcomments ne $torig_comments){
		print FILE "NEW COMMENTS  =\n $comments\n\n";
	}
	
	print FILE "PAST REMARKS =\n $orig_remarks\n\n";

	if($tremarks ne $torig_remarks){
		print FILE "NEW REMARKS =\n $remarks\n\n";
	}

#--------------

	@saved_line = ();	
    @alines     = ();

	print FILE "GENERAL CHANGES:\n";

	OUTER:
	foreach $name (@paramarray){
		foreach $comp (@prefarray){
			if($name eq $comp){
				next OUTER;
			}
		}

#-------------------
#---- general cases
#-------------------

		unless (($name =~/ORIG/) || ($name =~/OBSID/) || ($name =~/USER/) 
                || ($name =~/COMMENTS/) || ($name =~/ACISTAG/) 
			    || ($name =~/GENERALTAG/) || ($name =~/SITAG/) || ($name eq "RA") 
                || ($name eq "DEC") || ($name eq 'ASIS') || ($name eq 'REMARKS')){

			$a         = 0;
			$aw        = 0;
			$g         = 0;
			$new_entry = lc($name);
			$new_value = ${$new_entry};
			$old_entry = 'orig_'."$new_entry";
			$old_value = ${$old_entry};
			$test1     = $new_value;
			$test2     = $old_value;
			$test1     =~ s/\n+//g;
			$test1     =~ s/\t+//g;
			$test1     =~ s/\s+//g;
			$test2     =~ s/\n+//g;
			$test2     =~ s/\t+//g;
			$test2     =~ s/\s+//g;

#-------------------------------------
#---if it is acis param, put it aside
#-------------------------------------

			unless ($test1 eq $test2){
				foreach $param3 (@acisarray){
					if ($name eq $param3){
						if($test2 eq ''){
							$aline = "$name changed from $blank2 to $new_value\n";
						}else{
							$aline = "$name changed from $old_value to $new_value\n";
						}
						push(@alines,$aline);
						$a++;
					}
				}
				if ($a == 0){
					if($test2 eq ''){
						print FILE "$name changed from $blank2 to $new_value\n";
					}else{
						print FILE "$name changed from $old_value to $new_value\n";
					}
					$j++;
				}
			}
		}

#---------------------
#------ time order case
#---------------------

		if($name =~ /TIME_ORDR/){
			for($j = 1; $j <= $time_ordr; $j++){
				foreach $tent ('WINDOW_CONSTRAINT', 'TSTART', 'TSTOP'){
					$new_entry = lc ($tent);
					$new_value = ${$new_entry}[$j];
					$old_entry = 'orig_'."$new_entry";
					$old_value = ${$old_entry}[$j];

					if($new_value ne $old_value){
						print FILE  "time_ordr= $j: ";
						if($old_value eq ''){
							print FILE  "$tent changed from $blank2 to $new_value\n";
						}else{
							print FILE  "$tent changed from $old_value to $new_value\n";
						}
					}
				}
			}
		}

#---------------------
#----- roll order cae
#---------------------

		if($name =~ /ROLL_ORDR/){
			for($j = 1; $j <= $roll_ordr; $j++){
				foreach $tent ('ROLL_CONSTRAINT', 'ROLL_180','ROLL', 'ROLL_TOLERANCE'){
					$new_entry = lc ($tent);
					$new_value = ${$new_entry}[$j];
					$old_entry = 'orig_'."$new_entry";
					$old_value = ${$old_entry}[$j];

					if($new_value ne $old_value){
						print FILE "roll_ordr= $j: ";
						if($old_value eq ''){
							print FILE "$tent changed from $blank2 to $new_value\n";
						}else{
							print FILE "$tent changed from $old_value to $new_value\n";
						}
					}
				}
			}
		}
							
#---------------------
#----RA and DEC cases
#---------------------

		if ($name eq "RA"){
			$ra = sprintf("%3.6f",$ra);
			unless ($ra == $orig_ra){
				#$ra      = $dra;
				$orig_ra = "$orig_dra";
				if($orig_ra eq ''){
					print FILE "$name changed from $blank2 to $ra\n";
				}else{
					print FILE "$name changed from $orig_ra to $ra\n";
				}
			}   
		}
		if ($name eq "DEC"){
			$dec = sprintf("%3.6f",$dec);
			unless ($dec == $orig_dec){
				#$dec = "$dec";
				$orig_dec = "$orig_ddec";
				if($orig_dec eq ''){
					print FILE "$name changed from $blank2 to $dec\n";
				}else{
					print FILE "$name changed from $orig_dec to $dec\n";
				}
			}   
		}
	}

#---------------------
#---- Acis param case
#---------------------

	print FILE "\n\nACIS CHANGES:\n";
	foreach $aline2 (@alines){
		print FILE "$aline2";
	}

#---------------------
#----Acis window cases
#---------------------

	print FILE "\n\nACIS WINDOW CHANGES:\n";
	
	for($j = 0; $j < $aciswin_no; $j++){
		$jj = $j + 1;
		foreach $tent ('ORDR', 'CHIP', #'INCLUDE_FLAG',
				       'START_ROW','START_COLUMN',
				       'HEIGHT','WIDTH','LOWER_THRESHOLD','PHA_RANGE',
				       'SAMPLE'){
			$new_entry = lc ($tent);
			$new_value = ${$new_entry}[$j];
			$old_entry = 'orig_'."$new_entry";
			$old_value = ${$old_entry}[$j];
			if($new_value ne $old_value){
				print FILE "acis window entry $jj: ";
				if($old_value eq ''){
					print FILE "$tent changed from $blank2 to $new_value\n";
				}else{
					print FILE "$tent changed from $old_value to $new_value\n";
				}
			}
		}
	}

    print FILE "\n------------------------------------------------------------------------------------------\n";
    print FILE "Below is a full listing of obscat parameter values at the time of submission,\nas well as new";
	print FILE " values submitted from the form.  If there is no value in column 3,\nthen this is an unchangable";
	print FILE " parameter on the form.\nNote that new RA and Dec will be slightly off due to rounding errors in";
	print FILE " double conversion.\n\n";
    print FILE "PARAM NAME          ORIGINAL VALUE        REQUESTED VALUE         ";
    print FILE "\n------------------------------------------------------------------------------------------\n";
	
#---------------------------------------------------------
#---- we want the log to always be in decimal degrees, so:
#---------------------------------------------------------

	foreach $nameagain (@paramarray){
		$lc_name   = lc ($nameagain);
		$old_name  = 'orig_'."$lc_name";
		$old_value = ${$old_name};

    		unless (($lc_name =~/TARGNAME/i) || ($lc_name =~/TITLE/i)
			|| ($lc_name =~ /^WINDOW_CONSTRAINT/i) || ($lc_name =~ /^TSTART/i) || ($lc_name =~/^TSTOP/i) 
			|| ($lc_name =~ /^ROLL_CONSTRAINT/i) || ($lc_name =~ /^ROLL_180/i)
			|| ($lc_name =~/^CHIP/i) || ($lc_name =~ /^INCLUDE_FLAG/i) || ($lc_name =~ /^START_ROW/i)
			|| ($lc_name =~/^START_COLUMN/i) || ($lc_name =~/^HEIGHT/i) || ($lc_name =~ /^WIDTH/i)
			|| ($lc_name =~/^LOWER_THRESHOLD/i) || ($lc_name =~ /^PHA_RANGE/i) || ($lc_name =~ /^SAMPLE/i)
			|| ($lc_name =~/^SITAG/i) || ($lc_name =~ /^ACISTAG/i) || ($lc_name =~ /^GENERALTAG/i)
			){

#----------------------
#----- time order case
#----------------------
			if($lc_name =~ /TIME_ORDR/i){
				$current_entry = ${$lc_name};
				print_param_line();
				for($j = 1; $j <= $time_ordr; $j++){
					$nameagain     = 'WINDOW_CONSTRAINT'."$j";
					$current_entry = $window_constraint[$j];
					$old_value     = $orig_window_constraint[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'TSTART'."$j";
					$current_entry = $tstart[$j];
					$old_value     = $orig_tstart[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'TSTOP'."$j";
					$current_entry = $tstop[$j];
					$old_value     = $orig_tstop[$j];
					check_blank_entry();
					print_param_line();
				}

#-----------------------
#------- roll order case
#-----------------------

			}elsif ($lc_name =~ /ROLL_ORDR/i){
				$current_entry = ${$lc_name};
				print_param_line();
				for($j = 1; $j <= $roll_ordr; $j++){
					$nameagain     = 'ROLL_CONSTRAINT'."$j";
					$current_entry = $roll_constraint[$j];
					$old_value     = $orig_roll_constraint[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'ROLL_180'."$j";
					$current_entry = $roll_180[$j];
					$old_value     = $orig_roll_180[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'ROLL'."$j";
					$current_entry = $roll[$j];
					$old_value     = $orig_roll[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'ROLL_TOLERANCE'."$j";
					$current_entry = $roll_tolerance[$j];
					$old_value     = $orig_roll_tolerance[$j];
					check_blank_entry();
					print_param_line();
				}

#----------------------
#---- window order case
#----------------------

			}elsif ($lc_name =~/^ACISWIN_ID/i){
				for($j = 0; $j < $aciswin_no; $j++){
					$jj = $j + 1;
					$nameagain     = 'ORDR'."$jj";
					$current_entry = $ordr[$j];
					$old_value     = $orig_ordr[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'CHIP'."$jj";
					$current_entry = $chip[$j];
					$old_value     = $orig_chip[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'INCLUDE_FLAG'."$jj";
					$current_entry = $include_flag[$j];
					$old_value     = $orig_include_flag[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'START_ROW'."$jj";
					$current_entry = $start_row[$j];
					$old_value     = $orig_start_row[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'START_COLUMN'."$jj";
					$current_entry = $start_column[$j];
					$old_value     = $orig_start_column[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'HEIGHT'."$jj";
					$current_entry = $height[$j];
					$old_value     = $orig_height[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'WIDTH'."$jj";
					$current_entry = $width[$j];
					$old_value     = $orig_width[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'LOWER_THRESHOLD'."$jj";
					$current_entry = $lower_threshold[$j];
					$old_value     = $orig_lower_threshold[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'PHA_RANGE'."$jj";
					$current_entry = $pha_range[$j];
					$old_value     = $orig_pha_range[$j];
					check_blank_entry();
					print_param_line();

					$nameagain     = 'SAMPLE'."$jj";
					$current_entry = $sample[$j];
					$old_value     = $orig_sample[$j];
					check_blank_entry();
					print_param_line();
				}
    		}elsif($lc_name =~ /\w/){
        		$current_entry = ${$lc_name};

			check_blank_entry();

    			print_param_line();
    		}else{
        		$current_entry = ${$old_name};

			check_blank_entry();

    			print_param_line();
    		}

#----------------------------------------
#----  devisions between different groups
#----------------------------------------

			if($nameagain eq 'EXTENDED_SRC' || $nameagain eq 'PHASE_END_MARGIN' ||
	   		   $nameagain eq 'Z_PHASE' || $nameagain eq 'TIMING_MODE' || 
	   		   $nameagain eq 'SPWINDOW'){
				print FILE "\n----------------------------\n";
			}
    	}
	}
	close FILE;

#-------------------------------------------------------------------------
#-----  create the "arnold line".  Will not be used later if not required
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#-----  get user, pad to be 8 characters
#-------------------------------------------------------------------------

	$nuser = $submitter;
	@chars = split ("", $nuser);
	$cnt   = $#chars;
	$pad   = 7 - $cnt;
	$y=0;
	if ($cnt < 7){
    		while ($y <= $pad){
			    $submitter = "$submitter ";
			    $y++;
    		}
	}
	$date =`date '+%Y-%m-%d'`;
	chop $date;
	$chips="$ccdi0_on$ccdi1_on$ccdi2_on$ccdi3_on$ccds0_on$ccds1_on$ccds2_on$ccds3_on$ccds4_on$ccds5_on";
	$subarrayframetime = $subarray_frame_time;
	$secondaryexpcount = $secondary_exp_count;
	$primaryexptime    = $primary_exp_time;
	$secondaryexptime  = $secondary_exp_time;
	$subarraystartrow  = $subarray_start_row;
	$subarrayrowcount  = $subarray_row_count;
	@arnoldarray=($subarrayframetime,$secondaryexpcount,$primaryexptime,$secondaryexptime,$subarraystartrow,$subarrayrowcount);
	$z=0;
	foreach $thing (@arnoldarray){
    		$thing = ($thing +0) unless ($thing =~/NULL/);
    		$thing = $arnoldarray[$z];
    		$z++;
	}
	@spwarray=(SPWINDOW, START_ROW, START_COLUMN, WIDTH, HEIGHT, LOWER_THRESHOLD, PHA_RANGE, SAMPLE);
	foreach $spwparam (@spwarray){
		$new_entry = lc($spwparam);
		$old_entry = 'orig_'."$new_entry";
		$new_value = ${$new_entry};
		$old_value = ${$old_entry};
    		unless ($new_value eq $old_value){
			    $spw = 1;
	    	}
	}

	open (ARNOLDFILE, ">$temp_dir/arnold.$sf");
	print ARNOLDFILE "$obsid\t$submitter$date\t$chips\t$exp_mode-$bep_pack\t$arnoldarray[0]\t$arnoldarray[1]\t";
    print ARNOLDFILE "$arnoldarray[2]\t$arnoldarray[3]\t$arnoldarray[4]\t$arnoldarray[5]\n";
	print ARNOLDFILE "\t\t\t\t\t\tSpatial window, see update page\n" if ($spw);
	close (ARNOLDFILE);
    }						#------ END OF GENERAL CASE IF CASE STARTED AROUND LINE 7662 ---------#
}

#########################################################################
## print_param_line: print out formatted parameter value line          ##
#########################################################################

sub print_param_line{
=comment
print out formatted parameter value line
input: $nameagain, $old_value, $current_entry
output: printed out line
=cut
    printf FILE "%-26s %-26s %-26s", $nameagain, $old_value, $current_entry;
    print  FILE "\n";
}

#########################################################################
### print out table row according to three different ways             ###
#########################################################################

sub print_table_row{
	($t_name, $o_value, $n_value, $color) = @_;
	
    if ($color eq ''){
        $color= '#FF0000'
    }
    if($o_value eq 'same'){
        $pline = "$pline"."<tr><th>$t_name</th><td style='text-align:center'>$n_value</td>";
        $pline = "$pline"."<td style='text-align:center;font-size:70%'>No Change</td></tr>";
    }elsif($o_value eq $blank){
        $pline = "$pline"."<tr style='color:$color'><th>$t_name</th><td style='text-align:center'>$blank</td>";
        $pline = "$pline"."<td style='text-align:center'>$n_value</td></tr>";
    }else{
        $pline = "$pline"."<tr style='color:$color'><th>$t_name</th><td style='text-align:center'>$o_value</td>";
        $pline = "$pline"."<td style='color:#FF0000;text-align:center'>$n_value</td></tr>";
    }
}

#########################################################################
### check "" and change it to <Blank> entry                          ####
#########################################################################

sub check_blank_entry{
	$ctest1 = $current_entry;
	$ctest1 =~ s/\n+//g;
	$ctest1 =~ s/\t+//g;
	$ctest1 =~ s/\s+//g;
	$ctest2 = $old_value;
	$ctest2 =~ s/\n+//g;
	$ctest2 =~ s/\t+//g;
	$ctest2 =~ s/\s+//g;

	if($ctest1 ne ''){ 
		if($ctest2 eq ''){
			$old_value = $blank2;
		}
	}
}

#########################################################################
### read_name: read descriptive name of database name		         ####
#########################################################################

sub read_name{
	open(FH, "$data_dir/name_list");
	@name_list = ();
	while(<FH>){
		chomp $_;
		@wtemp = split(/\t+/, $_);
		$ent   = "$wtemp[0]:$wtemp[1]";
		push(@name_list, $ent);
	}
	close(FH);
}

#########################################################################
### find_name: match database name to descriptive name    		      ###
#########################################################################

sub find_name{
	$web_name = '';
	$comp = uc ($db_name);
	OUTER:
	foreach $fent (@name_list){
		@wtemp  = split(/:/, $fent);
		$upname = uc ($wtemp[1]);
		if($comp eq $upname){
			$web_name = $wtemp[0];
			last OUTER;
		}
	}
}

####################################################################################
### oredit: update approved list, updates_list, updates data, and send out email ###
####################################################################################

sub oredit{
    (my $obsid, my $sf, my $pind) = @_;

	$date = `date '+%D'`;
	chop $date;
	$on = "ON";

#-------------------------------------------------
#-----  construct mail to dutysci and CUS archive
#-------------------------------------------------

#------------------
# get the contents
#------------------

	open (OSLOG, "<$temp_dir/$obsid.$sf");
	@oslog = <OSLOG>;
	close (OSLOG);

	open (FILE, ">$temp_dir/ormail_$obsid.$sf");

#--------------------------------------------------------------------------------
#-------if the submitter is non-cxc person, use email address given to the person
#--------------------------------------------------------------------------------

	$s_yes = 0;
	$s_cnt = 0;
		
#----------------------------------------------------------------------------------
#------ without printing everything, for the case of asis, remove, and clone cases 
#------ tell the CUS that these asis, remove or clone case. otherwise print all info
#----------------------------------------------------------------------------------

	if($asis =~ /ASIS/){
		print FILE 'Submitted as "AS IS"---Observation'."  $obsid". ' is added to the approved list',"\n";

	}elsif($asis =~/REMOVE/){
        $schk = sp_list_test($split_list);
        if($$schk == 1){
            @t_out = split_string_to_list($split_list, $obsid);
            $aline = "$obsid";
            foreach $oent (@t_out){
                $aline = "$aline"." "."$oent";
            }
            print FILE 'Submitted as "REMOVE"--Observation'."  $aline";
            print FILE ' are removed from the approved list',"\n";
        }else{
            print FILE 'Submitted as "REMOVE"--Observation'."  $obsid";
            print FILE ' is removed from the approved list',"\n";
        }

	}elsif($asis =~ /CLONE/){
		print FILE 'Submitted as "CLONE"-- Clone observation: '."$obsid\n";
		print FILE "\nExplanation: $comments\n";

	}else{
		foreach $ent (@paramarray){
			unless($ent =~ /ACISTAG/ || $ent =~ /ACISWINTAG/ || $ent =~ /SITAG/ || $ent =~ /GENERALTAG/){
				$new_entry = lc ($ent);
				$new_value = ${$new_entry};
				$old_entry = 'orig_'."$new_entry";
				$old_value = ${$old_entry};
				$test1 = $new_value;
				$test2 = $old_value;
				$test1 =~ s/\n+//g;
				$test1 =~ s/\t+//g;
				$test1 =~ s/\s+//g;
				$test2 =~ s/\n+//g;
				$test2 =~ s/\t+//g;
				$test2 =~ s/\s+//g;

				if($test1 ne $test2){
					change_old_value_to_blank();
					print FILE "$ent $old_value\:\:$new_value\n";
#
#--- if this is for the base obsid case, save the changed param names and values
#--- for the later use.
#
                    if($pbase == 1){
                        $base_entry = 'base_'."$new_entry";
                        ${$base_entry} = $new_value;
                        push(@base_list, $new_entry);
                    }
				}
			}

#--------------------
#---- time order case
#--------------------

			if($ent =~ /TIME_ORDR/){
				for($j = 1; $j <= $time_ordr; $j++){
                    $jj = $j;
					foreach $tent ('WINDOW_CONSTRAINT', 'TSTART', 'TSTOP'){
                        $tname = 'TIME_ORDR';
                        update_order_case($tent, $j, $chk=0);
					}
				}
			}

#--------------------
#--- roll order case
#--------------------

			if($ent =~ /ROLL_ORDR/){
				for($j = 1; $j <= $roll_ordr; $j++){
                    $jj = $j;
					foreach $tent ('ROLL_CONSTRAINT', 'ROLL_180','ROLL', 'ROLL_TOLERANCE'){
                        $tname = 'ROLL_ORDR';
                        update_order_case($tent, $j, $chk=0);
					}
				}
                $chk = find_rank(@r_const);
                if($chk > 0){
                    $roll_flag  = 'Y';
                    $droll_flag = 'YES';
                }
			}
	
#---------------------
#--- acis window case
#---------------------

			if($ent eq "ACISWIN_NO"){
				for($j = 0; $j <  $aciswin_no; $j++){
                    $jj = $j + 1;
					foreach $tent ('ORDR', 'CHIP', 'START_ROW','START_COLUMN',
							       'HEIGHT','WIDTH','LOWER_THRESHOLD','PHA_RANGE',
							       'SAMPLE'){
                        $tname = 'Entry';
                        update_order_case($tent, $j, $chk=1);
					}
				}
			}
		}
	}

	print FILE "\n\n";
	print FILE "------------------------------------------------------------------------------------------\n";
	print FILE "\n\n";

	print FILE "@oslog";

	close FILE;
#
#--- external sub to complete oredit task; this may reduce the chance that this cgi 
#--- script stack in unresponsive browser
#
	$asis_ind = param('ASIS');

	if($generaltag eq ''){
		$generaltag = 'OFF';
	}
	if($acistag eq ''){
		$acistag    = 'OFF';
	}
	if($sitag eq ''){
		$sitag      = 'OFF';
	}

	$test = `ls $temp_dir/$obsid.$sf`;           #--- testing whether the data actually exits.

	if($test =~ /$obsid.$sf/){
        $asis = $asis_ind;
    	oredit_sub($obsid, $sf);
	}
    
    $cmd = 'rm -rf '."$temp_dir/$obsid".'*';
    system($cmd);

#----------------------------------------------
#----  if it hasn't died yet, then close nicely
#----------------------------------------------

    if ($pind == 1){
        print "<p><strong>Thank you.  Your request has been submitted. ";
        print "Approvals occur immediately, changes may take 48 hours. </strong></p>";
    
        $schk = sp_list_test($split_list);
        if($schk == 1 && $asis ne "CLONE"){
            print "<p>Please make sure that all your obsids submitted are logged, ";
            print "either by checking emails you received, or going to: <br>";
            print "<a href='https://icxc.harvard.edu/mta/CUS/Usint/orupdate.cgi'>";
            print "<i>Target Parameter Update Status Form</i> Page.</p>";
        }
    
	    print "<A HREF=\"https://cxc.cfa.harvard.edu/cgi-bin/target_search/search.html\">";
        print "Go Back to Search  Page</a>";
    }
}

#####################################################################################
#####################################################################################
#####################################################################################

sub update_order_case{

    (my $tent, my $j, my $chk) = @_;

	$new_entry = lc ($tent);
	$new_value = ${$new_entry}[$j];
	$old_entry = 'orig_'."$new_entry";
	$old_value = ${$old_entry}[$j];
    $jj = $j + $chk;


	if($new_value ne $old_value){

	    change_old_value_to_blank();

		print FILE "\t$tname  $jj   $tent $old_value\:\:$new_value\n";
        if($pbase == 1){
            $n_name        = "$new_entry".'.'."$jj";
            $base_entry    = 'base_'."$n_name";
            ${$base_entry} = $new_value;
            push(@base_list, $n_name);
        }
    }
}

#####################################################################################
#####################################################################################
#####################################################################################

sub change_old_value_to_blank{

	$stest = $old_value;
	$stest =~ s/\n+//g;
	$stest =~ s/\t+//g;
	$stest =~ s/\s+//g;

	if($stest eq ''){
		$old_value = $blank2;
	}
}

#####################################################################################
### mod_time_format: convert and devide input data format                         ###
#####################################################################################

sub mod_time_format{
	@tentry = split(/\W+/, $input_time);
	$ttcnt  = 0;
	foreach (@tentry){
		$ttcnt++;
	}
	
	$hr_add = 0;
	if($tentry[$ttcnt-1] eq 'PM' || $tentry[$ttcnt-1] eq 'pm'){
		$hr_add = 12;
		$ttcnt--;
	}elsif($tentry[$ttcnt-1] eq 'AM' || $tentry[$ttcnt-1] eq'am'){
		$ttcnt--;
	}elsif($tentry[$ttcnt-1] =~/PM/){
		$hr_add       = 12;
		@tatemp       = split(/PM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];
	}elsif($tentry[$ttcnt-1] =~/pm/){
		$hr_add       = 12;
		@tatemp       = split(/pm/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];
	}elsif($tentry[$ttcnt-1] =~ /AM/){
		@tatemp       = split(/AM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];
	}elsif($tentry[$ttcnt-1] =~ /am/){
		@tatemp       = split(/AM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];
	}
	
	$mon_lett = 0;
	if($tentry[0]  =~ /\D/){
		$day   = $tentry[1];
		$month = $tentry[0];
		$year  = $tentry[2];
		$mon_lett = 1;
	}elsif($tentry[1] =~ /\D/){
		$day   = $tentry[0];
		$month = $tentry[1];
		$year  = $tentry[2];
		$mon_lett = 1;
	}elsif($tentry[0] =~ /\d/ && $tentry[1] =~ /\d/){
		$day   = $tentry[0];
		$month = $tentry[1];
		$year  = $tentry[2];
	}	
	
	$day = int($day);
	if($day < 10){
		$day = '0'."$day";
	}
	
	if($mon_lett > 0){
        $out   = change_lmon_to_nmon($month);
        $mohth = adjust_digit($out);
	}
	
	@btemp = split(//, $year);
	$yttcnt = 0;
	foreach(@btemp){
		$yttcnt++;
	}
	if($yttcnt < 3){
		if($year > 39){
			$year = '19'."$year";
		}else{
			$year = '20'."$year";
		}
	}
		
	if($ttcnt == 4){
		$hr = $tentry[3];
		unless($hr eq '12' && $hr_add == 12){
			if($hr eq '12' && $hr_add == 0){
				$hr = 0;
			}
			$hr  = $hr + $hr_add;
			$hr  = int($hr);
			if($hr < 10){
				$hr = '0'."$hr";
			}
		}
		$min = '00';
		$sec = '00';
	}elsif($ttcnt == 5){
		$hr = $tentry[3];
		unless($hr eq '12' && $hr_add == 12){
			if($hr eq '12' && $hr_add == 0){
				$hr = 0;
			}
			$hr  = $hr + $hr_add;
			$hr  = int($hr);
			if($hr < 10){
				$hr = '0'."$hr";
			}
		}
		$min = $tentry[4];
		$min = int($min);
		if($min < 10){
			$min = '0'."$min";
		}
		$sec = '00';
	}elsif($ttcnt == 6){
		$hr = $tentry[3];
		unless($hr eq '12' && $hr_add == 12){
			if($hr eq '12' && $hr_add == 0){
				$hr = 0;
			}
			$hr = $hr + $hr_add;
			$hr = int($hr);
			if($hr < 10){
				$hr = '0'."$hr";
			}
		}
		$min = $tentry[4];
		$min = int($min);
		if($min < 10){
			$min = '0'."$min";
		}
		$sec = $tentry[5];
		$sec = int($sec);
		if($sec < 10){
			$sec = '0'."$sec";
		}
	}
	
	$time = "$hr".":$min".":$sec";
}

####################################################################
####################################################################
####################################################################

sub change_lmon_to_nmon{
    my $lmon, $lyear, $month, $add;
    my @m_list = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec');
    my @n_list = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334);

    my @values = @_;
     $lmon = $values[0];
    if(scalar @values > 1){
        $lyear = $value[1];
    }else{
        $lyear = 'NA';
    }

    for($i = 0; $i< 12; $i++){
        if($lmon =~ /$m_list[$i]/i){
            $month = $i + 1;
            $add   = $n_list[$i];
            last;
        }
    }

    if($lyear ne 'NA'){
        $ychk = is_leap_year($lyear);
        if($ychk == 1){
		    if($month > 2){
			    $add++;
		    }
	    }
        return ($month, $add);
    }else{
        return $month;
    }
}

####################################################################
####################################################################
####################################################################

sub adjust_digit{
    my $vlen   = 2;

    my @values = @_;
    my $val    = int($values[0]);
    if(scalar @values > 1){
        $vlen = $values[1];
    }
    $start = length($val);
    for($i= $start; $i < $vlen; $i++){
        $val ='0'."$val";
    }

    return $val;
}

####################################################################
####################################################################
####################################################################

sub nmon_to_lmon{

    my @m_list = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec');
    (my $nmon) = @_;

    return $m_list[$nmon-1];
}

####################################################################
### series_rev: getting mointoring observation things           ####
####################################################################

sub series_rev{

#--------------------------------------------------------------
#--- this one and the next subs are taken from target_param.cgi
#--- written by Mihoko Yukita.(10/28/2003)
#--------------------------------------------------------------

 	push @monitor_series, $_[0];
 	my @partial_series;
 	$sqlh1 = $dbh1->prepare(qq(select
      	pre_id from target where obsid = $_[0]));
     	$sqlh1->execute();
 	my $row;
	
 	while ($row = $sqlh1->fetchrow){
	  	return if (! $row =~ /\d+/);
      	push @partial_series, $row;
      	$sqlh2 = $dbh1->prepare(qq(select
           	obsid from target where pre_id = $row));
      	$sqlh2->execute();
      	my $new_row;

      	while ($new_row = $sqlh2->fetchrow){
      		if ($new_row != $_[0]){
          		&series_fwd($new_row);
      		}
      	}
      	$sqlh2->finish;
 	}
 	$sqlh1->finish;

 	$skip = 0;
 	OUTER:
 	foreach $ent (@monitor_series){
   		foreach $comp (@partial_series){
       		if($ent == $comp){
           		$skip = 1;
           		last OUTER;
       		}
   		}
 	}

 	if($skip == 0){
 		foreach $monitor_elem (@partial_series) {
      		&series_rev($monitor_elem);
 		}
 	}
}

####################################################################
### series_fwd: getting monitoring observation things           ####
####################################################################

sub series_fwd{
 	push @monitor_series, $_[0];
 	my @partial_series;
 	$sqlh1 = $dbh1->prepare(qq(select
      	obsid from target where pre_id = $_[0]));
     	$sqlh1->execute();
 	my $row;

 	while ($row = $sqlh1->fetchrow){
      	push @partial_series, $row;
      	$sqlh2 = $dbh1->prepare(qq(select
           	pre_id from target where obsid = $row));
      	$sqlh2->execute();
      	my $new_row;

      	while ($new_row = $sqlh2->fetchrow){
      		if ($new_row != $_[0]){
          		&series_rev($new_row);
      		}
      	}
      	$sqlh2->finish;
 	}
 	$sqlh1->finish;

 	$skip = 0;
 	OUTER:
 	foreach $ent (@monitor_series){
    	foreach $comp (@partial_series){
        	if($ent == $comp){
            	$skip = 1;
            	last OUTER;
        	}
    	}
 	}

 	if($skip == 0){
    	foreach $monitor_elem (@partial_series) {
        	&series_fwd($monitor_elem);
    	}
 	}
}

######################################################################
### find_planned_roll: get planned roll from mp web page          ####
######################################################################

sub find_planned_roll{

    open(PFH, "$obs_ss/mp_long_term");
    OUTER:
    while(<PFH>){
		chomp $_;
		@ptemp = split(/:/, $_);
    	%{planned_roll.$ptemp[0]} = (planned_roll =>["$ptemp[1]"], planned_range =>["$ptemp[2]"]);
    }
    close(PFH);
}

#####################################################################
### rm_from_approved_list: remove entry from approved list        ###
#####################################################################

sub rm_from_approved_list{

    @temp_app = ();

	open(FH, "$ocat_dir/approved");

#---------------------------------------------------------------
#---- read data, store it except the one which we need to remove
#---------------------------------------------------------------

    OUTER:
    while(<FH>){
        chomp $_;
        @atemp = split(/\t/,$_);
        if($atemp[0] =~ /$obsid/){
            next OUTER;
        }else{
            push(@temp_app, $_);
        }
    }
    close(FH);

	system("mv $ocat_dir/approved $ocat_dir/approved~");

#-----------------------------------
#--- print out the new approved list
#-----------------------------------

	open(AOUT, ">$ocat_dir/approved");

    foreach $ent (@temp_app){
        print AOUT "$ent\n";
    }
    close(AOUT);
    system("chmod 644 $ocat_dir/approved");
}

#######################################################################################
### send_email_to_mp: sending email to MP if the obs is in an active OR list        ###
#######################################################################################

sub send_email_to_mp{

#
#--- check whether there are parameter changes for other obsids
#   
    $schk = sp_list_test($split_list);
    if ($schk == 1){
        @tobs_list = split_string_to_list($split_list, $obsid);
        unshift(@tobs_list, $obsid);
        $tchk = 1;
    }else{
        @tobs_list = ($obsid);
        $tchk = 0;
    }
#
#---- start printing the email to MP
#
    $temp_file = "$temp_dir/mp_request";
    open(ZOUT, ">$temp_file");
    
    print ZOUT "\n\nA user: $submitter submitted changes of  ";
    print ZOUT "OBSID: $obsid which is in the current OR list.\n";
    if($tchk > 0){
        print ZOUT "The user also submitted related obsids with the same parameter changes.\n";
        print ZOUT "OBSIDS: $split_list\n";
    }   
    print ZOUT "\n";
    
    print ZOUT "The contact email_address address is: $email_address\n\n";
    
    if($tchk == 0){
        print ZOUT "Its Ocat Data Page is:\n";
    }else{
        print ZOUT "Their Ocat Data Page are:\n";
    }
    foreach $tobsid (@tobs_list){
        print ZOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?$tobsid";
        $mchk = 0;
        foreach $mtest (@mp_scheduled_list){
            if($tobsid eq $mtest){
                print ZOUT "\t in OR list\n";
                $mchk = 1;
                last;
            }
        }
        if($mchk == 0){
            print ZOUT "\n";
        }
    }
    print ZOUT "\n\n";

    print ZOUT "If you like to see what were changed:\n";

    foreach $tobsid (@tobs_list){   
        ($file_name, $la) = find_latest_rev($tobsid, @u_list);
         $file_name       = increment_obidrev($file_name, $tobsid);
        print ZOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?$file_name\n";
    }
    print ZOUT "\n\n";

	print ZOUT "If you have any question about this email, please contact ";
	print ZOUT "bwargelin\@head.cfa.harvard.edu.","\n\n\n";
#
#--- today's date
#
	($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	$uyear = 1900 + $year;
	
	if($mon < 10){
    	$mon = '0'."$mon";
	}
	
	$mon++;
	if($mday < 10){
    	$mday = '0'."$mday";
	}
	
	$date = "$mon/$mday/$uyear";
	
	print ZOUT  "$date\n";
	close(ZOUT);
#
#--- find out who is the mp contact person for this obsid
#

	open(IN, "$obs_ss/scheduled_obs_list");
	OUTER:
	while(<IN>){
		chomp $_;
		@mtemp = split(/\s+/, $_);
		if($obsid == $mtemp[0]){
			$mp_contact = $mtemp[1];
			last OUTER;
		}
	}
	close(IN);
	

	if($usint_on =~ /test/){
        $cmd = "cat $temp_file | mailx -s\"Subject:TEST!! Change to ";
        $cmd = "$cmd"."Obsid $obsid Which Is in Active OR List ($mp_email)\" $test_email";
		system($cmd);
	}else{
        $cmd = "cat $temp_file | mailx -s\"Subject: Change to Obsid $obsid ";
        $cmd = "$cmd"."Which Is in Active OR List\"  $mp_email cus\@head.cfa.harvard.edu";
		system($cmd);
	}

	system("rm $temp_file");
}


#######################################################################################
### send_email_to_cdo sending email to CDO if there are CDO warning                 ###
#######################################################################################

sub send_email_to_cdo{

#
#--- check whether there are parameter changes for other obsids
#   
    $schk = sp_list_test($split_list);
    if ($schk == 1){
        @tobs_list = split_string_to_list($split_list, $obsid);
        unshift(@tobs_list, $obsid);
        $tchk = 1;
    }else{
        @tobs_list = ($obsid);
        $tchk = 0;
    }
#
#---- start printing the email to CDO
#
    $temp_file = "$temp_dir/cdo_request";
    open(ZOUT, ">$temp_file");
    
    print ZOUT "\n\nA user: $submitter submitted changes of  ";
    print ZOUT "OBSID: $obsid which requires CDO permissions.\n";
    if($tchk > 0){
        print ZOUT "The user also submitted related obsids with the same parameter changes.\n";
        print ZOUT "OBSIDS: $split_list\n";
    }   
    print ZOUT "\n";
    
    print ZOUT "The contact email_address address is: $email_address\n\n";
    
    if($tchk == 0){
        print ZOUT "Its Ocat Data Page is:\n";
    }else{
        print ZOUT "Their Ocat Data Page are:\n";
    }
    foreach $tobsid (@tobs_list){
        print ZOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?$tobsid";
        print ZOUT "\n";
    }
    print ZOUT "\n";

    print ZOUT "The user requested the following change(s):\n\n";

    print ZOUT "$cdo_notes";

    print ZOUT "\n\n";

    print ZOUT "If you like to see what else were changed:\n";

    foreach $tobsid (@tobs_list){   
        ($file_name, $la) = find_latest_rev($tobsid, @u_list);
         $file_name       = increment_obidrev($file_name, $tobsid);
        print ZOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?$file_name\n";
    }
    print ZOUT "\n\n";

	print ZOUT "If you have any question about this email, please contact ";
	print ZOUT "bwargelin\@head.cfa.harvard.edu.","\n\n\n";
#
#--- today's date
#
	($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	$uyear = 1900 + $year;
	
	if($mon < 10){
    	$mon = '0'."$mon";
	}
	
	$mon++;
	if($mday < 10){
    	$mday = '0'."$mday";
	}
	
	$date = "$mon/$mday/$uyear";
	
	print ZOUT  "$date\n";
	close(ZOUT);

	if($usint_on =~ /test/){
        $cmd = "cat $temp_file | mailx -s\"Subject:TEST!! Change to ";
        $cmd = "$cmd"."Obsid $obsid Which Requires CDO Approval ($cdo_email)\" $test_email";
		system($cmd);
	}else{
        $cmd = "cat $temp_file | mailx -s\"Subject: Change to Obsid $obsid ";
        $cmd = "$cmd"."Which Requires CDO Approval\"  $cdo_email cus\@head.cfa.harvard.edu";
		system($cmd);
	}

	system("rm $temp_file");
}

#######################################################################################
### send_email_to_mp: sending email to MP if there are MP warning                   ###
#######################################################################################

sub send_email_to_mp{
#
#--- check whether there are parameter changes for other obsids
#   
    $schk = sp_list_test($split_list);
    if ($schk == 1){
        @tobs_list = split_string_to_list($split_list, $obsid);
        unshift(@tobs_list, $obsid);
        $tchk = 1;
    }else{
        @tobs_list = ($obsid);
        $tchk = 0;
    }
#
#---- start printing the email to MP 
#
    $temp_file = "$temp_dir/mp_request";
    open(ZOUT, ">$temp_file");
    
    print ZOUT "\n\nA user: $submitter submitted changes:\n  ";
    print ZOUT "$mp_notes";
    print ZOUT "\nin OBSID: $obsid.\n";
    if($tchk > 0){
        print ZOUT "The user also submitted related obsids with the same parameter changes.\n";
        print ZOUT "OBSIDS: $split_list\n";
    }   
    print ZOUT "\n";
    
    print ZOUT "The contact email_address address is: $email_address\n\n";
    
    if($tchk == 0){
        print ZOUT "Its Ocat Data Page is:\n";
    }else{
        print ZOUT "Their Ocat Data Page are:\n";
    }
    foreach $tobsid (@tobs_list){
        print ZOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?$tobsid";
        print ZOUT "\n";
    }

    print ZOUT "\n\n";

    print ZOUT "If you like to see what else were changed:\n";

    foreach $tobsid (@tobs_list){   
        ($file_name, $la) = find_latest_rev($tobsid, @u_list);
         $file_name       = increment_obidrev($file_name, $tobsid);
        print ZOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?$file_name\n";
    }
    print ZOUT "\n\n";

	print ZOUT "If you have any question about this email, please contact ";
	print ZOUT "bwargelin\@head.cfa.harvard.edu.","\n\n\n";
#
#--- today's date
#
	($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	$uyear = 1900 + $year;
	
	if($mon < 10){
    	$mon = '0'."$mon";
	}
	
	$mon++;
	if($mday < 10){
    	$mday = '0'."$mday";
	}
	
	$date = "$mon/$mday/$uyear";
	
	print ZOUT  "$date\n";
	close(ZOUT);

	if($usint_on =~ /test/){
        $cmd = "cat $temp_file | mailx -s\"Subject:TEST!! Change to ";
        $cmd = "$cmd"."Obsid $obsid Which Requires MP Approval ($mp_email)\" $test_email";
		system($cmd);
	}else{
        $cmd = "cat $temp_file | mailx -s\"Subject: Change to Obsid $obsid ";
        $cmd = "$cmd"."Which Requires MP Approval\"  $mp_email cus\@head.cfa.harvard.edu";
		system($cmd);
	}

	system("rm $temp_file");
}

####################################################################################
### oredit_sub: external part of oredit; a part ocatdata2html.cgi                ###
####################################################################################

sub oredit_sub{
    (my $obsid, my $sf) = @_;

	$date = `date '+%D'`;
	chop $date;
	$on = "ON";

#-------------------------------------------------
#-----  construct mail to dutysci and CUS archive
#-------------------------------------------------

#------------------
# get the contents
#------------------

	open (OSLOG, "<$temp_dir/$obsid.$sf");
	@oslog = <OSLOG>;
	close (OSLOG);

#-----------------------------
#-----  couple temp variables
#-----------------------------

    	$dutysci_status = "NA";

	if ($asis =~ /ASIS/){

#-----------------------------------------------------
#---- asis case; we need to update the approved list
#-----------------------------------------------------

    	$general_status = "NULL";			#--- these are for the status verification page
    	$acis_status    = "NULL";			#--- orupdate.cgi
    	$si_mode_status = "NULL";
    	$hrc_si_mode_status = "NULL";       #--- UPDATED 06/23/21!!!!!

    	$dutysci_status = "$dutysci $date";

		open(ASIN, "$ocat_dir/approved");

		@temp_data = ();

		while(<ASIN>){
			chomp $_;
			push(@temp_data,$_);
		}
		close(ASIN);

		system("mv $ocat_dir/approved $ocat_dir/approved~");

		open(ASIN,">$ocat_dir/approved");

		NEXT:
		foreach $ent (@temp_data){
			@atemp = split(/\t/,$ent);
			if($atemp[0] eq "$obsid"){
				next NEXT;
			}else{
				print ASIN "$ent\n";
			}
		}

		print ASIN "$obsid\t$seq_nbr\t$dutysci\t$date\n";
		close(ASIN);
		system("chmod 644 $ocat_dir/approved");

	} elsif ($asis =~ /REMOVE/){

#------------------------------------------------------------------
#-----  remove; we need to remove this obs data from approved list
#------------------------------------------------------------------

    	$general_status = "NULL";
    	$acis_status    = "NULL";
    	$si_mode_status = "NULL";
    	$hrc_si_mode_status = "NULL";
		$dutysci_status = "$dutysci $date";
		@temp_app       = ();

		open(FH, "$ocat_dir/approved");

		OUTER:
		while(<FH>){
			chomp $_;
			@atemp = split(/\t/,$_);
			if($atemp[0] =~ /$obsid/){
				next OUTER;
			}else{
				push(@temp_app, $_);
			}
		}
		close(FH);

		system("mv $ocat_dir/approved $ocat_dir/approved~");

		open(AOUT,">$ocat_dir/approved");

		foreach $ent (@temp_app){
			print AOUT "$ent\n";
		}
		close(AOUT);
		system("chmod 644 $ocat_dir/approved");

	} elsif ($asis =~/CLONE/){

#-----------------------------------------------------
#---- clone case; no need to update the approved list; 
#---  so just set param for the verification page
#-----------------------------------------------------

		$general_status = "NA";
		$acis_status    = "NULL";
		$si_mode_status = "NULL";
		$hrc_si_mode_status = "NULL";

	} else {

#-----------------
#---- general case
#-----------------

        if($hrc_si_select eq 'yes'){
            $general_status = "NULL";
            $acis_status    = "NULL";
            $si_mode_status = "NULL";
            $hrc_si_mode_status = "NA";
        } else {

#------------------------------------------------------
#---- check and update params for the verification page
#------------------------------------------------------

		    if ($generaltag =~/ON/){
			    $general_status = "NA";
		    } else {
			    $general_status = "NULL";
		    }
		    if ($acistag =~/ON/ && $instrument =~ /ACIS/i){
			    $acis_status        = "NA";
			    $si_mode_status     = "NA";
                $hrc_si_mode_status = "NULL";
		    } else {
			    $acis_status        = "NULL";
                $si_mode_status     = "NULL";
                $hrc_si_mode_status = "NULL";
                if($instrument =~ /HRC/){           #---- UPDATED 06/23/21!!!! (see hrc_si_mode_status)
                    if(($hrc_si_mode eq '') || ($hrc_si_mode =~ /NULL/) 
                             || ($hrc_si_mode =~ /DEFAULT/)){
                        $hrc_si_mode_status = 'NULL';

                    }elsif($orig_hrc_si_mode eq $hrc_si_mode){

                        $hrc_si_mode_status = 'NULL'
                    }else{
                        $hrc_si_mode_status = 'NA';
                    }
			    }elsif ($si_mode =~/NULL/){

				    $si_mode_status = "NA";
			    } else {
    
				    if ($sitag =~/ON/){
					    $si_mode_status = "NA";
				    } else {
					    $si_mode_status = "NULL";
				    }
			    }
		    }
        }
	}

#------------------------------------------------------
#-----  (scan for updates directory) read updates_table.list
#-----  find the revision number for obsid in question
#------------------------------------------------------

	system("cat  $ocat_dir/updates_table.list |grep $obsid > $temp_dir/utemp");
	open(UIN, "$temp_dir/utemp");
	@usave = ();
	$ucnt  = 0;
	while(<UIN>){
		chomp $_;
		@utemp = split(/\s+/, $_);
		@vtemp = split(/\./, $utemp[0]);
		$i_val = int ($vtemp[1]);
		push(@usave, $i_val);
		$ucnt++;
	}
	close(UIN);
	system("rm  $temp_dir/utemp");
	
	@usorted = sort{$a<=>$b} @usave;
	$rev     = int($usorted[$ucnt-1]);
	$rev++;

	if ($rev < 10){
    	$rev = "00$rev";
	} elsif (($rev >= 10) && ($rev < 100)){
    	$rev = "0$rev";
	}

#-------------------------------------
#----  get master log file for editing
#-------------------------------------

	$lpass    = 0;
	$wtest    = 0;
	my $efile = "$ocat_dir/updates_table.list";
	OUTER:
	while($lpass == 0){
		open(my $update, '>>', $efile) or die "Locked";
		if($@){
#
#--- wait 2 cpu seconds before attempt to check in another round
#
			print "Database access is not available... wating a permission<br />";

			$diff  = 0;
			$start = (times)[0];
			while($diff < 2){
				$end  = (times)[0];
				$diff = $end - $start;
			}
	
			$wtest++;
			if($wtest > 5){
				print "Something is wrong in the submission. Terminating the process.<br />";
				exit();
			}
		}else{
			$lpass = 1;

#--------------------------------------------------------------------------------------------------
#----  if it is not being edited, write update updates_table.list---data for the verificaiton page
#--------------------------------------------------------------------------------------------------

			flock($update, LOCK_EX) or die "died while trying to lock the file<br />\n";	
			print $update "$obsid.$rev\t$general_status\t$acis_status\t";
            print $update "$si_mode_status\t$hrc_si_mode_status\t";         #--- UPDATED 06/23/21!!!!
            print $update "$dutysci_status\t$seq_nbr\t$dutysci\n";
 			close $update;

#---------------------
#----  checkin update
#---------------------

			$chk = "$obsid.$rev";
			$in_test = `cat $ocat_dir/updates_table.list`;
			if($in_test =~ /$chk/i){

#-----------------------------------------------------
#----  copy the revision file to the appropriate place
#-----------------------------------------------------

				system("cp $temp_dir/$obsid.$sf  $ocat_dir/updates/$obsid.$rev");
	
				last OUTER;
			}
		}
	}

#---------------------------#
#----  send messages  ------#
#---------------------------#


	if($asis_ind =~ /ASIS/i){

		if($sp_user eq 'no'){
			open(ASIS, ">$temp_dir/asis.$sf");
			print ASIS "$obsid is approved for flight. Thank you \n";
			close(ASIS);

			if($usint_on =~ /test/){
                $cmd = "cat $temp_dir/asis.$sf| tr -d '\015'  |mailx -s\"Subject:TEST!!  ";
                $cmd = "$cmd"."$obsid is approved\" $test_email";
				system($cmd);
			}else{
                $cmd = "cat $temp_dir/asis.$sf| tr -d '\015'  |mailx -s\"Subject: ";
                $cmd = "$cmd"."$obsid is approved\" -c$cus_email $email_address";
				system($cmd);
			}
			system("rm $temp_dir/asis.$sf");
		}else{
			if($usint_on =~ /test/){
                $cmd = "cat $temp_dir/ormail_$obsid.$sf| tr -d '\015'  |mailx -s\"Subject:TEST!! ";
                $cmd = "$cmd"."Parameter Changes (Approved) log  $obsid.$rev\" $test_email";
				system($cmd);
			}else{
                $cmd = "cat $temp_dir/ormail_$obsid.$sf| tr -d '\015'  |mailx -s\"Subject: ";
                $cmd = "$cmd"."Parameter Changes (Approved) log  $obsid.$rev\" -c$cus_email $email_address";
				system($cmd);
			}
		}

	}else{
		if($sp_user eq 'no'){
			open(USER, ">$temp_dir/user.$sf");
			print USER "Your change request for obsid $obsid have been received.\n";
			print USER "You will be notified when the changes have been made.\n";
			close(USER);

			if($usint_on =~ /test/){
                $cmd = "cat $temp_dir/user.$sf| tr -d '\015'  |mailx -s\"Subject:TEST!!  ";
                $cmd = "$cmd"."Parameter Changes log  $obsid.$rev\n\"  $test_email";
				system($cmd);
			}else{
                $cmd = "cat $temp_dir/user.$sf| tr -d '\015'  |mailx -s\"Subject: ";
                $cmd = "$cmd"."Parameter Changes log  $obsid.$rev\"  -c$cus_email $email_address";
				system($cmd);
			}
			system("rm $temp_dir/user.$sf");
		}else{
			if($usint_on =~ /test/){
                $cmd = "cat $temp_dir/ormail_$obsid.$sf| tr -d '\015'  |mailx -s\"Subject:TEST!! ";
                $cmd = "$cmd"."Parameter Changes log  $obsid.$rev\" $test_email";
				system($cmd);
			}else{
                $cmd = "cat $temp_dir/ormail_$obsid.$sf| tr -d '\015'  |mailx -s\"Subject: ";
                $cmd = "$cmd"."Parameter Changes log  $obsid.$rev\" -c$cus_email  $email_address";
				system($cmd);
			}
		}

		if($usint_on =~ /test/){
            $cmd = "cat $temp_dir/ormail_$obsid.$sf| tr -d '\015'  |mailx -s\"Subject:TEST!! ";
            $cmd = "$cmd"."Parameter Changes log  $obsid.$rev\" $test_email";
			system($cmd);
		}else{
            $cmd = "cat $temp_dir/ormail_$obsid.$sf| tr -d '\015'  |mailx -s\"Subject: ";
            $cmd = "$cmd"."Parameter Changes log  $obsid.$rev\" $cus_email";
			system($cmd);
		}
#
#--- sending hrc si mode change email
#
        if (($instrument =~ /HRC/i) && ($hrc_si_mode ne $orig_hrc_si_mode)){
            $schk = sp_list_test($split_list);
            if($schk == 1){
                @si_obs_list = split_string_to_list($split_list, $obsid);
                push(@si_obs_list, $obsid);
            }else{
                @si_obs_list = ($obsid);
            }

            if($asis eq "NORM" || $asis eq ''){
                foreach $tobsid (@si_obs_list){
                    $hrc_si_file = "$tobsid".'hrc_si_mode';
                    open(HOUT, ">$temp_dir/$hrc_si_file");
                    print HOUT "Obsid: $tobsid HRC SI Mode Check is requested. SI Mode: $hrc_si_mode\n";
                    print HOUT "If it is OK, please sign off si mode column on ";
                    print HOUT "https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi.\n";
                    close(HOUT);
                    if($usint_on =~ /test/){
                        $cmd = "cat $temp_dir/$hrc_si_file |mailx -s\"Subject: ";
                        $cmd = "$cmd"."TEST!! HRC SI Mode Check Requested (Obsid: $tobsid)\" ";
                        $cmd = "$cmd"."$test_email";
                        system($cmd);
                    }else{
                        $cmd = "cat $temp_dir/$hrc_si_file |$mailx -s\"Subject: ";
                        $cmd = "$cmd"."HRC SI Mode Check Requested (Obsid: $tobsid)\" ";
                        $cmd = "$cmd"."hrcdude\@cfa.harvard.edu";
                        system($cmd);
                    }
                }
            }
        }
	}

#--------------------------------------------------------------------
#---- if CDO requests exist, send out email to an appropriate person
#--------------------------------------------------------------------

	$cdo_file = "$obsid".'_cdo_warning';
	open(CIN, "$temp_dir/$cdo_file");
	@cdo_warning = ();
	$cdo_w_cnt   = 0;
	while(<CIN>){
		chomp $_;
		$ent = $_;
		$ent = s/<->/:  /g;
		push(@cdo_warning, $_);
		$cdo_w_cnt++;
	}
	close(CIN);
	system("rm $temp_dir/$cdo_file");

	if($cdo_w_cnt > 0){
		$large_coord = 0;
		open(COUT, ">$temp_dir/$cdo_file");
		print COUT "The following entries of OBSOD:$obsid  need CDO assistance:\n\n";
		foreach $ent (@cdo_warning){
			if($ent =~ /DEC/i){
				$large_coord++;
			}
			print COUT "$ent\n";
		}
		close(COUT);

		system("rm $temp_dir/$cdo_file");
#
#--- if there is a large coordinate shift, keep the record so that oredit.cgi can 
#---read and mark the observations
#		
		if($large_coord > 0){
			open(LOUT, ">>$ocat_dir/cdo_warning_list");
			print LOUT "$obsid.$rev\n";
			close(LOUT);
		}
	}

#--------------------------
#----  get rid of the junk
#--------------------------

	system("rm -f $temp_dir/*.$sf");
    system("chmod 775 $ocat_dir/updates_table.list*");
}

##################################################################################
### adjust_o_values: adjust output letter values to a correct one              ###
##################################################################################

sub adjust_o_values{

    $orig_name = 'orig_'."$d_name";            #--- original value is kept here

    if(${$d_name} =~ /CONSTRAINT/i){
        ${$d_name} = 'Y';
    }elsif(${$d_name} =~ /PREFERENCE/i){
        ${$d_name} = 'P';
    }elsif(${$d_name} =~ /INCLUDE/i){
        ${$d_name} = 'I';
    }elsif(${$d_name} =~ /EXCLUDE/i){
        ${$d_name} = 'E';
    }elsif(${$d_name} =~ /YES/i){
        ${$d_name} = 'Y';

    }elsif(${$d_name} =~ /NO/i){
        if(${$orig_name} eq 'NO'){
            ${$d_name} = 'NO';
        }elsif(${$orig_name} eq ''){
            ${$d_name} = '';
        }else{
            ${$d_name} = 'N';
        }

    }elsif(${$d_name} =~ /NULL/i){
        if(${$orig_name} eq 'N'){
            ${$d_name} = 'N';
        }elsif(${$orig_name} eq ''){
            ${$d_name} = '';
        }

    }elsif(${$d_name} =~ /NONE/i){
        if(${$orig_name} eq 'NO'){
            ${$d_name} = 'NO';
        }elsif(${$orig_name} eq 'N'){
            ${$d_name} = 'N';
        }elsif(${$orig_name} eq ''){
            ${$d_name} = '';
        }
    }
}

##################################################################################
## send_lt_warning_email: send out a warning email to mp about a late submission #
##################################################################################

sub send_lt_warning_email{
	
    $aline = '';
    if ($smchk == 0){
        $file_name = "$obsid".'.'."$rev";
        $dobsid    = $obsid;
        $dsot_diff = $sot_diff;

        $aline = "$aline"."\n\n".'A user: '."$submitter".' submitted changes of  ';
        $aline = "$aline".'OBSID: '."$obsid".' which is scheduled in 10 days.'."\n\n";
        $aline = "$aline".'The contact email_address address is: '."$email_address"."\n\n";
        $aline = "$aline".'Its Ocat Data Page is:'."\n";
        $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?'."$obsid"."\n\n\n";
        $aline = "$aline".'If you like to see what were changed:'."\n";
        $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?'."$file_name"."\n\n\n";
    }else{
        @tobs_list = split_string_to_list($split_list, $obsid);
        unshift(@tobs_list, $obsid);

        $aline = "$aline"."\n\n".'A user: '."$submitter".' submitted changes of  ';
        $aline = "$aline".'several related (split observations?) obsids: '."$obsid".', '."$split_list";
        $aline = "$aline".' of  which, at least, one of them is scheduled in 10 days.'."\n\n";
        
        $aline = "$aline".'Ocat Data Pages are:'."\n";
        foreach $tobsid (@tobs_list){
            $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?';
            $aline = "$aline"."$tobsid"."\t\t";

            $tlts = find_planned_date($tobsid);
            if($tlts eq ''){
                $aline = "$aline".'---'."\n";
            }else{
                $aline = "$aline"."$tlts"."\n";
            }
#
#--- keep the violating obsid
#
            ($xchk, $tdiff) = check_obs_date_coming($tlts);
            if ($tdiff < 10){
                $dobsid    = $tobsid;
                $dsot_diff = $tdiff;
            }
        }
        $aline = "$aline"."\n\n";

        $aline = "$aline".'If you like to see what were changed: '."\n";
            
        foreach $tobsid (@tobs_list){
            ($file_name, $la) = find_latest_rev($tobsid, @u_list);
            $file_name        = increment_obidrev($file_name, $tobsid);
            $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?'."$file_name"."\n";
        }
        $aline = "$aline"."\n\n";
    }
    $aline = "$aline".'If you have any question about this email, please contact ';
    $aline = "$aline".'bwargelin@head.cfa.harvard.edu.'."\n\n\n";
#
#--- print out to a temp file
#
	$temp_file = "$temp_dir/mp_lts";
	open(ZOUT, ">$temp_file");
    print ZOUT "$aline";
    close(ZOUT);
#
#--- find out who is the mp contact person for this obsid
#
    $mp_contact = '';
	open(IN, "$obs_ss/scheduled_obs_list");
	OUTER:
	while(<IN>){
		chomp $_;
		@mtemp = split(/\s+/, $_);
        $msave = $mtemp[1];
		if($obsid == $mtemp[0]){
			$mp_contact = $mtemp[1];
			last OUTER;
		}
	}
	close(IN);
#
#--- if no mp is assigned for this obsid, use the last person listed on the list
#
    if($mp_contact eq ''){
        $mp_contact = $msave;
    }


	if($usint_on =~ /test/){
        $cmd = "cat $temp_file | mailx -s\"Subject:TEST!! Change to Obsid $dobsid ";
        $cmd = "$cmd"."Which Is Scheduled in $dsot_diff days ($mp_email)\" $test_email";
		system($cmd);
	}else{
        $cmd = "cat $temp_file | mailx -s\"Subject: Change to Obsid $dobsid ";
        $cmd = "$cmd"."Which Is Scheduled in $idsot_diff days\"  ";
        $cmd = "$cmd"."$mp_email cus\@head.cfa.harvard.edu";
		system($cmd);
	}
	system("rm $temp_file");
}

###################################################################################
### send_lt_warning_email2: send out a warning email to USINT  a late submission ##
###################################################################################

sub send_lt_warning_email2{
#
#--- find out who is the mp contact person for this obsid
#
    $mp_contact = '';
    open(IN, "$obs_ss/scheduled_obs_list");
    OUTER:
    while(<IN>){
        chomp $_;
        @mtemp = split(/\s+/, $_);
        $msave = $mtemp[1];
        if($obsid == $mtemp[0]){
            $mp_contact = $mtemp[1];
            last OUTER;
        }
    }
    close(IN);
#
#--- if no mp is assigned for this obsid, use the last person listed on the list
#
    if($mp_contact eq ''){
        $mp_contact = $msave;
    }
#
#--- notifying observation scheduled is coming less than 10 days
#--- if smchk > 1, one of the split observations is coming less than 10 days
#
    $aline = '';
    if ($smchk == 0){
        $file_name = "$obsid".'.'."$rev";
        $dobsid    = $obsid;
        $dltd_diff = $ltd_diff;

        $aline = "$aline"."\n\n".' You submitted changes of  ';
        $aline = "$aline".'OBSID: '."$obsid".' which is scheduled in 10 days.'."\n\n";
        $aline = "$aline".'The email_address of MP: mp\@cfa.harvard.edu.'."\n\n";
        $aline = "$aline".'Its Ocat Data Page is:'."\n";
        $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?'."$obsid"."\n\n\n";
        $aline = "$aline".'If you like to see what were changed:'."\n";
        $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?'."$file_name"."\n\n\n";

    }else{
        @tobs_list = split_string_to_list($split_list, $obsid);
        unshift(@tobs_list, $obsid);

        $aline = "$aline"."\n\n".'You submitted changes of  ';
        $aline = "$aline".'several related (split observations?) obsids: '."$obsid".', '."$split_list";
        $aline = "$aline".' of  which, at least, one of them is scheduled in 10 days.'."\n\n";
        $aline = "$aline".'The email_address of MP: mp@cfa.harvard.edu.'."\n\n";
        $aline = "$aline".'Ocat Data Pages are:'."\n";

        foreach $tobsid (@tobs_list){
            $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/ocatdata2html.cgi?';
            $aline = "$aline"."$tobsid"."\t\t";
            $tlts = find_planned_date($tobsid);
            if ($tlts eq ''){
                $aline = "$aline"."---\n";
            }else{
                $aline = "$aline"."$tlts\n";
            }
            ($xchk, $tdiff) = check_obs_date_coming($tlts);
            if ($tdiff < 10){
                $dobsid    = $tobsid;
                $dltd_diff = $tdiff;
            }
        }
        $aline = "$aline"."\n\n";

        $aline = "$aline".'If you like to see what were changed:'."\n";
            
        foreach $tobsid (@tobs_list){
            ($file_name, $la) = find_latest_rev($tobsid, @u_list);
            $file_name        = increment_obidrev($file_name, $tobsid);
            $aline = "$aline".'https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi?'."$file_name"."\n";
        }
        $aline = "$aline"."\n\n";
    }
    
    $aline = "$aline".'If you have any question about this email, please contact ';
    $aline = "$aline".'bwargelin@head.cfa.harvard.edu.'."\n\n\n";
#
#--- print out to the temp file
#
    $temp_file = "$temp_dir/mp_lts";
    open(ZOUT, ">$temp_file");
    print ZOUT "$aline";
    close(ZOUT);
    
    if($usint_on =~ /test/){
        $cmd = "cat $temp_file | mailx -s\"Subject:TEST!! Change to Obsid $dobsid ";
        $cmd = "$cmd"."Which Is Scheduled in $dsot_diff days ($email_address)\" $test_email";
        system($cmd);
    }else{
        $cmd = "cat $temp_file | mailx -s\"Subject: Change to Obsid $dobsid ";
        $cmd = "Which Is Scheduled in $dsot_diff days\"  $email_address cus\@head.cfa.harvard.edu";
        system($cmd);
    }
    system("rm $temp_file");
}

##################################################################################
## check_obs_date_coming: check whether obs date is coming less than 10 days    ##
##################################################################################

sub check_obs_date_coming{
=comment
check whether obs date is coming less than 10 days
input:  obs_date    --- obs date
output: 1           --- planned date is coming less than equal 10 days
        0           --- planned date is more than 10 days away
=cut
    my $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $uyear; 
    (my $obs_date) = @_;
    if(length($obs_date) == 0){
        return 0;
    }
#
#--- today's date
#
	($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	$uyear = 1900 + $year;
#
#--- convert today's date in fractional year
#
    $val = is_leap_year($uyear);
    if($val == 1){
        $base = 366;
    }else{
        $base = 365;
    }

    $tyear = $uyear + $yday / $base;
#
#--- convert the lts date into fractional year
#
    my $lts = obs_date_to_fyear($obs_date);
#
#--- warning date: how many more day left to lts date
#
    $diff        = $lts - $tyear;
    my $sot_diff = int($diff * $base);
#
#--- setting the warning start date to the Monday before the real lts date
#
    if($wday == 0){
        $sday = 6;
    }else{
        $sday = $wday -1;
    }
#
#-- 11 day + M interval in fractional year
#
    $interval = (11.0 + $sday) / $base;

    if($diff <= $interval){
        return (1, $sot_diff);
    }else{
        return (0, $sot_diff);
    }
}    

##################################################################################
## obs_date_to_fyear: converting obs date format to fractional year format     ###
##################################################################################

sub obs_date_to_fyear{
=comment
converting obs date format to fractional year format
input:  $obs_date   --- lts date
output: $fyear      --- time in fractional year
=cut
    (my $obs_date) = @_;

    if($obs_date eq ''){
        return "";
    }

    @atemp   = split(/\s+/, $obs_date);
    my $mon  = $atemp[0];
    my $day  = $atemp[1];
    my $year = $atemp[2];
#
#--- month is in the letter from; convert it into digit
#
    my $i = 1;
    foreach $cmon ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'){
        if($mon eq $cmon){
            $mon = $i;
            last;
        }else{
            $i++;
        }
    }
#
#--- check whether the year is a leap year
#
    $val = is_leap_year($year);

    if($val == 1){
        @m_list =(0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335);
        $base = 366;
    }else{
        @m_list =(0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334);
        $base = 365;
    }

    $add = $m_list[$mon-1];

    $fyear = $year + ($add + $day) / $base;

    return $fyear;
}

##################################################################################
## is_leap_year: check a given year is a leap year                             ###
##################################################################################

sub is_leap_year{
=comment
check a given year is a leap year
input:  lyear   --- year
output: 1 --- leap year 0 --- normal year
=cut

    (my $lyear) = @_;

    my $chk  = $lyear % 4;
    my $chk2 = $lyear % 100;
    my $chk3 = $lyear % 400;

    my $val = 0;
    if($chk == 0){
        $val = 1;
        if($chk2 == 0){
            $val = 0;
        }
    }
    if($chk3 == 0){
        $val = 1;
    }
    
    return $val;
}
        
##################################################################################
##################################################################################
###  split observation copy related functions start here!!                     ###
##################################################################################
##################################################################################


#---------------------------------------------------------------------------------------
#--copy_split_observations: duplicate the records of the original obsid to split obsid in the given list
#---------------------------------------------------------------------------------------

sub copy_split_observations{
=comment
duplicate the records of the original obsid to split obsids in the given list
input:      $mobsid     --- original obsid
            $input_list --- a string of a list of split obsids
            $asis_ind   --- asis stauts 
output:     $record duplicated for all split observations
            email sent out for the notifications
=cut
    my $obsid, $obsidrev, $seq_nbr;
    my $mobsid, $mseq_nbr, $mobsidrev, $mlastest, $asis_ind;
    my $ifile, $ofile, $line, $aline, $bline, $record, $input_line;
    my @split_list, @u_list, @org_text;
#
#--- today's date
#
    $date = `date '+%D'`;
    chop $date;
#
#--- main obsid and all other split obsids in the list
#
    ($mobsid, $input_list, $asis_ind) = @_;
#
#--- convert stiring of a list of split observations into a list
#
    @split_list = split_string_to_list($input_list, $mobsid);
#
#--- cloning requested; do nothing
#
    if($asis_ind =~ /CLONE/i){
        return;
    }
#
#--- removing split observations from approved list requested
#
    if($asis_ind =~ /REMOVE/i) {
        split_obsids_remove(@split_list);
    }
#
#--- remember the origial rank values
#
    $ot_ordr = $orig_time_ordr;
    $or_ordr = $orig_roll_ordr;
    $ow_ordr = $orig_aciswin_no;
#
#--- if large numbers of obsids are submitted for updates, notify arc_ops
#
    if($asis_ind =~ /NORM/i){
        arcops_notificaiton($mobsid, $input_list);
    }
#
#--- submit parameter changes of all obsids
#
    $pind  = 0;
    foreach $obsid (@split_list){
#
#--- checking whether to print the closing message
#
        if ($obsid eq $split_list[-1]){
            $pind = 1;
        }
#
#--- reset rank parameters to make sure that nothing passed from the last round
#
        reset_rank_data();
        $rep_ind = 1;
#
#--- read parameter values of the split obsid from the database
#
        read_databases($obsid, $rep_ind);
        $asis   = $asis_ind;
        $t_ordr = $time_ordr;
        $r_ordr = $roll_ordr;
        $w_ordr = $aciswin_no;
#
#--- update only parameters which were changed in the original obsids
#--- first, update none ranked values
#
        foreach $ent (@base_list){
            if($ent !~/\./){
                $name        = 'base_'."$ent";
                ${$ent}      = ${$name};
            }
        }
        $time_ordr  = $t_ordr;
        $roll_ordr  = $r_ordr;
        $aciswin_no = $w_ordr;
#
#--- update raneked values
#
        update_rank_values_in_other();
#
#--- update updates_table.list/approved list etc
#
        read_name();
        prep_submit(1);
#
#--- "0" below indicates not to display the parameter change verification page
#
        submit_entry(0, $obsid, $sf);
        oredit($obsid, $sf, $pind);
    }
}

#---------------------------------------------------------------------------------------
#-- increment_obidrev: increment rev # of the obsid                                   --
#---------------------------------------------------------------------------------------

sub increment_obidrev{
=comment
increment rev # of the obsid
input:  $obsidrev   --- the latest obsidrev (<obsid>.<rev>)
        $obsid      --- obsid
output: $obsidrev   --- updated obsidrev
=cut
    my $rev;
    (my $obsidrev, my $obsid) = @_;

    if($obsidrev == 0.0){
        $obsidrev = "$obsid".".001"
    }else{
        @atemp = split(/\./, $obsidrev);
        $rev   = int($atemp[1]) + 1;
        if($rev < 10){
            $obsidrev = "$obsid".'.00'."$rev";
        }elsif ($rev < 100){
            $obsidrev = "$obsid".'.0'."$rev";
        }else{
            $obsidrev = "$obsid".'.'."$rev";
        }
    }

    return $obsidrev;
}

#---------------------------------------------------------------------------------------
#-- find_rank: find the starting rank which the new data will be saved                --
#---------------------------------------------------------------------------------------

sub find_rank{
=comment
find the starting rank which the new data will be saved
input:  @tlist  --- a list of elements in the group
output: $k      --- a rank
=cut
    my $k, $cnt, $name, $val;

    (my @tlist) = @_;
    for($k = 1; $k < 30; $k++){
#
#--- check any elements are assigned values
#
        $cnt = 0;
        foreach $ent (@tlist){
            $name = "$ent"."$k";
            $val  = ${$name};
#
#--- acis window include_flag default is 'E'; ignore that from cunting
#
            if(($val ne '') && ($val !~ /NULL/i) && ($val !~ /E/i)){
                $cnt++;
            }
        }
#
#--- if none of the element is assigned a value, that is the rank to be used
#
        if($cnt == 0){
            return $k-1;
        }
    }
    return 0;
}

#---------------------------------------------------------------------------------------
#-- find_which_group: check which group the element belongs                           --
#---------------------------------------------------------------------------------------

sub find_which_group{
=comment
check which group the element belongs
input:  $elem   --- the element to be checked
        @t_const    --- a list of time constraint list
        @r_const    --- a list of roll constraint list
        @w_const    --- a list of window constraint list
            --- these are global lists
output: 1: time constraints, 2: roll constraint, 3: window constraint
=cut
    ($elem) = @_;
    if(check_element(@t_const, $elem) == 1){
        return 1;

    }elsif(check_element(@r_const, $elem) == 1){
        return 2;

    }elsif(check_element(@w_const, $elem) == 1){
        return 3;

    }else{
        return 0;
    }
}
    
#---------------------------------------------------------------------------------------
#-- check_element: check whether the element in the list                             ---
#---------------------------------------------------------------------------------------

sub check_element{
=comment
check whether the element in the list
input:  @tlist      --- a list of element 
        $element    --- the element to be checked
output: 0 --- no the element is not in the list
        1 --- yes the element is in the list
=cut
    (my @tlist) = @_;
#
#--- element is passes as the last entry of the list
#
    my $element = pop @tlist;

    foreach $ent (@tlist){
        if($element =~ /$ent/i){
            return 1;
        }
    }

    return 0;
}

#---------------------------------------------------------------------------------------
#-- find_latest_rev: find the last revision number of the obsid                      ---
#---------------------------------------------------------------------------------------

sub find_latest_rev{
=comment
find the last revision number of the obsid
input:      obsid       --- obsid
            u_list      --- a list of signoff request record (flobal)
ouptput:    lobsidrev   --- <obsid>.<rev>
            latest      --- the record of the signoff request:
                        <obisd>.<rev> <gen> <acis> <si mode> <signoff> <seq #> <poc>
=cut
    my $ent, $obsid, $trev, @u_list;
    (my$obsid, my @u_list) = @_;
    my $prev               = 0;
    my $latest             = '';
    my $lobsidrev          = 0.0;
#
#--- go through the updates_table.list content to find matched obsid
#
    foreach $ent (@u_list){
        @atemp = split(/\s+/, $ent);
        @btemp = split(/\./,  $atemp[0]);
        if ($btemp[0] == $obsid){
#
#--- keep the latest obsid.rev
#
            $trev = int($btemp[1]);
            if($trev > $prev){
                $latest    = $ent;
                $lobsidrev = $atemp[0];
                $prev      = $trev;
            }
        }
    }
    return ($lobsidrev, $latest);
}

#---------------------------------------------------------------------------------------
#-- find_seq_nbr: find the sequence number for a given obsid                          --
#---------------------------------------------------------------------------------------

sub find_seq_nbr{
=comment
find the sequence number for a given obsid
input:  obsid   --- obsid
output: seq_nbr --- sequence number
=cut
#
#--- set sql parameters
#
    $server    = "ocatsqlsrv";
    if($web =~ /icxc/){
        $db_user   = "mtaops_internal_web";
        $db_passwd =`cat $pass_dir/.targpass_internal`;
    }else{
        $db_user = "mtaops_public_web";
        $db_passwd =`cat $pass_dir/.targpass_public`;
    }
    chomp $db_passwd;
#
#--- set sql command
#
    (my $obsid) = @_;
    my $db = "server=$server;database=axafocat";
    $dsn1  = "DBI:Sybase:$db";
    $dbh1  = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});
    
    my $seq_nbr = '';
#
#--- run sql
#
    $sqlh1 = $dbh1->prepare(qq(select seq_nbr from target where obsid=$obsid));
        $sqlh1->execute();
        ($seq_nbr) = $sqlh1->fetchrow_array;
        $sqlh1->finish;

    chomp $seq_nbr;
    return $seq_nbr;
}

#---------------------------------------------------------------------------------------
#-- find_planned_date: find the planned observation date for a given obsid            --
#---------------------------------------------------------------------------------------

sub find_planned_date{
=comment
find the planned observation date for a given obsid
input:  obsid       --- obsid
output: either lts_lt_plan or soe_st_sched_date
=cut
#
#--- set sql parameters
#
    $server    = "ocatsqlsrv";
    if($web =~ /icxc/){
        $db_user   = "mtaops_internal_web";
        $db_passwd =`cat $pass_dir/.targpass_internal`;
    }else{
        $db_user = "mtaops_public_web";
        $db_passwd =`cat $pass_dir/.targpass_public`;
    }
    chomp $db_passwd;
#
#--- set sql command
#
    (my $obsid) = @_;
    my $db = "server=$server;database=axafocat";
    $dsn1  = "DBI:Sybase:$db";
    $dbh1  = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});
    
    my $lts_lt_plan       = '';
    my $soe_st_sched_date = '';
#
#--- run sql
#
    $sqlh1 = $dbh1->prepare(qq(select lts_lt_plan from target where obsid=$obsid));
        $sqlh1->execute();
        ($lts_lt_plan) = $sqlh1->fetchrow_array;
        $sqlh1->finish;

    $sqlh1 = $dbh1->prepare(qq(select soe_st_sched_date from target where obsid=$obsid));
        $sqlh1->execute();
        ($soe_st_sched_date) = $sqlh1->fetchrow_array;
        $sqlh1->finish;

    chomp $lts_lt_plan;
    chomp $soe_st_sched_date;

    if(length($soe_st_sched_date) > 0){
        return $soe_st_sched_date;

    }else{
        return $lts_lt_plan;
    }
}

#---------------------------------------------------------------------------------------
#-- split_obs_date_check: check whether obs dates of any of split obsid are coming less than 10 days
#---------------------------------------------------------------------------------------

sub split_obs_date_check{
=comment
check whether obs dates of any of split obsid are coming less than 10 days
input:  $input_list --- a string of a list of obsids
        $obs_diff   --- the obs date difference of the main obsid
        $mobsid     --- the main obsid
output: $chk        --- if >0, yes, if ==0 no
        $obs_diff   --- the smallest obs date difference among all obsids
        @sobs_list  --- a list of obsids of those scheduled in 10 days
=cut
#
#-- find obs date for split observations
#
    my $tobsid, $obs, $schk, $diff;
    (my $input_list, my $obs_diff, my $mobsid) = @_;
    my @split_list = split_string_to_list($input_list, $mobsid);
    my @sobs_list  = ();

    my $chk = 0;
    foreach $tobsid (@split_list){
        $obs           = find_planned_date($tobsid);
        ($schk, $diff) = check_obs_date_coming($obs);
        $chk          += $schk;
        if($diff < 10){
            push(@sobs_list, $tobsid);
            if($diff < $obs_diff){
                $obs_diff = $diff;
            }
        }
    }

    return ($chk, $obs_diff, @sobs_list);
}

#---------------------------------------------------------------------------------------
#-- check_obsid_in_database: check any of the obsids in the split_list are not in the database
#---------------------------------------------------------------------------------------

sub check_obsid_in_database{
=comment
check any of the obsids in the split_list are not in the database
input:  $input_list --- a string of a list of obsids
        $mobsid     --- the main obsid
output: $tchk       --- number of obsids which are not in the databse
        @nobs_list  --- a list of obsids which are not in the databse
=cut
    (my $input_list, my $mobsid) = @_;
    my @split_list   = split_string_to_list($input_list, $mobsid);
    my @nobs_list    = ();
    my $tchk         = 0;
    foreach $tobsid (@split_list){
        $schk = find_seq_nbr($tobsid);
        if($schk eq ''){
            push(@nobs_list, $tobsid);
            $tchk += 1;
        }
    }

    return ($tchk, @nobs_list);
}
    
#---------------------------------------------------------------------------------------
#-- split_obsids_remove: removing all split observations from approved list           --
#---------------------------------------------------------------------------------------

sub split_obsids_remove{
=comment
removing all split observations from approved list
input:  @split_list     --- a list of split obsids
output: updated <ocat_dir>/approved
=cut
#
#--- create split obsid list from a string
#
    (my @split_list) = @_;
#
#---- read approved list and remove obsids
#
    my $aline = '';
    open(FH, "$ocat_dir/approved");
    OUTER:
    while(<FH>){
        chomp $_;
        @atemp = split(/\t+/, $_);
        if ($atemp[0] ~~ @split_list){
            next OUTER;
        }else{
            $aline = "$aline"."$_"."\n";
        }
    }
    close(FH);
#
#--- move the current approved list to backup and update
#
    system("mv $ocat_dir/approved $ocat_dir/approved~");

    open(OUT, ">$ocat_dir/approved");
    print OUT $aline;
    close(OUT);
    system("chmod 644  $ocat_dir/approved");
}
            
#---------------------------------------------------------------------------------------
#-- split_obsid_email: sending out email to dusty sci                                 --
#---------------------------------------------------------------------------------------

sub split_obsid_email {
=comment
sending out email to dusty sci
input:  $obidrev    --- the full path to the record of obsid.rev
        $asis       --- ASIS status such as "asis"
output: email sent
Note: email address is assume to be same as the global email address $email_address
=cut
    (my $obsidrev, my $asis) = @_;
#
#--- separate obsid.rev from the line
#
    @atemp   = split(/\//, $obsidrev);
    my $orev = $atemp[-1];
    if ($orev eq ''){
        $orev = $obsidrev;
    }
    $obsidrev = "$ocat_dir"."/updates/$obsidrev";
#
#--- set subject line
#
    if($asis =~ /ASIS/i){
        $subject = " Parameter Changes (Approved) log  $orev";
    }else{
        $subject = " Parameter Changes log  $orev";
    }
#
#--- send out email
#
    if($usint_on =~ /test/){
        system("cat $obsidrev |mailx -s\"Subject: TEST!! $subject\" $test_email");
    }else{
        system("cat $obsidrev |mailx -s\"Subject: $subject\"  -c $cus_email $email_address");
    }
}
    
#---------------------------------------------------------------------------------------
#-- split_string_to_list: create split obsid list from a string                       --
#---------------------------------------------------------------------------------------

sub split_string_to_list{
=comment
create split obsid list from a string
input:  $input_line --- a string of a list of obsids
        $mobsid     --- the main obsid
output: @split_list --- a list of obsids
=cut
    my $i, $k, $start, $stop;
    my @split_list   = ();
    my @temp_liist   = ();
    my $ent, $start, $stop;
    (my $input_list, my $mobsid) = @_;
#
#--- remove leading and tailing spaces
#
    $input_list =~ s/^\s+|\s+$//g;
#
#--- change deliminators to a space
#
    $input_list =~ s/\,/ /g;
    $input_list =~ s/\;/ /g;
    $input_list =~ s/\:/ /g;
    $input_list =~ s/\// /g;
#
#--- make a list delimited by a space
#
    @temp_list  = split(/\s+|\t+/, $input_list);
#
#--- check any entry is marked by '-' which indcates entry interval
#
    my $cnt = scalar @temp_list;
    for($i= 0; $i < $cnt; $i++){
        $ent = $temp_list[$i];
        if($ent =~ /\-/){
#
#--- case like: 3333 - 3334
#
            if($ent eq '-'){
                $start = $temp_list[$i-1] + 1;
                $stop  = $temp_list[$i+1];
                for($k = $start; $k< $stop; $k++){
                    push(@split_list, $k);
                }
#
#--- case like: 3333-3334
#
            }else{
                @atemp = split(/\-/, $ent);
                for($k=int($atemp[0]); $k<=int($atemp[1]); $k++){
                    push(@split_list, $k);
                }
            }
        }else{
            push(@split_list, $ent);
        }
    }
#
#--- remove duplicated entries
#
    @split_list = uniq_ent(@split_list);
    my @c_list = ();
    foreach $ent (@split_list){
        if($ent eq ''){
            next;
        }elsif($ent == $mobsid){
            next;
        }else{
            push(@c_list, $ent);
        }
    }
    @split_list = @c_list;

    return @split_list;
}

#---------------------------------------------------------------------------------------
#-- make_obsid_list: create a display list of obsids                                 ---
#---------------------------------------------------------------------------------------

sub make_obsid_list{
=comment
create a display list of obsids
input:  $temp_list  --- a string of a list of obsids
        $schk       --- indicator of two types of description
output: $line       --- a html format of a list
=cut
    (my $temp_list, my $schk) = @_;
    my @split_list  = split_string_to_list($temp_list);
    my $line        = '';

    my $lchk = scalar(@split_list);
    if($lchk == 0){
        return  $line;

    }elsif($lchk == 1){
        if($schk == 1){
            $line = '<p><b>The same changes will apply to Obsid: ';
        }else{
            $line = '<p><b>This also apply to Obsid: ';
        }

    }else{
        if($schk == 1){
            $line = '<p><b>The same changes will apply to Obsids: ';
        }else{
            $line = '<p><b>This also apply to Obsids: ';
        }
    }
    
    foreach $ent (@split_list){
        $ohtml = './ocatdata2html.cgi?'."$ent";
        $link  = '<a href="javascript:WindowOpener(\''."$ohtml".'\')">'."$ent".'</a>';
        $line = "$line"."<br> <span style='padding-left:20px;'>$link</span>";
    }

    $line = "$line </b><p>";
        
    return $line;
}

#---------------------------------------------------------------------------------------
#-- check_spl_obs_on_mp_list: check wether any of obsid on the split_list are on the active list
#---------------------------------------------------------------------------------------

sub check_spl_obs_on_mp_list{
=comment
check wether any of obsid on the split_list are on the active list
input:  $in_list    --- a string of a list of obsids
output: $mp_check   --- 1 if any of the obsids are on the active list, otherwise, 0
        @mp_w_list  --- a list of obsids which are in OR list
=cut
    (my $in_list) = @_;

    my @t_list    = split_string_to_list($in_list);
    my $mp_check  = 0;
    my @mp_w_list = ();

    foreach $tobsid (@t_list){
        foreach $check (@mp_scheduled_list){
            if($check =~ /$tobsid/){
                $mp_check += 1;
                push(@mp_w_list, $tobsid);
            }
        }
    }

    return ($mp_check, @mp_w_list);
}

#---------------------------------------------------------------------------------------
#-- save_ranked_data: save the ranked parameter values of the main obsid (control func) 
#---------------------------------------------------------------------------------------

sub save_ranked_data{
=comment
save the ranked parameter values of the main obsid (control func)
input:  @t_const    --- a list of time constraint parameter values
        @r_const    --- a list of rank constraint parameter values
        @w_const    --- a list of acis window parameter values
        $nt_ordr    --- a rank of time constraint
        $nr_ordr    --- a rank of rank constraint
        $nw_ordr    --- a rnak of acis window 
output: @{$ob_name} --- a list of original values
        @{$nv_name} --- a list of updated values
=cut
    $ot_ordr  = param('ORIG_TIME_ORDR');
    $nt_ordr  = param('TIME_ORDR');
    $or_ordr  = param('ORIG_ROLL_ORDR');
    $nr_ordr  = param('ROLL_ORDR');
    $ow_ordr  = param('ORIG_ACISWIN_NO');
    $nw_ordr  = param('ACISWIN_NO');

    save_rank_values(\@t_const, $nt_ordr, 1);
    save_rank_values(\@r_const, $nr_ordr, 1);
    save_rank_values(\@w_const, $nw_ordr, 0);
}

#---------------------------------------------------------------------------------------
#-- save_rank_values: save the ranked parameter values of the main obsid              --
#---------------------------------------------------------------------------------------

sub save_rank_values{
=comment
save the ranked parameter values of the main obsid
input:  @r_list     --- a list of constraint parameter values
        $rordr      --- a rank
        $start      --- starting rank value, either 0 or 1 (0 for aciswindow)
output: @{$ob_name} --- a list of original values
        @{$nv_name} --- a list of updated values
=cut
    my $k, $name, $o_name, $ov_name, $nv_name;
    my @r_list = @{$_[0]};
    my $rordr  = $_[1];
    my $start  = $_[2];
    my $stop   = $rordr + $start;

    for($k = $start; $k < $stop; $k++){
        foreach $name (@r_list){
            $name     = lc($name);
            $o_name   = 'orig_'."$name";
            $n_name   = $name;
            $ov_name  = 'ov_'."$name";
            $nv_name  = 'nv_'."$name";

            ${$ov_name}[$k] = ${$o_name}[$k];
            ${$nv_name}[$k] = ${$n_name}[$k];
        }
    }
}

#---------------------------------------------------------------------------------------
#-- update_rank_values_in_other: update ranked parameter values of the secondary obsids (control func)
#---------------------------------------------------------------------------------------

sub update_rank_values_in_other{
=comment
update ranked parameter values of the secondary obsids (control func)
input:  @t_const    --- a list of time constraint parameter values
        @r_const    --- a list of rank constraint parameter values
        @w_const    --- a list of acis window parameter values
        $time_ordr  --- a time constraint rank of the secondary obsids
        $ot_ordr    --- an original time constraint rank of the main obsid
        $nt_ordr    --- an updated time constraint rank of the main obsid
        $roll_ordr  --- a roll constraint rank of the secondary obsids
        $or_ordr    --- an original roll constraint rank of the main obsid
        $nw_ordr    --- an updated roll constraint rank of the main obsid
        $aciswin_no --- an acis window rank of the secondary obsids
        $or_ordr    --- an original acis window rank of the main obsid
        $nr_ordr    --- an updated acis window rank of the main obsid
output: all ranked parameter values 
        $time_ordr  --- the rank of time constraint
        $roll_ordr  --- the rank of roll constraint
        $aciswin_no --- the rank of acis window constraint
=cut

    $time_ordr  = compare_rank_values(\@t_const, $time_ordr,  $nt_ordr, $ot_ordr, 1);
    $roll_ordr  = compare_rank_values(\@r_const, $roll_ordr,  $nr_ordr, $or_ordr, 1);
    $aciswin_no = compare_rank_values(\@w_const, $aciswin_no, $nw_ordr, $ow_ordr, 0);
}

#---------------------------------------------------------------------------------------
#-- compare_rank_values: update ranked parameter values of the secondary obsids       --
#---------------------------------------------------------------------------------------

sub compare_rank_values{
=comment
update ranked parameter values of the secondary obsids
input:  @c_const    --- a list of parameters
        $c_ordr     --- a rank of the current obsid
        $nv_ordr    --- a rank of the main obsid
        $ov_ordr    --- a original rank of the main obisd
        $start      --- a rank starting value 0 or 1 (acis win start from 0)
output: updated ranked parameter values
        $n_ordr     --- the rank of the constraint of the secondary obsid
=cut
    my $k, $chk, $chk2, $chk3, $chk4;
    my @c_const = @{$_[0]};         #--- a list of parameters
    my $c_ordr  = $_[1];            #--- a rank of the current obsid
    my $nv_ordr = $_[2];            #--- a rank of the main obsid
    my $ov_ordr = $_[3];            #--- a original rank of the main obisd
    my $start   = $_[4];            #--- a rank starting value 0 or 1 (acis win start from 0)
    my $n_ordr  = $c_ordr;
#
#--- for the case the rank of the current obsid is larger than that of the main obsid
#
    if($c_ordr > $nv_ordr){
        $chk5 = 0;
        for($k = $start; $k <= $nv_ordr; $k++){
#
#--- $chk  --- compare values in current and the original main obsid
#--- $chk2 --- check current values are Null
#--- $chk3 --- check any values in main obsid are updated
#--- $chk4 --- check all original values of main obsid are null
#--- $chk5 --- check whether still valid data ara around (for the case the rank is removed)
#
            ($chk, $chk2, $chk3, $chk4) = check_data_situation($k, \@c_const);
#
#--- if the orig values are same between the current and the main obsids:
#
            if($chk == 0){
#
#--- if there was value updates in the main obsid 
#
                if($chk3 > 0){
                    foreach $name (@c_const){
                        $name  = lc($name);
                        $nname = 'nv_'."$name";
                        $nval  = ${$nname}[$k]; 
                        ${$name}[$k] = $nval;
                        $chk5++;
                    }
                }
            }
        }
#
#--- if some rank are removed in the main obsid, make sure that it does same for here
#
        if($chk5 >0 && $ov_ordr > $nv_ordr && $ov_ordr == $c_ordr){
            for($k =$nv_ordr+1; $k <=$ov_ordr; $k++){
                foreach $name (@c_const){
                    $name  = lc($name);
                    $nname = 'nv_'."$name";
                    $nval  = ${$nname}[$k]; 
                    ${$name}[$k] = $nval;
                }
                $n_ordr--;
            }
        }
#
#--- for the case the current ordr is same or smaller than that of the main obsid
#
    }elsif($c_ordr <= $nv_ordr){
        for($k = $start; $k <= $c_ordr; $k++){
            ($chk, $chk2, $chk3, $chk4) = check_data_situation($k, \@c_const);

#
#--- if the orig values are same between the current and the main obsids:
#
            if($chk == 0){
#
#--- if there was value updates in the main obsid 
#
                if($chk3 > 0){
                    foreach $name (@c_const){
                        $name  = lc($name);
                        $nname = 'nv_'."$name";
                        $nval  = ${$nname}[$k]; 
                        ${$name}[$k] = $nval;
                    }
                }
#
#--- if the orig values are different between the main and current obsids 
#--- but the values of orig data of the main obsids are null and the new 
#--- values are not null, add a new rank to the current obsid 
#
            }else{
                if($chk3  > 0 && $chk4 == 0){
                    $n_ordr++;
                    foreach $name (@c_const){
                        $name  = lc($name);
                        $nname = 'nv_'."$name";
                        $nval  = ${$nname}[$k];
                        ${$name}[$n_ordr] = $nval;
                    }
                }
            }
        }
#
#--- the main obsid has a larger rank than the current one; add a new rank to the current one
#
        if($nv_ordr > $c_ordr){
            for($k = $c_ordr+1; $k <= $nv_ordr; $k++){
#
#--- check the value changes
#
                ($chk, $tmp2, $chk3, $chk4) = check_data_situation($k,      \@c_const);
                ($tmp, $chk2, $tmp3, $tmp4) = check_data_situation($n_ordr, \@c_const);
#
#--- the values in the main obsids are updated
#
                if($chk3 > 0){
#
#--- make sure that the updated values of the main obsid are not null
#
                    if($chk4 == 0){
                        if($chk2 > 0){
                            $n_ordr++;
                        }
                        foreach $name (@c_const){
                            $name  = lc($name);
                            $nname = 'nv_'."$name";
                            $nval  = ${$nname}[$k];
                            ${$name}[$n_ordr] = $nval;
                        }
                    }
                }
            }
#
#--- aciswin case starts index of 0. So for the rank value, add 1
#
            if($start == 0){
                $n_ordr++;
            }
        }
    }
    return $n_ordr;
}

#---------------------------------------------------------------------------------------
#-- reset_rank_data: reset rank parameters to NULL values                             --
#---------------------------------------------------------------------------------------

sub reset_rank_data{
=comment
reset rank parameters to NULL values
input:  @t_const    --- parameter values of time constraints 
        @r_const    --- parameter values of roll constraints
        @w_const    --- parameter values of acis window 
output: @t_const/@r_const/$w_const with NULL value settings
=cut 
    my $k, $name, $o_name;

    for($k = 0; $k < 30; $k++){
        foreach $name (@t_const, @r_const, @w_const){
            $name          = lc($name);
            $o_name        = 'orig_'."$name";
            ${$name}[$k]   = "NULL";
            ${$o_name}[$k] = "NULL";
        }
    }
}

#---------------------------------------------------------------------------------------
#-- check_data_situation: check which conditions the data sets are in                 --
#---------------------------------------------------------------------------------------

sub check_data_situation{
=comment
check which conditions the data sets are in
input:  $k          --- the position in the rank
        @c_const    --- a list of parameter values
output: $chk        --- compare values in current and th oroginal main obsid
        $chk2       --- check current values are Null
        $chk3       --- check any values in main obsid are updated
        $chk4       --- check all orig values of main obsid are null
=cut
    my $name, $oname, $nname, $val, $oval, $nval;
    my $k    = $_[0];
    my $temp = $_[1];
    my @c_const = @{$temp};

    my $chk  = 0;                   #--- compare values in current and th oroginal main obsid
    my $chk2 = 0;                   #--- check current values are Null
    my $chk3 = 0;                   #--- check any values in main obsid are updated
    my $chk4 = 0;                   #--- check all orig values of main obsid are null
#
#--- first, check any changes of values occured
#
    foreach $name (@c_const){
        $name  = lc($name);
        $oname = 'ov_'."$name";
        $nname = 'nv_'."$name";             
        $val   = ${$name}[$k];              #--- value of the current obsid 
        $oval  = ${$oname}[$k];             #--- orig value form the main obsid
        $nval  = ${$nname}[$k];             #--- new value from the main obsid
#
#--- checking whether the current value and the value of the main obsid is same
#
        if($val ne $oval){
            $chk++;
        }
#
#--- checking the current value is null value
#
        $chk2 += check_null_value($val);
#
#--- checking the any values of this rank of the main obisd are updated
#
        if($oval ne $nval){
            $chk3++;
        }
#
#--- check orig values were null
#
        $chk4 += check_null_value($oval);
    }

    return ($chk, $chk2, $chk3, $chk4);
}

#---------------------------------------------------------------------------------------
#-- check_null_value: check whether the value is in null set ("", "NULL", "E")        --
#---------------------------------------------------------------------------------------

sub check_null_value{
=comment
check whether the value is in null set ("", "NULL", "E")
input:  $val    --- value
output: $chk    --- 0: not NULL / 1: NULL
=cut
    (my $val) = @_;
    my $chk   = 0;
    if(($val ne '') && ($val !~ /NULL/i) && ($val !~ /E/i)){
        $chk = 1;
    }

    return $chk;
}

#---------------------------------------------------------------------------------------
#-- uniq_ent: create a list of unqiue entries                                         --
#---------------------------------------------------------------------------------------

sub uniq_ent{
=comment
create a list of unqiue entries
input:  @temp_list  --- a list of data
output: @out_list   --- a list of unique data
=cut
    (my @temp_list) = @_;

    @temp_list   = sort @temp_list;
    my $prev     = @temp_list[0];
    my @out_list = ($prev);

    foreach $ent (@temp_list){
        if($ent != $prev){
            push(@out_list, $ent);
            $prev = @ent;
        }
    }
    
    return @out_list;
}

#---------------------------------------------------------------------------------------
#-- sp_list_test: check whether the input string can convert to a list of obsids      --
#---------------------------------------------------------------------------------------

sub sp_list_test{
=commnet
check whether the input string can convert to a list of obsids
input:  $stest  --- a string to be tested
output: 0: no / 1: yes
=cut
    (my $stest) = @_;
    $stest =~ s/^\s+|\s+$//g;
    $stest =~ s/ //g;
    if($stest eq ''){
        return 0;
    }else{
        return 1;
    }
}

#---------------------------------------------------------------------------------------
#-- create_year_list: create a year list for a pulldown menu                          --
#---------------------------------------------------------------------------------------

sub create_year_list{
=comment
create a year list for a pulldown menu
input:  $t_beg  --- assigned year in the rank. it can be "null"; then current year will be given
output: @y_list --- a list of year including "NULL"
=cut
    (my $t_beg) = @_;
    my $sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst;
    my $k, $tyear;
#
#--- starting year is given in the rank, use that 
#
    if($t_beg ne '' && $t_beg !~ /N/i){
        $tyear = $t_beg;
#
#--- if starting year is not given (say, newly added rank), use the current year
#
    }else{
        ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime();
        $tyear = $year + 1900;
    }
#
#--- start the year list from one year before of the given year
#
    my $lyear  = $tyear -1;
    my $temp   = $lyear;
    my @y_list = ('NULL');

    for($k = 0; $k < 12; $k++){
        $temp = $lyear + $k;
        push(@y_list, $temp);
    }

    return @y_list;
}
        
#---------------------------------------------------------------------------------------
#-- arcops_notificaiton: sending a notification to arc_ops if  multiple obsids updates
#---------------------------------------------------------------------------------------

sub arcops_notificaiton{
=comment
sending a notification to arc_ops if there are a large numbers of multiple obsids updates
input:  $mobsid     --- the main obsid
        $input_list --- a string of obsid list
        @base_list  --- a list of modified parameter names
output: email sent to arc_ops
=cut
    my @split_list = ();
    my $mobsid     = '';
    ($mobsid, $input_list) = @_;
    @split_list    = split_string_to_list($input_list, $mobsid); 
#
#--- add the main obsid to the list
#
    push(@split_list, $mobsid);
    @split_list = sort {$a<=>$b} @split_list;
#
#--- if there are more than 10 obsids to be updated, notify arcops
#
    #if( (scalar @split_list) < 10){
    if( (scalar @split_list) < 2){
        return 
    }
#
#--- start writing the mail content
#
    $line = "A USINT user ($email_address) submitted parameter change requests to multiple obsids: \n\n";

    $k    = 1;
    foreach $ent (@split_list){
        $line  = "$line $ent \t";
#
#--- eight obsids per line
#
        if($k % 8 == 0){
            $line = "$line\n";
        }
        $k++;
    }
    $line = "$line"."\n\n";
#
#--- if this is a normal parameter changes, list changed parameters and their values
#
    if ((scalar @base_list) == 1){
        $line = "$line"."The updated parameter is:\n\n";
    }else{
        $line = "$line"."The updated parameters are:\n\n";
    }
    $line = "$line"."Parameter\t\tNew Value\n";
    $line = "$line"."------------------------------------------------\n";

    foreach $name (@base_list){
        $val   = ${$name};

        $lcnt  = length($name);
        if($lcnt < 4){
            $line  = "$line"."$name:\t\t\t\t$val\n";
        }elsif($lcnt < 8){
            $line  = "$line"."$name:\t\t\t$val\n";
        }else{
            $line  = "$line"."$name:\t\t$val\n";
        }
    }
#
#--- creating email
#
    $mail_file = "$temp_dir".'/arcops';
    open(OUT, ">$mail_file");
    print OUT "$line";
    close(OUT);

    $subject = 'Multiple Obsids Are Submitted for Parameter Changes';
#
#--- sending email to arc ops
#
    if($usint_on =~ /test/){
        system("cat $mail_file |mailx -s\"Subject: TEST!! $subject\" $test_email");  
    }else{
        system("cat $mail_file |mailx -s\"Subject: $subject\" -c $cus_email $arcops_email");  
    }

    $cmd = "rm -rf $mail_file";
    system($cmd);
}

