#!/usr/bin/perl 

BEGIN
{
    #$ENV{SYBASE}   = "/soft/SYBASE15.7";
    $ENV{SYBASE}   = "/soft/SYBASE16.0";
    $ENV{LANG}     = "en_US.UTF-8";
    $ENV{LC_CTYPE} = "en_US.UTF-8";
}

use DBI;
use DBD::Sybase;
use CGI qw/:standard :netscape /;

use Fcntl qw(:flock SEEK_END); # Import LOCK_* constants

#########################################################################################
#											                                            #
# orupdate.cgi: display target paramter update status form page				            #
#											                                            #
# R. Kilgard, Jan 30/31 2000								                            #
# This script generates a dynamic webpage for keeping track of updates to		        #
# target parameters.									                                #
#											                                            #
# T. Isobe (isobe@cfa.harvard.edu) Aug 20, 2003						                    #
# added password check function. This distinguish normal users and special users 	    #
# (who are usually GOT owers). The special users can sign off only their own data	    #
#											                                            #
# T. Isobe Mar 23, 2004									                                #
# added a new email send out for si mode sign off					                    #
#											                                            #
#											                                            #
# T. Isobe Nov 01. 2004									                                #
# updated email problem ( http@... was replaced by cus@... etc)				            #
#											                                            #
# T. Isobe Nov 18, 2004									                                #
# changed a temporary writing space to /data/mta4/www/CUs/Usint/Temp			        #
#											                                            #
# T. Isobe Jul 27, 2006									                                #
# cleaning up the script.								                                #
#											                                            #
# T. Isobe Sep 20, 2006									                                #
# add comment check 									                                #
#											                                            #
# T. Isobe Sep 27, 2006									                                #
# add large coordinate shift warning							                        #
#											                                            #
#											                                            #
# T. Isobe Feb 27, 2006									                                #
# change a path to the main CUS page							                        #
#											                                            #
# T. Isobe Dec 08, 2008									                                #
# add TOO/DDT notification								                                #
#											                                            #
# T. Isobe Aug 26, 2009									                                #
# https://icxc.harvard.edu/mta/CUS/ ---> https://icxc.harvard.edu/cus/index.html 	    #
#											                                            #
# T. Isobe Oct 09, 2009									                                #
#   mailx function input format modified						                        #
#											                                            #
# T. Isobe Nov 12, 2009									                                #
#   increased efficiency								                                #
#											                                            #
# T. Isobe Dec 17, 2009									                                #
#   added multiple entry indicator etc							                        #
#											                                            #
# T. Isobe Dec 29, 2009									                                #
#   added a function to percolate up the user's obsids to the top			            #
#											                                            #
# T. Isobe May 26, 2010									                                #
#    cosmetic change									                                #
#											                                            #
# T. Isobe Feb 25, 2011									                                #
#    directories are now read froma file kept in Info					                #
#											                                            #
# T. Isobe Aug 31, 2011									                                #
#     DDT/TOO final sign off request email notification added				            #
#											                                            #
# T. Isobe Nov 17, 2011									                                #
#    sign off problem fixed (line1441)							                        #
#											                                            #
# T. Isobe Oct 01, 2012									                                #
#    sccs is replaced by flock								                            #
#											                                            #
# T. Isobe Nov 06, 2012									                                #
#    html 5 conformed									                                #
#											                                            #
# T. Isobe Nov 28, 2012									                                #
#    flock bug fixed									                                #
#											                                            #
# T. Isobe Mar 27, 2013									                                #
#    linux transition and https://icxc ---> https://cxc					                #
#                                                                                       #
# T. Isobe Jun 27, 2013                                                                 #
#    mailx's "-r" option removed                                                        #
#                                                                                       #
# T. Isobe Oct  7, 2013									                                #
#    end_body cgi system function commented out						                    #
#											                                            #
# T. Isobe Sep 23, 2014									                                #
#    sybase update (/soft/SYBASE15.7)							                        #
#                                                                                       #
# T. Isobe Apr 24, 2015                                                                 #
# /soft/ascds/DS.release/ots/bin/perl ---> /usr/bin/perl (make accessible from cxc)     #
#                                                                                       #
# T. Isobe Nov 21, 2016                                                                 #
# archive access user changed from borwer to mtaops_internal/public                     #
#											                                            #
# T. Isobe Jan 4 2017                                                                   #
#  HRC mail address changed from juda to kashyap                                        #
#                                                                                       #
# T. Isobe Jun 4, 2019                                                                  #
#  a bug of "verified by" with higher rev # already signed off corrected                #
#                                                                                       #
# T. Isobe Jul 16, 2019                                                                 #
#  a cosmetic update                                                                    #
#                                                                                       #
# T. Isobe Sep 11, 2019                                                                 #
#  an approved button added with a full approval capacity.                              #
#                                                                                       #
#  T. Isobe Sep 24, 2019                                                                #
#  an approved button had a bug Approve --> Update & Approve                            #
#                                                                                       #
# T. Isobe Jul 21, 2020                                                                 #
# sybase 15.7 --> 16.0                                                                  #
#                                                                                       #
# T. Isobe Jan 12, 2021                                                                 #
# minor design change                                                                   #
#                                                                                       #
# T. Isobe Jan 26, 2021                                                                 #
# mailx subject line change                                                             #
#                                                                                       #
# T. Isobe Mar 31, 2021                                                                 #
# TOO/DDT si mode email: send to hrcdude if the instrument is hrc                       #
#                                                                                       #
# T. Isobe Jun 25, 2021                                                                 #
# HRC SI column added/ ACIS column removed                                              #
#                                                                                       #
# T. Isobe Sep 15, 2021                                                                 #
# ACIS column is added back                                                             #
#                                                                                       #
# T. Isobe Sep. 20, 2021                                                                #
# a couple more cosmetic updates                                                        #
#                                                                                       #
#########################################################################################

###############################################################################
#---- before running this script, make sure the following settings are correct.
###############################################################################
#
#---- if this is usint version, set the following param to 'yes', otherwise 'no'
#

#$usint_on = 'yes';                     ##### USINT Version
#$usint_on = 'no';                      ##### USER Version
$usint_on = 'test_yes';                 ##### Test Version USINT
#$usint_on = 'test_no';                 ##### Test Version USER

@color_table = ('#E6E6FA', '#F5F5DC', '#FFDAB9', '#90EE90', '#BDB76B',\
                '#DDA0DD', '#808000', '#FF69B4', '#9ACD32', '#6A5ACD', '#228B22');
#
#--- sot contact email address etc
#
$sot_contact = 'bwargelin@head.cfa.harvard.edu';
$cus_email   = 'cus@head.cfa.harvard.edu';
#
#---- set directory pathes
#
#open(IN, '/data/udoc1/ocat/Info_save/dir_list');
#open(IN, '/proj/web-cxc-dmz/htdocs/mta/CUS/Usint/ocat/Info_save/dir_list');
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
$usint_http   = 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/';      #--- web site for usint users
$main_http    = 'https://cxc.cfa.harvard.edu/cus/index.html';      #--- USINT page
$obs_ss_http  = 'https://cxc.cfa.harvard.edu/cgi-bin/obs_ss/';     #--- web site for none usint users (GO Expert etc)
#$test_http    = 'https://cxc.cfa.harvard.edu/mta/CUS/Obscat/';     #--- web site for test
$test_http    = 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/test_dir'; #--- website for test
############################
#----- end of settings
############################

#---------------------------------------------------------------------
# ----- here are non CXC GTOs who have an access to data modification.
#---------------------------------------------------------------------

@special_user = ("$test_user", 'mta');
$no_sp_user   = 2;

if($usint_on =~ /yes/){
        open(FH, "$pass_dir/usint_users");
        while(<FH>){
                chomp $_;
                @atemp = split(//, $_);
                if($atemp[0] ne '#'){
                        @btemp = split(/\s+/,$_);
                        push(@special_user,  $btemp[0]);
                        push(@special_email, $btemp[1]);
                }
        }
}

$ac_user = $ENV{REMOTE_USER};
#
#---- set a name and email address of a test person
#
$test_user  = $ac_user;
$test_email = $test_user.'@head.cfa.harvard.edu';


print header(-type => 'text/html; charset=utf-8');

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print "<title>Target Parameter Update Status Form</title>";
print "<style  type='text/css'>";
print "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid";
print "border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
#
#--- descriptions for (Dec 16, 2009 changes)
#
print <<ENDOFHTML;
<script>
<!-- hide me

	var text = '<p style="text-align:justify; padding-right:4em"><b>Changes are separated into <em>General</em> ' 
	 + 'and <em>ACIS categories</em> in the ascii <em>OBSID.revision</em> file.  All changes in each category '
	 + 'should be completed before "signing" the form. </b></p> ' 
	 + '<p style="text-align:justify; padding-right:4em"><b>When "signing" a box, it is only necessary to '
	 + 'enter your username. The date is appended automatically.</b></p>'
	 + '<ol style="text-align:justify;margin-left:2em; margin-right:7em;">'
	 + '<li style="padding-bottom:1em"> Different revisions of the same obsid are indicated by the same color marker '
	 + 'on the "OBSID.revision" column.</li>'
	 + '<li style="padding-bottom:1em"> If "<font color=#D2691E>Multiple Revisions Open</font>" is listed in the "Note column" '
	 + '- that particular obsid has multiple revision entries on the table which have not been signed off. Please verify '
	 + 'all earlier revisions before verifying the latest one.</li>'
	 + '<li style="padding-bottom:1em"> If "<font color=#4B0082>Higher Rev # Was Already Signed Off</font>" is listed '
	 + 'in the "Note column"  - that particular obsid has had a newer entry already signed off. '
	 + 'Please verify all versions of the obsid on the table, as the newest one (which was already signed off) supersedes '
	 + 'all previous revisions.</li>'
	 + '<li style="padding-bottom:1em"> If you are the owner of the entry - you can clear all these out-of-date entries '
	 + 'by signing in the "Verified by" column, even if general obscat, ACIS obscat, or SI Mode edits columns are not signed '
	 + 'off yet.  Any of the unsigned column entries will be recorded as "N/A" in the database.</li>'
     +'<li style="padding-bottom:1em">If multiple observations are ready to be "Verified" (e.g., all other fields '
     + 'are signed off), you can fill all "Verified by" fields and "Update" all '
     + 'of them at once. </li>'

	 //+ '<li style="padding-bottom:1em"> There is a new button "Regroup by Obsids" on the right top corner of the table. '
	 //+ 'This rearranges the table so that all entries are regrouped by obsids, and makes it easy to see all open revisions '
	 //+ 'for an obsid. You can go back to (reversed) time ordered table by clicking "Arranged by Date of Submission" button '
	 //+ '(when you are on Obsid grouped table). </li>'
	 //+ '<li style="padding-bottom:1em">If you are a submitter, type your ID in the "Your User ID" box, and click "Submit" '
	 //+ '(or Regrouping button). It will percolate up all your obsids to the top of the list. </li>'
	 + '</ol>'

function WindowOpen(){

        var new_window =
                window.open("","name","height=600,width=800,scrollbars=yes,resizable=yes","true");

        new_window.document.writeln('<html><head><title>Description</title></head><body>');
        new_window.document.write(text);
        new_window.document.writeln('</body></html>');
        new_window.document.close();
        new_window.focus();
}

//show me  -->
</script>

ENDOFHTML

print "</head>";
print "<body style='color:#000000;background-color:#FFFFE0'>";

#-------------------
#--- starting a form
#-------------------

print start_form();
#if-then block for page generation without password checks


special_user();


#-------------------------------------------------------
#----- go to the main part to print a verification page
#----- check whether there are any changes, if there are
#----- go into update_info sub to update the table
#-------------------------------------------------------

$ap_cnt     = param('ap_cnt');
@name_list  = ();
@value_list = ();
$chk_cnt    = 0;
for($k = 0; $k < $ap_cnt; $k++){
	$name  = param("pass_name.$k");
	$value = param("$name");
	push(@name_list,  $name);
	push(@value_list, $value);
	if($value =~ /\w/){
		$chk_cnt++;
	}
}
if($chk_cnt > 0){
	update_info();		# this sub update updates_table.list
}

orupdate_main();		# this sub creates and displays a html page



print end_form();
print end_html();


#########################################################################
### special_user: check whether the user is a special user            ###
#########################################################################

sub special_user{
	$sp_user = 'no';
	OUTER:
	foreach $comp (@special_user){
		$user = lc ($ac_user);
		if($ac_user eq $comp){
			$sp_user = 'yes';
			last OUTER;
		}
	}
}

#########################################################################
### pi_check: check whether pi has an access to the data              ###
#########################################################################

sub pi_check{
	$user_i = 0;
	$luser  = lc($ac_user);
	$luser  =~ s/\s+//g;

        open(FH, "$pass_dir/user_email_list");
        while(<FH>){
                chomp $_;
                @atemp = split(/\s+/, $_);
		if($luser eq $atemp[2]){
			$usr_last_name     = $atemp[0];
			$usr_first_name    = $atemp[1];
			$usr_email_address = $atemp[3];
		}
        }
        close(FH);

	open(FH, "$obs_ss/access_list");
	@user_data_list = ();
	while(<FH>){
		chomp $_;
		@dtemp = split(/\s+/, $_);
		@etemp = split(/:/,$dtemp[3]);
		@ftemp = split(/:/,$dtemp[4]);

		if(($usr_last_name eq $etemp[0] && $usr_first_name eq $etemp[1])
			 || ($usr_last_name eq $ftemp[0] && $usr_first_name eq $ftemp[1])){
			push(@user_data_list, $dtemp[0]);
		}
	}
	close(FH);
}

#########################################################################
### get_too_ddt_values: get too/ddt related values from database     ####
#########################################################################

sub get_too_ddt_values {

#----------------------------------------------------------------------
#----- to access sybase, we need to set user password and a server name
#----------------------------------------------------------------------

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

#----------------------------------------------
#-----------  get proposal_id from target table
#----------------------------------------------


	$sqlh1 = $dbh1->prepare(qq(select
			type,pre_id  
	from target where obsid=$obsid));
	$sqlh1->execute();
	@targetdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$too_id = $targetdata[0];
	$pre_id = $targetdata[1];
	
	$too_id =~ s/\s+//g;
	$pre_id =~ s/\s+//g;

#--------------------------------------------------------------------
#---- if it is a TOO/DDT observation, mark it for a speical treatment
#--------------------------------------------------------------------

	$too_chk = 0;
	$ddt_chk = 0;
	if($too_id =~ /TOO/i && ($pre_id eq '' || $pre_id !~ /\d/)){
		$too_chk = 1;
	}
	if($too_id =~ /DDT/i && ($pre_id eq '' || $pre_id !~ /\d/)){
		$ddt_chk = 1;
	}
}

###########################################################################
### orupdate_main: printing a verification page                         ###
###########################################################################

##########################################################################
#
#----- this sub is adapted from Kilgard's original orupdate.cgi.
# R. Kilgard, Jan 30/31 2000
# This script generates a dynamic webpage for keeping track of updates to
# target parameters.  
###########################################################################

sub orupdate_main{

$cj      = 0;		#--- counter for the color table 0 - 10.


#
#--- read CDO warning list--- only large coordinate shift case recorded
#
	open(IN, "$ocat_dir/cdo_warning_list");
	@cdo_warning_list = ();
	while(<IN>){
		chomp $_;
		push(@cdo_warning_list, $_);
	}
	close(IN);
#
#--- reverse the list so that the entry can read the most recently entered item first.
#
	@reversed         = reverse (@cdo_warning_list);
	@cdo_warning_list = @reversed;

#------------------------------------------------------------------------------------------
#----@pass_list will hold all editable entries so that we can pass them as parameters later
#------------------------------------------------------------------------------------------

	@pass_list = ();
	if ($usint_on =~ /test/){
		print "<h1>Target Parameter Update Status Form: Test Version</h1>";
		print "<h3> User: $ac_user	---	Directory: $ocat_dir</h3>";
	}else{
		print "<h1>Target Parameter Update Status Form</h1>";
	}
	print "<p style='text-align:justify; padding-right:4em'><strong>";
	print "This form contains all requested updates which ";
    print "have either not been verified or ";
	print "have been verified in the last 24 hours.</strong></p>";
#
    print "<div style='margin-left:20px; margin-right:300px;'>";

    print '<p>';
    print 'The "Update" button will Verify that the requested revisions are complete. ';
    print 'The "Update & Approve" button will Verify and also add that ObsID ';
    print 'to the "Approved List" without having to go back to the Ocat Data Page ';
    print 'and submit "Observation is Approved for flight."';
    print '</p><p>';
    print 'The "Update" button can be used to Verify multiple revisions at once. ';
    print '</p><p>';
    print 'The "Update & Approve" button ONLY applies to the associated "OBSID.revision", ';
    print 'i.e., one at a time.  To Verify and Approve multiple ObsIDs, you can Verify ';
    print 'several at once with "Update" on this page, and then go to the ';
    print '<a href="./express_signoff.cgi">"Express Approval" page</a>.';
    print '</p>';

    print "</div>";

#-------------------------------------------------------------------------------------
#---- a button to rearrnage the entries. one is by obsid, and the other 
#----is by (reversed) submitted time order
#-------------------------------------------------------------------------------------

    print "<div style='float:right;padding-right:20px;'>";

	$reorder = param('reorder');
	$userid  = param('userid');
    print "<b style='padding-bottom:5px;'>Order unverified revisions by:</b><br>";

    print '<ul>';
	if($reorder eq 'Obsids'){
		print "<li><input type=\"submit\" name ='reorder' value=\"Date of Submission\"></li>"; 
        print "<li>Obsids</li>";
	}else{
        print "<li>Date of Submission</li>";
		print "<li><input type=\"submit\" name ='reorder' value=\"Obsids\"></li>"; 
    }
	print "<li><input type=\"submit\" value=\"User ID\"> "; 
	print "<input type=\"text\" size='6' name ='userid' value=\"$userid\"></li>";
    print "</ul>";
    print "<div style='padding-bottom:3px;'></div>";

    print "</div>";


	print '<p style="padding-bottom:20px;">';
    print '<div style="padding-top:1px;"></div>';
    print '<a href="#" onClick="WindowOpen(text);return false;">';
    print '<span style="background-color:black;color:yellow;font-size:150%;"><strong> Help Page </strong></span></a>';
    print '<br>';

	if($usint_on =~ /test/i){
		print "<a href=\"$test_http/rm_submission.cgi/\">";
        print "<b>Remove An Accidental Submission Page</b></a>";
	}else{
		print "<a href=\"$usint_http/rm_submission.cgi/\">";
        print "<b>Remove An Accidental Submission Page</b></a>";
	}
    print '<br>';
	if($usint_on =~ /no/){
		print "<strong><a href=\"$obs_ss_http/index.html\">Verification Page</a></strong> ";
	}else{
		print "<strong><a href=\"$main_http\">";
        print "Go To Chandra Uplink Support Organizational Page</a></strong>";
	}
	print '</p>';

	print hidden(-name=>"reorder", -value=>"$reorder");
	print hidden(-name=>"userid", -value=>"$userid");
	print '<div style="padding-bottom:20px"></div>';

#-----------------------------------------------------------------------------
#--- limit the data reading to the only part which has not been signed off yet
#-----------------------------------------------------------------------------

	@revisions = ();
	system("cat $ocat_dir/updates_table.list | grep NA > $temp_dir/ztemp");
	open (FILE, "$temp_dir/ztemp");
	@revisions = <FILE>;
	system("rm $temp_dir/ztemp");
	close(FILE);

	print "<table border=1>";
	print "<tr><th>OBSID.revision</th>";
    print "<th style='background-color:rgb(0,179,170);'>General edits by</th>";
    print "<th style='background-color:rgb(0,179,170);'>ACIS edits by</th>";
	print "<th>ACIS SI Mode edits by</th><th>HRC SI MODE edits by</th><th>Verified by";
	print "</th><th>&nbsp;</th><th>Note</th></tr>";
#
#---- save "hidden" value pass till the end of the table
#
	@save_dname     = ();
	@save_lnmae     = ();
	@save_lval      = ();
	@save_too_obsid = ();
	@save_too_val   = ();
	@save_ddt_obsid = ();
	@save_ddt_val   = ();
	@pass_name_save = ();
	@pass_name_val  = ();
	@ap_cnt_save	= ();
	@ap_cnt_val   	= ();

#-----------------------------------------------------------------------------------------
#--- keep the record of revision # of each obsid; one is the highest rev # submitted, and 
#--- the other is the highest rev # still open to be signed off.
#-----------------------------------------------------------------------------------------

#---------------------------------------------------------------
#--- first, find rev # of the obsids which need to be signed off
#---------------------------------------------------------------

	@temp_save  = ();
	OUTER3:
	foreach $ent (@revisions){
		@ctemp = split(/\t+/, $ent);
		if($ctemp[5] !~ /NA/){			#--- if it is already "verified", skip
			next OUTER3;
		}
		@dtemp = split(/\./,  $ctemp[0]);
		push(@temp_save, $dtemp[0]);

		$dname = 'data'."$dtemp[0]";
		$rname = 'cnt'."$dtemp[0]";
		if(${$rname} !~ /\d/){
			${$dname} = int($dtemp[1]);
			${$rname} = 1;
		}else{
			${$rname}++;
			if(${$dname} < $dtemp[1]){
				${$dname} = int($dtemp[1]);
			}
		}
	}

#------------------------------------------
#--- make a list of obsids on the open list
#------------------------------------------

	@temp = sort{$a<=>$b}@temp_save;
	$comp = shift(@temp);
	@ob_list = ("$comp");
	OUTER5:
	foreach $ent (@temp){
		foreach $comp (@ob_list){
			if($ent == $comp){
				next OUTER5;
			}
		}
		push(@ob_list, $ent);
	}

#--------------------------------------------------------------------
#--- now find what is the highest rev # opened so far for each obsid
#--------------------------------------------------------------------

	foreach $ent (@ob_list){
		$chk      = "$ocat_dir/updates/$ent".'*';
		$test     = ` ls $chk`;
		$test     =~ s/$ocat_dir\/updates\///g;
		@temp     = split(/\s+/, $test);
		@otemp    = sort{$a<=>$b} @temp;
		$lastone  = pop(@otemp);
		@ltemp    = split(/\./, $lastone);
		$lname    = 'lastrev'."$ent";
		${$lname} = $ltemp[1];

#----------------------------------------------------------------------------
#--- if a rev # which is already "verfied" is higher than the opened rev #'s
#--- mark it so that we can put a notice of the table
#----------------------------------------------------------------------------

		$dname = 'data'."$ent";
		if(${$dname} < $ltemp[1]){
			$ychk = 1;
		}else{
			$ychk = 0;
		}
		$chklist    = 'chk'."$ent";
		${$chklist} = $ychk;

		push(@save_dname, $dname);
		push(@save_lnmae, $lname);
		push(@save_lval,  $ychk);

#-------------------------------------
#--- assign color code for each obsid
#-------------------------------------

		$color = 'color'."$ent";

		$cname = 'cnt'."$ent";			#--- cname has # of opened revisions of the obsid

		if(${$cname} <= 1){
			${$color} = '#FFFFE0';		#--- if it is the newest, just white background
		}else{
			${$color} = $color_table[$cj];
			$cj++;
			if($cj > 10){
				$cj == 0;
			}
		}
			
	}
#---------------------------------------------------------
#----- because log is appended to, rather than added to...
#---------------------------------------------------------

	if($reorder eq 'Obsids'){
		@revisions = sort{$a<=>$b} (@revisions);
	}
	@revisions = reverse(@revisions);

#------------------------------------------------------------------------------
#---- if user id is typed in, percolate all obsids owned by the user to the top
#------------------------------------------------------------------------------

	if($userid =~ /\w/){
		@u_list = ();
		@o_list = ();
		foreach $chk (@revisions){
			@btemp = split(/\t+/, $chk);
			if($btemp[7] =~ /$userid/){
				push(@u_list, $chk);
			}else{
				push(@o_list, $chk);
			}
		}
		@revisions = @u_list;
		foreach $ent (@o_list){
			push(@revisions, $ent);
		}
	}

	$today = `date '+%D'`;
	chop $today;

	ROUTER:
	foreach $line (@revisions){
		chomp $line;
		@values         = split ("\t", $line);

		if($values[5] !~ /NA/){				#--- if it is signed off, removed from our list
			next ROUTER;
		}

		$obsrev         = $values[0];
		@atemp          = split(/\./, $obsrev);
		$obsid          = $atemp[0];
		$general_status = $values[1];
		$acis_status    = $values[2];
		$si_mode_status = $values[3];
		$hrc_si_mode_status = $values[4];               #--- UPDATE 06/24/21
		$dutysci_status = $values[5];
		$seqnum         = $values[6];
		$user           = $values[7];
		@atemp          = split(/\./,$obsrev);
		$tempid         = $atemp[0];

#-------------------------------------------------------------------------
#---- checking whether a ac_user has a permission to sign off the case.
#---- $user and $ac_user could be same, but usually different persons.
#-------------------------------------------------------------------------

		$sign_off = 'no';
		if($sp_user eq 'yes'){ 
			$sign_off = 'yes';
		}else{
			pi_check();
			OUTER:
			foreach $comp (@user_data_list){
				if($obsid == $comp){
					$sign_off = 'yes';
					last OUTER;
				}
			}
		}

		($na0,$na1,$na2,$na3,$na4,$na5,$na6,$na7,$na8,$mtime,$na10,$na11,$na12) 
						= stat "$ocat_dir/updates/$obsrev";
#----------------
#------ get time
#----------------

        $ftime = get_date($mtime);

#----------------------------------------------------------------------------------------------
#---- if dutysci_status is NA (means not signed off yet), print the entry for the verification
#----------------------------------------------------------------------------------------------

		if ($dutysci_status =~/NA/){

#-----------------------------------------
#---- get information about TOO/DDT status
#-----------------------------------------

			get_too_ddt_values();

			if($too_chk > 0){
				$name = "too_status.$obsid";
				push(@save_too_obsid, $name);
				push(@save_too_val,   'Y');
			}elsif($ddt_chk > 0){
				$name = "ddt_status.$obsid";
				push(@save_ddt_obsid, $name);
				push(@save_ddt_val,   'Y');
			}else{
				$name = "too_status.$obsid";
				$name = "ddt_status.$obsid";
				push(@save_too_obsid, $name);
				push(@save_too_val,   'F');
				push(@save_ddt_obsid, $name);
				push(@save_ddt_val,   'F');
			}

#--------------------
#---- OBSID & revison
#--------------------
			$usint_user = 'no';
			OUTER:
			foreach $comp (@special_user){
				if($user eq $comp){
					$usint_user = 'yes';
					last OUTER;
				}
			}
			if($usint_user eq 'no'){
				print '<tr>';
			}else{
				print "<tr>";
			}

#-----------------------------------------
#--- recall info related rev# of the obsid
#-----------------------------------------

			@etemp = split(/\./, $obsrev);
			$rname = 'data'."$etemp[0]";		#-- highest rev # on the open list
			$sname = 'cnt'."$etemp[0]";		    #-- # of rev # open for a given obsid
			$lrev  = 'lastrev'."$etemp[0]";		#-- highest rev # so far for a given obsid
			$hirev = 'chk'."$etemp[0]";		    #-- a marker whether higher rev # already "verified"

			$color = 'color'."$etemp[0]";
			print "<td style='background-color:${$color}'>";

			if($usint_on =~  /no/){
				print "<a href=\"$obs_ss_http/chkupdata.cgi";
			}elsif ($usint_on =~ /test/){
				print "<a href=\"$test_http/chkupdata.cgi";
			}else{
				print "<a href=\"$usint_http/chkupdata.cgi";
			}

			print "\?$obsrev\">$obsrev</a><br />$seqnum<br />$ftime<br />$user</td>";
#--------------------
#----- general obscat
#--------------------
			if ($general_status =~/NULL/){
				    print "<td style='background-color:rgb(0,179,170);'>$general_status</td>";
			} elsif ($general_status =~/NA/){

#----------------------------------------------------------------------------
#----- the case a special user hass a permission to sign off the observation
#----------------------------------------------------------------------------

				if($sp_user eq 'yes'){
					print "<td style='background-color:rgb(0,179,170);'><input type=\"text\" ";
                    print "name=\"general_status#$obsrev\" size=\"12\"></td>";
					push(@pass_list, "general_status#$obsrev");
				}else{
					print "<td style='background-color:rgb(0,179,170);'>---</td>";
				}

			} else {
				print "<td style='background-color:rgb(0,179,170);'>$general_status</td>";
			}
#------------------
#----- acis obscat
#------------------
			if ($acis_status =~/NULL/){
				print "<td style='text-align:center;background-color:rgb(0,179,170);'>$acis_status</td>";
			} elsif ($acis_status =~/NA/){
				if($sp_user eq 'yes'){
					print "<td style='text-align:center;background-color:rgb(0,179,170);'><input type=\"text\"";
                    print " name=\"acis_status#$obsrev\" size=\"12\"></td>";
					push(@pass_list, "acis_status#$obsrev");
				}else{
					print "<td style='text-align:center;background-color:rgb(0,179,170);'>---</td>";
				}
			} else {
				print "<td style='text-align:center;background-color:rgb(0,179,170);'>$acis_status</td>";
			}
#-------------
#----- acis si mode
#-------------
			if ($si_mode_status =~/NULL/){
				print "<td style='text-align:center'>$si_mode_status</td>";
			} elsif ($si_mode_status =~/NA/){
				if($sp_user eq 'yes'){
					print "<td style='text-align:center'><input type=\"text\" ";
                    print " name=\"si_mode_status#$obsrev\" size=\"12\"></td>";
					push(@pass_list, "si_mode_status#$obsrev");
				}else{
						print "<td style='text-align:center'>---</td>";
				}
			} else {
				print "<td style='text-align:center'>$si_mode_status</td>";
			}

#-------------
#----- hrc si mode                  #--- UPEATE 06/24/21
#-------------
			if ($hrc_si_mode_status =~/NULL/){
				print "<td style='text-align:center'>$hrc_si_mode_status</td>";
			} elsif ($hrc_si_mode_status =~/NA/){
				if($sp_user eq 'yes'){
					print "<td style='text-align:center'><input type=\"text\" ";
                    print " name=\"hrc_si_mode_status#$obsrev\" size=\"12\"></td>";
					push(@pass_list, "hrc_si_mode_status#$obsrev");
				}else{
						print "<td style='text-align:center'>---</td>";
				}
			} else {
				print "<td style='text-align:center'>$hrc_si_mode_status</td>";
			}

#------------------
#---- Verification
#------------------

			if ($dutysci_status =~ /NA/){
				if($sign_off eq 'yes'){
					if($sp_user eq 'yes'){
						print "<td style='text-align:center'><input type=\"text\" ";
                        print " name=\"dutysci_status#$obsrev";
						print "\" size=\"12\"></td><td><input type=\"submit\" value=\"Update\">";
#
#--- if the obsrev seems to ready for approval, give the approve button, except
#--- it is already in approved list
#
                        if($general_status ne 'NA' && $acis_status ne 'NA' 
                                    && $si_mode_status ne 'NA' && $hrc_si_mode_status ne 'NA'){
                            $ochk = check_obsid_in_approve($obsid);
                            if($ochk == 0){
						        print "<br /><br /><input type=\"submit\" name=\"approve\" ";
                                print " value=\"Update & Approve\" style='font-size:80%;color:green;";
                                print "width:10em;text-align:left;padding-left:0px;'>";
                                print "<input type=\"hidden\" name=\"seqnum#$obsrev\" value=\"$seqnum\">";
                            }
                        }

						push(@pass_list, "dutysci_status#$obsrev");
					}elsif($general_status ne 'NA' && $acis_status ne 'NA' 
                                    && $si_mode_status ne 'NA' && $hrc_si_mode_status ne 'NA'){
						print "<td style='text-align:center'><input type=\"text\" ";
                        print " name=\"dutysci_status#$obsrev";

						print "\" size=\"12\"></td><td><input type=\"submit\" value=\"Update\">";
						push(@pass_list, "dutysci_status#$obsrev");
					}else{
						print "<td style='text-align:center'><font color='red'>";
                        print "Not Ready for Sign Off</font></td>";
					}
				}else{
					print "<td style='text-align:center'><font color='red'>No Access</font></td>";
					print "<td style='text-align:center'>&#160</td>";
				}
			} else {
				print "<td style='text-align:center'><font color=\"#005C00\">$dutysci_status</font></td>";
				print "<td style='text-align:center'>---</td>";
			}

#---------------------------------------------------------
#---- check whether there is new comment in this obsid/rev
#---------------------------------------------------------

			open(IN, "$ocat_dir/updates/$obsrev");
			$new_comment = 0;
			OUTER:
			while(<IN>){
				chomp $_;
				if($_ =~ /NEW COMMENT/i && ($_ !~ /NA/i || $_!~ /N\/A/i)){
					$new_comment = 1;
					last OUTER;
				}elsif($_ =~ /Below is /){
					last OUTER;
				}
			}
			close(IN);

#----------------------------------------------------------
#--- check whether CDO warning is posted for this obsid/rev
#----------------------------------------------------------

			$large_coord = 0;
			LOUTER:
			foreach $lchk (@cdo_warning_list){
				if($lchk =~ /$obsrev/){
					$large_coord = 1;
					last LOUTER;
				}
			}

#------------------------------------
#--- print a comment in the note area
#------------------------------------

			$bchk = 0;
			if($new_comment == 1 && $large_coord == 0){
				print "<td><span style='color:red'>New Comment</span>";
				$bchk++;
			}elsif($new_comment == 1 && $large_coord == 1){
				print '<td><span style="color:red">New Comment</span><br/>';
				print '<span style="color:blue">Large Coordinates Shift</span>';
				$bchk++;
			}elsif($new_comment == 0 && $large_coord == 1){
				print '<td><span style="color:blue">Large<br/> Coordinates <br/>Shift</span>';
				$bchk++;
			}

#-------------------------------------------------------------------
#---- if there is maltiple resion entries for a given obsid, say so
#-------------------------------------------------------------------

			if(${$sname} > 1){
				if($bchk > 0){
					print '<br><span style="color:#D2691E">Multiple Revisions Open</span>';
				}else{
					print '<td><span style="color:#D2691E">Multiple Revisions Open</span>';
					$bchk++;
				}
			}

#-----------------------------------------------------------------------------------------
#---- if revision newer than any of them listed on the table is already signed off, say so
#-----------------------------------------------------------------------------------------

			if(${$hirev}  > 0){ 
				if($bchk > 0){
					print "<br><span style='color:#4B0082'>Higher Rev # (${$lrev}) ";
                    print "Was Already Signed Off</span>";
				}else{
					print "<td><span style='color:#4B0082'>Higher Rev # (${$lrev}) ";
                    print "Was Already Signed Off</span>";
					$bchk++;
				}
			}
		}

		if($bchk == 0){
			print '<td>&#160;';
		}

		print "</td>";
		print "</tr>";

	}

#-------------------------------
#-----pass the changes as params 
#-------------------------------
	$ap_cnt = 0;
	foreach $ent (@pass_list){
		$name = 'pass_name.'."$ap_cnt";
#		print hidden(-name=>"$name", -value=>"$ent", -override=>"$ent");
		push(@pass_name_save, $name);
		push(@pass_name_val,  $ent);
		$ap_cnt++;
	}
#	print hidden(-name=>'ap_cnt', -value=>"$ap_cnt", override=>"$ap_cnt");
	push(@ap_cnt_save, 'ap_cnt');
	push(@ap_cnt_val,  $ap_cnt);
	
#------------------------------------------------------------------
#--- adding already signed off entries from the past couple of days
#------------------------------------------------------------------

    $yesterday = yesterday_date();

	@recent   = ();
	open (INFILE, "<$ocat_dir/updates_table.list");
	@all_list   = <INFILE>;
	close (INFILE);

	@all_list_reversed = reverse(@all_list);

	$chk = 0;
	$bchk = 0;
	FEND:
	foreach $line (@all_list_reversed){
		if($line !~ /NA/){
			if($line =~ /$date/){
				push(@recent, $line);
			}elsif($line =~ /$yesterday/){
				push(@recent, $line);
			}
		}
		$chk++;
		if($chk > 100){
			last FEND;
		}
	}

	foreach $line (@recent){
		chomp $line;
		@btemp = split(/\t+/, $line);

    		($na0,$na1,$na2,$na3,$na4,$na5,$na6,$na7,$na8,$mtime,$na10,$na11,$na12) 
						= stat "$ocat_dir/updates/$btemp[0]";

            $ftime = get_date($mtime);

		print "<tr>";
		print "<td><a href=\"$usint_http/";
		print "chkupdata.cgi\?$btemp[0]\">$btemp[0]</a><br />$btemp[6]<br />$ftime";
		print "<br />$btemp[7]</td>";

        print "<td style='text-align:center;background-color:rgb(0,179,170);'>$btemp[1]</td>";
        print "<td style='text-align:center;background-color:rgb(0,179,170);'>$btemp[2]</td>";
        print "<td style='text-align:center'>$btemp[3]</td>";
		print "<td style='text-align:center'>$btemp[4]</td>";
        print "<td style='text-align:center;color;#005C00'>";
		print "$btemp[5]</td><td>&nbsp;</td><td>&nbsp;</td></tr>";
	}

	print "</table>";

#
#--- now pass the hidden values to the next round
#
	foreach $dname (@save_dname){
		print hidden(-name=>"$dname", -value=>"${$dname}", -override=>"${$dname}");
	}

	$j = 0;
	foreach $name (@save_too_obsid){
		$val = $save_too_val[$j];
		print hidden(-name=>"$name", -override=>"$val", -value=>"$val");
		$j++;
	}

	$j = 0;
	foreach $name (@save_ddt_obsid){
		$val = $save_ddt_val[$j];
		print hidden(-name=>"$name", -override=>"$val", -value=>"$val");
		$j++;
	}

	$j = 0;
	foreach $name (@pass_name_save){
		$ent = $pass_name_val[$j];
		print hidden(-name=>"$name", -value=>"$ent", -override=>"$ent");
		$j++;
	}

	foreach $ap_cnt (@ap_cnt_val){
		print hidden(-name=>'ap_cnt', -value=>"$ap_cnt", override=>"$ap_cnt");
	}
}  

###################################################################################
###################################################################################
###################################################################################

sub approve_obsid {
    my $date, $obsrev, $obsid, $seqnum, $user;
    ($obsrev) = @_;
    @otemp    = split(/\./, $obsrev);
    $obsid    = $otemp[0];
    $chk      = check_obsid_in_approve($obsid);
    $seqnum   = param("seqnum#$obsrev");
    $user     = param("dutysci_status#$obsrev");
    if($chk  == 0){
        ocat_approve($obsid, $user);
    }
    print "";       #---- keep this to end this sub cleanly
}

###################################################################################
###################################################################################
###################################################################################

sub check_obsid_in_approve{
    my $obsid;
    ($obsid) = @_;

    if($usint_on eq 'yes'){
        open(FH, "/data/mta4/CUS/www/Usint/ocat/approved");
    }else{
        open(FH, "/proj/web-cxc-dmz/cgi-gen/mta/Obscat/ocat/approved");
    }
    while(<FH>){
        chomp $_;
        @atemp = split(/\s+/, $_);
        if($atemp[0] eq $obsid){
            return 1;
            last;
        }
    }
    return 0;
}

###################################################################################
###################################################################################
###################################################################################

sub get_date{

    ($atime) = @_;

    if($atime eq 'today'){
        ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
    }else{
        ($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime($atime);
    }

    @atemp = split(//, $year);
    $uyear = "$atemp[1]"."$atemp[2]";
    $mon++;
    if($mon < 10){
        $mon = '0'."$mon";
    }
    if($mday < 10){
        $mday = '0'."$mday";
    }
    $date = "$mon".'/'."$mday".'/'."$uyear";

    return $date;
}

###################################################################################
###################################################################################
###################################################################################

sub yesterday_date{

	$date = `date '+%D'`;
	chop $date;
	@atemp = split(/\//, $date);
	$atemp[1]--;

	if($atemp[1] == 0){
		$atemp[0]--;
		if($atemp[0] == 0){
			$atemp[2]--;
			$atemp[0] = 12;
			$atemp[1] = 31;
			if($atemp[2] < 10){
				$atemp[2] = int($atemp[2]);
				$atemp[2] = '0'."$atemp[2]";
			}

		}elsif($atemp[0] == 1 || $atemp[0] == 3 || $atemp[0] == 5 || $atemp[0] == 7
    			|| $atemp[0] == 8 || $atemp[0] == 10){
			$atemp[1] = 31;

		}elsif($atemp[0] == 2){
            if(is_leapyear($atemp[2]) == 1){
				$atemp[1] = 29;
			}else{
				$atemp[1] = 28;
			}

		}else{
			$atemp[1] = 30;
		}

		if($atemp[0] < 10){
			$atemp[0] = int($atemp[0]);
			$atemp[0] = '0'."$atemp[0]";
		}
	}
	if($atemp[1] < 10){
		$atemp[1] = int($atemp[1]);
		$atemp[1] = '0'."$atemp[1]";
	}

	my $yesterday = "$atemp[0]/$atemp[1]/$atemp[2]";

    return $yesterday;
}
###################################################################################
### update_info: will perform updates to table                                 ####
###################################################################################

sub update_info {

#--------------------------------------------
#------- foreach parameter entered from table    
#--------------------------------------------

	$incl = 0;
	$date = `date '+%D'`;
	chop $date;

	@newoutput = ();
	$jmod      = 0;

#---------------------------------------------------------------
#--- select out the data line which still needs to be signed off
#---------------------------------------------------------------

	system("cat $ocat_dir/updates_table.list | grep NA > $temp_dir/xtemp");
	open (INFILE, "<$temp_dir/xtemp");
   	@revcopy   = <INFILE>;
   	close (INFILE);
	system("rm $temp_dir/xtemp");

#------------------------------------------------------
#--- name_list contains the signed off cell information
#------------------------------------------------------

	@stat_type = ();
	@obsline   = ();
	@info      = ();
	$ent_cnt   = 0;

	OUTER:
	foreach $param (@name_list) {

#-----------------------------------------------------------
#------- split it, get the type of update and the obsid line
#-----------------------------------------------------------

		@tmp       = split ("#", $param);
		$stat_type = $tmp[0];
		$obsline   = $tmp[1];
		$info      = $value_list[$incl];
		$incl++;
		if($info eq ''){		#----  only when someone signed off, go to the next step
			next OUTER;
		}

		push(@stat_save, $stat_type);
		push(@obs_save,  $obsline);
		push(@info_save, $info);
		$ent_cnt++;
		${gadd.$obsline} = 0;       #--- general case indicator
		${hadd.$obsline} = 0;       #--- acis case indicator
		${madd.$obsline} = 0;       #--- acis si mode indicator
		${padd.$obsline} = 0;       #--- hrc si mode indicator
	}

	for($j = 0; $j < $ent_cnt; $j++){
		$stat_type = $stat_save[$j];
		$obsline   = $obs_save[$j];
		$info      = $info_save[$j];
		
#----------------------------------------------------------------
#------- if there is really a change, make the change	
#----------------------------------------------------------------

		${si_sign.$obsline}   = 0;
		${last_sign.$obsline} = 0;

		NOUTER:
		foreach $newline (@revcopy){
        	chomp $newline;
        	@newvalues         = split ("\t", $newline);
        	$newobsrev         = $newvalues[0];
        	$newgeneral_status = $newvalues[1];
        	$newacis_status    = $newvalues[2];
        	$newsi_mode_status = $newvalues[3];
        	$newhrc_si_mode_status = $newvalues[4];
        	$newdutysci_status = $newvalues[5];
        	$newseqnum         = $newvalues[6];
        	$newuser           = $newvalues[7];

#-------------------------------------------
#---- there is obs id match, change the line
#-------------------------------------------

			if($newobsrev !~ /$obsline/){
				next NOUTER;
			}

    		$jmod++;

#-----------------
#---- general case
#-----------------
			if ($stat_type =~/general/){
				$tline = "$newobsrev\t$info $date\t$newacis_status\t";
                $tline = "$tline"."$newsi_mode_status\t$newhrc_si_mode_status\t";
                $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";
				push (@newoutput, $tline);
				${gadd.$obsline}++;
					
#-------------
#--- acis case
#-------------
            } elsif ($stat_type =~/acis/){
				if(${gadd.$obsline} == 0){
					$tline = "$newobsrev\t$newgeneral_status\t";
                    $tline = "$tline"."$info $date\t$newsi_mode_status\t";
                    $tline = "$tline"."$newhrc_si_mode_status\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}else{
					pop(@newoutput);
					$tline = "$newobsrev\t$info $date\t$info $date\t";
                    $tline = "$tline"."$newsi_mode_status\t$newhrc_si_mode_status\t";
                    $tline = "$tline"."$newdutysci_status\t";
                    $tline = "$tline"."$newseqnum\t$newuser\n";
				}
				push (@newoutput, $tline);
				${hadd.$obsline}++;

#---------------------------------------
#--- if si mode is NA, set email notice
#---------------------------------------

				if($newsi_mode_status =~ /NA/i){
					open(OUT, ">$temp_dir/si_mail.$obsline.tmp");
					print OUT "Please sign off SI Mode for obsid.rev: $newobsrev at: \n";

					if($usint_on =~ /no/){
						print OUT "$obs_ss_http/orupdate.cgi","\n";
					}elsif($usint_on =~ /yes/){
						print OUT "$usint_http/orupdate.cgi","\n";
					}

					print OUT 'This message is generated by a sign-off web page, ';
                    print OUT 'so no reply is necessary.',"\n";
					close(OUT);
					${si_sign.$obsline} = 1;
				}

                if($newhrc_si_mode_status =~ /NA/i){
                    open(OUT, ">$temp_dir/hrc_si_mail.$obsline.tmp");
                    print OUT "Please sign off SI Mode for obsid.rev: $newobsrev at: \n";

                    if($usint_on =~ /no/){
                        print OUT "$obs_ss_http/orupdate.cgi","\n";
                    }elsif($usint_on =~ /yes/){
                        print OUT "$usint_http/orupdate.cgi","\n";
                    }

                    print OUT 'This message is generated by a sign-off web page, ';
                    print OUT 'so no reply is necessary.',"\n";
                    close(OUT);
                    ${si_sign.$obsline} = 1;
                }

#------------------
#--- acis si mode case
#------------------
            } elsif ($stat_type =~/mode/ && $stat_type !~ /hrc/){

				if(${gadd.$obsline} == 0 && ${hadd.$obsline} == 0){
					$tline = "$newobsrev\t$newgeneral_status\t";
                    $tline = "$tline"."$newacis_status\t$info $date\t";
                    $tline = "$tline"."$newhrc_si_mode_status\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}elsif(${gadd.$obsline} != 0 && ${hadd.$obsline} == 0){
					pop(@newoutput);
					$tline = "$newobsrev\t$info $date\t$newacis_status\t";
                    $tline = "$tline"."$info $date\t";
                    $tline = "$tline"."$newhrc_si_mode_status\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}elsif(${gadd.$obsline} == 0 && ${hadd.$obsline} != 0){
					pop(@newoutput);
					$tline = "$newobsrev\t$newgeneral_status\t$info $date\t";
                    $tline = "$tline"."$info $date\t$newhrc_si_mode_status\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}else{
					pop(@newoutput);
					$tline = "$newobsrev\t$info $date\t$info $date\t";
                    $tline = "$tline"."$info $date\t$newhrc_si_mode_status\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";
				}
				push (@newoutput, $tline);
				${madd.$obsline}++;

#------------------
#---- hrc si mode case
#------------------
            } elsif ($stat_type =~/mode/ && $stat_type =~ /hrc/){

				if(${gadd.$obsline} == 0 && ${hadd.$obsline} == 0){
					$tline = "$newobsrev\t$newgeneral_status\t";
                    $tline = "$tline"."$newacis_status\t$newsi_mode_status\t";
                    $tline = "$tline"."$info $date\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}elsif(${gadd.$obsline} != 0 && ${hadd.$obsline} == 0){
					pop(@newoutput);
					$tline = "$newobsrev\t$info $date\t$newacis_status\t";
                    $tline = "$tline"."$newsi_mode_status\t";
                    $tline = "$tline"."$info $date\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}elsif(${gadd.$obsline} == 0 && ${hadd.$obsline} != 0){
					pop(@newoutput);
					$tline = "$newobsrev\t$newgeneral_status\t$info $date\t";
                    $tline = "$tline"."$newsi_mode_status\t$info $date\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";

				}else{
					pop(@newoutput);
					$tline = "$newobsrev\t$info $date\t$info $date\t";
                    $tline = "$tline"."$newsi_mode_status\t$info $date\t";
                    $tline = "$tline"."$newdutysci_status\t$newseqnum\t$newuser\n";
				}
				push (@newoutput, $tline);
				${padd.$obsline}++;

#----------------------
#---- duty sci sign off
#----------------------
    		} elsif ($stat_type =~/dutysci/){

#-------------------------------------------------------------------------------------
#--- if the owner of the entry wants to 'verifiy' it without any of general, 
#--- acis or si mode are signed off s/he can, except the most recent revision.
#-------------------------------------------------------------------------------------

				@rtemp  = split(/\./, $newobsrev);
				$toprev = 'data'."$rtemp[0]";
#
#--- highest rev # currently opened on the table
#
				$rval   = param("$toprev");
#
#--- find the highest rev # already signed off
#
                $vval   = find_highest_rev($rtemp[0]);

                if ($vval > $rval){
                    $rval = $vval;
                }
#
#--- this observation can be closed without a problem
#
                $mchk = 0;
				if(($rval  >  $rtemp[1])  && ($info =~ /$newuser/i)){
					if(${gadd.$obsline} == 0 && $newgeneral_status =~ /NA/){
						$newgeneral_status = "N/A";
					}
					if(${hadd.$obsline} == 0 && $newacis_status =~ /NA/){
						$newacis_status = "N/A";
					}
					if(${madd.$obsline} == 0 && $newsi_mode_status =~ /NA/){
						$newsi_mode_status = "N/A";
					}
					if(${padd.$obsline} == 0 && $newhrc_si_mode_status =~ /NA/){
						$newhrc_si_mode_status = "N/A";
					}
                    $mchk = 1

				}else{
					if($newgeneral_status eq 'NA' 
                            || $newacis_status eq 'NA' 
                            || $newsi_mode_status eq 'NA'
                            || $newhrc_si_mode_status eq 'NA'){
						next NOUTER;
					}
				}

                if(${gadd.$obsline} == 0 && ${hadd.$obsline} == 0){
                    if(${madd.$obsline} != 0){
					    $tline = "$newobsrev\t$newgeneral_status\t$newacis_status\t";
                        $tline = "$tline"."$info $date\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }elsif(${padd.$obsline} != 0){
					    $tline = "$newobsrev\t$newgeneral_status\t$newacis_status\t";
                        $tline = "$tline"."$newsi_mode_status\t$info $date\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }else{
					    $tline = "$newobsrev\t$newgeneral_status\t$newacis_status\t";
                        $tline = "$tline"."$newsi_mode_status\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }

                }elsif(${gadd.$obsline} != 0 && ${hadd.$obsline} == 0){
                    if(${madd.$obsline} != 0){
					    $tline = "$newobsrev\t$info $date\t$newacis_status\t";
                        $tline = "$tline"."$info $date\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }elsif(${padd.$obsline} != 0){
					    $tline = "$newobsrev\t$info $date\t$newacis_status\t";
                        $tline = "$tline"."$newsi_mode_status\t$info $date\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }else{
					    $tline = "$newobsrev\t$info $date\t$newacis_status\t";
                        $tline = "$tline"."$newsi_mode_status\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }

                }elsif(${gadd.$obsline} == 0 && ${hadd.$obsline} != 0){
                    if(${madd.$obsline} != 0){
					    $tline = "$newobsrev\t$newgeneral_status\t$info $date\t";
                        $tline = "$tline"."$info $date\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }elsif(${padd.$obsline} != 0){
					    $tline = "$newobsrev\t$newgeneral_status\t$info $date\t";
                        $tline = "$tline"."$newsi_mode_status\t$info $date\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }else{
					    $tline = "$newobsrev\t$newgeneral_status\t$info $date\t";
                        $tline = "$tline"."$newsi_mode_status\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }

                }else{
                    if(${madd.$obsline} != 0){
					    $tline = "$newobsrev\t$info $date\t$info $date\t";
                        $tline = "$tline"."$info $date\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }elsif(${padd.$obsline} != 0){
					    $tline = "$newobsrev\t$info $date\t$info $date\t";
                        $tline = "$tline"."$newsi_mode_status\t$info $date\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }else{
					    $tline = "$newobsrev\t$info $date\t$info $date\t";
                        $tline = "$tline"."$newsi_mode_status\t$newhrc_si_mode_status\t";
                        $tline = "$tline"."$info $date\t$newseqnum\t$newuser\n";

                    }
                }
                    
				push (@newoutput,$tline);

                ${last_sign.$obsline} = 1;

                open(OUT, ">$temp_dir/dutysci_mail.$obsline.tmp");
                print OUT 'All requested edits have been made for the following obsid.rev',"\n";
                print OUT "$newobsrev\n";
                $achk = param('approve');

                if($achk eq 'Update & Approve'){
                    print OUT "and the observation is sent to the approved list.\n";
                    approve_obsid($newobsrev);

                }else{
				    if($usint_user eq 'no'){
					    print OUT 'This observation will be automatically approved in 24 hrs',"\n";
				    }else{
					    @etemp = split(/\./,$newobsrev);
					    $obsid = $etemp[0];
					    print OUT 'Please remember you still need to approve the observation at:',"\n";
					    print OUT "$usint_http/ocatdata2html.cgi?","$obsid\n";
				    }
                }
                print OUT 'This message is generated by a sign-off web page, ';
                print OUT 'so no reply is necessary.',"\n";
                close(OUT);

                open(FH, "$pass_dir/user_email_list");
                OUTER:
                while(<FH>){
                    chomp $_;
                    @atemp = split(/\s+/, $_);
                    if($atemp[0] eq $newuser){
                        $email_address = $atemp[3];
                        last OUTER;
                    }
                }
                close(FH);
            }


#--------------------------------------------------------------------------
#--- check whether this is a TOO/DDT, and if so, check any status changed.
#--------------------------------------------------------------------------

			@btemp    = split(/\./, $newobsrev);
			$newobsid = $btemp[0];

#-------------
#--- TOO case
#-------------
			$name = "too_status.$newobsid";
			$too_status = param($name);

			if($too_status =~ /Y/i){
#
#--- GENERAL entries signed off
#
				if($stat_type =~/general/){
					if($newacis_status =~ /NA/){
						
						#--- ask to sign off ACIS
						
#						open(OUT, ">$temp_dir/too_gen_change");
#						print OUT "Editing of General entries of $newobsrev ";
#						print OUT "were finished and signed off. ";
#						print OUT "Please  update ACIS entries, then go to: ";
#						print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#						print OUT "and sign off ACIS Status.\n";
#
#						if($usint_on =~ /test/){
#							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: TEST!! TOO ACIS Status Signed Off Request: ";
#							$cmd = "$cmd"."OBSID: $newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#							$cmd = "$cmd"." $test_email";
#							system($cmd);
#						}else{
#							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: TOO ACIS Status Signed Off Request: ";
#							$cmd = "$cmd"."OBSID: $newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#							$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address");
#							system($cmd);
#
#							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: TOO ACIS Status Signed Off Request: ";
#							$cmd = "$cmd"."OBSID: $newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#							$cmd = "$cmd"."$test_email";
#							system($cmd);
#						}
#						system("rm $temp_dir/too_gen_change");

					}else{
						if($newsi_mode_status =~ /NA/ || $newhrc_si_mode_status =~ /NA/){

							#--- ask to sing off SI MODE

							open(OUT, ">$temp_dir/too_gen_change");
							print OUT "Editing of General/ACIS entries of $newobsrev ";
							print OUT "were finished and signed off. ";
							print OUT "Please  update SI Mode entries, then go to: ";
							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
							print OUT "and sign off SI Mode Status.\n";
	
							if($usint_on =~ /test/){
                                $cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TEST!! TOO SI Status Signed Off Request: OBSID: ";
                                $cmd = "$cmd"." $newobsid\"  $test_email";
								system($cmd);

							}else{
                                $inst = find_value('instrument', $obsid);

                                $cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TOO SI Status Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."  $newobsid\"  -ccus\@head.cfa.harvard.edu ";
                                if($inst =~ /ACIS/i){
                                    $cmd = "$cmd"." acisdude\@head.cfa.harvard.edu";
                                }else{
                                    $cmd = "$cmd"." hrcdude\@head.cfa.harvard.edu";
                                }
								system($cmd);

                                $cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TOO SI Status Signed Off Request: OBSID: ";
                                $cmd = "$cmd"." $newobsid\"  $test_email";
                                system($cmd);
							}
							system("rm $temp_dir/too_gen_change");

						}else{
							#--- ask to VERIFY the final status

							open(OUT, ">$temp_dir/too_gen_change");
							print OUT "Editing of all entries of $newobsrev ";
							print OUT "were finished and signed off. ";
							print OUT "Please  verify it, then go to: ";
							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
							print OUT "and sign off 'Verified By' column.\n";
	
							if($usint_on =~ /test/){
                
								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TEST!! TOO Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);

							}else{
								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
                                $cmd = "$cmd"."$email_address";
                                system($cmd);

								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);
							}
							system("rm $temp_dir/too_gen_change");
						}
					}

#				}elsif($stat_type =~ /acis/){
##
##--- ACIS entires signed off
##
#					if($newgeneral_status =~ /NA/){
#
#						#--- ask to sign off GENERAL
#
##						open(OUT, ">$temp_dir/too_gen_change");
##						print OUT "Editing of ACIS entries of $newobsrev ";
##						print OUT "were finished and signed off, but General entries are not yet. ";
##						print OUT "Please  update General entries, then go to: ";
##						print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
##						print OUT "and sign off General Status.\n";
##
##						if($usint_on =~ /test/){
##							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
##							$cmd = "$cmd"."Subject: TOO General Status Signed Off Request: OBSID: ";
##							$cmd = "$cmd"."$newobsid\n\"   $test_email";
##							system($cmd);
##						}else{
##							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
##							$cmd = "$cmd"."Subject: TOO General Status Signed Off Request: OBSID: ";
##							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
##							$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address";
##							system($cmd);
##
##							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
##							$cmd = "$cmd"."Subject: TOO General Status Signed Off Request: OBSID: ";
##							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
##							system($cmd);
##						}
##						system("rm $temp_dir/too_gen_change");
#
#					}else{
#						if($newsi_mode_status =~ /NA/){
#
#							#--- ask to sing off SI MODE
#
#							open(OUT, ">$temp_dir/too_gen_change");
#							print OUT "Editing of ACIS entries of $newobsrev ";
#							print OUT "were finished and signed off. ";
#							print OUT "Please  update SI Mode entries, then go to: ";
#							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#							print OUT "and sign off SI Mode Status.\n";
#	
#							if($usint_on =~ /test/){
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: TOO SI Status Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#							}else{
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: TOO SI Status Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\" -ccus\@head.cfa.harvard.edu ";
#                                $cmd = "$cmd"."acisdude\@head.cfa.harvard.edu";
#                                system($cmd);
#
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: TOO SI Status Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#							}
#							system("rm $temp_dir/too_gen_change");
#
#						}else{
#							#--- ask to VERIFY the final status
#
#							open(OUT, ">$temp_dir/too_gen_change");
#							print OUT "Editing of all entries of $newobsrev ";
#							print OUT "were finished and signed off. ";
#							print OUT "Please  verify it, then go to: ";
#							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#							print OUT "and sign off 'Verified By' column.\n";
#	
#							if($usint_on =~ /test/){
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#
#							}else{
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
#                                $cmd = "$cmd"."$email_address";
#                                system($cmd);
#
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#							}
#							system("rm $temp_dir/too_gen_change");
#						}
#					}
#
				}elsif($stat_type =~ /si_mode/){
#
#--- SI MODE entires signed off
#
					if($newgeneral_status =~ /NA/){

						#--- ask to sign off GENERAL

#						open(OUT, ">$temp_dir/too_gen_change");
#						print OUT "Editing of SI entries of $newobsrev ";
#						print OUT "were finished and signed off, but General entries are not yet. ";
#						print OUT "Please  update General entries, then go to: ";
#						print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#						print OUT "and sign off General Status.\n";
#
#						if($usint_on =~ /test/){
#							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: TOO General Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu  $test_email";
#							system($cmd);
#						}else{
#							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: TOO General Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#							$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address";
#							system($cmd);
#
#							$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: TOO General Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
#							system($cmd);
#						}
#						system("rm $temp_dir/too_gen_change");

					}else{
						if($newacis_status =~ /NA/){

							#---- ask to sign off ACIS

#							open(OUT, ">$temp_dir/too_gen_change");
#							print OUT "Editing of SI Mode entries of $newobsrev ";
#							print OUT "were finished and signed off, but ACIS entires are not. ";
#							print OUT "Please  update ACIS entries, then go to: ";
#							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#							print OUT "and sign off ACIS Status.\n";
#	
#							if($usint_on =~ /test/){
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#								$cmd = "$cmd"."Subject: TOO ACIS Status Signed Off Request: OBSID: ";
#								$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu  $test_email";
#								system($cmd);
#							}else{
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#								$cmd = "$cmd"."Subject: TOO ACIS Status Signed Off Request: OBSID: ";
#								$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#								$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address";
#								system($cmd);
#
#								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
#								$cmd = "$cmd"."Subject: TOO ACIS Status Signed Off Request: OBSID: ";
#								$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
#								system($cmd);
#							}
#							system("rm $temp_dir/too_gen_change");
	
						}else{

							#---- ask to VERIFY the final staus

							open(OUT, ">$temp_dir/too_gen_change");
							print OUT "Editing of all entries of $newobsrev ";
							print OUT "were finished and signed off. ";
							print OUT "Please  verify it, then go to: ";
							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
							print OUT "and sign off 'Verified By' column.\n";
	
							if($usint_on =~ /test/){
								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TEST!! TOO Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);
							}else{
								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\" -ccus\@head.cfa.harvard.edu ";
                                $cmd = "$cmd"."$email_address";
                                system($cmd);

								$cmd = "cat $temp_dir/too_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TOO Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);
							}
							system("rm $temp_dir/too_gen_change");
						}
					}
				}
			}

#-------------
#--- DDT case
#-------------
			$name = "ddt_status.$newobsid";
			$ddt_status = param($name);

			if($ddt_status =~ /Y/i){
#
#--- GENERAL entries signed off
#
				if($stat_type =~/general/){
					if($newacis_status =~ /NA/){
						
						#--- ask to sign off ACIS
						
#						open(OUT, ">$temp_dir/ddt_gen_change");
#						print OUT "Editing of General entries of $newobsrev ";
#						print OUT "were finished and signed off. ";
#						print OUT "Please  update ACIS entries, then go to: ";
#						print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#						print OUT "and sign off ACIS Status.\n";
#
#						if($usint_on =~ /test/){
#							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: DDT ACIS Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu  $test_email";
#							system($cmd);
#						}else{
#							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: DDT ACIS Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#							$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address");
#							system($cmd);
#							
#							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: DDT ACIS Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
#							system($cmd);
#						}
#						system("rm $temp_dir/ddt_gen_change");

					}else{
						if($newsi_mode_status =~ /NA/ || $newhr_si_mode_status =~ /NA/){

							#--- ask to sign off SI MODE

							open(OUT, ">$temp_dir/ddt_gen_change");
							print OUT "Editing of General/ACIS entries of $newobsrev ";
							print OUT "were finished and signed off. ";
							print OUT "Please  update SI Mode entries, then go to: ";
							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
							print OUT "and sign off SI Mode Status.\n";
	
							if($usint_on =~ /test/){
								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TEST!! DDT SI Status Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);

							}else{

                                $inst = find_value('instrument', $obsid);
                                    
								$cmd ="cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: DDT SI Status Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
                                if($inst =~/ACIS/i){
                                    $cmd = "$cmd"."acisdude\@head.cfa.harvard.edu";
                                }else{
                                    $cmd = "$cmd"."hrcdude\@head.cfa.harvard.edu";
                                }
                                system($cmd);

								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: DDT SI Status Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);
							}
							system("rm $temp_dir/ddt_gen_change");

						}else{
							#--- ask to VERIFY the final status

							open(OUT, ">$temp_dir/ddt_gen_change");
							print OUT "Editing of all entries of $newobsrev ";
							print OUT "were finished and signed off. ";
							print OUT "Please  verify it, then go to: ";
							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
							print OUT "and sign off 'Verified By' column.\n";
	
							if($usint_on =~ /test/){
								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TEST!! DDT Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);

							}else{
								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
                                $cmd = "$cmd"."$email_address";
                                system($cmd);

								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);
							}
							system("rm $temp_dir/ddt_gen_change");
						}
					}

#				}elsif($stat_type =~ /acis/){
##
##--- ACIS entires signed off
##
#					if($newgeneral_status =~ /NA/){
#
#						#--- ask to sign off GENERAL
#
##						open(OUT, ">$temp_dir/ddt_gen_change");
##						print OUT "Editing of ACIS entries of $newobsrev ";
##						print OUT "were finished and signed off, but General entries are not yet. ";
##						print OUT "Please  update General entries, then go to: ";
##						print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
##						print OUT "and sign off General Status.\n";
##
##						if($usint_on =~ /test/){
##							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
##							$cmd = "$cmd"."Subject: DDT General Status Signed Off Request: OBSID: ";
##							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu  $test_email";
##							system($cmd);
##						}else{
##							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
##							$cmd = "$cmd"."Subject: DDT General Status Signed Off Request: OBSID: ";
##							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
##							$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address";
##							system($cmd);
##
##							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
##							$cmd = "$cmd"."Subject: DDT General Status Signed Off Request: OBSID: ";
##							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
##							system($cmd);
##						}
##						system("rm $temp_dir/ddt_gen_change");
#
#					}else{
#						if($newsi_mode_status =~ /NA/){
#
#							#--- ask to sing off SI MODE
#
#							open(OUT, ">$temp_dir/ddt_gen_change");
#							print OUT "Editing of ACIS entries of $newobsrev ";
#							print OUT "were finished and signed off. ";
#							print OUT "Please  update SI Mode entries, then go to: ";
#							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#							print OUT "and sign off SI Mode Status.\n";
#	
#							if($usint_on =~ /test/){
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: DDT SI Status Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#
#							}else{
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: DDT SI Status Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
#                                $cmd = "$cmd"."acisdude\@head.cfa.harvard.edu";
#                                system($cmd);
#
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: DDT SI Status Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#							}
#
#							system("rm $temp_dir/ddt_gen_change");
#
#						}else{
#							#--- ask to VERIFY the final status
#
#							open(OUT, ">$temp_dir/ddt_gen_change");
#							print OUT "Editing of all entries of $newobsrev ";
#							print OUT "were finished and signed off. ";
#							print OUT "Please  verify it, then go to: ";
#							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#							print OUT "and sign off 'Verified By' column.\n";
#	
#							if($usint_on =~ /test/){
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#
#							}else{
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
#                                $cmd = "$cmd"."$email_address";
#                                system($cmd);
#
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
#                                $cmd = "$cmd"."$newobsid\"  $test_email";
#                                system($cmd);
#							}
#
#							system("rm $temp_dir/ddt_gen_change");
#						}
#					}
#
				}elsif($stat_type =~ /si_mode/){
#
#--- SI MODE entires signed off
#
					if($newgeneral_status =~ /NA/){

						#--- ask to sign off GENERAL

#						open(OUT, ">$temp_dir/ddt_gen_change");
#						print OUT "Editing of SI entries of $newobsrev ";
#						print OUT "were finished and signed off, but General entries are not yet. ";
#						print OUT "Please  update General entries, then go to: ";
#						print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#						print OUT "and sign off General Status.\n";
#
#						if($usint_on =~ /test/){
#							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: DDT General Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu  $test_email";
#							system($cmd);
#						}else{
#							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: DDT General Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#							$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address";
#							system($cmd);
#
#							$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#							$cmd = "$cmd"."Subject: DDT General Status Signed Off Request: OBSID: ";
#							$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
#							system($cmd);
#						}
#						system("rm $temp_dir/ddt_gen_change");

					}else{
						if($newacis_status =~ /NA/){

							#---- ask to sign off ACIS

#							open(OUT, ">$temp_dir/ddt_gen_change");
#							print OUT "Editing of SI Mode entries of $newobsrev ";
#							print OUT "were finished and signed off, but ACIS entires are not. ";
#							print OUT "Please  update ACIS entries, then go to: ";
#							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
#							print OUT "and sign off ACIS Status.\n";
#	
#							if($usint_on =~ /test/){
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#								$cmd = "$cmd"."Subject: DDT ACIS Status Signed Off Request: OBSID: ";
#								$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu  $test_email";
#								system($cmd);
#							}else{
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#								$cmd = "$cmd"."Subject: DDT ACIS Status Signed Off Request: OBSID: ";
#								$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu ";
#								$cmd = "$cmd"."-ccus\@head.cfa.harvard.edu $email_address");
#								system($cmd);
#
#								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
#								$cmd = "$cmd"."Subject: DDT ACIS Status Signed Off Request: OBSID: ";
#								$cmd = "$cmd"."$newobsid\n\" -rcus\@head.cfa.harvard.edu $test_email";
#								system($cmd);
#							}
#							system("rm $temp_dir/ddt_gen_change");
	
						}else{

							#---- ask to VERIFY the final staus

							open(OUT, ">$temp_dir/ddt_gen_change");
							print OUT "Editing of all entries of $newobsrev ";
							print OUT "were finished and signed off. ";
							print OUT "Please  verify it, then go to: ";
							print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/orupdate.cgi ';
							print OUT "and sign off 'Verified By' column.\n";
	
							if($usint_on =~ /test/){
								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: TEST!! DDT Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);

							}else{
								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  -ccus\@head.cfa.harvard.edu ";
                                $cmd = "$cmd"."$email_address";
                                system($cmd);

								$cmd = "cat $temp_dir/ddt_gen_change|mailx -s\"";
                                $cmd = "$cmd"."Subject: DDT Verification Signed Off Request: OBSID: ";
                                $cmd = "$cmd"."$newobsid\"  $test_email";
                                system($cmd);
							}
							system("rm $temp_dir/ddt_gen_change");
						}
					}
				}
			}
		}
	}
#----------------------------------------------------------------------
#---- start updating the updates_table.list, if there are any changes.
#----------------------------------------------------------------------

	if($jmod >= 0){
	    $lpass = 0;
	    $wtest = 0;
	    my $efile = "$ocat_dir/updates_table.list";

	    OUTER:
	    while($lpass == 0){
	        open(my $update, '+<', $efile) or die "Locked";
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

#------------------------------------------------------
#--- else, if the file is being updated, print an error
#------------------------------------------------------

    				print "<b><font color=\"#FF0000\">ERROR: The update file is ";
                    print "currently being edited by someone else.<br />";
    				print "Please use the back button to return to the previous page, ";
                    print "and resubmit.</font></b>";
    				print "</body>";
    				print "</html>";

#-----------------------------------------------------------------------
#----- if there is an error, exit now so no mail or file writing happens
#-----------------------------------------------------------------------
    				exit();
	            }
            }else{
#--------------------------------------------------------------------------------------------------
#----  if it is not being edited, write update updates_table.list---data for the verificaiton page
#--------------------------------------------------------------------------------------------------

                open (INFILE, "<$efile");
			    @all_list   = <INFILE>;
			    close (INFILE);
			    @all_list_reversed = reverse(@all_list);
                $lpass = 1;
                flock($update, LOCK_EX) or die "died while trying to lock the file<br />\n";
#
#--- count a modified entries
#
			    @temp_head = ();
			    $tcnt      = 0;
			    foreach $ent (@newoutput){
			        @atemp = split(/\s+/, $ent);
				    push(@temp_head, $atemp[0]);
				    $tcnt++;
				}

				@new_list = ();
				$chk = 0;
				FOUTER:
				foreach $line (@all_list_reversed){

				    if($chk < $tcnt){
				        for($m = 0; $m < $tcnt; $m++){
					        if($line =~ /$temp_head[$m]/){
						        push(@new_list, $newoutput[$m]);
							    $chk++;
							    next  FOUTER;
					        }
						}
			        }
			        push(@new_list, $line);
			    }
	
			    @new_list_reversed = reverse(@new_list);
			    foreach $ent (@new_list_reversed){
			        print $update "$ent";
			    }

	            close $update;

#-------------------
#--- sending si mail
#-------------------
                for $e_id (@temp_head){
			        if(${si_sign.$e_id} > 0){
				        if($usint_on =~ /test/){
			                $cmd = "cat $temp_dir/si_mail.$e_id.tmp |mailx -s\"";
                            $cmd = "$cmd"."Subject: TEST!! Signed Off Notice\" ";
                            $cmd = "$cmd"."-rcus\@head.cfa.harvard.edu  $test_email";
                            system($cmd);

						}else{
						    if($acis_status =~ /NULL/){
                                $cmd = "cat $temp_dir/si_mail.$e_id.tmp |mailx -s\"";
                                $cmd = "$cmd"."Subject: Signed Off Notice\"  ";
                                $cmd = "$cmd"."-ccus\@head.cfa.harvard.edu  ";
                                $cmd = "$cmd"."kashyap\@head.cfa.harvard.edu,";
                                $cmd = "$cmd"."dpatnaude\@cfa.harvard.edu";
                                system($cmd);

						    }else{
#                               $cmd = "cat $temp_dir/si_mail.$e_id.tmp |mailx -s\"";
#                               $cmd = "$cmd"."Subject: Signed Off Notice\n\" ";
#                               $cmd = "$cmd"."-rcus\@head.cfa.harvard.edu ";
#                               $cmd = "$cmd"."-ccus\@head.cfa.harvard.edu  ";
#                               $cmd = "$cmd"."acisdude\@head.cfa.harvard.edu";
#                               system($cmd);
						    }
				        }
					    system("rm $temp_dir/si_mail.$e_id.tmp");
	                }
#---------------------------
#--- sending  sign off mail
#---------------------------
                    if(${last_sign.$e_id} > 0 ){
			            if($usint_on =~ /test/){
 	                        $cmd = "cat $temp_dir/dutysci_mail.$e_id.tmp |mailx -s\"";
                            $cmd = "$cmd"."Subject: TEST!! Signed Off Notice\" ";
                            $cmd = "$cmd"."-rcus\@head.cfa.harvard.edu  $test_email";
                            system($cmd);

				        }else{
                            $cmd = "cat $temp_dir/dutysci_mail.$e_id.tmp |mailx -s\"";
                            $cmd = "$cmd"."Subject: Signed Off Notice\"  -c  ";
                            $cmd = "$cmd"."cus\@head.cfa.harvard.edu  $email_address";
                            system($cmd);

                   	        $cmd = "cat $temp_dir/dutysci_mail.$e_id.tmp |mailx -s\"";
                            $cmd = "$cmd"."Subject: Signed Off Notice\" $test_email";
                            system($cmd);
                        }
                        system("rm $temp_dir/dutysci_mail.$e_id.tmp");
                    }
		        }
            }
        }
    }
}

#################################################################################
#################################################################################
#################################################################################

sub ocat_approve{
    ($obsid, $submitter) = @_;
#
#--- other emai address
    $dutysci     = $submitter;
#
#--- read poc email address and create a hash table
#
    %poc_email;
    $poc_email{'mta'} = "$test_email";

    open(FH, "$pass_dir/usint_users");
    while(<FH>){
        chomp $_;
        @atemp = split(//,$_);
        if($atemp[0] ne '#'){
            @btemp = split(/\s+/,$_);
            $poc_email{$btemp[0]} = $btemp[1];
        }
    }
#
#--- set html pages
#
    $usint_http   = 'https://icxc.cfa.harvard.edu/mta/CUS/Usint/';      #--- web site for usint users
#
#
#--- start main part
#
#--- read database for this obsid
#
    read_databases();
#
#--- choice of "asis" is only "ASIS"
#
    $asis = 'ASIS';

    prep_submit();                          # sub to  print a modification check page
    
    submit_entry();
    
    oredit();
#
#--- if the observation is in an active OR list, send warning to MP
#
    open(IN, "$obs_ss/scheduled_obs_list");
    
    while(<IN>){
	    chomp $_;
	    @mtemp = split(/\s+/, $_);
        $comp  = $mtemp[0];
        chomp $comp;
        if ($obsid == $comp){
	        send_email_to_mp();
            last;
        }
    }
    close(IN);
#
#--- check approved obsids is actually in apporved list and send out email to the user
#
#    check_apporved_list();
}

################################################################################
### sub read_databases: read out values from databases                       ###
################################################################################

sub read_databases{

        $web = $ENV{'HTTP_REFERER'};
        if($web =~ /icxc/){
            $db_user   = "mtaops_internal_web";
            $db_passwd =`cat $pass_dir/.targpass_internal`;
        }else{
            $db_user = "mtaops_public_web";
            $db_passwd =`cat $pass_dir/.targpass_public`;
        }
        chop $db_passwd;
        $server  = "ocatsqlsrv";

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
                tooid, constr_in_remarks, group_id, obs_ao_str, roll_flag, window_flag, 
                spwindow_flag, multitelescope_interval
        from target where obsid=$obsid));

        $sqlh1->execute();
        @targetdata = $sqlh1->fetchrow_array;
        $sqlh1->finish;

#--------------------------------------------------------------------------
#------- fill values from target table
#------- doing this the long way so I can see what I'm doing and make sure
#------- everything is accounted for
#--------------------------------------------------------------------------

        $targid                         = $targetdata[1];
        $seq_nbr                        = $targetdata[2];
        $targname                       = $targetdata[3];
        $obj_flag                       = $targetdata[4];
        $object                         = $targetdata[5];
        $si_mode                        = $targetdata[6];
        $photometry_flag                = $targetdata[7];
        $vmagnitude                     = $targetdata[8];
        $ra                             = $targetdata[9];
        $dec                            = $targetdata[10];
        $est_cnt_rate                   = $targetdata[11];
        $forder_cnt_rate                = $targetdata[12];
        $y_det_offset                   = $targetdata[13];
        $z_det_offset                   = $targetdata[14];
        $raster_scan                    = $targetdata[15];
        $dither_flag                    = $targetdata[16];
        $approved_exposure_time         = $targetdata[17];
        $pre_min_lead                   = $targetdata[18];
        $pre_max_lead                   = $targetdata[19];
        $pre_id                         = $targetdata[20];
        $seg_max_num                    = $targetdata[21];
        $aca_mode                       = $targetdata[22];
        $phase_constraint_flag          = $targetdata[23];
        $proposal_id                    = $targetdata[24];
        $acisid                         = $targetdata[25];
        $hrcid                          = $targetdata[26];
        $grating                        = $targetdata[27];
        $instrument                     = $targetdata[28];
        $rem_exp_time                   = $targetdata[29];
        $soe_st_sched_date              = $targetdata[30];
        $type                           = $targetdata[31];
        $lts_lt_plan                    = $targetdata[32];
        $mpcat_star_fidlight_file       = $targetdata[33];
        $status                         = $targetdata[34];
        $data_rights                    = $targetdata[35];
        $tooid                          = $targetdata[36];
        $description                    = $targetdata[37];
        $total_fld_cnt_rate             = $targetdata[38];
        $extended_src                   = $targetdata[39];
        $uninterrupt                    = $targetdata[40];
        $multitelescope                 = $targetdata[41];
        $observatories                  = $targetdata[42];
        $tooid                          = $targetdata[43];
        $constr_in_remarks              = $targetdata[44];
        $group_id                       = $targetdata[45];
        $obs_ao_str                     = $targetdata[46];
        $roll_flag                      = $targetdata[47];
        $window_flag                    = $targetdata[48];
        $spwindow                       = $targetdata[49];
	    $multitelescope_interval	    = $targetdata[50];

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
           undef $pre_min_lead;
           undef $pre_max_lead;
           undef $pre_id;

           $sqlh1 = $dbh1->prepare(qq(select obsid
                from target where group_id = \'$group_id\'));
                $sqlh1->execute();

            while(@group_obsid = $sqlh1->fetchrow_array){
                $group_obsid = join("<td>", @group_obsid);
                @group       = (@group, "<a href=\"\.\/ocatdata2html.cgi\?$group_obsid\"
                                                                            >$group_obsid<\/a> ");
            }

#------  output formatting

            $group_count = 0;
            foreach (@group){
                    $group_count ++;
                    if(($group_count % 10) == 0){
                            @group[$group_count - 1] = "@group[$group_count - 1]<br>";
                    }
            }
            $group_cnt    = $group_count;
            $group_count .= " obsids for ";
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
                    last OUTER;
            }
            $roll_ordr = $rollreq_data[0];
            $roll_ordr =~ s/\s+//g;
        }
        if($roll_ordr =~ /\D/ || $roll_ordr eq ''){
            $roll_ordr = 1;
        }

#-------------------------------------------------
#---- updating AO number for the observation
#---- ao value is different from org and current
#-------------------------------------------------

        $proposal_id =~ s/\s+//g;
        $sqlh1 = $dbh1->prepare(qq(select ao_str
            from prop_info where ocat_propid=$proposal_id ));

        $sqlh1->execute();
        @updatedata   = $sqlh1->fetchrow_array;
        $sqlh1->finish;
        $obs_ao_str = $updatedata[0];
        $obs_ao_str =~ s/\s+//g;

#-----------------------------------------------------------------
#-------- get the rest of the roll requirement data for each order
#-----------------------------------------------------------------

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
                last OUTER;
            }
            $time_ordr = $timereq_data[0];                          # here is time order
            $time_ordr =~ s/\s+//g;
        }
        if($time_ordr =~ /\D/ || $time_ordr eq ''){
            $time_ordr = 1;
        }

#--------------------------------------------------------------
#----- get the rest of the time requirement data for each order
#--------------------------------------------------------------

        for($tordr = 1; $tordr <= $time_ordr; $tordr++){
            $sqlh1 = $dbh1->prepare(qq(select
                    window_constraint, tstart, tstop
            from timereq where ordr = $tordr and obsid=$obsid));
            $sqlh1->execute();
            @timereq_data = $sqlh1->fetchrow_array;
            $sqlh1->finish;

            $window_constraint[$tordr] = $timereq_data[0];
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

#                       hrc_config,hrc_chop_duty_cycle,hrc_chop_fraction,
#                       hrc_chop_duty_no,hrc_zero_block,timing_mode,si_mode
        if ($hrcid){
            $sqlh1 = $dbh1->prepare(qq(select
                    hrc_zero_block,timing_mode,si_mode
            from hrcparam where hrcid=$hrcid));
            $sqlh1->execute();
            @hrcdata = $sqlh1->fetchrow_array;
            $sqlh1->finish;

            $hrc_zero_block      = $hrcdata[0];
            $hrc_timing_mode     = $hrcdata[1];
            $hrc_si_mode         = $hrcdata[2];
        } else {
            $hrc_zero_block      = "N";
            $hrc_timing_mode     = "N";
            $hrc_si_mode         = "NULL";
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

            $exp_mode               = $acisdata[0];
            $ccdi0_on               = $acisdata[1];
            $ccdi1_on               = $acisdata[2];
            $ccdi2_on               = $acisdata[3];
            $ccdi3_on               = $acisdata[4];

            $ccds0_on               = $acisdata[5];
            $ccds1_on               = $acisdata[6];
            $ccds2_on               = $acisdata[7];
            $ccds3_on               = $acisdata[8];
            $ccds4_on               = $acisdata[9];
            $ccds5_on               = $acisdata[10];

            $bep_pack               = $acisdata[11];
            $onchip_sum             = $acisdata[12];
            $onchip_row_count       = $acisdata[13];
            $onchip_column_count    = $acisdata[14];
            $frame_time             = $acisdata[15];

            $subarray               = $acisdata[16];
            $subarray_start_row     = $acisdata[17];
            $subarray_row_count     = $acisdata[18];
            $duty_cycle             = $acisdata[19];
            $secondary_exp_count    = $acisdata[20];

            $primary_exp_time       = $acisdata[21];
            $eventfilter            = $acisdata[22];
            $eventfilter_lower      = $acisdata[23];
            $eventfilter_higher     = $acisdata[24];
            $most_efficient         = $acisdata[25];

            $dropped_chip_count     = $acisdata[26];
            $multiple_spectral_lines = $acisdata[27];
            $spectra_max_count      = $acisdata[28];

#           $bias_after             = $acisdata[27];

#           $secondary_exp_time     = $acisdata[22];
#           $bias_request           = $acisdata[25];
#           $fep                    = $acisdata[27];
#           $subarray_frame_time    = $acisdata[28];
#           $frequency              = $acisdata[30];
        } else {
            $exp_mode               = "NULL";
            $ccdi0_on               = "NULL";
            $ccdi1_on               = "NULL";
            $ccdi2_on               = "NULL";
            $ccdi3_on               = "NULL";
            $ccds0_on               = "NULL";
            $ccds1_on               = "NULL";
            $ccds2_on               = "NULL";
            $ccds3_on               = "NULL";
            $ccds4_on               = "NULL";
            $ccds5_on               = "NULL";
            $bep_pack               = "NULL";
            $onchip_sum             = "NULL";
            $onchip_row_count       = "NULL";
            $onchip_column_count    = "NULL";
            $frame_time             = "NULL";
            $subarray               = "NONE";
            $subarray_start_row     = "NULL";
            $subarray_row_count     = "NULL";
            $subarray_frame_time    = "NULL";
            $duty_cycle             = "NULL";
            $secondary_exp_count    = "NULL";
            $primary_exp_time       = "";
            $eventfilter            = "NULL";
            $eventfilter_lower      = "NULL";
            $eventfilter_higher     = "NULL";
            $spwindow               = "NULL";
#           $bias_request           = "NULL";
            $most_efficient         = "NULL";
#           $fep                    = "NULL";
            $dropped_chip_count     = "NULL";
#           $secondary_exp_time     = "";
#           $frequency              = "NULL";
#           $bias_after             = "NULL";
	        $multiple_spectral_lines = "NULL";
	        $spectra_max_count      = "NULL";
        }

#-------------------------------------------------------------------
#-------  get values from aciswin table
#-------  first, get win_ordr to see how many orders in the database
#-------------------------------------------------------------------

        OUTER:
        for($incl= 1; $incl < 30; $incl++){
            $sqlh1 = $dbh1->prepare(qq(select ordr from aciswin where ordr=$incl and  obsid=$obsid));
            $sqlh1->execute();
            @aciswindata = $sqlh1->fetchrow_array;
            $sqlh1->finish;
            if($aciswindata[0] eq ''){
                last OUTER;
            }
            $ordr  = $aciswindata[0];                       # here is the win_ordr
            $ordr  =~ s/\s+//g;
        }
        if($ordr =~ /\D/ || $ordr eq ''){
            $ordr = 1;
        }
#----------------------------------------------------------------------
#------- get the rest of acis window requirement data from the database
#----------------------------------------------------------------------

        $awc_l_th = 0;
        for($j =1; $j <= $ordr; $j++){
            $sqlh1 = $dbh1->prepare(qq(select
                start_row,start_column,width,height,lower_threshold,
                pha_range,sample,chip,include_flag
            from aciswin where ordr = $j and  obsid=$obsid));
            $sqlh1->execute();
            @aciswindata = $sqlh1->fetchrow_array;
            $sqlh1->finish;

            $start_row[$j]       = $aciswindata[0];
            $start_column[$j]    = $aciswindata[1];
            $width[$j]           = $aciswindata[2];
            $height[$j]          = $aciswindata[3];
            $lower_threshold[$j] = $aciswindata[4];
            if($lower_threshold[$j] > 0.5){
                $awc_l_th = 1;
            }
            $pha_range[$j]       = $aciswindata[5];
            $sample[$j]          = $aciswindata[6];
            $chip[$j]            = $aciswindata[7];
            $include_flag[$j]    = $aciswindata[8];
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

        $sqlh1 = $dbh1->prepare(qq(select soe_roll from soe where obsid=$obsid));
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

#-------------------------------------------------------------
#<<<<<<------>>>>>>  switch to axafusers <<<<<<------>>>>>>>>
#-------------------------------------------------------------

#        $db = "server=$server;database=axafusers";
#        $dsn1 = "DBI:Sybase:$db";
#        $dbh1 = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});
#
#--------------------------------
#-----  get proposer's last name
#--------------------------------
#
#        $sqlh1 = $dbh1->prepare(qq(select
#            last from person_short s,axafocat..prop_info p
#        where p.ocat_propid=$proposal_id and s.pers_id=p.piid));
#        $sqlh1->execute();
#        @namedata = $sqlh1->fetchrow_array;
#        $sqlh1->finish;
#
#        $PI_name = $namedata[0];
#
#---------------------------------------------------------------------------
#------- if there is a co-i who is observer, get them, otherwise it's the pi
#---------------------------------------------------------------------------
#
#        $sqlh1 = $dbh1->prepare(qq(select
#            coi_contact from person_short s,axafocat..prop_info p
#        where p.ocat_propid = $proposal_id));
#        $sqlh1->execute();
#        ($observerdata) = $sqlh1->fetchrow_array;
#        $sqlh1->finish;
#
#        if ($observerdata =~/N/){
#            $Observer = $PI_name;
#        } else {
#            $sqlh1 = $dbh1->prepare(qq(select
#                last from person_short s,axafocat..prop_info p
#            where p.ocat_propid = $proposal_id and p.coin_id = s.pers_id));
#            $sqlh1->execute();
#            ($observerdata) = $sqlh1->fetchrow_array;
#            $sqlh1->finish;

#            $Observer=$observerdata;
#        }

#-------------------------------------------------
#---- Disconnect from the server
#-------------------------------------------------

        $dbh1->disconnect();


#-----------------------------------------------------------------
#------ these ~100 lines are to remove the whitespace from most of
#------ the obscat dump entries.
#-----------------------------------------------------------------
        $targid                 =~ s/\s+//g;
        $seq_nbr                =~ s/\s+//g;
        $targname               =~ s/\s+//g;
        $obj_flag               =~ s/\s+//g;
        if($obj_flag            =~ /NONE/){
                $obj_flag       = "NO";
        }
        $object                 =~ s/\s+//g;
        $si_mode                =~ s/\s+//g;
        $photometry_flag        =~ s/\s+//g;
        $vmagnitude             =~ s/\s+//g;
        $ra                     =~ s/\s+//g;
        $dec                    =~ s/\s+//g;
        $est_cnt_rate           =~ s/\s+//g;
        $forder_cnt_rate        =~ s/\s+//g;
        $y_det_offset           =~ s/\s+//g;
        $z_det_offset           =~ s/\s+//g;
        $raster_scan            =~ s/\s+//g;
        $defocus                =~ s/\s+//g;
        $dither_flag            =~ s/\s+//g;
        $roll                   =~ s/\s+//g;
        $roll_tolerance         =~ s/\s+//g;
        $approved_exposure_time =~ s/\s+//g;
        $pre_min_lead           =~ s/\s+//g;
        $pre_max_lead           =~ s/\s+//g;
        $pre_id                 =~ s/\s+//g;
        $seg_max_num            =~ s/\s+//g;
        $aca_mode               =~ s/\s+//g;
        $phase_constraint_flag  =~ s/\s+//g;
        $proposal_id            =~ s/\s+//g;
        $acisid                 =~ s/\s+//g;
        $hrcid                  =~ s/\s+//g;
        $grating                =~ s/\s+//g;
        $instrument             =~ s/\s+//g;
        $rem_exp_time           =~ s/\s+//g;
        #$soe_st_sched_date     =~ s/\s+//g;
        $type                   =~ s/\s+//g;
        #$lts_lt_plan           =~ s/\s+//g;
        $mpcat_star_fidlight_file =~ s/\s+//g;
        $status                 =~ s/\s+//g;
        $data_rights            =~ s/\s+//g;
        $server_name            =~ s/\s+//g;
        $hrc_zero_block         =~ s/\s+//g;
        $hrc_timing_mode        =~ s/\s+//g;
        $hrc_si_mode            =~ s/\s+//g;
        $exp_mode               =~ s/\s+//g;
#       $standard_chips         =~ s/\s+//g;
        $ccdi0_on               =~ s/\s+//g;
        $ccdi1_on               =~ s/\s+//g;
        $ccdi2_on               =~ s/\s+//g;
        $ccdi3_on               =~ s/\s+//g;
        $ccds0_on               =~ s/\s+//g;
        $ccds1_on               =~ s/\s+//g;
        $ccds2_on               =~ s/\s+//g;
        $ccds3_on               =~ s/\s+//g;
        $ccds4_on               =~ s/\s+//g;
        $ccds5_on               =~ s/\s+//g;
        $bep_pack               =~ s/\s+//g;
        $onchip_sum             =~ s/\s+//g;
        $onchip_row_count       =~ s/\s+//g;
        $onchip_column_count    =~ s/\s+//g;
        $frame_time             =~ s/\s+//g;
        $subarray               =~ s/\s+//g;
        $subarray_start_row     =~ s/\s+//g;
        $subarray_row_count     =~ s/\s+//g;
        $subarray_frame_time    =~ s/\s+//g;
        $duty_cycle             =~ s/\s+//g;
        $secondary_exp_count    =~ s/\s+//g;
        $primary_exp_time       =~ s/\s+//g;
        $secondary_exp_time     =~ s/\s+//g;
        $eventfilter            =~ s/\s+//g;
        $eventfilter_lower      =~ s/\s+//g;
        $eventfilter_higher     =~ s/\s+//g;

	    $multiple_spectral_lines =~ s/\s+//g;
	    $spectra_max_count       =~ s/\s+//g;

        $spwindow               =~ s/\s+//g;
	    $multitelescope_interval=~ s/\s+//g;
        $phase_period           =~ s/\s+//g;
        $phase_epoch            =~ s/\s+//g;
        $phase_start            =~ s/\s+//g;
        $phase_end              =~ s/\s+//g;
        $phase_start_margin     =~ s/\s+//g;
        $phase_end_margin       =~ s/\s+//g;
        $PI_name                =~ s/\s+//g;
        $proposal_number        =~ s/\s+//g;
        $trans_offset           =~ s/\s+//g;
        $focus_offset           =~ s/\s+//g;
        $tooid                  =~ s/\s+//g;
        $description            =~ s/\s+//g;
        $total_fld_cnt_rate     =~ s/\s+//g;
        $extended_src           =~ s/\s+//g;
        $y_amp                  =~ s/\s+//g;
        $y_freq                 =~ s/\s+//g;
        $y_phase                =~ s/\s+//g;
        $z_amp                  =~ s/\s+//g;
        $z_freq                 =~ s/\s+//g;
        $z_phase                =~ s/\s+//g;
        $most_efficient         =~ s/\s+//g;
        $fep                    =~ s/\s+//g;
        $dropped_chip_count     =~ s/\s+//g;
        $timing_mode            =~ s/\s+//g;
        $uninterrupt            =~ s/\s+//g;
        $proposal_joint         =~ s/\s+//g;
        $proposal_hst           =~ s/\s+//g;
        $proposal_noao          =~ s/\s+//g;
        $proposal_xmm           =~ s/\s+//g;
        $roll_obsr              =~ s/\s+//g;
        $multitelescope         =~ s/\s+//g;
        $observatories          =~ s/\s+//g;
        $too_type               =~ s/\s+//g;
        $too_start              =~ s/\s+//g;
        $too_stop               =~ s/\s+//g;
        $too_followup           =~ s/\s+//g;
        $roll_flag              =~ s/\s+//g;
        $window_flag            =~ s/\s+//g;
        $constr_in_remarks      =~ s/\s+//g;
        $group_id               =~ s/\s+//g;
        $obs_ao_str             =~ s/\s+//g;

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
#           $tstart[$k]            =~ s/\s+//g;
#           $tstop[$k]             =~ s/\s+//g;
        }

        for($k = 1; $k <= $ordr; $k++){
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

        $ra   = sprintf("%3.6f", $ra);          # setting to 6 digit after a dicimal point
        $dec  = sprintf("%3.6f", $dec);
        $dra  = $ra;
        $ddec = $dec;

#---------------------------------------------------------------------------
#------- time need to be devided into year, month, day, and time for display
#---------------------------------------------------------------------------

        for($k = 1; $k <= $time_ordr; $k++){
            if($tstart[$k] ne ''){
                $input_time      = $tstart[$k];
                mod_time_format();              # sub mod_time_format changes time format
                $start_year[$k]  = $year;
                $start_month[$k] = $month;
                $start_date[$k]  = $day;
                $start_time[$k]  = $time;
                $tstart[$k]      = "$month:$day:$year:$time";
            }

            if($tstop[$k] ne ''){
                $input_time    = $tstop[$k];
                mod_time_format();
                $end_year[$k]  = $year;
                $end_month[$k] = $month;
                $end_date[$k]  = $day;
                $end_time[$k]  = $time;
                $tstop[$k]     = "$month:$day:$year:$time";
            }
        }

#---------------------------------------------------------------------------------
#------ here are the cases which database values and display values are different.
#---------------------------------------------------------------------------------

        if($multitelescope eq '')    {$multitelescope = 'N'}

        if($proposal_joint eq '')    {$proposal_joint = 'N/A'}

        if($proposal_hst eq '')      {$proposal_hst = 'N/A'}

        if($proposal_noao eq '')     {$proposal_noao = 'N/A'}

        if($proposal_xmm eq '')      {$proposal_xmm = 'N/A'}

        if($rxte_approved_time eq ''){$rxte_approved_time = 'N/A'}

        if($vla_approved_time eq '') {$vla_approved_time = 'N/A'}

        if($vlba_approved_time eq ''){$vlba_approved_time = 'N/A'}


        if($roll_flag    eq 'NULL')     {$droll_flag = 'NULL'}
        elsif($roll_flag eq '')         {$droll_flag = 'NULL'; $roll_flag = 'NULL';}
        elsif($roll_flag eq 'Y')        {$droll_flag = 'YES'}
        elsif($roll_flag eq 'N')        {$droll_flag = 'NO'}
        elsif($roll_flag eq 'P')        {$droll_flag = 'PREFERENCE'}

        if($window_flag    eq 'NULL')   {$dwindow_flag = 'NULL'}
        elsif($window_flag eq '')       {$dwindow_flag = 'NULL'; $window_flag = 'NULL';}
        elsif($window_flag eq 'Y')      {$dwindow_flag = 'YES'}
        elsif($window_flag eq 'N')      {$dwindow_flag = 'NO'}
        elsif($window_flag eq 'P')      {$dwindow_flag = 'PREFERENCE'}

        if($dither_flag    eq 'NULL')   {$ddither_flag = 'NULL'}
        elsif($dither_flag eq '')       {$ddither_flag = 'NULL'; $dither_flag = 'NULL';}
        elsif($dither_flag eq 'Y')      {$ddither_flag = 'YES'}
        elsif($dither_flag eq 'N')      {$ddither_flag = 'NO'}

        if($uninterrupt    eq 'NULL')   {$duninterrupt = 'NULL'}
        elsif($uninterrupt eq '')       {$duninterrupt = 'NULL'; $uninterrupt = 'NULL';}
        elsif($uninterrupt eq 'N')      {$duninterrupt = 'NO'}
        elsif($uninterrupt eq 'Y')      {$duninterrupt = 'YES'}
        elsif($uninterrupt eq 'P')      {$duninterrupt = 'PREFERENCE'}

        if($photometry_flag    eq 'NULL')       {$dphotometry_flag = 'NULL'}
        elsif($photometry_flag eq '')           {$dphotometry_flag = 'NULL'; $photometry_flag = 'NULL'}
        elsif($photometry_flag eq 'Y')          {$dphotometry_flag = 'YES'}
        elsif($photometry_flag eq 'N')          {$dphotometry_flag = 'NO'}

        for($k = 1; $k <= $time_ordr; $k++){
            if($window_constraint[$k]    eq 'Y')   {$dwindow_constraint[$k] = 'CONSTRAINT'}
            elsif($window_constraint[$k] eq 'P')   {$dwindow_constraint[$k] = 'PREFERENCE'}
            elsif($window_constraint[$k] eq 'N')   {$dwindow_constraint[$k] = 'NONE'}
            elsif($window_constraint[$k] eq 'NULL'){$dwindow_constraint[$k] = 'NULL'}
            elsif($window_constraint[$k] eq ''){
                $window_constraint[$k]  = 'NULL';
                $dwindow_constraint[$k] = 'NULL';
            }
        }

        for($k = 1; $k <= $roll_ordr; $k++){
            if($roll_constraint[$k]    eq 'Y')   {$droll_constraint[$k] = 'CONSTRAINT'}
            elsif($roll_constraint[$k] eq 'P')   {$droll_constraint[$k] = 'PREFERENCE'}
            elsif($roll_constraint[$k] eq 'N')   {$droll_constraint[$k] = 'NONE'}
            elsif($roll_constraint[$k] eq 'NULL'){$droll_constraint[$k] = 'NULL'}
            elsif($roll_constraint[$k] eq ''){
                $roll_constraint[$k]  = 'NULL';
                $droll_constraint[$k] = 'NULL';
            }

            if($roll_180[$k]    eq 'Y'){$droll_180[$k] = 'YES'}
            elsif($roll_180[$k] eq 'N'){$droll_180[$k] = 'NO'}
            else{$droll_180[$k] = 'NULL'}
        }

        if($constr_in_remarks eq ''){$dconstr_in_remarks = 'NO'; $constr_in_remarks = 'N'}
        elsif($constr_in_remarks eq 'N'){$dconstr_in_remarks = 'NO'}
        elsif($constr_in_remarks eq 'Y'){$dconstr_in_remarks = 'YES'}
        elsif($constr_in_remarks eq 'P'){$dconstr_in_remarks = 'PREFERENCE'}

        if($phase_constraint_flag eq 'NULL'){$dphase_constraint_flag = 'NULL'}
        elsif($phase_constraint_flag eq '') {
            $dphase_constraint_flag = 'NONE'; $phase_constraint_flag = 'NULL'
        }
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

        if($multitelescope eq 'Y')   {$dmultitelescope = 'YES'}
        elsif($multitelescope eq 'N'){$dmultitelescope = 'NO'}
        elsif($multitelescope eq 'P'){$dmultitelescope = 'PREFERENCE'}

        if($hrc_zero_block eq 'NULL'){$dhrc_zero_block = 'NULL'}
        elsif($hrc_zero_block eq '') {$dhrc_zero_block = 'NO'; $hrc_zero_block = 'N';}
        elsif($hrc_zero_block eq 'Y'){$dhrc_zero_block = 'YES'}
        elsif($hrc_zero_block eq 'N'){$dhrc_zero_block = 'NO'}

        if($hrc_timing_mode eq 'NULL'){$dhrc_timing_mode = 'NULL'}
        elsif($hrc_timing_mode eq '') {$dhrc_timing_mode = 'NO'; $hrc_timing_mode = 'N';}
        elsif($hrc_timing_mode eq 'Y'){$dhrc_timing_mode = 'YES'}
        elsif($hrc_timing_mode eq 'N'){$dhrc_timing_mode = 'NO'}

        if($ordr =~ /\W/ || $ordr == '') {
                $ordr = 1;
        }

        if($most_efficient eq 'NULL'){$dmost_efficient = 'NULL'}
        elsif($most_efficient eq '') {$most_efficient = 'NULL'; $dmost_efficient  = 'NULL'}
        elsif($most_efficient eq 'Y'){$dmost_efficient = 'YES'}
        elsif($most_efficient eq 'N'){$dmost_efficient = 'NO'}

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
#---- ACIS subarray setting
#
        if($subarray eq '')         {$dsubarray = 'NO'}
        elsif($subarray eq 'N')     {$dsubarray = 'NO'}
        elsif($subarray eq 'NONE')  {$dsubarray = 'NO'}
        elsif($subarray eq 'CUSTOM'){$dsubarray = 'YES'}
        elsif($subarray eq 'Y')     {$dsubarray = 'YES'}

        if($duty_cycle eq 'NULL')  {$dduty_cycle = 'NULL'}
        elsif($duty_cycle eq '')   {$dduty_cycle = 'NULL'; $duty_cycle = 'NULL'}
        elsif($duty_cycle eq 'Y')  {$dduty_cycle = 'YES'}
        elsif($duty_cycle eq 'YES'){$dduty_cycle = 'YES'}
        elsif($duty_cycle eq 'N')  {$dduty_cycle = 'NO'}
        elsif($duty_cycle eq 'NO') {$dduty_cycle = 'NO'}

        if($onchip_sum eq 'NULL')  {$donchip_sum = 'NULL'}
        elsif($onchip_sum eq '')   {$donchip_sum = 'NULL'; $onchip_sum = 'NULL'}
        elsif($onchip_sum eq 'Y')  {$donchip_sum = 'YES'}
        elsif($onchip_sum eq 'N')  {$donchip_sum = 'NO'}

        if($eventfilter eq 'NULL') {$deventfilter = 'NULL'}
        elsif($eventfilter eq '')  {$deventfilter = 'NULL'; $eventfilter = 'NULL'}
        elsif($eventfilter eq 'Y') {$deventfilter = 'YES'}
        elsif($eventfilter eq 'N') {$deventfilter = 'NO'}

        if($multiple_spectral_lines eq 'NULL') {$dmultiple_spectral_lines = 'NULL'}
        elsif($multiple_spectral_lines eq '')  {
            $dmultiple_spectral_lines = 'NULL'; $multiple_spectral_lines = 'NULL'
        }
        elsif($multiple_spectral_lines eq 'Y') {$dmultiple_spectral_lines = 'YES'}
        elsif($multiple_spectral_lines eq 'N') {$dmultiple_spectral_lines = 'NO'}

        if($spwindow eq 'NULL')    {$dspwindow = 'NULL'}
        elsif($spwindow eq '' )    {$dspwindow = 'NULL'; $spwindow = 'NULL'}
        elsif($spwindow eq 'Y')    {$dspwindow = 'YES'}
        elsif($spwindow eq 'N')    {$dspwindow = 'NO'}

        if($spwindow eq 'NULL')    {$dspwindow = 'NULL'}
        elsif($spwindow eq '' )    {$dspwindow = 'NULL'; $spwindow = 'NULL'}
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
            UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FALG,VMAGNITUDE,EST_CNT_RATE,
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
            MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,             #--- added 03/29/11
            EVENTFILTER_HIGHER,SPWINDOW,ORDR, FEP,DROPPED_CHIP_COUNT, BIAS_RREQUEST,
            TOO_ID,TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
            REMARKS,COMMENTS,
            MONITOR_FLAG,                           #---- this one is added 3/1/06
            MULTITELESCOPE_INTERVAL			        #---- this one is added 9/2/08
        );

#--------------------------------------------------
#----- all the param names passed between cgi pages
#--------------------------------------------------

        @paramarray = (
            SI_MODE,
            INSTRUMENT,GRATING,TYPE,PI_NAME,OBSERVER,APPROVED_EXPOSURE_TIME,
            RA,DEC,ROLL_OBSR,Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
            DITHER_FLAG,Y_AMP, Y_FREQ, Y_PHASE, Z_AMP, Z_FREQ, Z_PHASE,Y_AMP_ASEC, Z_AMP_ASEC,
            Y_FREQ_ASEC, Z_FREQ_ASEC, UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FALG,
            VMAGNITUDE,EST_CNT_RATE, FORDER_CNT_RATE, TIME_ORDR,WINDOW_FLAG, ROLL_ORDR,ROLL_FLAG,
            CONSTR_IN_REMARKS,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,
            PHASE_START,PHASE_START_MARGIN, PHASE_END,PHASE_END_MARGIN,
            PRE_ID,PRE_MIN_LEAD,PRE_MAX_LEAD,MULTITELESCOPE, OBSERVATORIES,
            MULTITELESCOPE_INTERVAL,
            HRC_CONFIG,HRC_ZERO_BLOCK,HRC_TIMING_MODE,HRC_SI_MODE,
            EXP_MODE,BEP_PACK,FRAME_TIME,MOST_EFFICIENT,
            CCDI0_ON, CCDI1_ON, CCDI2_ON, CCDI3_ON, CCDS0_ON, CCDS1_ON,
            CCDS2_ON, CCDS3_ON,CCDS4_ON, CCDS5_ON,
            SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
            DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
            ONCHIP_SUM,ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
            EVENTFILTER_HIGHER,SPWINDOW,ORDR,
            MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,          #--- added 03/29/11
            REMARKS,COMMENTS, ACISTAG,ACISWINTAG,SITAG,GENERALTAG,
            DROPPED_CHIP_COUNT, GROUP_ID, MONITOR_FLAG
        );

#---------------------------------------------------------------
#----- all the param names passed not editable in ocat data page
#---------------------------------------------------------------

        @passarray = (
            SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,GROUP_ID,OBS_AO_STR,TARGNAME,
            REM_EXP_TIME,RASTER_SCAN,ACA_MODE,
            PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
            PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
            TOO_ID,TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
            FEP,DROPPED_CHIP_COUNT
#--- removed ID
#           SI_MODE,
        );

#--------------------------------------
#----- all the param names in acis data
#--------------------------------------

        @acisarray=(EXP_MODE,BEP_PACK,MOST_EFFICIENT,FRAME_TIME,
            CCDI0_ON,CCDI1_ON,CCDI2_ON,CCDI3_ON,
            CCDS0_ON,CCDS1_ON,CCDS2_ON,CCDS3_ON,CCDS4_ON,CCDS5_ON,
            SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
            DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
            ONCHIP_SUM,
            ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
            EVENTFILTER_HIGHER,DROPPED_CHIP_COUNT,SPWINDOW,
            MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT     #--- added 03/29/11
        );

#---------------------------------------
#----- all the param in acis window data
#---------------------------------------

        @aciswinarray=(START_ROW,START_COLUMN,HEIGHT,WIDTH,LOWER_THRESHOLD,
                       PHA_RANGE,SAMPLE,ORDR,CHIP,
#                       INCLUDE_FLAG
                        );

#-------------------------------------------
#----- all the param in general data dispaly
#-------------------------------------------

        @genarray=(REMARKS,INSTRUMENT,GRATING,TYPE,RA,DEC,APPROVED_EXPOSURE_TIME,
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
            MULTITELESCOPE, OBSERVATORIES,MULTITELESCOPE_INTERVAL, 
            ROLL_CONSTRAINT, WINDOW_CONSTRAINT,
            ROLL_ORDR, TIME_ORDR, ROLL_180,CONSTR_IN_REMARKS,ROLL_FLAG,WINDOW_FLAG,
            MONITOR_FLAG
        );

#-------------------------------
#------ save the original values
#-------------------------------

        foreach $ent (@namearray){
            $lname    = lc ($ent);
#
#--- or the original value, all variable name start from "orig_"
#
            $wname    = 'orig_'."$lname";
            ${$wname} = ${$lname};
        }

#-------------------------------------
#---     special cases
#-------------------------------------

        $orig_ra  = $dra;
        $orig_dec = $ddec;

#----------------------------------------------
#------- special treatment for time constraint
#----------------------------------------------

        $ptime_ordr = $time_ordr + 1;
        for($j = $ptime_ordr; $j < 30; $j++){
            $start_date[$j]  = 'NULL';
            $start_month[$j] = 'NULL';
            $start_year[$j]  = 'NULL';
            $end_date[$j]    = 'NULL';
            $end_month[$j]   = 'NULL';
            $end_year[$j]    = 'NULL';
#           $tstart[$j]      = 'NULL';
#           $tstop[$j]       = 'NULL';
            $tstart[$j]      = '';
            $tstop[$j]       = '';
            $window_constraint[$j] = 'NULL';
        }
        for($j = 1; $j < 30; $j++){
            $orig_start_date[$j]  = $start_date[$j];
            $orig_start_month[$j] = $start_month[$j];
            $orig_start_year[$j]  = $start_year[$j];
            $orig_end_date[$j]    = $end_date[$j];
            $orig_end_month[$j]   = $end_month[$j];
            $orig_end_year[$j]    = $end_year[$j];
            $orig_tstart[$j]      = $tstart[$j];
            $orig_tstop[$j]       = $tstop[$j];
            $orig_window_constraint[$j] = $window_constraint[$j];
        }

#----------------------------------------------
#------ special treatment for roll requirements
#----------------------------------------------
#
#--- make sure that all entries have some values for each order
#
        for($j = 1; $j <= $roll_ordr; $j++){
            if($roll_constraint[$j] eq ''){ $roll_constraint[$j] = 'NULL'}
            if($roll_180[$j] eq ''){$roll_180[$j] = 'NULL'}
        }

        $proll_ordr = $roll_ordr + 1;
#
#--- set default values up to order < 30, assuming that
#
        for($j = $proll_ordr; $j < 30; $j++){ 
            $roll_constraint[$j] = 'NULL';          # we do not get the order larger than 29
            $roll_180[$j]        = 'NULL';
            $roll[$j]            = '';
            $roll_tolerance[$j]  = '';
        }

        for($j = 1; $j < 30; $j++){                     # save them as the original values
            $orig_roll_constraint[$j] = $roll_constraint[$j];
            $orig_roll_180[$j]        = $roll_180[$j];
            $orig_roll[$j]            = $roll[$j];
            $orig_roll_tolerance[$j]  = $roll_tolerance[$j];
        }

#--------------------------------------------
#----- special treatment for acis window data
#--------------------------------------------

        for($j = 1; $j <= $ordr; $j++){
            if($chip[$j] eq '') {$chip[$j] = 'NULL'}
            if($chip[$j] eq 'N'){$chip[$j] = 'NULL'}
            if($include_flag[$j] eq '') {$dinclude_flag[$j] = 'INCLUDE'; $include_flag[$j] = 'I'}
            if($include_flag[$j] eq 'I'){$dinclude_flag[$j] = 'INCLUDE'}
            if($include_flag[$j] eq 'E'){$dinclude_flag[$j] = 'EXCLUDE'}
        }

        $pordr = $ordr + 1;

        for($j = $pordr; $j < 30; $j++){
            $chip[$j] = 'NULL';
            $include_flag[$j] = 'I';
        }

        for($j = 1; $j < 30; $j++){
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
#--------------------------------------------
#--- check planned roll
#--------------------------------------------

        find_planned_roll();

        $scheduled_roll = ${planned_roll.$obsid}{planned_roll}[0];

}

##################################################################################
### prep_submit: preparing the data for submission                             ###
##################################################################################

sub prep_submit{

#----------------------
#----- time order cases
#----------------------

	for($j = 1; $j <= $time_ordr; $j++){
        ($tstart[$j], $chk_start) 
            = change_time_format($start_year[$j], $start_month[$j], $start_date[$j], $start_time[$j]);

        ($tstop[$j], $chk_end) 
            = change_time_format($end_year[$j], $end_month[$j], $end_date[$j], $end_time[$j]);

		$time_ok[$j] = 0;
		if($chk_start != -9999 && $chk_end != -9999){			# check tstop > tstart
			$time_ok[$j] = 1;
			if($chk_end >= $chk_start){
				$time_ok[$j] = 2;
			}
		}
		if($window_constraint[$j] eq 'NONE'){$window_constraint[$j] = 'N'}
		elsif($window_constraint[$j] eq 'NULL'){$window_constraint[$j] = 'NULL'}
		elsif($window_constraint[$j] eq 'CONSTRAINT'){$window_constraint[$j] = 'Y'}
		elsif($window_constraint[$j] eq 'PREFERENCE'){$window_constraint[$j] = 'P'}
	}

#----------------------
#---- roll order cases
#----------------------

	for($j = 1; $j <= $roll_ordr; $j++){
		if($roll_constraint[$j] eq 'NONE'){$roll_constraint[$j] = 'N'}
		elsif($roll_constraint[$j] eq 'NULL'){$roll_constraint[$j] = 'NULL'}
		elsif($roll_constraint[$j] eq 'CONSTRAINT'){$roll_constraint[$j] = 'Y'}
		elsif($roll_constraint[$j] eq 'PREFERENCE'){$roll_constraint[$j] = 'P'}
		elsif($roll_constraint[$j] eq ''){$roll_constraint[$j] = 'NULL'}

		if($roll_180[$j] eq 'NULL'){$roll_180[$j] = 'NULL'}
		elsif($roll_180[$j] eq 'NO'){$roll_180[$j] = 'N'}
		elsif($roll_180[$j] eq 'YES'){$roll_180[$j] = 'Y'}
		elsif($roll_180[$j] eq ''){$roll_180[$j] = 'NULL'}
	}
#-------------------
#--- aciswin cases
#-------------------

	for($j = 1; $j <= $ordr; $j++){
		if($include_flag[$j] eq 'INCLUDE'){$include_flag[$j] = 'I'}
		elsif($include_flag[$j] eq 'EXCLUDE'){$include_flag[$j] = 'E'}
	}
		
#----------------------------------------------------------------
#-- these have different values shown in Ocat Data Page
#-- find database values for them
#----------------------------------------------------------------
	
	if($proposal_joint eq 'NULL'){$proposal_joint = 'NULL'}
	elsif($proposal_joint eq 'YES'){$proposal_joint = 'Y'}
	elsif($proposal_joint eq 'NO'){$proposal_joint = 'N'}
	
	if($roll_flag eq 'NULL'){$roll_flag = 'NULL'}
	elsif($roll_flag eq 'YES'){$roll_flag = 'Y'}
	elsif($roll_flag eq 'NO'){$roll_flag = 'N'}
	elsif($roll_flag eq 'PREFERENCE'){$roll_flag = 'P'}
	
	if($window_flag eq 'NULL'){$window_flag = 'NULL'}
	elsif($window_flag eq 'YES'){$window_flag = 'Y'}
	elsif($window_flag eq 'NO'){$window_flag = 'N'}
	elsif($window_flag eq 'PREFERENCE'){$window_flag = 'P'}
	
	if($dither_flag eq 'NULL'){$dither_flag = 'NULL'}
	elsif($dither_flag eq 'YES'){$dither_flag = 'Y'}
	elsif($dither_flag eq 'NO'){$dither_flag = 'N'}
	
	if($uninterrupt eq 'NULL'){$uninterrupt = 'NULL'}
	elsif($uninterrupt eq 'NO'){$uninterrupt ='N'}
	elsif($uninterrupt eq 'YES'){$uninterrupt ='Y'}
	elsif($uninterrupt eq 'PREFERENCE'){$uninterrupt = 'P'}
	
	if($photometry_flag eq 'NULL'){$photometry_flag = 'NULL'}
	elsif($photometry_flag eq 'YES'){$photometry_flag = 'Y'}
	elsif($photometry_flag eq 'NO'){$photometry_flag = 'N'}

	if($multitelescope eq 'NO'){$multitelescope = 'N'}
	elsif($multitelescope eq 'YES'){$multitelescope = 'Y'}
	elsif($multitelescope eq 'PREFERENCE'){$multitelescope = 'P'}
	
	if($hrc_zero_block eq 'NULL'){$hrc_zero_block = 'NULL'}
	elsif($hrc_zero_block eq 'YES'){$hrc_zero_block = 'Y'}
	elsif($hrc_zero_block eq 'NO'){$hrc_zero_block = 'N'}
	
	if($hrc_timing_mode eq 'NULL'){$hrc_timing_mode = 'NULL'}
	elsif($hrc_timing_mode eq 'YES'){$hrc_timing_mode = 'Y'}
	elsif($hrc_timing_mode eq 'NO'){$hrc_timing_mode = 'N'}
	
	if($most_efficient eq 'NULL'){$most_efficient = 'NULL'}
	elsif($most_efficient eq 'YES'){$most_efficient = 'Y'}
	elsif($most_efficient eq 'NO'){$most_efficient = 'N'}
	
	if($standard_chips eq 'NULL'){$standard_chips = 'NULL'}
	elsif($standard_chips eq 'YES'){$standard_chips = 'Y'}
	elsif($standard_chips eq 'NO'){$standard_chips = 'N'}
	
	if($onchip_sum eq 'NULL'){$onchip_sum = 'NULL'}
	elsif($onchip_sum eq 'YES'){$onchip_sum = 'Y'}
	elsif($onchip_sum eq 'NO'){$onchip_sum = 'N'}
	
	if($duty_cycle eq 'NULL'){$duty_cycle = 'NULL'}
	elsif($duty_cycle eq 'YES'){$duty_cycle = 'Y'}
	elsif($duty_cycle eq 'NO') {$duty_cycle = 'N'}
	
	if($eventfilter eq 'NULL'){$eventfilter = 'NULL'}
	elsif($eventfilter eq 'YES'){$eventfilter = 'Y'}
	elsif($eventfilter eq 'NO'){$eventfilter  = 'N'}

        if($multiple_spectral_lines    eq 'NULL')  {$multiple_spectral_lines = 'NULL'}
        elsif($multiple_spectral_lines eq 'YES')   {$multiple_spectral_lines = 'Y'}
        elsif($multiple_spectral_lines eq 'NO')    {$multiple_spectral_lines = 'N'}
	
	if($spwindow eq 'NULL'){$spwindow = 'NULL'}
	elsif($spwindow eq 'YES'){$spwindow = 'Y'}
	elsif($spwindow eq 'NO'){$spwindow = 'N'}
	
	if($phase_constraint_flag eq 'NULL'){$phase_constraint_flag = 'NULL'}
	elsif($phase_constraint_flag eq 'NONE'){$phase_constraint_flag = 'N'}
	elsif($phase_constraint_flag eq 'CONSTRAINT'){$phase_constraint_flag = 'Y'}
	elsif($phase_constraint_flag eq 'PREFERENCE'){$phase_constraint_flag = 'P'}
	
	if($window_constrint eq 'NONE'){$window_constrint = 'N'}
	elsif($window_constrint eq 'NULL'){$window_constrint = 'NULL'}
	elsif($window_constrint eq 'CONSTRAINT'){$window_constrint = 'Y'}
	elsif($window_constrint eq 'PREFERENCE'){$window_constrint = 'P'}
	
	if($constr_in_remarks eq 'YES'){$constr_in_remarks = 'Y'}
	elsif($constr_in_remarks eq 'PREFERENCE'){$constr_in_remarks = 'P'}
	elsif($constr_in_remarks eq 'NO'){$constr_in_remarks = 'N'}
	
	if($ccdi0_on eq 'NULL'){$ccdi0_on = 'NULL'}
	elsif($ccdi0_on eq 'YES'){$ccdi0_on = 'Y'}
	elsif($ccdi0_on eq 'NO'){$ccdi0_on = 'N'}
	
	if($ccdi1_on eq 'NULL'){$ccdi1_on = 'NULL'}
	elsif($ccdi1_on eq 'YES'){$ccdi1_on = 'Y'}
	elsif($ccdi1_on eq 'NO'){$ccdi1_on = 'N'}
	
	if($ccdi2_on eq 'NULL'){$ccdi2_on = 'NULL'}
	elsif($ccdi2_on eq 'YES'){$ccdi2_on = 'Y'}
	elsif($ccdi2_on eq 'NO'){$ccdi2_on = 'N'}
	
	if($ccdi3_on eq 'NULL'){$ccdi3_on = 'NULL'}
	elsif($ccdi3_on eq 'YES'){$ccdi3_on = 'Y'}
	elsif($ccdi3_on eq 'NO'){$ccdi3_on = 'N'}
	
	if($ccds0_on eq 'NULL'){$ccds0_on = 'NULL'}
	elsif($ccds0_on eq 'YES'){$ccds0_on = 'Y'}
	elsif($ccds0_on eq 'NO'){$ccds0_on = 'N'}
	
	if($ccds1_on eq 'NULL'){$ccds1_on = 'NULL'}
	elsif($ccds1_on eq 'YES'){$ccds1_on = 'Y'}
	elsif($ccds1_on eq 'NO'){$ccds1_on = 'N'}
	
	if($ccds2_on eq 'NULL'){$ccds2_on = 'NULL'}
	elsif($ccds2_on eq 'YES'){$ccds2_on = 'Y'}
	elsif($ccds2_on eq 'NO'){$ccds2_on = 'N'}
	
	if($ccds3_on eq 'NULL'){$ccds3_on = 'NULL'}
	elsif($ccds3_on eq 'YES'){$ccds3_on = 'Y'}
	elsif($ccds3_on eq 'NO'){$ccds3_on = 'N'}
	
	if($ccds4_on eq 'NULL'){$ccds4_on = 'NULL'}
	elsif($ccds4_on eq 'YES'){$ccds4_on = 'Y'}
	elsif($ccds4_on eq 'NO'){$ccds4_on = 'N'}
	
	if($ccds5_on eq 'NULL'){$ccds5_on = 'NULL'}
	elsif($ccds5_on eq 'YES'){$ccds5_on = 'Y'}
	elsif($ccds5_on eq 'NO'){$ccds5_on = 'N'}
	
    $email_address = $poc_email{$submitter};
}

###################################################################################
###################################################################################
###################################################################################

sub change_time_format{
    my $syear, $smonth, $sdate, $stime;
    ($syear, $smonth, $sdate, $stime) = @_;
    my $t_time = 0;

    $smonth    = convert_month_format($smonth);

	if($sdate =~ /\d/ && $smonth =~ /\d/ && $syear =~ /\d/ ){
		@ttemp = split(/:/, $stime);
		$tind = 0;
		$time_ck = 0;
		foreach $tent (@ttemp){
			if($tent =~ /\D/ || $tind eq ''){
				$tind++;
			}else{
				$time_ck = "$time_ck"."$tent";
			}
		}
		if($tind == 0){
			$t_time_new = "$smonth:$sdate:$syear:$stime";
			$ctime = -9999;
			if($t_time_new =~ /\s+/ || $t_time_new == ''){
                print "";
			}else{
				$t_time = $t_time_new;
				$ctime  = "$syear$smonth$sdate$time_ck";
			}
		}
	}
    return $t_time, $ctime;
}
		
###################################################################################
### submit_entry: check and submitting the modified input values                ###
###################################################################################

sub submit_entry{

# counters
	$k = 0;						# acisarray counter
	$l = 0; 					# aciswin array counter
	$m = 0;						# generalarray counter

#------------------------------------------------------
#---- start writing email to the user about the changes
#------------------------------------------------------

	open (FILE, ">$temp_dir/$obsid.tmp");		# a temp file which email to a user written in.

	print FILE "OBSID    = $obsid\n";
	print FILE "SEQNUM   = $seq_nbr\n";
	print FILE "TARGET   = $targname\n";
	print FILE "USERNAME = $submitter\n";
	if($asis eq "ASIS"){
		print FILE "VERIFIED OK AS IS\n";
   	}elsif($asis eq "REMOVE") {
       	print FILE "VERIFIED  REMOVED\n";
   	}

   	print FILE "\n------------------------------------------------------";
    print FILE "------------------------------------\n";
   	print FILE "Below is a full listing of obscat parameter values at the time ";
    print FILE "of submission,\nas well as new";
	print FILE " values submitted from the form.  If there is no value ";
    print FILE "in column 3,\nthen this is an unchangable";
	print FILE " parameter on the form.\nNote that new RA and Dec will be ";
    print FILE "slightly off due to rounding errors in";
	print FILE " double conversion.\n\n";
   	print FILE "PARAM NAME                  ";
    print FILE "ORIGINAL VALUE                ";
    print FILE "REQUESTED VALUE             ";
   	print FILE "\n------------------------------------------------------";
    print FILE "------------------------------------\n";
	
   	close FILE;
 
	format PARAMLINE =
	@<<<<<<<<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        	$nameagain $old_value $current_entry
.
   
	open (PARAMLINE, ">>$temp_dir/$obsid.tmp");
	foreach $nameagain (@paramarray){

		$lc_name = lc ($nameagain);
		$old_name = 'orig_'."$lc_name";
		$old_value = ${$old_name};

    		unless (($lc_name =~/TARGNAME/i)          || ($lc_name =~/TITLE/i)
			    || ($lc_name =~/^WINDOW_CONSTRAINT/i) || ($lc_name =~ /^TSTART/i) 
                || ($lc_name =~/^TSTOP/i)             || ($lc_name =~/^ROLL_CONSTRAINT/i) 
                || ($lc_name =~ /^ROLL_180/i)         || ($lc_name =~/^CHIP/i) 
                || ($lc_name =~ /^INCLUDE_FLAG/i)     || ($lc_name =~ /^START_ROW/i)
			    || ($lc_name =~/^START_COLUMN/i)      || ($lc_name =~/^HEIGHT/i) 
                || ($lc_name =~ /^WIDTH/i)            || ($lc_name =~/^LOWER_THRESHOLD/i) 
                || ($lc_name =~ /^PHA_RANGE/i)        || ($lc_name =~ /^SAMPLE/i)
			    || ($lc_name =~/^SITAG/i)             || ($lc_name =~ /^ACISTAG/i) 
                || ($lc_name =~ /^GENERALTAG/i)       || ($lc_name =~/ASIS/i) 
                || ($lc_name =~ /MONITOR_FLAG/i)
			){  

#---------------------
#---- time order case
#---------------------

			if($lc_name =~ /TIME_ORDR/){
				$current_entry = $oring_time_ordr;
				write (PARAMLINE);
				for($j = 1; $j <= $orig_time_ordr; $j++){
					$nameagain = 'WINDOW_CONSTRAINT'."$j";
					$current_entry = $window_constraint[$j];
					$old_value = $orig_window_constraint[$j];
					write (PARAMLINE);
					$nameagain = 'TSTART'."$j";
					$current_entry = $tstart[$j];
					$old_value = $orig_tstart[$j];
					write (PARAMLINE);
					$nameagain = 'TSTOP'."$j";
					$current_entry = $tstop[$j];
					$old_value = $orig_tstop[$j];
					write (PARAMLINE);
				}

#--------------------
#--- roll order case
#--------------------

			}elsif ($lc_name =~ /ROLL_ORDR/){
				$current_entry = $orig_roll_ordr;
				write(PARAMLINE);
				for($j = 1; $j <= $orig_roll_ordr; $j++){
					$nameagain = 'ROLL_CONSTRAINT'."$j";
					$current_entry = $roll_constraint[$j];
					$old_value = $orig_roll_constraint[$j];
					write(PARAMLINE);
					$nameagain = 'ROLL_180'."$j";
					$current_entry = $roll_180[$j];
					$old_value = $orig_roll_180[$j];
					write (PARAMLINE);

					$nameagain = 'ROLL'."$j";
					$current_entry = $roll[$j];
					$old_value = $orig_roll[$j];
					write (PARAMLINE);
					$nameagain = 'ROLL_TOLERANCE'."$j";
					$current_entry = $roll_tolerance[$j];
					$old_value = $orig_roll_tolerance[$j];
					write (PARAMLINE);
				}

#--------------------------
#--- acis window order case
#--------------------------

			}elsif ($lc_name eq 'ORDR'){
				$current_entry = $orig_ordr;
				write(PARAMLINE);
				for($j = 1; $j <= $orig_ordr; $j++){
					$nameagain = 'CHIP'."$j";
					$current_entry = $chip[$j];
					write(PARAMLINE);
					$nameagain = 'INCLUDE_FLAG'."$j";
					$current_entry = $include_flag[$j];
					write(PARAMLINE);
					$nameagain = 'START_ROW'."$j";
					$current_entry = $start_row[$j];
					write(PARAMLINE);
					$nameagain = 'START_COLUMN'."$j";
					$current_entry = $start_column[$j];
					write(PARAMLINE);
					$nameagain = 'HEIGHT'."$j";
					$current_entry = $height[$j];
					write(PARAMLINE);
					$nameagain = 'WIDTH'."$j";
					$current_entry = $width[$j];
					write(PARAMLINE);
					$nameagain = 'LOWER_THRESHOLD'."$j";
					$current_entry = $lower_threshold[$j];
					write(PARAMLINE);
					$nameagain = 'PHA_RANGE'."$j";
					$current_entry = $pha_range[$j];
					write(PARAMLINE);
					$nameagain = 'SAMPLE'."$j";
					$current_entry = $sample[$j];
					write(PARAMLINE);
				}
        		}else{
                		$current_entry = ${$old_name};
        			write (PARAMLINE);
        		}
    		}
	}
	close PARAMLINE;
}

####################################################################################
### oredit: update approved list, updates_list, updates data, and send out email ###
####################################################################################

sub oredit{

	$date = `date '+%D'`;
	chop $date;
	$on = "ON";

#------------------------------------------------------
#-----  (scan for updates directory) read updates_table.list
#-----  find the revision number for obsid in question
#------------------------------------------------------

        open(UIN, "$ocat_dir/updates_table.list");
        @usave = ();
        $ucnt  = 0;
        while(<UIN>){
            chomp $_;
            if($_ =~ /$obsid\./){
                @utemp = split(/\s+/, $_);
                @vtemp = split(/\./, $utemp[0]);
                $i_val = int ($vtemp[1]);
                push(@usave, $i_val);
                $ucnt++;
            }
        }
        close(UIN);

        @usorted = sort{$a<=>$b} @usave;
        $rev     = int($usorted[$ucnt-1]);
        $rev++;

        if ($rev < 10){
            $rev = "00$rev";
        } elsif (($rev >= 10) && ($rev < 100)){
            $rev = "0$rev";
        }

#-------------------------------------------------
#-----  construct mail to dutysci and CUS archive
#-------------------------------------------------

#------------------
# get the contents
#------------------
	open (OSLOG, "<$temp_dir/$obsid.tmp");
	@oslog = <OSLOG>;
	close (OSLOG);

	open (FILE, ">$temp_dir/ormail_$obsid.tmp");

	$s_yes = 0;
	$s_cnt = 0;
		
	print FILE 'Submitted as "AS IS"---Observation'."  $obsid";
    print FILE ' is added to the approved list',"\n";
	print FILE "@oslog";
	close FILE;

#-----------------------
#-----  get the contents
#-----------------------

	open (OSLOG, "<$temp_dir/$obsid.tmp");
	@oslog = <OSLOG>;
	close (OSLOG);

#-----------------------------
#-----  couple temp variables
#-----------------------------

	$dutysci_status = "NA";
    $general_status = "NULL";			# these are for the status verification page
   	$acis_status    = "NULL";			# orupdate.cgi
   	$si_mode_status = "NULL";
   	$hrc_si_mode_status = "NULL";       #--- UPDATED 06/24/21
	$dutysci_status = "$dutysci $date";
	
	open(ASIN,"$ocat_dir/approved");

	@temp_data = ();
	while(<ASIN>){

		chomp $_;
		push(@temp_data, $_);
	}
	close(ASIN);

	system("mv $ocat_dir/approved $ocat_dir/approved~");

	open(ASIN,">$ocat_dir/approved");

	NEXT:
	foreach $ent (@temp_data){
		@atemp = split(/\t/, $ent);
		if($atemp[0] eq "$obsid"){
			next NEXT;
		}else{
			print ASIN "$ent\n";
		}
	}
	print ASIN "$obsid\t$seq_nbr\t$submitter\t$date\n";
	close(ASIN);
	system("chmod 644 $ocat_dir/approved");

#-------------------------------------
#----  get master log file for editing
#-------------------------------------

    $lpass = 0;
    $wtest = 0;
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
                print "Something is wrong in the submission. ";
                print "Terminating the process.<br />";
                exit();
            }
        }else{
            $lpass = 1;

#--------------------------------------------------------------------------------------------------
#----  if it is not being edited, write update updates_table.list---data for the verificaiton page
#--------------------------------------------------------------------------------------------------

            flock($update, LOCK_EX) or die "died while trying to lock the file<br />\n";
            print $update "$obsid.$rev\tNULL\tNULL\tNULL\tNULL\t$dutysci_status\t";
            print $update "$seq_nbr\t$submitter\n";
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

                system("cp  $temp_dir/$obsid.tmp $ocat_dir/updates/$obsid.$rev");
                last OUTER;
            }
        }
    }

#----------------------------------------------
#----  append arnold update file, if necessary
#----------------------------------------------

    if ($acistag =~/ON/){
   		open (ARNOLD, "<$temp_dir/arnold.tmp");
   		@arnold = <ARNOLD>;
   		close (ARNOLD);
   		$arnoldline = shift @arnold;
    }

#---------------------------#
#----  send messages  ------#
#---------------------------#

    if($usint_on =~ /test/){
        #system("cat $temp_dir/ormail_$obsid.tmp| tr -d '\015'  |mailx -s\"Subject: TEST!! \
        #    Parameter Changes (Approved) log  $obsid.$rev\n\" $test_email");
    }else{
        #system("cat $temp_dir/ormail_$obsid.tmp| tr -d '\015'  |mailx -s\"Subject: \
        #    Parameter Changes (Approved) log  $obsid.$rev\n\" -c$cus_email $email_address");
    }

#--------------------------
#----  get rid of the junk
#--------------------------

    system("rm -f $temp_dir/$obsid.tmp");
    system("rm -f $temp_dir/ormail_$obsid.tmp");
    system("rm -f $temp_dir/arnold.tmp");
}

#####################################################################################
### mod_time_format: convert and devide input data format                         ###
#####################################################################################

sub mod_time_format{
	@tentry = split(/\W+/, $input_time);
	$ttcnt = 0;
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
		$hr_add = 12;
		@tatemp = split(/PM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];

	}elsif($tentry[$ttcnt-1] =~/pm/){
		$hr_add = 12;
		@tatemp = split(/pm/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];

	}elsif($tentry[$ttcnt-1] =~ /AM/){
		@tatemp = split(/AM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];

	}elsif($tentry[$ttcnt-1] =~ /am/){
		@tatemp = split(/AM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];
	}
	
	$mon_lett = 0;
	if($tentry[0] =~ /\D/){
		$day  = $tentry[1];
		$month = $tentry[0];
		$year  = $tentry[2];
		$mon_lett = 1;

	}elsif($tentry[1] =~ /\D/){
		$day  = $tentry[0];
		$month = $tentry[1];
		$year  = $tentry[2];
		$mon_lett = 1;

	}elsif($tentry[0] =~ /\d/ && $tentry[1] =~ /\d/){
		$day  = $tentry[0];
		$month = $tentry[1];
		$year  = $tentry[2];
	}	
	
	$day = int($day);
	if($day < 10){
		$day = '0'."$day";
	}
	
	if($mon_lett > 0){
        $month = convert_month_format($month);
	}
	
	@btemp = split(//,$year);
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
			$hr = $hr + $hr_add;
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
			$hr = $hr + $hr_add;
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

#########################################################################
### lts_date_check:   check ltd_date is in 30 days or not            ####
#########################################################################

sub lts_date_check{
    @mon_days = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334);
	if( $lts_lt_plan eq ''){
		$lts_more30 = 'yes';
	}else{
		@ttemp = split(/\s+/, $lts_lt_plan);
        $month = convert_month_format($ttemp[0]);
        $add   = $mon_day[$month-1];

        if(is_leapyear($ttemp[2]) == 1){
            if($month > 2){
                $add++;
            }
        }
		$comp_date = $ttemp[1] + $add;
		$year = $ttemp[2];
        $dom = find_dom($year, $comp_date);
	
		($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	
		$uyear = 1900 + $year;
        $cdom = find_dom($uyear, $yday);
	
		$lts_more30 = 'yes';
		$diff = $dom - $cdom;
		if($diff < 0){
			$lts_more30 = 'closed';
		}elsif($diff < 30){
			$lts_more30 = 'no';
		}
	}
}

####################################################################
### series_rev: getting mointoring observation things           ####
####################################################################

sub series_rev{
#
#--- this one and the next subs are taken from target_param.cgi
#--- written by Mihoko Yukita.(10/28/2003)
#
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
        %{planned_roll.$ptemp[0]} = (planned_roll =>["$ptemp[1]"]);
    }
    close(PFH);
}

#######################################################################################
### send_email_to_mp: sending email to MP if the obs is in an active OR list        ###
#######################################################################################

sub send_email_to_mp{

	open(IN, "$pass_dir/user_email_list");
#
#--- find out submitter's email address
#
	while(<IN>){
		chomp $_;
		@dtemp = split(/\s+/, $_);
		if($submitter eq $dtemp[0]){
			$email_address = $dtemp[3];
			last;
		}
	}
	close(IN);

    $temp_file = "$temp_dir/mp_request";
    open(ZOUT, ">$temp_file");

    print ZOUT "\n\nA user: $submitter submitted changes/approval of obsid(s):\n\n";

	foreach $ent (@mp_warn_list){
		print ZOUT "$ent\n";
	}

    print ZOUT "\n which is in the current OR list.\n\n";
    print ZOUT "The contact email_address address is: $email_address\n\n";
    print ZOUT "Its Ocat Data Page is:\n";

	foreach $obsid (@mp_warn_list){
       	print ZOUT "$usint_http/ocatdata2html.cgi?$obsid\n\n";
	}
    print ZOUT "\nIf you have any question about this email, please contact $sot_contact.\n\n\n";
#
#--- today's date
#
    $date = get_date('today');

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

    $mp_email = "$mp_contact".'@head.cfa.harvard.edu';

	if($usint_on =~ /test/){
    	$cmd = "cat $temp_file | mailx -s\"";
        $cmd = "$cmd"."Subject: TEST!! Change to Obsids Which Is in Active OR List ";
        $cmd = "$cmd"."($mp_email)\"  $test_email";
        system($cmd);
	}else{
		$cmd = "cat $temp_file | mailx -s\"";
        $cmd = "$cmd"."Subject: Change Obsids Which Is in Active OR List\"  ";
        $cmd = "$cmd"."$mp_email cus\@head.cfa.harvard.edu";
       system($cmd);
	}

    system("rm $temp_file");
}

#########################################################################
## check_apporved_list: check approved obsids and notify the user     ###
#########################################################################

sub check_apporved_list{
#
#----!!!! we are not using this function in orupdate.cgi !!!!
#

	open(FIN, "$ocat_dir/approved");

	@approved_list = ();
	while(<FIN>){
		chomp $_;
		push(@approved_list, $_);
	}
	close(FIN);
	@approved_list = reverse(@approved_list);

	@list1 = ();
	@list2 = ();
	$cnt   = 0;
	OUTER:
	foreach $ent (@obsid_list){
		$chk = 0;
		foreach $comp (@approved_list){
			@btemp = split(/\s+/, $comp);
			if($ent == $btemp[0]){
				push(@list1, $comp);
				$chk = 1;
				next OUTER;
			}	
		}
		if($chk == 0){
			push(@list2, $ent);
			$cnt++;
		}
	}

	open(AOUT, ">$temp_dir/alist.tmp");
	print AOUT "\n\nThe following obsid is added on the approved list.\n\n";
	foreach $ent (@list1){
		print AOUT "$ent\n";
	}
	print AOUT "\n\n";
	if($cnt > 0){
		print AOUT "The following obsid was not added to the approved list.\n";
		print AOUT "You may want to try them again.\n";
		foreach $ent (@list2){
			print AOUT "$ent\n";
		}
	}

	if($usint_on =~ /test/i){
		$cmd = "cat $temp_dir/alist.tmp |mailx -s\"";
        $cmd = "$cmd"."Subject: TEST!! Approved Obsids by  $email_address \"  $test_email";
        system($cmd);
	}else{
		$cmd = "cat $temp_dir/alist.tmp |mailx -s\"";
        $cmd = "$cmd"."Subject: Approved Obsids by $email_address \"  ";
        $cmd = "$cmd"."$email_address  cus\@head.cfa.harvard.edu";
        system($cmd);
	}

	system("rm  $temp_dir/alist.tmp");
}

###################################################################################
###################################################################################
###################################################################################

sub convert_month_format{
    my $smonth;
    ($smonth) = @_;
	if($smonth ne 'NULL'){
		if($smonth eq /^Jan/i){$smonth = '01'}
		elsif($smonth eq /^Feb/i){$smonth = '02'}
		elsif($smonth eq /^Mar/i){$smonth = '03'}
		elsif($smonth eq /^Apr/i){$smonth = '04'}
		elsif($smonth eq /^May/i){$smonth = '05'}
		elsif($smonth eq /^Jun/i){$smonth = '06'}
		elsif($smonth eq /^Jul/i){$smonth = '07'}
		elsif($smonth eq /^Aug/i){$smonth = '08'}
		elsif($smonth eq /^Sep/i){$smonth = '09'}
		elsif($smonth eq /^Oct/i){$smonth = '10'}
		elsif($smonth eq /^Nov/i){$smonth = '11'}
		elsif($smonth eq /^Dec/i){$smonth = '12'}
	}
    return $smonth;
}

###################################################################################
###################################################################################
###################################################################################

sub is_leapyear{

    my $year, $chk, $chk2, $chk3, $val;
    ($year) = @_;
    $chk    = $year %   4;
    $chk2   = $year % 100;
    $chk3   = $year % 400;
    
    $val    = 0;
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

###################################################################################
###################################################################################
###################################################################################

sub find_dom{
    my $year, $yday;
    ($year, $yday) = @_;
    
    $dom = $yday; 
    if($year == 1999){
        $dom -= 202;
    }elsif ($year >= 2000){
        $add = ($year - 1997) /4.0;
        $dom += 163 + ($year - 2000) * 365 + $add;
    }else{
        $dom = 0;
    }

    return $dom;
}

###################################################################################
###################################################################################
###################################################################################

sub find_highest_rev{
    my $obsid;
    ($obsid) = @_;
    if($usint_on eq 'yes'){
        open(FH, '/data/mta4/CUS/www/Usint/ocat/updates_table.list');
    }else{
        open(FH, '/proj/web-cxc-dmz/cgi-gen/mta/Obscat/ocat/updates_table.list');
    }
    @save = ();
    $cnt  = 0;
    while(<FH>){
        chomp $_;
        if($_ =~ /$obsid/){
            @atemp = split(/\./, $_);
            push(@save, $atemp[1]);
            $cnt++;
        }
    }
    close(FH);

    if($cnt > 0){
        @out = sort{$a<=>$b} @save;
        return $out[-1];
    }else{
        return 0;
    }
}

###################################################################################
###################################################################################
###################################################################################

sub find_value{
    my $cname, $obsid;
    ($cname, $obsid) = @_;
    $web = $ENV{'HTTP_REFERER'};
    if($web =~ /icxc/){
        $db_user   = "mtaops_internal_web";
        $db_passwd =`cat $pass_dir/.targpass_internal`;
    }else{
        $db_user = "mtaops_public_web";
        $db_passwd =`cat $pass_dir/.targpass_public`;
    }
    chop $db_passwd;
    $server  = "ocatsqlsrv";

    my $db = "server=$server;database=axafocat";
    $dsn1  = "DBI:Sybase:$db";
    $dbh1  = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});

    $sqlh1 = $dbh1->prepare(qq(select remarks  from target where obsid=$obsid));
    $sqlh1->execute();
    ($remarks) = $sqlh1->fetchrow_array;
    $sqlh1->finish;

    $sqlh1 = $dbh1->prepare(qq(select mp_remarks  from target where obsid=$obsid));
    $sqlh1->execute();
    ($mp_remarks) = $sqlh1->fetchrow_array;
    $sqlh1->finish;

    $sqlh1 = $dbh1->prepare(qq(select $cname from target where obsid=$obsid));

    $sqlh1->execute();
    @targetdata = $sqlh1->fetchrow_array;
    $sqlh1->finish;
    
    $out  = $targetdata[0];
    $out  =~ s/\s+//g;

    $dbh1->disconnect();

    return $out;
}
