#!/usr/bin/perl

BEGIN
{
    $ENV{SYBASE} = "/soft/SYBASE16.0";
} 

use DBI;
use DBD::Sybase;
use CGI qw/:standard :netscape /;

use Fcntl qw(:flock SEEK_END); # Import LOCK_* constants

#################################################################################
#										#
#	express_signoff.cgi: This script let a user to sign off multiple obsids	#
#				 at one process.				#
#										#
#	author: t. isobe (tisobe@cfa.harvard.edu)				#
#										#
#	last update: Feb 01, 2023	           				#
#										#
#################################################################################

#-------------------------------------------------------------------------------
#---- if this is usint version, set the following param to 'yes', otherwise 'no'
#-------------------------------------------------------------------------------

############################
#--- a few settings ....
############################

#$usint_on = 'yes';                     ##### USINT Version
#$usint_on = 'no';                      ##### USER Version
$usint_on = 'test_yes';                 ##### Test Version USINT
#$usint_on = 'test_no';                 ##### Test Version USER

#
#---- set directory paths : updated to read from a file (02/25/2011)
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
$usint_home   = 'https://cxc.cfa.harvard.edu/cus/';                 #--- USINT page
$usint_http   = 'https://cxc.cfa.harvard.edu/cus/Usint';       #--- web site for usint users
$chandra_http = 'https://cxc.cfa.harvard.edu/';                         #--- chandra main web site
$cdo_http     = 'https://icxc.cfa.harvard.edu/cgi-bin/cdo/';        #--- CDO web site

#$test_http    = 'https://cxc.cfa.harvard.edu/cgi-gen/mta/Obscat/';  #--- web site for test    
$test_http    = 'https://cxc.cfa.harvard.edu/cus/Usint/test_dir';  #--- web site for test
$obs_ss_http  = 'https://cxc.cfa.harvard.edu/cgi-bin/obs_ss/';      #--- test site

############################
#----- end of settings
############################

$org_obsid = $ARGV[0];
chomp $org_obsid;

#-------------------------------------------------------------------
#---- read approved list, and check whether this obsid is listed.
#---- if it does, send warning.
#-------------------------------------------------------------------

open(FH, "$ocat_dir/approved");

@app_obsid = ();
while(<FH>){
    chomp $_;
    @atemp = split(/\s+/, $_);
    push(@app_obsid, $atemp[0]);
}
close(FH);

$prev_app = 0;

#--------------------------------------------------------------------
#----- here are non CXC GTOs who have an access to data modification.
#--------------------------------------------------------------------

@special_user  = ("$test_user",  'mta');
@special_email = ("$test_email", "$test_email");
$no_sp_user    = 2;

if($usint_on =~ /yes/){
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
}


$submitter = $ENV{REMOTE_USER};

#
#---- set a name and email address of a test person
#
$test_user  = $submitter;
$test_email = $test_user.'@head.cfa.harvard.edu';



print header(-type => 'text/html;charset=utf-8');

#----------------------------------------------------------------------------------
#------- start printing a html page here.
#------- there are three distinct html page. one is Ocat Data Page (data_input_page),
#------- second is Submit page (prep_submit), and the lastly, Oredit page (oredit).
#----------------------------------------------------------------------------------

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print '<meta charset="UTF-8">';
print "<title>Express Sign Off Page</title>";
print "<style  type='text/css'>";
print "table{text-align:center;margin-left:auto;margin-right:auto;";
print "border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
print "</head>";
print "<body style='color:#000000;background-color:#FFFFE0'>";

print start_form();

$no_access  = 0;                                #--- this indicator used for special user previledge
$send_email = 'yes';

if($usint_on =~ /test/){
#	system("chmod 777 $test_dir/ocat/approved");
#	system("chmod 777 $test_dir/ocat/updates_table.list");
#	system("chmod 777 $test_dir/ocat/updates/*");
}

$check   = param("Check");                      #--- a param which indicates which page to be displayed
$change  = param("Change");
$approve = param("Approve");
$final   = param("Final");
$back    = param("Back");

print hidden(-name=>'send_email', -value=>"$send_email");
print hidden(-name=>'Check',      -value=>"$check");

#-------------------------------------------------
#--------- checking password!
#-------------------------------------------------

$pass  = param("pass");
if($submitter !~ /\w/){
    $submitter = param('submitter');
}
$dutysci = $submitter;

if($email_adress !~ /\w/){
	$email_address = param('email_adress');
}

#New if-then blocks for page generation without password checks


if ($approve !~ /Approve/ && $final !~ /Finalize/ && ($check eq '' || $check =~ /Submit/ || $back =~ /Back to the Previous Page/)){
	input_obsid();

}elsif($approve =~ /Approve/){
#
#--- convert inputted string of obsids list into a list of obsids
#
	$temp       = param("obsid_list");
    @obsid_list = split_string_to_list($temp);
#
#--- read which obsids are in the avtive OR list
#
	open(IN, "$obs_ss/scheduled_obs_list");
	@or_list = ();
	while(<IN>){
		chomp $_;
		@mtemp = split(/\s+/, $_);
		push(@or_list, $mtemp[0]);
	}
	close(IN);

	print "<h2 style='padding-top:20px;padding-bottom:10px'>";
    print "Are you sure to approve the observations of:</h2>";
	print '<table border=1>';
	print '<tr><th>OBSID</th>';
	print '<th>ID</th>';
	print '<th>Seq #</th>';
	print '<th>Title</th>';
	print '<th>Target</th>';
	print '<th>PI</th>';
	print '<th>Note</th></tr>';

	$chk_app  = 0;
	$chk_app2 = 0;
	$chk_app3 = 0;
	$mp_warn_list = '';
	foreach $obsid (@obsid_list){
		OUTER:
		foreach $comp (@app_obsid){
			if($obsid == $comp){
				$chk_app = 1;
				$bgcolor='red';
				last;
			}
		}
		OUTER2:
		foreach $comp (@or_list){
			if($obsid == $comp){
				$chk_app2 = 1;
				$bgcolor2 = 'yellow';
				last;
			}
		}
#
#--- read parameter data from the database
#
		read_databases();

		if($si_mode =~ /blank/i || $si_mode =~ /NULL/i || $si_mode eq '' || $si_mode =~ /\s+/){
			$chk_app3 = 1;
			$bgcolor  = 'orange';
		}

		if($usint_on =~ /test/){
			print "<tr><td style='background-color:$bgcolor'>";
            print "<a href=\"$test_http/ocatdata2html.cgi?$obsid\" target='_blank'>$obsid</td>";

		}elsif($usint_on =~ /yes/){
			print "<tr><td style='background-color:$bgcolor'>";
            print "<a href=\"$usint_http/ocatdata2html.cgi?$obsid\" target='_blank'>$obsid</td>";

		}else{
			print "<tr><td style='background-color:$bgcolor'>";
            print "<a href=\"$obs_ss_http/ocatdata2html.cgi?$obsid\" target='_blank'>$obsid</td>";
		}
		print "<td style='background-color:$bgcolor'>$targid</td>";
		print "<td style='background-color:$bgcolor'>$seq_nbr</td>";
		print "<td style='background-color:$bgcolor'>$proposal_title</td>";
		print "<td style='background-color:$bgcolor'>$targname</td>";
		print "<td style='background-color:$bgcolor'>$PI_name</td>";

		if($chk_app  > 0){
			print "<td style='background-color:$bgcolor'>Already Approved </td></tr>";
			$chk_app     = 0;
			$app_warning = 1;

		}elsif($chk_app2 > 0){
			print "<td style='background-color:$bgcolor2'>in Active OR List</td></tr>";
			$mp_warn_list = "$mp_warn_list:"."$obsid";
			$chk_app2     = 0;

		}elsif($chk_app3 > 0){
			print "<td style='background-color:$bgcolor'>SI Mode Is Not Set</td></tr>";
			$chk_app     = 0;
			$app_warning3= 3;

		}else{
			print "<td>&#160;</td></tr>";
		}
		$bgcolor  = 'white';
		$bgcolor2 = 'white';
	}
	print "</table>";
	
	print hidden(-name=>'obsid_list',   -value=>"$temp");
	print hidden(-name=>'mp_warn_list', -value=>"$mp_warn_list");

	print "<div style='padding-bottom:30px;'></div>";

	if($app_warning > 0){
		print "<h3>The observation marked by<span style='color:red'> ";
        print "red </span>is already in the approved list. ";
		print "Please go back and remove it from the list.</h3>";
	}
	if($app_warning3 > 0){
		print "<h3>The observation marked by<span style='color:orange'> ";
        print "orange </span>is missing SI mode. ";
		print "Please go back and remove it from the list.</h3>";
	}
	if($chk_app == 0 && $chk_app2 == 0 && $chk_app3 == 0){	
		print '<input type="submit" name="Final" value="Finalize">';
	}

	print '<br /><br />';
	print '<input type="submit" name="Back" value="Back to the Previous Page">';
	
}elsif($final =~ /Finalize/){
#
#--- convert inputted string of obsids list into a list of obsids
#
	$temp       = param("obsid_list");
    @obsid_list = split_string_to_list($temp);

	print "<br /><h3>Approving.....  (it may take a few minutes)</h3>";
#
#--- update databases for each obsid as "asis"
#
	foreach $obsid(@obsid_list){

		read_databases();                   #--- read parameters

		$asis = 'ASIS';
		print hidden(-name=>'seq_nbr',-override=>"$seq_nbr", -value=>"$seq_nbr");

		read_name();                        #--- read descriptive name of parameters
		prep_submit();                      #--- sub to  print a modification check page
		submit_entry();                     #--- check and submitting the modified input values
		oredit();                           #---  update approved list etc and send out email
	}
#
#--- if the observation is in an active OR list, send warning to MP
#
	$mp_list      = param('mp_warn_list');
	@atemp        =  split(/:/, $mp_list);
	@mp_warn_list = ();
	$chk          = 0;
	OUTER:
	foreach $obsid (@atemp){
		if($obsid =~ /\d/){
			push(@mp_warn_list, $obsid);
			$chk++;
		}
	}
	if($chk > 0){
		send_email_to_mp();
	}
#
#--- check approved obsids is actually in apporved list and send out email to the user
#
	check_apporved_list();

#
#--- notify the user the task is done and display the ending message.
#
    print "";
    print "<h2 style='padding-bottom:15px'>ALL DONE!!</h2>";
    print "<h3 style='padding-bottom:30px'>You should receive confirmation email shortly.</h3>";

	if($usint_on =~ /test/){
		if($org_obsid =~ /\d/){
			print "<h3>Back to <a href=\"$test_http/ocatdata2html.cgi?$org_obsid\">";
            print "Ocat Data Page (obsid: $org_obsid)</a>";
		}

        	print "<h3>Back to <a href=\"$test_http/express_signoff.cgi\">";
            print "Top of Express Approval Page</a></h3>";

	}elsif($usint_on =~ /yes/i){

		if($org_obsid =~ /\d/){
			print "<h3>Back to <a href=\"$usint_http/ocatdata2html.cgi?$org_obsid\">";
            print "Ocat Data Page (obsid: $org_obsid)</a></h3>";
		}
		print "<h3>Back to <a href=\"$usint_http/express_signoff.cgi\">";
        print "Top of Express Approval Page</a></h3>";
        print "<h3>Back to <a href=\"$usint_home/\">USINT Page</a></h3>";

	}else{
		if($org_obsid =~ /\d/){
			print "<h3>Back to <a href=\"$obs_ss_http/ocatdata2html.cgi?$org_obsid\">";
            print "Ocat Data Page (obsid: $org_obsid)</a></h3>";
		}
		print "<h3>Back to <a href=\"$obs_ss_http/express_signoff.cgi\">";
        print "Top of Express Approval Page</a></h3>";
        print "<h3>Back to <a href=\"$obs_ss_http/\">USINT Page</a></h3>";
	}
	exit 1;
}


print end_form();
print "</body>";
print "</html>";

###########################################################################################################
### print_param: prints html text of the form parameters for testing purposes. Not necessary beyond testing
###########################################################################################################

sub print_param{
	print "<p>Print_param() is Running</p>";
	if (param() == 0){
		print "<p>No Form Parameters!</p>";
	}else{
		for $i (param()){
			print "<p>Parameter: $i, Value: ".param($i)."</p>";
		}
	}
}


################################################################################
### input_obsid: a page to write in list of obsids                           ###
################################################################################

sub input_obsid{

    if ($usint_on =~ /test/){
	print "<h2 style='padding-bottom:20px'>Welcome to Express Approval Page: Test Version</h2>";
	print "<h3> User: $submitter	----	Directory: $ocat_dir</h3>";
    }else{	
	print "<h2 style='padding-bottom:20px'>Welcome to Express Approval Page</h2>";
    }
    print '<h3>Please type all obsids which you want to approve. ';
    print 'You can use <i>comma, colon, semi-colon</i>, "/", or by "  " ';
    print '(&lt;<i> blank space</i>&gt;) to separate them. ';
	print '<h3>If the entries are sequential without  any breaks, ';
    print 'put the first and the last obsids with "-" ';
	print 'between two obsids (e.g., 12507-12533). The values are <em>INCLUSIVE</em>.</h3>';

    print textfield(-name=>'obsid_list', -value=>'', -size=>100);

    print "<div style='padding-top:20px;padding-botom:20px'>";
    print '<input type="submit" name="Approve" value="Approve">';
    print '</div>';

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

    $server  = "ocatsqlsrv";

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
		    multitelescope_interval
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

        $sqlh1 = $dbh1->prepare(qq(select
                obsid
        from target where group_id = \'$group_id\'));
        $sqlh1->execute();

        while(@group_obsid = $sqlh1->fetchrow_array){
            $group_obsid = join("<td>", @group_obsid);
            @group       = (@group, "<a href=\"\.\/ocatdata2html.cgi\?$group_obsid\">$group_obsid<\/a> ");
        }
#
#---  output formatting
#
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
    $sqlh1 = $dbh1->prepare(qq(select
        ao_str
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
        $time_ordr = $timereq_data[0];                          #--- here is time order
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

        $exp_mode                = $acisdata[0];
        $ccdi0_on                = $acisdata[1];
        $ccdi1_on                = $acisdata[2];
        $ccdi2_on                = $acisdata[3];
        $ccdi3_on                = $acisdata[4];

        $ccds0_on                = $acisdata[5];
        $ccds1_on                = $acisdata[6];
        $ccds2_on                = $acisdata[7];
        $ccds3_on                = $acisdata[8];
        $ccds4_on                = $acisdata[9];
        $ccds5_on                = $acisdata[10];

        $bep_pack                = $acisdata[11];
        $onchip_sum              = $acisdata[12];
        $onchip_row_count        = $acisdata[13];
        $onchip_column_count     = $acisdata[14];
        $frame_time              = $acisdata[15];

        $subarray                = $acisdata[16];
        $subarray_start_row      = $acisdata[17];
        $subarray_row_count      = $acisdata[18];
        $duty_cycle              = $acisdata[19];
        $secondary_exp_count     = $acisdata[20];

        $primary_exp_time        = $acisdata[21];
        $eventfilter             = $acisdata[22];
        $eventfilter_lower       = $acisdata[23];
        $eventfilter_higher      = $acisdata[24];
        $most_efficient          = $acisdata[25];

        $dropped_chip_count      = $acisdata[26];
        $multiple_spectral_lines = $acisdata[27];
        $spectra_max_count       = $acisdata[28];

    } else {
        $exp_mode                = "NULL";
        $ccdi0_on                = "NULL";
        $ccdi1_on                = "NULL";
        $ccdi2_on                = "NULL";
        $ccdi3_on                = "NULL";

        $ccds0_on                = "NULL";
        $ccds1_on                = "NULL";
        $ccds2_on                = "NULL";
        $ccds3_on                = "NULL";
        $ccds4_on                = "NULL";
        $ccds5_on                = "NULL";

        $bep_pack                = "NULL";
        $onchip_sum              = "NULL";
        $onchip_row_count        = "NULL";
        $onchip_column_count     = "NULL";
        $frame_time              = "NULL";

        $subarray                = "NONE";
        $subarray_start_row      = "NULL";
        $subarray_row_count      = "NULL";
        $subarray_frame_time     = "NULL";
        $duty_cycle              = "NULL";
        $secondary_exp_count     = "NULL";

        $primary_exp_time        = "";
        $eventfilter             = "NULL";
        $eventfilter_lower       = "NULL";
        $eventfilter_higher      = "NULL";
        $spwindow                = "NULL";
        $most_efficient          = "NULL";

        $dropped_chip_count      = "NULL";
        $multiple_spectral_lines = "NULL";
        $spectra_max_count       = "NULL";
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
        $ordr  = $aciswindata[0];                       #--- here is the win_ordr
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

    $sqlh1 = $dbh1->prepare(qq(select 
        soe_roll 
    from soe where obsid=$obsid));

    $sqlh1->execute();
    @soedata = $sqlh1->fetchrow_array;
    $sqlh1->finish;

    $roll_obsr = $soedata[0];

#------------------------------------
#-------    get values from prop_info
#------------------------------------

    $sqlh1 = $dbh1->prepare(qq(select
        prop_num,title,joint 
    from prop_info where ocat_propid=$proposal_id));

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
        last  
    from view_pi where ocat_propid=$proposal_id));

    $sqlh1->execute();
    $PI_name = $sqlh1->fetchrow_array;
    $sqlh1->finish;

    $sqlh1 = $dbh1->prepare(qq(select  
        last  
    from view_coi where ocat_propid=$proposal_id));

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

    $targid                 =~ s/\s+//g;
    $seq_nbr                =~ s/\s+//g;
    $targname               =~ s/\s+//g;
    $obj_flag               =~ s/\s+//g;
    if($obj_flag            =~ /NONE/){
        $obj_flag            = "NO";
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
    $type                   =~ s/\s+//g;
    $mpcat_star_fidlight_file =~ s/\s+//g;
    $status                 =~ s/\s+//g;
    $data_rights            =~ s/\s+//g;
    $server_name            =~ s/\s+//g;
    $hrc_zero_block         =~ s/\s+//g;
    $hrc_timing_mode        =~ s/\s+//g;
    $hrc_si_mode            =~ s/\s+//g;
    $exp_mode               =~ s/\s+//g;
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

    $ra   = sprintf("%3.6f", $ra);          #--- setting to 6 digit after a dicimal point
    $dec  = sprintf("%3.6f", $dec);
    $dra  = $ra;
    $ddec = $dec;

#---------------------------------------------------------------------------
#------- time need to be devided into year, month, day, and time for display
#---------------------------------------------------------------------------

    for($k = 1; $k <= $time_ordr; $k++){
        if($tstart[$k] ne ''){
            $input_time      = $tstart[$k];
            mod_time_format();              #--- sub mod_time_format changes time format
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

    if($multitelescope eq '')       {$multitelescope = 'N'}
    if($proposal_joint eq '')       {$proposal_joint = 'N/A'}
    if($proposal_hst eq '')         {$proposal_hst = 'N/A'}
    if($proposal_noao eq '')        {$proposal_noao = 'N/A'}
    if($proposal_xmm eq '')         {$proposal_xmm = 'N/A'}
    if($rxte_approved_time eq '')   {$rxte_approved_time = 'N/A'}
    if($vla_approved_time eq '')    {$vla_approved_time = 'N/A'}
    if($vlba_approved_time eq '')   {$vlba_approved_time = 'N/A'}

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

    if($photometry_flag    eq 'NULL')        {$dphotometry_flag = 'NULL'}
    elsif($photometry_flag eq '')            {$dphotometry_flag = 'NULL'; $photometry_flag = 'NULL'}
    elsif($photometry_flag eq 'Y')           {$dphotometry_flag = 'YES'}
    elsif($photometry_flag eq 'N')           {$dphotometry_flag = 'NO'}

    for($k = 1; $k <= $time_ordr; $k++){
        if($window_constraint[$k]    eq 'Y')   {$dwindow_constraint[$k] = 'CONSTRAINT'}
        elsif($window_constraint[$k] eq 'P')   {$dwindow_constraint[$k] = 'PREFERENCE'}
        elsif($window_constraint[$k] eq 'N')   {$dwindow_constraint[$k] = 'NONE'}
        elsif($window_constraint[$k] eq 'NULL'){$dwindow_constraint[$k] = 'NULL'}
        elsif($window_constraint[$k] eq '')    {$window_constraint[$k]  = 'NULL';
                                                $dwindow_constraint[$k] = 'NULL';}
    }

    for($k = 1; $k <= $roll_ordr; $k++){
        if($roll_constraint[$k]    eq 'Y')   {$droll_constraint[$k] = 'CONSTRAINT'}
        elsif($roll_constraint[$k] eq 'P')   {$droll_constraint[$k] = 'PREFERENCE'}
        elsif($roll_constraint[$k] eq 'N')   {$droll_constraint[$k] = 'NONE'}
        elsif($roll_constraint[$k] eq 'NULL'){$droll_constraint[$k] = 'NULL'}
        elsif($roll_constraint[$k] eq '')    {$roll_constraint[$k]  = 'NULL';
                                              $droll_constraint[$k] = 'NULL';}

        if($roll_180[$k]    eq 'Y')          {$droll_180[$k] = 'YES'}
        elsif($roll_180[$k] eq 'N')          {$droll_180[$k] = 'NO'}
        else                                 {$droll_180[$k] = 'NULL'}
    }

    if($constr_in_remarks eq '')             {$dconstr_in_remarks = 'NO'; 
                                              $constr_in_remarks = 'N'}
    elsif($constr_in_remarks eq 'N')         {$dconstr_in_remarks = 'NO'}
    elsif($constr_in_remarks eq 'Y')         {$dconstr_in_remarks = 'YES'}
    elsif($constr_in_remarks eq 'P')         {$dconstr_in_remarks = 'PREFERENCE'}

    if($phase_constraint_flag eq 'NULL')     {$dphase_constraint_flag = 'NULL'}
    elsif($phase_constraint_flag eq '')      {$dphase_constraint_flag = 'NONE'; 
                                              $phase_constraint_flag = 'NULL'}
    elsif($phase_constraint_flag eq 'N')     {$dphase_constraint_flag = 'NONE'}
    elsif($phase_constraint_flag eq 'Y')     {$dphase_constraint_flag = 'CONSTRAINT'}
    elsif($phase_constraint_flag eq 'P')     {$dphase_constraint_flag = 'PREFERENCE'}

    if($monitor_flag eq 'NULL')              {$dmonitor_flag = 'NULL'}
    elsif($monitor_flag eq '')               {$dmonitor_flag = 'NULL'}
    elsif($monitor_flag eq 'Y')              {$dmonitor_flag = 'YES'}
    elsif($monitor_flag eq 'YES')            {$dmonitor_flag = 'YES'}
    elsif($monitor_flag eq 'N')              {$dmonitor_flag = 'NONE'}
    elsif($monitor_flag eq 'NONE')           {$dmonitor_flag = 'NONE'}
    elsif($monitor_flag eq 'NO')             {$dmonitor_flag = 'NO'}

    if($multitelescope eq 'Y')               {$dmultitelescope = 'YES'}
    elsif($multitelescope eq 'N')            {$dmultitelescope = 'NO'}
    elsif($multitelescope eq 'P')            {$dmultitelescope = 'PREFERENCE'}

    if($hrc_zero_block eq 'NULL')            {$dhrc_zero_block = 'NULL'}
    elsif($hrc_zero_block eq '')             {$dhrc_zero_block = 'NO'; 
                                              $hrc_zero_block = 'N';}
    elsif($hrc_zero_block eq 'Y')            {$dhrc_zero_block = 'YES'}
    elsif($hrc_zero_block eq 'N')            {$dhrc_zero_block = 'NO'}

    if($hrc_timing_mode eq 'NULL')           {$dhrc_timing_mode = 'NULL'}
    elsif($hrc_timing_mode eq '')            {$dhrc_timing_mode = 'NO'; 
                                              $hrc_timing_mode = 'N';}
    elsif($hrc_timing_mode eq 'Y')           {$dhrc_timing_mode = 'YES'}
    elsif($hrc_timing_mode eq 'N')           {$dhrc_timing_mode = 'NO'}

    if($ordr =~ /\W/ || $ordr == '') {
            $ordr = 1;
    }

    if($most_efficient eq 'NULL')            {$dmost_efficient = 'NULL'}
    elsif($most_efficient eq '')             {$most_efficient = 'NULL'; 
                                              $dmost_efficient  = 'NULL'}
    elsif($most_efficient eq 'Y')            {$dmost_efficient = 'YES'}
    elsif($most_efficient eq 'N')            {$dmost_efficient = 'NO'}

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


    if($duty_cycle eq 'NULL')   {$dduty_cycle = 'NULL'}
    elsif($duty_cycle eq '')    {$dduty_cycle = 'NULL'; $duty_cycle = 'NULL'}
    elsif($duty_cycle eq 'Y')   {$dduty_cycle = 'YES'}
    elsif($duty_cycle eq 'YES') {$dduty_cycle = 'YES'}
    elsif($duty_cycle eq 'N')   {$dduty_cycle = 'NO'}
    elsif($duty_cycle eq 'NO')  {$dduty_cycle = 'NO'}

    if($onchip_sum eq 'NULL')   {$donchip_sum = 'NULL'}
    elsif($onchip_sum eq '')    {$donchip_sum = 'NULL'; $onchip_sum = 'NULL'}
    elsif($onchip_sum eq 'Y')   {$donchip_sum = 'YES'}
    elsif($onchip_sum eq 'N')   {$donchip_sum = 'NO'}

    if($eventfilter eq 'NULL')  {$deventfilter = 'NULL'}
    elsif($eventfilter eq '')   {$deventfilter = 'NULL'; $eventfilter = 'NULL'}
    elsif($eventfilter eq 'Y')  {$deventfilter = 'YES'}
    elsif($eventfilter eq 'N')  {$deventfilter = 'NO'}

    if($multiple_spectral_lines eq 'NULL') {$dmultiple_spectral_lines = 'NULL'}
    elsif($multiple_spectral_lines eq '')  {$dmultiple_spectral_lines = 'NULL'; 
                                            $multiple_spectral_lines = 'NULL'}
    elsif($multiple_spectral_lines eq 'Y') {$dmultiple_spectral_lines = 'YES'}
    elsif($multiple_spectral_lines eq 'N') {$dmultiple_spectral_lines = 'NO'}

    if($spwindow eq 'NULL')     {$dspwindow = 'NULL'}
    elsif($spwindow eq '' )     {$dspwindow = 'NULL'; $spwindow = 'NULL'}
    elsif($spwindow eq 'Y')     {$dspwindow = 'YES'}
    elsif($spwindow eq 'N')     {$dspwindow = 'NO'}
 
    if($spwindow eq 'NULL')     {$dspwindow = 'NULL'}
    elsif($spwindow eq '' )     {$dspwindow = 'NULL'; $spwindow = 'NULL'}
    elsif($spwindow eq 'Y')     {$dspwindow = 'YES'}
    elsif($spwindow eq 'N')     {$dspwindow = 'NO'}

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
        SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,GROUP_ID,OBS_AO_STR,TARGname,
        SI_MODE,INSTRUMENT,GRATING,type,PI_name,OBSERVER,APPROVED_EXPOSURE_TIME, REM_EXP_TIME,
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
        EVENTFILTER_HIGHER,SPWINDOW,ORDR, FEP,DROPPED_CHIP_COUNT, BIAS_RREQUEST,
        TOO_ID,TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
        REMARKS,COMMENTS, MONITOR_FLAG, MULTITELESCOPE_INTERVAL	
    );

#--------------------------------------------------
#----- all the param names passed between cgi pages
#--------------------------------------------------

    @paramarray = (
        SI_MODE,
        INSTRUMENT,GRATING,type,PI_name,OBSERVER,APPROVED_EXPOSURE_TIME,
        RA,DEC,ROLL_OBSR,Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
        DITHER_FLAG,Y_AMP, Y_FREQ, Y_PHASE, Z_AMP, Z_FREQ, Z_PHASE,Y_AMP_ASEC, Z_AMP_ASEC,
        Y_FREQ_ASEC, Z_FREQ_ASEC, UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,
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
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT, 
        REMARKS,COMMENTS, ACISTAG,ACISWINTAG,SITAG,GENERALTAG,
        DROPPED_CHIP_COUNT, GROUP_ID, MONITOR_FLAG
    );

#---------------------------------------------------------------
#----- all the param names passed not editable in ocat data page
#---------------------------------------------------------------

    @passarray = (
        SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,GROUP_ID,OBS_AO_STR,TARGname,
        REM_EXP_TIME,RASTER_SCAN,ACA_MODE,
        PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
        PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
        TOO_ID,TOO_TRIG,TOO_type,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
        FEP,DROPPED_CHIP_COUNT
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
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT 
    );

#---------------------------------------
#----- all the param in acis window data
#---------------------------------------

    @aciswinarray=(START_ROW,START_COLUMN,HEIGHT,WIDTH,LOWER_THRESHOLD,
       PHA_RANGE,SAMPLE,ORDR,CHIP,
    );

#-------------------------------------------
#----- all the param in general data dispaly
#-------------------------------------------

    @genarray=(REMARKS,INSTRUMENT,GRATING,type,RA,DEC,APPROVED_EXPOSURE_TIME,
        Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET, FOCUS_OFFSET,DEFOCUS,
        RASTER_SCAN,DITHER_FLAG, Y_AMP, Y_FREQ, Y_PHASE, Z_AMP, Z_FREQ, Z_PHASE,
        UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,VMAGNITUDE,
        EST_CNT_RATE,FORDER_CNT_RATE,ROLL,ROLL_TOLERANCE,TSTART,TSTOP,
        PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD, PHASE_START,
        PHASE_START_MARGIN,PHASE_END,PHASE_END_MARGIN,PRE_MIN_LEAD,
        PRE_MAX_LEAD,PRE_ID,HRC_SI_MODE,HRC_TIMING_MODE,HRC_ZERO_BLOCK,
        TOOID,TARGname,DESCRIPTION,SI_MODE,ACA_MODE,EXTENDED_SRC,SEG_MAX_NUM,
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
#--- for the original value, all variable name start from "orig_"
#
        $wname    = 'orig_'."$lname";
        ${$wname} = ${$lname};
    }

#-------------------------------------
#------------------     special cases
#-------------------------------------

    $orig_ra  = $dra;
    $orig_dec = $ddec;

#----------------------------------------------
#------- special treatment for time constraint
#----------------------------------------------

    $ptime_ordr = $time_ordr + 1;
    for($j = $ptime_ordr; $j < 30; $j++){
        $start_date[$j]             = 'NULL';
        $start_month[$j]            = 'NULL';
        $start_year[$j]             = 'NULL';
        $end_date[$j]               = 'NULL';
        $end_month[$j]              = 'NULL';
        $end_year[$j]               = 'NULL';
        $tstart[$j]                 = '';
        $tstop[$j]                  = '';
        $window_constraint[$j]      = 'NULL';
    }
    for($j = 1; $j < 30; $j++){
        $orig_start_date[$j]        = $start_date[$j];
        $orig_start_month[$j]       = $start_month[$j];
        $orig_start_year[$j]        = $start_year[$j];
        $orig_end_date[$j]          = $end_date[$j];
        $orig_end_month[$j]         = $end_month[$j];
        $orig_end_year[$j]          = $end_year[$j];
        $orig_tstart[$j]            = $tstart[$j];
        $orig_tstop[$j]             = $tstop[$j];
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
        if($roll_180[$j] eq '')       {$roll_180[$j]         = 'NULL'}
    }

    $proll_ordr = $roll_ordr + 1;
#
#--- set default values up to order < 30, assuming that we do not get the order larger than 29
#
    for($j = $proll_ordr; $j < 30; $j++){
        $roll_constraint[$j] = 'NULL';  
        $roll_180[$j]        = 'NULL';
        $roll[$j]            = '';
        $roll_tolerance[$j]  = '';
    }
#
#--- save them as the original values
#
    for($j = 1; $j < 30; $j++){
        $orig_roll_constraint[$j] = $roll_constraint[$j];
        $orig_roll_180[$j]        = $roll_180[$j];
        $orig_roll[$j]            = $roll[$j];
        $orig_roll_tolerance[$j]  = $roll_tolerance[$j];
    }

#--------------------------------------------
#----- special treatment for acis window data
#--------------------------------------------

    for($j = 1; $j <= $ordr; $j++){
        if($chip[$j] eq '')         {$chip[$j]          = 'NULL'}
        if($chip[$j] eq 'N')        {$chip[$j]          = 'NULL'}

        if($include_flag[$j] eq '') {$dinclude_flag[$j] = 'INCLUDE'; 
                                     $include_flag[$j]  = 'I'}
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
		$tstart_new[$j] = '';					        #--- recombine tstart and tstop
		if($start_month[$j] ne 'NULL'){
			if($start_month[$j] eq 'Jan')   {$start_month[$j] = '01'}
			elsif($start_month[$j] eq 'Feb'){$start_month[$j] = '02'}
			elsif($start_month[$j] eq 'Mar'){$start_month[$j] = '03'}
			elsif($start_month[$j] eq 'Apr'){$start_month[$j] = '04'}
			elsif($start_month[$j] eq 'May'){$start_month[$j] = '05'}
			elsif($start_month[$j] eq 'Jun'){$start_month[$j] = '06'}
			elsif($start_month[$j] eq 'Jul'){$start_month[$j] = '07'}
			elsif($start_month[$j] eq 'Aug'){$start_month[$j] = '08'}
			elsif($start_month[$j] eq 'Sep'){$start_month[$j] = '09'}
			elsif($start_month[$j] eq 'Oct'){$start_month[$j] = '10'}
			elsif($start_month[$j] eq 'Nov'){$start_month[$j] = '11'}
			elsif($start_month[$j] eq 'Dec'){$start_month[$j] = '12'}
		}
		if($start_date[$j] =~ /\d/ && $start_month[$j] =~ /\d/ && $start_year[$j] =~ /\d/ ){
			@ttemp = split(/:/, $start_time[$j]);
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
				$tstart_new  = "$start_month[$j]:$start_date[$j]:$start_year[$j]:$start_time[$j]";
				$chk_start = -9999;
				if($tstart_new =~ /\s+/ || $tstart_new == ''){
				}else{
					$tstart[$j]    = $tstart_new;
					$chk_start = "$start_year[$j]$start_month[$j]$start_date[$j]$time_ck";
				}
			}
		}
		
		$tstop_new[$j] = '';
		if($end_month[$j] ne 'NULL'){
			if($end_month[$j] eq 'Jan')   {$end_month[$j] = '01'}
			elsif($end_month[$j] eq 'Feb'){$end_month[$j] = '02'}
			elsif($end_month[$j] eq 'Mar'){$end_month[$j] = '03'}
			elsif($end_month[$j] eq 'Apr'){$end_month[$j] = '04'}
			elsif($end_month[$j] eq 'May'){$end_month[$j] = '05'}
			elsif($end_month[$j] eq 'Jun'){$end_month[$j] = '06'}
			elsif($end_month[$j] eq 'Jul'){$end_month[$j] = '07'}
			elsif($end_month[$j] eq 'Aug'){$end_month[$j] = '08'}
			elsif($end_month[$j] eq 'Sep'){$end_month[$j] = '09'}
			elsif($end_month[$j] eq 'Oct'){$end_month[$j] = '10'}
			elsif($end_month[$j] eq 'Nov'){$end_month[$j] = '11'}
			elsif($end_month[$j] eq 'Dec'){$end_month[$j] = '12'}
		}

		if($end_date[$j] =~ /\d/ && $end_month[$j] =~ /\d/ && $end_year[$j] =~ /\d/ ){
			@ttemp = split(/:/, $end_time[$j]);
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
				$tstop_new = "$end_month[$j]:$end_date[$j]:$end_year[$j]:$end_time[$j]";
				$chk_end = -9999;
				if($tstop_new =~ /\s+/ || $tstop_new == ''){
				}else{
					$tstop[$j] = $tstop_new;
					$chk_end ="$end_year[$j]$end_month[$j]$end_date[$j]$time_ck";
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
		if($window_constraint[$j] eq 'NONE')         {$window_constraint[$j] = 'N'}
		elsif($window_constraint[$j] eq 'NULL')      {$window_constraint[$j] = 'NULL'}
		elsif($window_constraint[$j] eq 'CONSTRAINT'){$window_constraint[$j] = 'Y'}
		elsif($window_constraint[$j] eq 'PREFERENCE'){$window_constraint[$j] = 'P'}
	}

#----------------------
#---- roll order cases
#----------------------

	for($j = 1; $j <= $roll_ordr; $j++){
		if($roll_constraint[$j] eq 'NONE')         {$roll_constraint[$j] = 'N'}
		elsif($roll_constraint[$j] eq 'NULL')      {$roll_constraint[$j] = 'NULL'}
		elsif($roll_constraint[$j] eq 'CONSTRAINT'){$roll_constraint[$j] = 'Y'}
		elsif($roll_constraint[$j] eq 'PREFERENCE'){$roll_constraint[$j] = 'P'}
		elsif($roll_constraint[$j] eq '')          {$roll_constraint[$j] = 'NULL'}

		if($roll_180[$j] eq 'NULL')                {$roll_180[$j] = 'NULL'}
		elsif($roll_180[$j] eq 'NO')               {$roll_180[$j] = 'N'}
		elsif($roll_180[$j] eq 'YES')              {$roll_180[$j] = 'Y'}
		elsif($roll_180[$j] eq '')                 {$roll_180[$j] = 'NULL'}
	}

#-------------------
#--- aciswin cases
#-------------------

	for($j = 1; $j <= $ordr; $j++){
		if($include_flag[$j] eq 'INCLUDE')   {$include_flag[$j] = 'I'}
		elsif($include_flag[$j] eq 'EXCLUDE'){$include_flag[$j] = 'E'}
	}
		
#----------------------------------------------------------------
#----------- these have different values shown in Ocat Data Page
#----------- find database values for them
#----------------------------------------------------------------
	
	if($proposal_joint eq 'NULL')       {$proposal_joint = 'NULL'}
	elsif($proposal_joint eq 'YES')     {$proposal_joint = 'Y'}
	elsif($proposal_joint eq 'NO')      {$proposal_joint = 'N'}
	
	if($roll_flag eq 'NULL')            {$roll_flag = 'NULL'}
	elsif($roll_flag eq 'YES')          {$roll_flag = 'Y'}
	elsif($roll_flag eq 'NO')           {$roll_flag = 'N'}
	elsif($roll_flag eq 'PREFERENCE')   {$roll_flag = 'P'}
	
	if($window_flag eq 'NULL')          {$window_flag = 'NULL'}
	elsif($window_flag eq 'YES')        {$window_flag = 'Y'}
	elsif($window_flag eq 'NO')         {$window_flag = 'N'}
	elsif($window_flag eq 'PREFERENCE') {$window_flag = 'P'}
	
	if($dither_flag eq 'NULL')          {$dither_flag = 'NULL'}
	elsif($dither_flag eq 'YES')        {$dither_flag = 'Y'}
	elsif($dither_flag eq 'NO')         {$dither_flag = 'N'}
	
	if($uninterrupt eq 'NULL')          {$uninterrupt = 'NULL'}
	elsif($uninterrupt eq 'NO')         {$uninterrupt ='N'}
	elsif($uninterrupt eq 'YES')        {$uninterrupt ='Y'}
	elsif($uninterrupt eq 'PREFERENCE') {$uninterrupt = 'P'}
	
	if($photometry_flag eq 'NULL')      {$photometry_flag = 'NULL'}
	elsif($photometry_flag eq 'YES')    {$photometry_flag = 'Y'}
	elsif($photometry_flag eq 'NO')     {$photometry_flag = 'N'}

	if($multitelescope eq 'NO')           {$multitelescope = 'N'}
	elsif($multitelescope eq 'YES')       {$multitelescope = 'Y'}
	elsif($multitelescope eq 'PREFERENCE'){$multitelescope = 'P'}
	
	if($hrc_zero_block eq 'NULL')       {$hrc_zero_block = 'NULL'}
	elsif($hrc_zero_block eq 'YES')     {$hrc_zero_block = 'Y'}
	elsif($hrc_zero_block eq 'NO')      {$hrc_zero_block = 'N'}
	
	if($hrc_timing_mode eq 'NULL')      {$hrc_timing_mode = 'NULL'}
	elsif($hrc_timing_mode eq 'YES')    {$hrc_timing_mode = 'Y'}
	elsif($hrc_timing_mode eq 'NO')     {$hrc_timing_mode = 'N'}
	
	if($most_efficient eq 'NULL')       {$most_efficient = 'NULL'}
	elsif($most_efficient eq 'YES')     {$most_efficient = 'Y'}
	elsif($most_efficient eq 'NO')      {$most_efficient = 'N'}
	
	if($standard_chips eq 'NULL')       {$standard_chips = 'NULL'}
	elsif($standard_chips eq 'YES')     {$standard_chips = 'Y'}
	elsif($standard_chips eq 'NO')      {$standard_chips = 'N'}
	
	if($onchip_sum eq 'NULL')           {$onchip_sum = 'NULL'}
	elsif($onchip_sum eq 'YES')         {$onchip_sum = 'Y'}
	elsif($onchip_sum eq 'NO')          {$onchip_sum = 'N'}
	
	if($duty_cycle eq 'NULL')           {$duty_cycle = 'NULL'}
	elsif($duty_cycle eq 'YES')         {$duty_cycle = 'Y'}
	elsif($duty_cycle eq 'NO')          {$duty_cycle = 'N'}
	
	if($eventfilter eq 'NULL')          {$eventfilter = 'NULL'}
	elsif($eventfilter eq 'YES')        {$eventfilter = 'Y'}
	elsif($eventfilter eq 'NO')         {$eventfilter = 'N'}

    if($multiple_spectral_lines    eq 'NULL')  {$multiple_spectral_lines = 'NULL'}
    elsif($multiple_spectral_lines eq 'YES')   {$multiple_spectral_lines = 'Y'}
    elsif($multiple_spectral_lines eq 'NO')    {$multiple_spectral_lines = 'N'}
	
	if($spwindow eq 'NULL')             {$spwindow = 'NULL'}
	elsif($spwindow eq 'YES')           {$spwindow = 'Y'}
	elsif($spwindow eq 'NO')            {$spwindow = 'N'}
	
	if($phase_constraint_flag eq 'NULL')         {$phase_constraint_flag = 'NULL'}
	elsif($phase_constraint_flag eq 'NONE')      {$phase_constraint_flag = 'N'}
	elsif($phase_constraint_flag eq 'CONSTRAINT'){$phase_constraint_flag = 'Y'}
	elsif($phase_constraint_flag eq 'PREFERENCE'){$phase_constraint_flag = 'P'}
	
	if($window_constrint eq 'NONE')              {$window_constrint = 'N'}
	elsif($window_constrint eq 'NULL')           {$window_constrint = 'NULL'}
	elsif($window_constrint eq 'CONSTRAINT')     {$window_constrint = 'Y'}
	elsif($window_constrint eq 'PREFERENCE')     {$window_constrint = 'P'}
	
	if($constr_in_remarks eq 'YES')              {$constr_in_remarks = 'Y'}
	elsif($constr_in_remarks eq 'PREFERENCE')    {$constr_in_remarks = 'P'}
	elsif($constr_in_remarks eq 'NO')            {$constr_in_remarks = 'N'}
	
	if($ccdi0_on eq 'NULL')             {$ccdi0_on = 'NULL'}
	elsif($ccdi0_on eq 'YES')           {$ccdi0_on = 'Y'}
	elsif($ccdi0_on eq 'NO')            {$ccdi0_on = 'N'}
	
	if($ccdi1_on eq 'NULL')             {$ccdi1_on = 'NULL'}
	elsif($ccdi1_on eq 'YES')           {$ccdi1_on = 'Y'}
	elsif($ccdi1_on eq 'NO')            {$ccdi1_on = 'N'}
	
	if($ccdi2_on eq 'NULL')             {$ccdi2_on = 'NULL'}
	elsif($ccdi2_on eq 'YES')           {$ccdi2_on = 'Y'}
	elsif($ccdi2_on eq 'NO')            {$ccdi2_on = 'N'}
	
	if($ccdi3_on eq 'NULL')             {$ccdi3_on = 'NULL'}
	elsif($ccdi3_on eq 'YES')           {$ccdi3_on = 'Y'}
	elsif($ccdi3_on eq 'NO')            {$ccdi3_on = 'N'}
	
	if($ccds0_on eq 'NULL')             {$ccds0_on = 'NULL'}
	elsif($ccds0_on eq 'YES')           {$ccds0_on = 'Y'}
	elsif($ccds0_on eq 'NO')            {$ccds0_on = 'N'}
	
	if($ccds1_on eq 'NULL')             {$ccds1_on = 'NULL'}
	elsif($ccds1_on eq 'YES')           {$ccds1_on = 'Y'}
	elsif($ccds1_on eq 'NO')            {$ccds1_on = 'N'}
	
	if($ccds2_on eq 'NULL')             {$ccds2_on = 'NULL'}
	elsif($ccds2_on eq 'YES')           {$ccds2_on = 'Y'}
	elsif($ccds2_on eq 'NO')            {$ccds2_on = 'N'}
	
	if($ccds3_on eq 'NULL')             {$ccds3_on = 'NULL'}
	elsif($ccds3_on eq 'YES')           {$ccds3_on = 'Y'}
	elsif($ccds3_on eq 'NO')            {$ccds3_on = 'N'}
	
	if($ccds4_on eq 'NULL')             {$ccds4_on = 'NULL'}
	elsif($ccds4_on eq 'YES')           {$ccds4_on = 'Y'}
	elsif($ccds4_on eq 'NO')            {$ccds4_on = 'N'}
	
	if($ccds5_on eq 'NULL')             {$ccds5_on = 'NULL'}
	elsif($ccds5_on eq 'YES')           {$ccds5_on = 'Y'}
	elsif($ccds5_on eq 'NO')            {$ccds5_on = 'N'}
	
	read_user_name();					            #--- read registered user name
	
	$usr_ind = 0;
	$usr_cnt = 0;
	@list_of_user = @user_name;
	if($usint_on =~ /yes/){
		@list_of_user = @special_user;
	}

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

    print "<B> The user: <font color=magenta>$submitter</font> is not in our database </B>";
	print "<b> Please go back and enter a correct one</b>";

    print "</form>";
    print "</body>";
    print "</html>";
}

###################################################################################
### submit_entry: check and submitting the modified input values                ###
###################################################################################

sub submit_entry{
#
#--- counters
#
	$k = 0;						                #--- acisarray counter
	$l = 0; 					                #--- aciswin array counter
	$m = 0;						                #--- generalarray counter

#-----------------------------
#--------- pass the parameters
#-----------------------------

	foreach $ent (@paramarray){
        $new_entry = lc ($ent);
        $new_value = ${$new_entry};
		unless($ent =~ /TSTART/ || $ent =~ /TSTOP/ || $ent =~ /WINDOW_CONSTRAINT/
			|| $ent =~ /ACISTAG/ || $ent =~ /ACISWINTAG/ || $ent =~ /SITAG/ || $ent =~ /GENERALTAG/
			){
			print "<input type=\"hidden\" name=\"$ent\" value=\"$new_value\">";
		}
	}

#-------------------------
#------ hidden values here
#-------------------------

	print "<input type=\"hidden\" name=\"ASIS\"          value=\"$asis\">";
	print "<input type=\"hidden\" name=\"CLONE\"         value=\"$clone\">";
	print "<input type=\"hidden\" name=\"SUBMITTER\"     value=\"$submitter\">";
	print "<input type=\"hidden\" name=\"USER\"          value=\"$submitter\">";
	print "<input type=\"hidden\" name=\"SI_MODE\"       value=\"$si_mode\">";
	print "<input type=\"hidden\" name=\"email_address\" value=\"$email_address\">";

#----------------------------
#------ time constraint cases
#----------------------------

	print "<input type=\"hidden\" name=\"TIME_ORDR\" value=\"$time_ordr\">";
	for($j = 1; $j <= $time_ordr; $j++){
		foreach $ent ('START_DATE', 'START_MONTH', 'START_YEAR', 'START_TIME',
			          'END_DATE',   'END_MONTH',   'END_YEAR',   'END_TIME',
			          'WINDOW_CONSTRAINT'){
			$name = "$ent"."$j";
			$lname = lc ($ent);
			$val  = ${$lname}[$j];
			print "<input type=\"hidden\" name=\"$name\" value=\"$val\">";
		}
	}

#-----------------------------
#------ roll constraint cases
#-----------------------------

	print "<input type=\"hidden\" name=\"ROLL_ORDR\" value=\"$roll_ordr\">";
	for($j = 1; $j <= $roll_ordr; $j++){
		foreach $ent('ROLL_CONSTRAINT','ROLL_180','ROLL','ROLL_TOLERANCE'){
			$name = "$ent"."$j";
			$lname = lc ($ent);
			$val  = ${$lname}[$j];
			print "<input type=\"hidden\" name=\"$name\" value=\"$val\">";
		}
	}

#-------------------------
#------- acis window cases
#-------------------------

	print "<input type=\"hidden\" name=\"ORDR\" value=\"$ordr\">";
	for($j = 1; $j <=$ordr; $j++){
		foreach $ent ('CHIP','INCLUDE_FLAG','START_ROW','START_COLUMN','HEIGHT',
                      'WIDTH', 'LOWER_THRESHOLD','PHA_RANGE','SAMPLE'){
			$name = "$ent"."$j";
			$lname = lc ($ent);
			$val  = ${$lname}[$j];
			print "<input type=\"hidden\" name=\"$name\" value=\"$val\">";
		}
	}

#-------------------------------------------#
#-------------------------------------------#
#-------- ASIS and REMOVE case starts ------#
#-------------------------------------------#
#-------------------------------------------#

#   if ($asis eq "ASIS" || $asis eq "REMOVE"){

#------------------------------------------------------
#---- start writing email to the user about the changes
#------------------------------------------------------

	open (FILE, ">$temp_dir/$obsid.tmp");		#--- a temp file which email to a user written in.

	print FILE "OBSID    = $obsid\n";
   	print FILE "SEQNUM   = $seq_nbr\n";
   	print FILE "TARGET   = $targname\n";
   	print FILE "USERname = $submitter\n";

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
    	print FILE "PARAM name                  ORIGINAL value                REQUESTED value             ";
    	print FILE "\n------------------------------------------------------------------------------------------\n";
	
   	close FILE;
 
	format PARAMLINE =
	@<<<<<<<<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        	$nameagain $old_value $current_entry
.
#--- don't remove "." above!!
   
	open (PARAMLINE, ">>$temp_dir/$obsid.tmp");
	foreach $nameagain (@paramarray){

		$lc_name = lc ($nameagain);
		$old_name = 'orig_'."$lc_name";
		$old_value = ${$old_name};

   		unless (($lc_name =~/TARGname/i) || ($lc_name =~/TITLE/i)
			||  ($lc_name =~/^WINDOW_CONSTRAINT/i) || ($lc_name =~ /^TSTART/i) || ($lc_name =~/^TSTOP/i) 
			||  ($lc_name =~/^ROLL_CONSTRAINT/i) || ($lc_name =~ /^ROLL_180/i)
			||  ($lc_name =~/^CHIP/i) || ($lc_name =~ /^INCLUDE_FLAG/i) || ($lc_name =~ /^START_ROW/i)
			||  ($lc_name =~/^START_COLUMN/i) || ($lc_name =~/^HEIGHT/i) || ($lc_name =~ /^WIDTH/i)
			||  ($lc_name =~/^LOWER_THRESHOLD/i) || ($lc_name =~ /^PHA_RANGE/i) || ($lc_name =~ /^SAMPLE/i)
			||  ($lc_name =~/^SITAG/i) || ($lc_name =~ /^ACISTAG/i) || ($lc_name =~ /^GENERALTAG/i)
			||  ($lc_name =~/ASIS/i) || ($lc_name =~ /MONITOR_FLAG/i)
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

	$obsid_list = param("obsid_list");
   	print "<input type=\"hidden\" name=\"ASIS\"             value=\"ASIS\">";
    print "<input type=\"hidden\" name=\"access_ok\"        value=\"yes\">";
    print "<input type=\"hidden\" name=\"pass\"             value=\"$pass\">";
    print "<input type=\"hidden\" name=\"sp_user\"          value=\"$sp_user\">";
	print "<input type=\"hidden\" name=\"email_address\"    value=\"$email_address\">";
	print "<input type=\"hidden\" name=\"obsid_list\"       value=\"$obsid_list\">";
	print "<input type=\"hidden\" name =\"Last_Obsid\"      value=\"$obsid\">";

	print "</form></body></html>";

#   }               #--- close of ASIS if sentence which is commented out
}

#########################################################################
### read_name: read descriptive name of database name		     ####
#########################################################################

sub read_name{
	open(FH, "$obs_ss/name_list");
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
### find_name: match database name to descriptive name		      ###
#########################################################################

sub find_name{
	$web_name = '';
	$comp     = uc ($db_name);
	OUTER:
	foreach $fent (@name_list){
		@wtemp = split(/:/, $fent);
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

	$s_yes = 0;
	$s_cnt = 0;
		
	open (FILE, ">$temp_dir/ormail_$obsid.tmp");
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

#  	$general_status = "NULL";			        #--- these are for the status verification page
#    $acis_status    = "NULL";			        #--- orupdate.cgi
#    $si_mode_status = "NULL";
#    $hrc_si_mode_status = "NULL";

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
	print ASIN "$obsid\t$seq_nbr\t$dutysci\t$date\n";
	close(ASIN);
	system("chmod 644 $ocat_dir/approved");

	if($usint_on =~ /test/){
#		system("chmod 777 $test_dir/approved");
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

#--------------------------------------------------------------------------------------------------
#----  if it is not being edited, write update updates_table.list---data for the verificaiton page
#--------------------------------------------------------------------------------------------------

        }else{
            $lpass = 1;

            flock($update, LOCK_EX) or die "died while trying to lock the file<br />\n";
            print $update "$obsid.$rev\tNULL\tNULL\tNULL\tNULL\t$dutysci_status\t$seq_nbr\t$dutysci\n";
#--- UPDATED 06/24/21
            close $update;

#---------------------
#----  checkin update
#---------------------

            $chk     = "$obsid.$rev";
            $in_test = `cat $ocat_dir/updates_table.list`;

#-----------------------------------------------------
#----  copy the revision file to the appropriate place
#-----------------------------------------------------

            if($in_test =~ /$chk/i){
                system("cp  $temp_dir/$obsid.tmp $ocat_dir/updates/$obsid.$rev");
                last OUTER;
            }
        }
    }

#----------------------------------------------
#----  append arnold update file, if necessary
#----------------------------------------------

#	if ($acistag =~/ON/){
#    	open (ARNOLD, "<$temp_dir/arnold.tmp");
#    	@arnold = <ARNOLD>;
#    	close (ARNOLD);
#    	$arnoldline = shift @arnold;
#
#--- closed 02/25/2011; the directory does not exist anymore
#
#    	open (ARNOLDUPDATE, ">>/home/arcops/ocatMods/acis");
#    	print ARNOLDUPDATE "$arnoldline";
#    	close (ARNOLDUPDATE);
#	}

#---------------------------#
#----  send messages  ------#
#---------------------------#

###########
$send_email = 'yes';    
##########
	$asis_ind = param('ASIS');
	if($send_email eq 'yes'){
		if($sp_user eq 'no'){
			open(ASIS, '>$temp_dir/asis.tmp');
			print ASIS "$obsid is approved for flight. Thank you \n";
			close(ASIS);

			if($usint_on =~ /test/){
                $cmd = "cat $temp_dir/asis.tmp |mailx -s\"Subject:  TEST!! ";
                $cmd = "$cmd"."$obsid is approved\"  $test_email";
			    system($cmd);

			}else{
                $cmd = "cat $temp_dir/asis.tmp |mailx -s\"Subject: $obsid is approved\" ";
                $cmd = "$cmd"."  $email_address cus\@head-cfa.harvard.edu";
			    system($cmd);

			}

			system("rm $temp_dir/asis.tmp");

		}else{

			if($usint_on =~ /test/){
                $cmd = "cat $temp_dir/ormail_$obsid.tmp |mailx -s\"Subject: TEST!! ";
                $cmd = "$cmd"."Parameter Changes (Approved) log  $obsid.$rev\"  $test_email";
			    system($cmd);

			}else{
                $cmd = "cat $temp_dir/ormail_$obsid.tmp |mailx -s\"Subject: ";
                $cmd = "$cmd"."Parameter Changes (Approved) log  $obsid.$rev\"  ";
                $cmd = "$cmd"."$email_address  cus\@head.cfa.harvard.edu";
			    system($cmd);
			}
		}
	}

#--------------------------
#----  get rid of the junk
#--------------------------

	system("rm -f $temp_dir/$obsid.tmp");
	system("rm -f $temp_dir/ormail_$obsid.tmp");
	system("rm -f $temp_dir/arnold.tmp");
#	system("chmod 777 $temp_dir/Temp/*");
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
		$hr_add           = 12;
		@tatemp           = split(/PM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];

	}elsif($tentry[$ttcnt-1] =~/pm/){
		$hr_add           = 12;
		@tatemp           = split(/pm/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];

	}elsif($tentry[$ttcnt-1] =~ /AM/){
		@tatemp           = split(/AM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];

	}elsif($tentry[$ttcnt-1] =~ /am/){
		@tatemp           = split(/AM/, $tentry[$ttcnt-1]);
		$tentry[$ttcnt-1] = $tatemp[0];
	}
	
	$mon_lett = 0;
	if($tentry[0] =~ /\D/){
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
		if($month =~ /^JAN/i){$month = '01'}
		elsif($month =~ /^FEB/i){$month = '02'}
		elsif($month =~ /^MAR/i){$month = '03'}
		elsif($month =~ /^APR/i){$month = '04'}
		elsif($month =~ /^MAY/i){$month = '05'}
		elsif($month =~ /^JUN/i){$month = '06'}
		elsif($month =~ /^JUL/i){$month = '07'}
		elsif($month =~ /^AUG/i){$month = '08'}
		elsif($month =~ /^SEP/i){$month = '09'}
		elsif($month =~ /^OCT/i){$month = '10'}
		elsif($month =~ /^NOV/i){$month = '11'}
		elsif($month =~ /^DEC/i){$month = '12'}
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

	if( $lts_lt_plan eq ''){
		$lts_more30 = 'yes';
	}else{
		@ttemp = split(/\s+/, $lts_lt_plan);

       	if($ttemp[1] =~ /Jan/i){
        	$month = '1';
			$add = 0;
    	}elsif($ttemp[0] =~ /Feb/i){
        	$month = '2';
			$add = 31;
    	}elsif($ttemp[0] =~ /Mar/i){
        	$month = '3';
			$add = 59;
    	}elsif($ttemp[0] =~ /Apr/i){
        	$month = '4';
			$add = 90;
    	}elsif($ttemp[0] =~ /May/i){
        	$month = '5';
			$add = 120;
    	}elsif($ttemp[0] =~ /Jun/i){
        	$month = '6';
			$add = 151;
    	}elsif($ttemp[0] =~ /Jul/i){
        	$month = '7';
			$add = 181;
    	}elsif($ttemp[0] =~ /Aug/i){
        	$month = '8';
			$add = 212;
    	}elsif($ttemp[0] =~ /Sep/i){
        	$month = '9';
			$add = 243;
    	}elsif($ttemp[0] =~ /Oct/i){
        	$month = '10';
			$add = 273;
    	}elsif($ttemp[0] =~ /Nov/i){
        	$month = '11';
			$add = 304;
    	}elsif($ttemp[0] =~ /Dec/i){
        	$month = '12';
			$add = 334;
    	}

        $lchk = is_leap_year($$temp[2]);
        if($lchk == 1){
			if($month > 2){
				$add++;
			}
		}
		$comp_date = $ttemp[1] + $add;
		$year = $ttemp[2];
		if($year == 1999){
			$dom = $comp_date - 202;
		}elsif($year >= 2000){
			$dom = $comp_date + 163 + 365*($year - 2000);
			if($year > 2000) {
				$dom++;
			}
			if($year > 2004) {
				$dom++;
			}
			if($year > 2008) {
				$dom++;
			}
			if($year > 2012) {
				$dom++;
			}
			if($year > 2016) {
				$dom++;
			}
			if($year > 2020) {
				$dom++;
			}
			if($year > 2024) {
				$dom++;
			}
			if($year > 2028) {
				$dom++;
			}
			if($year > 2032) {
				$dom++;
			}
		}
	
		($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
	
		$uyear = 1900 + $year;
		if($uyear == 1999){
			$cdom = $yday - 202;
		}elsif($uyear >= 2000){
			$cdom = $yday + 163 + 365*($uyear - 2000);
			if($uyear > 2000) {
				$cdom++;
			}
			if($uyear > 2004) {
				$cdom++;
			}
			if($uyear > 2008) {
				$cdom++;
			}
			if($uyear > 2012) {
				$cdom++;
			}
			if($uyear > 2016) {
				$cdom++;
			}
			if($uyear > 2020) {
				$cdom++;
			}
			if($uyear > 2024) {
				$cdom++;
			}
			if($uyear > 2028) {
				$cdom++;
			}
			if($uyear > 2032) {
				$cdom++;
			}
		}
	
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
	$sot_contact = 'bwargelin@head.cfa.harvard.edu';
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

    $mp_email = "$mp_contact".'@head.cfa.harvard.edu';

	if($usint_on =~ /test/){
        $cmd = "cat $temp_file | mailx -s\"Subject: TEST!! Change to Obsids Which ";
        $cmd = "$cmd"."Is in Active OR List ($mp_email)\"  $test_email";
    	system($cmd);

	}else{
        $cmd = "cat $temp_file | mailx -s\"Subject: Change Obsids Which ";
        $cmd = "$cmd"."Is in Active OR List\"  $mp_email cus\@head.cfa.harvard.edu";
		system($cmd);
	}
    system("rm $temp_file");
}

#########################################################################
## check_apporved_list: check approved obsids and notify the user     ###
#########################################################################

sub check_apporved_list{

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
	print AOUT "\n\nThe following obsids are added on the approved list.\n\n";
	foreach $ent (@list1){
		print AOUT "$ent\n";
	}
	print AOUT "\n\n";
	if($cnt > 0){
		print AOUT "The following obsid(s) were not added to the approved list.\n";
		print AOUT "You may want to try them again.\n";
		foreach $ent (@list2){
			print AOUT "$ent\n";
		}
	}

	if($usint_on =~ /test/i){
        $cmd = "cat $temp_dir/alist.tmp |mailx -s\"Subject: TEST!! Approved Obsids ";
        $cmd = "$cmd"."by $test_email \"  $test_email";
		system($cmd);
	}else{
        $cmd = "cat $temp_dir/alist.tmp |mailx -s\"Subject: Approved Obsids ";
        $cmd = "$cmd"."by $email_address \"  $email_address  cus\@head.cfa.harvard.edu";
		system($cmd);
	}
	system("rm  $temp_dir/alist.tmp");
}

##################################################################################
## is_leap_year: check a given year is a leap year                             ###
##################################################################################

sub is_leap_year{

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
    
#---------------------------------------------------------------------------------------
#-- split_string_to_list: create split obsid list from a string                       --
#---------------------------------------------------------------------------------------

sub split_string_to_list{
=comment
create split obsid list from a string
input:  $input_line --- a string of a list of obsids
output: @split_list --- a list of obsids
=cut
    my @split_list   = ();
    my @temp_liist   = ();
    my $ent, $start, $stop;
    (my $input_list) = @_;
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
        }else{
            push(@c_list, $ent);
        }
    }
    @split_list = @c_list;

    return @split_list;
}

#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------

sub uniq_ent{
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
