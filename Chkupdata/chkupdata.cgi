#!/usr/bin/perl

BEGIN
{
#    $ENV{SYBASE} = "/soft/SYBASE_OCS15.7";
    $ENV{SYBASE} = "/soft/SYBASE16.0";
}

use DBI;
use DBD::Sybase;
use CGI qw/:standard :netscape /;

#########################################################################################
#	                                            										#
#	chkupdata.cgi: a script to display past data, requested changes, and data in	    #
#		       database.							                                    #
#											                                            #
#	author: T. Isobe (tisobe@cfa.harvard.edu)					                        #
#											                                            #
#	10/31/01:	first version							                                #
#	07/22/02:	uninterrupt added						                                #
#	last update	Dec 14, 2020							                                #
#											                                            #
#########################################################################################

$obsid = $ARGV[0];
chomp $obsid;

#
#---- set directory paths : updated to read from a file (02/25/2011)
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

###############################
#$dtest = 0;
$dtest = 1;      #---- this is a test case. 
###############################

if($dtest == 1){
	$ocat_dir = $test_dir;
}else{
	$ocat_dir = $real_dir;
}


#
#--- set html pages
#
$usint_http   = 'https://cxc.cfa.harvard.edu/cus/Usint';       #--- web site for usint users 
$test_http    = 'https://cxc.cfa.harvard.edu/cus/Usint/test_dir';  #--- web site for test


#
#--- find the last submission of the given obsid
#

check_update_datebase();


#
#--- if the data exists, extract data from the database
#

if($version_warning == 0){
	read_databases();
}

$dat   = $obsid;

#
#--- start html 
#
print "Content-type: text/html; charset=utf-8\n\n";

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print "<title>Ocat Data Check Page</title>";
print "<style  type='text/css'>";
print "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
print "</head>";

print "<body style='color:#000000;background-color:#FFFFE0'>";

#
#--- if the given version # does not exist, warn the user and exit.
#

if($version_warning > 0){

	print '<h2 style="padding-top:25px;color:red">Warning!!</h2>';
	print "<h2>The last updated version of Obsid $obsid_base is <span style='color:red'> $latest_version</span>,";
	print " but you requested version: <span style='color:red'>$c_version</span>. ";
	print ' Please enter a correct version number.</h2>';
	print '</body>';
	print '</html>';
	exit 1;

}

#
#--- read the data from the logged file
#

open(PRE,"$ocat_dir/updates/$dat");

$new_time_form = 'yes';
$chk_start     = 0;

OUTER:
while(<PRE>){
	chomp $_;
	if($_ =~ /-----------/){
		$chk_start = 1;
	}
	if($chk_start == 1 &&($_ =~ /TSTART/i || $_ =~ /TSTOP/i)){
		@atemp = split(//,$_);
		$cnt   = 0;
		$otime = '';
		$stime = '';

		foreach $ent  (@atemp){
			$cnt++;
#			if($cnt >= 29 && $cnt < 59){
			if($cnt >= 23 && $cnt < 53){
				$otime = "$otime"."$ent";
			}
#			if($cnt >= 59){
			if($cnt >= 53){
				$stime = "$stime"."$ent";
			}
		}
		$otest = $otime;
		$otest =~ s/\s+//g;
		if($otest =~ /\w/){
			@ctemp = split(/\s+/,$otime);
			if($ctemp[1] =~ /\d/){
				$omon = $ctemp[1];
			}else{
				if($ctemp[1] =~ /JAN/i){
					$omon = 1;	
				}elsif($ctemp[1] =~ /FEB/i){
					$omon = 2;
				}elsif($ctemp[1] =~ /MAR/i){
					$omon = 3;
				}elsif($ctemp[1] =~ /APR/i){
					$omon = 4;
				}elsif($ctemp[1] =~ /MAY/i){
					$omon = 5;
				}elsif($ctemp[1] =~ /JUN/i){
					$omon = 6;
				}elsif($ctemp[1] =~ /JUL/i){
					$omon = 7;
				}elsif($ctemp[1] =~ /AUG/i){
					$omon = 8;
				}elsif($ctemp[1] =~ /SEP/i){
					$omon = 9;
				}elsif($ctemp[1] =~ /OCT/i){
					$omon = 10;
				}elsif($ctemp[1] =~ /NOV/i){
					$omon = 11;
				}elsif($ctemp[1] =~ /DEC/i){
					$omon = 12;
				}
			}

			$odate = "$ctemp[2]";
		}
		if($stime ne ''){
			@btemp = split(/:/, $stime);
			$odate =~ s/\s+//g;
			if($odate =~ /\d/){
				if($omon == $btemp[0] && $odate == $btemp[1]){
					last OUTER;
				}
				if($odate == $btemp[1]){
					last OUTER;
				}
			}
			if($btemp[0] > 12){
				$new_time_form = 'no';
				last OUTER;
			}
		}
	}
}
close(PRE);
		

#print '<table style="border-width:0px;width:100%">';
#print '<tr><th style="font-size:120%"><strong>OBSERVATION: ',"$dat",'</strong></th>';
#
#print '<td><a href="./orupdate.cgi">Back to Target Parameter Update Status Form</a></td></tr>';
#
#print "</table>";
if ($dtest == 1){
	print "<a href=\"$test_http/orupdate.cgi\" style=\"float:right\">Back to Target Parameter Update Status Form</a>";
}else{
	print "<a href=\"$usint_http/orupdate.cgi\" style=\"float:right\">Back to Target Parameter Update Status Form</a>";
}
print "<h1>OBSERVATION: $dat</h1>";

print "<p style='text-align:right'><strong>(submitted:  $latest_upate)</strong></p>";

print '<hr />';

print '<h2>Observation Information</h2>';
print '<table style="border-width:0px">';
print '<tr><th>OBSID</th><td>',"$obsid",'</td><th>Sequence #</th><td>',"$seq_nbr",'</td>';
print '<th>Proposal #</th><td>',"$proposal_number",'</td></tr>';

print '<tr><th>Target Name</th><td>',"$targname",'</td><th>Group ID</th><td>',"$group_id",'</td>';
print '<th>Obs AO Str</th><td>',"$obs_ao_str",'</td></tr>';

print '<tr><th>PI Name</th><td>',"$PI_name",'</td><td>&#160;</td><td>&#160;</td><td>&#160;</td><td>&#160;</td></tr>';
print '</table>';
print '<hr />';
 
#
#--- set indicators for checking
#

$pcnt     = 0;
$ncnt     = 0;
$prmk     = 0;
$nrmk     = 0;
$gch      = 0;
$gchf     = 0;
$ach      = 0;
$awch     = 0;
$awchf    = 0;
$after    = 0;
$after1   = 0;
$gent     = 0;
$dent     = 0;
$aent     = 0;
$awent    = 0;
$awentf   = 0;
$tcls     = 0;
$fnum     = 0;
$dra_chk  = 0;
$ddec_chk = 0;
$achk     = 0;
$pass_rmk = 0;
$ordr_old = 999;
$awin_chk = -999;

open(FH,"$ocat_dir/updates/$dat");

while(<FH>){

#
#--- this part heavily depends on updates database format. if the format changes the reading
#--- mechanisms break down.
#
	chomp $_;
	$_ =~ s/<Blank>/       /g;				#---- converting <Blank> to "     " (Jun 12, 2014/updated Dec 14,2020) accomodating ocat data page change
	$atest = $_;
	@atemp = split(//,$_);
	if($_ =~ /Below is a full listing/){
		$after1 = 1;
		$after++;
	}
#
#---- information before and after '------' are distinct
#
	if($_ =~ /^-----------/ && $after1 > 0){
		$after++;
	}
	if(($achk > 0 || $after > 0) && $pass_rmk == 0){
		if($past_comments =~ /\w/){
            $ptemp = $past_comments;
		    $ptemp =~ s/\r/<br \/>/g;
		    print '<h3><u>PAST COMMENTS</u></h3>';
			print "$ptemp<br />";
		}

		if($new_comments =~ /\w/){
            $ntemp = $new_comments;
		    $ntemp =~ s/\r/<br \/>/g;
		    print '<h3><u>NEW COMMENTS</u></h3>';
			print "$ntemp<br />";
		}

		if($past_remarks =~ /\w/){
            $ptemp = $past_remarks;
		    $ptemp =~ s/\r/<br \/>/g;
		    print '<h3><u>PAST REMARKS</u></h3>';
			print "$ptemp<br />";
		}

		if($new_remarks =~ /\w/){
            $ntemp = $new_remarks;
		    $ntemps =~ s/\r/<br \/>/g;
            print '<h3><u>NEW REMARKS</u></h3>';
			print "$ntemp<br />";
		}
		$pass_rmk++;
	}
	if($after < 1){
		if($atest =~ /^NEW/ || $atest =~ /^PAST/){
			@btemp = split(/=/,$atest);
			if($btemp[0] =~ /PAST COMMENT/){
				$past_comments = $btemp[1];
				$pcnt++;
			}elsif($btemp[0] =~ /NEW COMMENT/){
				$new_comments = $btemp[1];
				$pcnt++;
				$ncnt++;
			}elsif($btemp[0] =~ /PAST REMARK/){
				$past_remarks = $btemp[1];
				$pcnt++;
				$ncnt++;
				$prmk++;
			}elsif($btemp[0] =~ /NEW REMARK/){
				$new_remarks = $btemp[1];
				$pcnt++;
				$ncnt++;
				$prmk++;
				$nrmk++;
			}
		}
		if($atest =~ /GENERAL/){
			$pcnt++;
			$ncnt++;
			$prmk++;
			$nrmk++;
			$achk++;
		}

		unless($atest =~ /PAST MP/){
			if($pcnt > 0 && $ncnt == 0 && $prmk == 0 && $nrmk == 0 && $achk == 0){
				unless($atest =~ /^PAST COMMENTS/){
					$past_comments = "$past_comments"."$atest";
				}
			}elsif($ncnt > 0 && $prmk == 0 && $nrmk == 0 && $achk == 0){
				unless($atest =~ /^NEW COMMENTS/){
					$new_comments = "$new_comments"."$atest";
				}
			}elsif($prmk > 0 && $nrmk == 0 && $achk == 0){
				unless($atest =~ /^PAST REMARKS/){
					$past_remarks = "$past_remarks"."$atest";
				}
			}elsif($nrmk > 0 && $achk == 0){
				unless($atest =~ /^NEW REMARKS/){
					$new_remarks = "$new_remarks"."$atest";
				}
			}
		}

		@ctemp = split(/:/,$_);
		if($ctemp[0] eq 'GENERAL CHANGES'){
			$general_changes = $ctemp[1];
			$gch++;
		}elsif($ctemp[0] eq 'ACIS CHANGES'){
			$acis_changes = $ctemp[1];
			$ach++;
		}elsif($ctemp[0] eq 'ACIS WINDOW CHANGES'){
			$acis_win_changes = $ctemp[1];
			$awch++;
		}

		if(($btemp[0] eq  'OBSID') || ($btemp[0] eq 'SEQNUM') || ($btemp[0] eq 'TARGET')
			|| ($btemp[0] eq 'USERNAME') || ($btemp eq 'STATUS') ||($btemp[0] eq 'PROPOSAL_NUMBER')
			|| ($btemp[0] eq 'GROUP_ID') || ($btemp[0] eq 'OBS_AO_STR')){
			########## DO NOTHING ########
		}elsif($gch == 0){
			########## DO NOTHING ########
		}else {
			if($ach == 0){
				@temp = split(/S:/,$_);
				if($temp[0] =~ /^GENERAL/){
					print '<table border=1 style="width:80%">';
					print "<tr><td colspan = 3><strong><span style='font-size:110%;color:green'><br />$temp[0]<br />",'</span></strong></td></tr>';
					print '<tr><th style="text-align:left">Name</th>';
					print '<th style="text-align:left;width:30%">Original</th>';
					print '<th style="text-align:left;width:30%">Requested</th></tr>';
					$tcls++;
				}else{
					@ctemp = split(/ changed from/,$_);
					@dtemp = split(/ to /,$ctemp[1]);
					if($ctemp[0] =~ /y_amp/i
					   || $ctemp[0] =~ /y_freq/i
					   || $ctemp[0] =~ /y_phase/i
					   || $ctemp[0] =~ /z_amp/i
					   || $ctemp[0] =~ /z_freq/i
					   || $ctemp[0] =~ /z_phase/i){
						$dname[$dent] = $ctemp[0];
						$dorg[$dent] = $dtemp[0];
						$dnew[$dent] = $dtemp[1];
						$dent++;
					}
					$gname[$gent] = $ctemp[0];
					$gorg[$gent] = $dtemp[0];
					$gnew[$gent] = $dtemp[1];
#
#----- special treatment is required for the case the instrument is changed from acis to hrc
#
					if($gname[$gent] =~ /INSTRUMENT/i){
						if(($gorg[$gent] =~ /ACIS/i) && ($gnew[$gent] =~ /HRC/i)){
							$acisid = 'none';
						}
					}

					if($gname[$gent] =~ /^REMARKS/i){
						$gorg[$gent] = 'See Above';
						$gnew[$gent] = '';
					}
#
#---- special treatment for time; need to change print format
#

					if(($gname[$gent] =~ /tstart/i || $gname[$gent] =~ /tstop/i)
						&& ($new_time_form eq 'no')){
						@stemp = split(//, $dtemp[0]);
						if($stemp[0] =~ /\d/){
							@stemp = split(/:/, $dtemp[0]);
							$t_cnt = 0;
							foreach(@stemp){
								$t_cnt++;
							}
							if($t_cnt > 1){
								$gorg[$gent] = "$stemp[1]:$stemp[0]:$stemp[2]:$stemp[3]:$stemp[4]:$stemp[5]";
							}
						}
						@stemp = split(//, $dtemp[1]);
						if($stemp[0] =~ /\d/){
							@stemp = split(/:/, $dtemp[1]);
							$t_cnt = 0;
							foreach(@stemp){
								$t_cnt++;
							}
							if($t_cnt > 1){
								$gnew[$gent] = "$stemp[1]:$stemp[0]:$stemp[2]:$stemp[3]:$stemp[4]:$stemp[5]";
							}
						}
					}

					if($gname[$gent] =~ /\w/){
						if($gname[$gent] =~ /y_amp/i
							||$gname[$gent] =~ /y_freq/i
							||$gname[$gent] =~ /y_phase/i
							||$gname[$gent] =~ /z_amp/i
							||$gname[$gent] =~ /z_freq/i
							||$gname[$gent] =~ /z_phase/i){
								#####--- do nothing
						}else{
						
							$p_yes = 0;
							OUTER:
							foreach $comp (@paramarray){
								if($gname[$gent] =~ /$comp/i){
									$p_yes = 1;
									last OUTER;
								}
							}
							if($p_yes == 1){
								print "<tr><th style='text-align:left'>$gname[$gent]</th>";
								if($gorg[$gent] =~ /\w/){
									print "<td>$gorg[$gent]</td>";
								}else{
									print "<td>&#160;</td>";
								}
								if($gnew[$gent] =~/\w/){
									print "<td>$gnew[$gent]</td></tr>";
								}else{
									print "<td>&#160;</td></tr>";
								}
							}
						}
						$gent++;
					}
				}
			}elsif($ach > 0 && $achf == 0){
				if($gent == 0){
					print '<tr><td colspan = 3> No Entry </td></tr>';
				}
				$achf++;
			}

			if($ach > 0 && $awch == 0){
				@temp = split(/S:/,$_);
				if($temp[0] =~ /^ACIS CHANGE/){

					if($dent > 0){
						print "<tr><td colspan=3><strong><span style='font-size:110%;color:green'><br />DITHER CHANGE<br />",'</span></strong></td></tr>';
						print '<tr><th style="text-align:left">Name</th>';
						print '<th style="text-align:left;width:30%">Original</th>';
						print '<th style="text-align:left;width:30%">Requested</th></tr>';
						for($di = 0; $di < $dent; $di++){

							if($dname[$di] eq 'Y_AMP' || $dname[$di] eq 'Y_FREQ' || $dname[$di] eq 'Y_PHASE'
								|| $dname[$di] eq 'Z_AMP' || $dname[$di] eq 'Z_FREQ' 
								|| $dname[$di] eq 'Z_PHASE'){
								print "<tr><th style='text-align:left'>$dname[$di]</th>";
								if($dorg[$di] =~ /\w/){
									print "<td>$dorg[$di]</td>";
								}else{
									print "<td>&#160;</td>";
								}
								if($dnew[$di] =~ /\w/){
									print "<td>$dnew[$di]</td></tr>";
								}else{
									print "<td>&#160;</td></tr>";
								}
							}
						}
					}
					print "<tr><td colspan = 3><strong><span style='font-size:110%;color:green'><br />$temp[0]<br />",'</span></strong></td></tr>';
					print '<tr><th style="text-align:left">Name</th>';
					print '<th style="text-align:left;width:30%">Original</th>';
					print '<th style="text-align:left;width=30%">Requested</th></tr>';
					$tcls++;
				}else{
					if($acisid eq 'none' && $acisid_wrote ne 'yes'){
						print "<tr><th style='align:left'>ACISID</th>";
						print "<td>&#160;</td><td>NONE</td></tr>";
						$acisid_wrote = 'yes';
					}elsif($acisid ne 'none'){
						@ctemp = split(/ changed from/,$_);
						@dtemp = split(/ to /,$ctemp[1]);
						$aname[$aent] = $ctemp[0];
						$aorg[$aent] = $dtemp[0];
						$anew[$aent] = $dtemp[1];
						if($aname[$aent] =~ /\w/){
							print "<tr><th style='text-align:left'>$aname[$aent]</th>";
							if($aorg[$aent] =~ /\w/){
								print "<td>$aorg[$aent]</td>";
							}else{
								print "<td>&#160;</td>";
							}
							print "<td>$anew[$aent]</td></tr>";
	
							$aent++;
						}
					}else{
							$aent++;
					}
				}
			}elsif($ach > 0 && $awch > 0 && $awchf == 0){
				if($aent == 0){
					print '<tr><td colspan = 3> No Entry </td></tr>';
				}
				$awchf++;
			}

			if($awch > 0){
				@temp = split(/S:/,$_);
				if($acisid eq  'none'){
					$awent++;
				}else{
					if($temp[0] =~ /^ACIS WINDOW/){
						print "<tr><td colspan = 3><strong><span style='font-size:110%;color:green'><br />$temp[0]<br />",'</span></strong></td></tr>';
						print '<tr><th style="text-align:left">Name</th>';
						print '<th style="text-align:left;width:30%">Original</th>';
						print '<th style="text-align:left;width:30%">Requested</th></tr>';
						$tcls++;
					}else{
						@ctemp = split(/ changed from/,$_);
						@dtemp = split(/ to /,$ctemp[1]);
						$awname[$awent] = $ctemp[0];
						$aworg[$awent] = $dtemp[0];
						$awnew[$awent] = $dtemp[1];
						if($awname[$awent] =~ /\w/){
							print "<tr><th style='text-align:left'>$awname[$awent]</th>";
							if($aworg[$awent] =~ /\w/){
								print "<td>$aworg[$awent]</td>";
							}else{
								print "<td>&#160;</td>";
							}
							print "<td>$awnew[$awent]</td></tr>";
	
							$awent++;
						}
					}
				}
			}
		}
	}elsif($after >= 2){
		if($tcls == 0){
			print "<p style='font-size:120%;padding-top:25px;padding-bottom:25px'><strong>No Update </strong></p>";
			$tcls++;
			$awentf++;
		}else{
			if($awent == 0 && $awentf == 0){
				print '<tr><td colspan = 3> No Entry </td></tr>';
				$awentf++;
			print "</table>";
			}
		}

#
#---	this part is totally input format dependent. if the input formant change it does not work.
#---	in fact, this script does not work with earlier input data.
#---XXXXX	we assume the name is column 1-28, original data is in columns 29-58, and the new data is in 59 and after.
#---	we assume the name is column 1-23, original data is in columns 23-53, and the new data is in 53 and after.
#

		@btemp = split(//,$_);
		@line = ();
		$tname = '';
		$torg = '';
		$tnew = '';
		$cnt = 1;
		foreach $ent (@btemp){
#			if($cnt < 29){
			if($cnt < 23){
				if($ent =~ /\w/){
					$tname = "$tname"."$ent";
				}
#			}elsif($cnt >= 29 && $cnt < 59){
			}elsif($cnt >= 23 && $cnt < 53){
				if($tname eq 'SOE_ST_SCHED_DATE'	# dated entry needs white spaces
					|| $tname =~ /TSTART/
					|| $tname =~ /TSTOP/
					|| $tname eq 'LTS_LT_PLAN'){
					$torg = "$torg"."$ent";
				}elsif($ent =~/\w/ || $ent eq '.' || $ent eq '_' || $ent eq '-'
					|| $ent eq ':' || $ent eq '+' || $ent eq '/'){
					$torg = "$torg"."$ent";
				}
#			}elsif($cnt >=59){
			}elsif($cnt >=53){
				if($tname eq 'SOE_ST_SCHED_DATE'
					|| $tname =~ /TSTART/
					|| $tname =~ /TSTOP/
					|| $tname eq 'LTS_LT_PLAN'){
					$tnew = "$tnew"."$ent";
				}elsif($ent =~/\w/ || $ent eq '.' || $ent eq '_' || $ent eq '-'
					|| $ent eq ':' || $ent eq '+'|| $ent eq '/'){
					$tnew = "$tnew"."$ent";
				}
			}
			$cnt++;
		}
		push(@line, $tname);
		push(@line, $torg);
		push(@line, $tnew);

#
#--- change format for ra and dec, if required
#
		if($line[0] eq 'RA'){

#
#---checking for the case format is 00 00 00.0 type
#
			$ra_org = '';
			$ra_new = '';
#			for($i=58;$i<70;$i++){
			for($i=52;$i<64;$i++){
				$ra_new = $ra_new.$btemp[$i];
			}
			@ctemp = split(/ /,$ra_new);
			$f_chk_r = 0;
#
#--- check for 00 00 00 case.
#
#			if($btemp[60] eq ' ' || $btemp[61] eq ' ' ){	
			if($btemp[54] eq ' ' || $btemp[55] eq ' ' ){	
 
				$r_ra = 15.0*($ctemp[0] + $ctemp[1]/60.0 + $ctemp[2]/3600.0);
				$f_chk_r = 1;
			}

			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];

			@ctemp = split(/:/,$line[2]);	# this is 00:00:00 case
			if($ctemp[1] =~ /\w/){
				$r_ra = 15.0*($ctemp[0] + $ctemp[1]/60.0 + $ctemp[2]/3600.0);
			}else{
				if($f_chk_r == 0){
					$r_ra = $line[2];
				}
			}
		} elsif($line[0] eq 'DEC'){
#
#---- checking for the case format is 00 00 00.0 type
#
			$dec_org = '';
			$dec_new = '';
#			for($i=58;$i<70;$i++){
			for($i=52;$i<64;$i++){
				$dec_new = $dec_new.$btemp[$i];
			}
			@ctemp = split(/ /,$dec_new);
			$f_chk_d = 0;
#			if($btemp[60] eq ' ' || $btemp[61] eq ' ' ){
			if($btemp[54] eq ' ' || $btemp[55] eq ' ' ){
				if($ctemp[0] < 0){
					$r_dec = -1.0*(-1.0*$ctemp[0] + $ctemp[1]/60.0 + $ctemp[2]/3600.0);
				}else{
					$r_dec = $ctemp[0] + $ctemp[1]/60.0 + $ctemp[2]/3600.0;
					$f_chk_d = 1;
				}
			}

			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];

			@ctemp = split(/:/,$line[2]);
#
#---- heck '-' before computer dec value.
#
			if($ctemp[1] =~ /\w/){
				if($ctemp[0] < 0){
					$r_dec = -1.0*(-1.0*$ctemp[0] + $ctemp[1]/60.0 + $ctemp[2]/3600.0);
				}else{
					$r_dec = $ctemp[0] + $ctemp[1]/60.0 + $ctemp[2]/3600.0;
				}
			}else{
				if($f_chk_d == 0){
					$r_dec = $line[2];
				}
			}
#
#---- DRA and DDEC take RA and DEC unless they already have entries
#
		} elsif($line[0] eq 'DRA'){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			if($line[2]  =~ /\d/){
				$new[$fnum] = $line[2];
				$new[$fnum] = $r_ra;
				$dra_chk = 2;
			}else{
				$new[$fnum] = $r_ra;
				$dra_chk = 1;
			}
		} elsif($line[0] eq 'DDEC'){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			if($line[2]  =~ /\d/){
				$new[$fnum] = $line[2];
				$new[$fnum] = $r_dec;
				$ddec_chk = 2;
			}else{
				$new[$fnum] = $r_dec;
				$ddec_chk = 1;
			}
		}elsif($line[0] eq 'WINDOW_CONSTRAINT'){
			$name[$fnum] = 'WINDOW_CONSTRAINT1';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] eq 'TSTART'){
			$name[$fnum] = 'TSTART1';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] eq 'TSTOP'){
			$name[$fnum] = 'TSTOP1';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];


		}elsif($line[0] eq 'ROLL_CONSTRAINT'){
			$name[$fnum] = 'ROLL_CONSTRAINT1';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] eq 'ROLL_180'){
			$name[$fnum] = 'ROLL_1801';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] eq 'ROLL'){
			$name[$fnum] = 'ROLL1';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] eq 'ROLL_TOLERANCE'){
			$name[$fnum] = 'ROLL_TOLERANCE1';
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
#
#--- some older database use win_order so we need to correct it.
#
		} elsif($line[0] =~ /^win_order/i){
			$name[$fnum] = 'ORDR';	
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^ordr/i){
			if($line[0] eq 'ORDR' && $ordr_old != 0){
				$name[$fnum] = 'ORDR';
				$org[$fnum]  = $line[1];
				$new[$fnum]  = $line[2];
				$ordr_old = 1;
			}else{
				$name[$fnum] = $line[0];
				$org[$fnum]  = $line[1];
				$new[$fnum]  = $line[2];
				$ordr_old = 0;
			}
#
#--- accept chip and CHIP
#
		} elsif($line[0] =~ /^CHIP\b/i){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
#
#--- accept inculde_flag and INCLUDE_FLAG
#
#		} elsif($line[0] eq 'include_flag'|| $line[0] eq 'INCLUDE_FLAG'){
#			$name[$fnum] = 'INCLUDE_FLAG1';
#			$org[$fnum]  = $line[1];
#			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^START_ROW/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^START_COLUMN/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^HEIGHT/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^WEIGHT/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^LOWER_THRESHOLD/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^PHA_RANGE/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}elsif($line[0] =~ /^SAMPLE/){
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		} else {
			$name[$fnum] = $line[0];
			$org[$fnum]  = $line[1];
			$new[$fnum]  = $line[2];
		}
		$fnum++;
	}
}

@new_list = ();

OUTER:
foreach $ent (@paramarray2){
	foreach $comp (@name){
		$test = uc ($comp);
		if($test eq $ent){
			next OUTER;
		}
	}
	push(@new_list, $ent);
}

#
#---- the following sub makes most of the html page
#

html_print();
if ($dtest == 1){
	print "<p  style='text-align:right'><a href=\"$test_http/orupdate.cgi\">Back to Target Parameter Update Status Form</a></p>";
}else{
	print "<p  style='text-align:right'><a href=\"$usint_http/orupdate.cgi\">Back to Target Parameter Update Status Form</a></p>";
}

print "</body>";
print "</html>";

###########################################################
### check_update_database: find a newest entry for obsid ##
###########################################################

sub check_update_datebase {
	@ctemp      = split(/\./, $obsid);
	$obsid_base = $ctemp[0];
	$c_version  = $ctemp[1];

#
#--- check whether a user accidentally put such as 2344.02 instead of 2344.002
#

	@v_chk = split(//, $c_version);
	$chk   = 0;
	foreach (@v_chk){
		$chk++;
	}
	$c_diff = 3 - $chk;
	for($i = 0; $i < $c_diff; $i++){
		$c_version = '0'."$c_version";
	}
	$obsid = "$obsid_base".'.'."$c_version";


	$name       = "$obsid_base".'*';

	system("ls $ocat_dir/updates/$name > $temp_dir/zdatlist.tmp");

	open(FH,"$temp_dir/zdatlist.tmp");
	$latest_version = 0;

	while(<FH>){
		chomp $_;
		@zlist = split(/\./,$_);
		if($zlist[1] > $latest_version){
			$latest_version = $zlist[1];
		}
	}
	close(FH);
	system("rm $temp_dir/zdatlist.tmp");

	$version_warning = 0;
	if($c_version > $latest_version){
		$version_warning = 1;
	}

	$line         = `ls -l $ocat_dir/updates/$obsid`;

	@ctemp        = split(/\s+/, $line);
#
#--- today's date
#
	($lsec, $lmin, $lhour, $lmday, $lmon, $lyear, $lwday, $lyday, $isdst) = localtime(time);

	$this_year = 1900 + $lyear;
#
#--- if the file is created this year, the format is slightly different from that of the past years
#
	if($ctemp[7] =~ /:/){
		conv_lmon_to_ydate($ctemp[5]);
		if($mydate < 0){
			$pyear = $this_year -1;
		}elsif($mydate > $lyday){
			$pyear = $this_year -1;
		}else{
			$pyear = $this_year;
		}
	}else{
		$pyear = $ctemp[7];
	}
		
	$latest_upate = "$ctemp[5] $ctemp[6] $pyear";
}
		


###########################################################
### 	html_print: printing html page                 	###
###########################################################

sub html_print{
	print "<hr />";
	print "<h2>All Entries</h2>";

    print "<div style='text-align:left;padding-bottom:10px;'>";
    print "<table border=0 style='text-align:left;' >";
    print "<tr><th>Color Cording: </th></tr>";
    print "<tr>";
    print "<td style='color:green;'>Requested value is in the database.</td>";
    print "</tr><tr>";
    print "<td style='color:red;'>Requested value is not in the database yet.</td>";
    print "</tr><tr>";
    print "<td style='color:fuchsia;'> There was no request for the update, ";
    print "but the database value is changed.</td>";
    print "</tr>";
    print "</table>";
    print "</div>";


	print "<table border=1>\n";
	print "<tr><th colspan=4><span style='font-size:110%'>General Parameters</span></th></tr>";
	print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
	print "<span style='color:green'>ORIGINAL VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";
	foreach $entry (@gen_paramarray){
		match_param();
	}
	print "</table>\n";
	print "<div style='padding-bottom:20px'></div>";

	print "<table border=1>\n";
	print "<tr><th colspan=4><span style='font-size:110%'>Dither Parameters</span></th></tr>";
	print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
	print "<span style='color:green'>ORIGINAL VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";
	foreach $entry (@dither_paramarray){
		match_param();
	}
	print "</table>\n";
	print "<div style='padding-bottom:20px'></div>";

	print "<table border=1>\n";
	print "<tr><th colspan=4><span style='font-size:110%'>Time Constraint Parameters</span></th></tr>";
	print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
	print "<span style='color:green'>ORIGINAL VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";

	$entry = 'TIME_ORDR';
	match_param();

	$u_lim = $snew;
	unless($u_lim =~ /\d/ && $u_lim > 0){
		$lcase = lc($entry);
		$u_lim = ${$lcase};
	}

	for($it = 1; $it <= $u_lim; $it++){
		foreach $tent (@time_const_paramarray){
			$entry = "$tent"."$it";
			if(${$entry} =~ /\W/){
				$entry = $tent;
			}
			match_param();
		}
	}
	print "</table>\n";
	print "<div style='padding-bottom:20px'></div>";

	print "<table border=1>\n";
	print "<tr><th colspan=4><span style='font-size:110%'>Roll Constraint Parameters</span></th></tr>";
	print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
	print "<span style='color:green'>ORIGINAL VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";


	$entry = 'ROLL_ORDR';
	match_param();

	$u_lim = $snew;
	unless($u_lim =~ /\d/ && $u_lim > 0){
		$lcase = lc($entry);
		$u_lim = ${$lcase};
	}

	for($it = 1; $it <= $u_lim; $it++){
		foreach $tent (@roll_const_paramarray){
			$entry = "$tent"."$it";
			match_param();
		}
	}
	print "</table>\n";
	print "<div style='padding-bottom:20px'></div>";

	print "<table border=1>\n";
	print "<tr><th colspan=4><span style='font-size:110%'>Constraints</span></th></tr>";
	print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
	print "<span style='color:green'>ORIGINAL VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";
	foreach $entry (@const_paramarray){
		match_param();
	}
	print "</table>\n";
	print "<div style='padding-bottom:20px'></div>";

	if($instrument =~ /HRC/i){
		print "<table border=1>\n";
		print "<tr><th colspan=4><span style='font-size110%'>HRC  Parameters</span></th></tr>";
		print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
		print "<span style='color:green'>ORIGINAL VALUE</span></th>";
		print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
		print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";
		foreach $entry (@hrc_paramarray){
			match_param();
		}
		print "</table>\n";
		print "<div style='padding-bottom:20px'></div>";
	}

	if($instrument =~ /ACIS/i){
		print "<table border=1>\n";
		print "<tr><th colspan=4><span style='font-size:110%'>ACIS Parameters</span></th></tr>";
		print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
		print "<span style='color:green'>ORIGINAL VALUE</span></th>";
		print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
		print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";
		foreach $entry (@acis_gen_paramarray){
			match_param();
		}
		print "</table>\n";
		print "<div style='padding-bottom:20px'></div>";
	
		print "<table border=1>\n";
		print "<tr><th colspan=4><span style='font-size:110%'>ACIS Window Constraint Parameters</span></th></tr>";
		print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
		print "<span style='color:green'>ORIGINAL VALUE</span></th>";
		print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
		print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";

#
#------ ACIS WINDOW CONSTRATINTS
#

#		$entry = 'SPWINDOW_FLAG';
		$entry = 'SPWINDOW';

		match_param();

#
#---- this is an indicator whether ordr in older format is filled or kept empty
#
		$aw_cls = 0;
		if($snew =~ /N/i && $sorg =~ /N/i && $ddat =~ /N/i){
			$aw_cls = 1;					#---- keep ordr raw empty
		}

		if($ordr_old == 1){
#
#---- older format for acis window constraint
#
			$entry = 'ORDR';
        		for($m = 1; $m < $fnum; $m++){
                		if($entry eq $name[$m]){
                        		last;
                		}
        		}
			
				$ltent = lc($entry);
				$ddat  = ${$ltent}[$u_lim];
				$ddat  =~ s/\s+//g;

			$u_lim = $new[$m];
			unless($u_lim =~ /\d/ && $u_lim > 0){
				$lcase = lc($entry);
				$u_lim = ${$lcase};
			}
		
			for($it = 1; $it <= $u_lim; $it++){
				AOUTER:
				foreach $tent (@acis_win_const_array){
					$entry = "$tent"."$it";
					$awin_chk = $it;
					match_param();
					$awin_chk = -999;
				}
			}
		}else{
#
#---- newer format for acis window constraint
#
			LOUTER:
			for($it = 1; $it <= 30; $it++){
				foreach $tent (@acis_win_const_array){
					$entry = "$tent"."$it";
					if($tent =~ /ORDR/i){
						$lchk = 0;
						IOUTER:
						for($i = 1; $i < $fnum; $i++){
                					if($entry eq $name[$i]){
								$lchk = 1;
                        					last IOUTER;
                       				 	}
						}
						if($lchk == 0){
							last LOUTER;
						}
					}
					$awin_chk = $it;
					match_param();
					$awin_chk = -999;
				}
			}
		}

		print "</table>\n";
		print "<div style='padding-bottom:20px'></div>";
	}

#
#--- TOO
#

	print "<table border=1>\n";
	print "<tr><th colspan=4><span style='font-size:110%'>TOO Parameters</span></th></tr>";
	print "<tr style='text-align:left'><th style='width:40%'><span style='color:green'>PARAM NAME</span></th><th style='width:20%'>";
	print "<span style='color:green'>ORIGINAL VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>REQUESTED VALUE</span></th>";
	print "<th style='width:20%'><span style='color:green'>UPDATED VALUE</span></th></tr>\n";
	foreach $entry (@too_paramarray){
		match_param();
	}
	print "</table>\n";
	print "<div style='padding-bottom:20px'></div>";

	print "<h2>REMARKS</h2>";
	
	OUTER:
	for($i = 1; $i < $fnum; $i++){
		if($name[$i] =~ /REMARKS/i){
			last;
		}
	}
	
	if($org[$i] eq 'NULL'){
		$org[$i] = '';
	}
	if($new[$i] eq 'NULL'){
		$new[$i] = '';
	}

	$sorg = $past_remarks;
	$sorg =~ s/\s+//g;
	$snew = $new_remarks;
	$snew =~ s/\s+//g;
    $snew =~ s/\r//g;
	$ddat = $remarks;
	$ddat =~ s/\s+//g;

	print "<table border=1>";
	print '<tr><th style="width:10%">ORIGINAL</th>';
	if($sorg eq ''){
		print '<td>&#160;</td></tr>';
	}else{
		print "<td>$past_remarks</td></tr>";
	}

	print '<tr><th style="width:10%">REQUESTED</th>';
	if($snew eq ''){
		print '<td>&#160;</td></tr>';
	}else{
		print "<td>$new_remarks</td></tr>";
	}

	print '<tr><th style="width:10%">UPDATED</th>';
	if($snew eq '' &&  $ddat eq ''){
		print '<td>&#160;</td></tr>';
	}elsif($snew ne $ddat){
		if($ddat eq ''){
			print "<td style='background-color:red'>&#160;</td></tr>";
		}elsif($ddat eq $sorg && $snew eq ''){
			print "<td>$remarks</td></tr>";
		}else{
			print "<td style='background-color:red'>$remarks</td></tr>";
		}
	}else{
		print "<td>$remarks</td></tr>";
	}

	print "</table>";
	print "<div style='padding-bottom:20px'></div>";

#
#--- Comment
#

	print "<h2>COMMENTS</h2>";
	
	OUTER:
	for($i = 1; $i < $fnum; $i++){
		if($name[$i] =~ /COMMENTS/i){
			last;
		}
	}
	
	if($org[$i] eq 'NULL'){
		$org[$i] = '';
	}
	if($new[$i] eq 'NULL'){
		$new[$i] = '';
	}

	$sorg = $past_comments;
	$sorg  =~ s/\s+//g;
	$snew = $new_comments;
	$snew =~ s/\s+//g;
	$ddat = $comments;
	$ddat =~ s/\s+//g;

	print "<table border=1 style='width:80%'>";
	print '<tr><th style="width:10%">ORIGINAL</th>';
	if($sorg eq ''){
		print '<td>&#160;</td></tr>';
	}else{
		print "<td>$past_comments</td></tr>";
	}

	print '<tr><th style="width:10%">REQUESTED</th>';
	if($snew eq ''){
		print '<td>&#160;</td></tr>';
	}else{
		print "<td>$new_comments</td></tr>";
	}

	print '<tr><th style="idth:10%">UPDATED</th>';
	if($snew eq '' && $ddat eq ''){
		print '<td>&#160;</td></tr>';
	}elsif($snew ne $ddat){
		if($ddat eq ''){
			print "<td>&#160;</td></tr>";
		}elsif($ddat eq $sorg && $snew eq ''){
			print "<td>$comments</td></tr>";
		}else{
			print "<td>$comments</td></tr>";
		}
	}else{
		print "<td>$comments</td></tr>";
	}

	print "</table>";
	print "<div style='padding-bottom:20px'></div>";
}

########################################################################################################
### match_param: compare the database parameters to those of submitted paramters                     ###
########################################################################################################

sub match_param{

	$mchk = 0;
	OUTER:
	for($i = 1; $i < $fnum; $i++){
		if($entry eq $name[$i]){
			$mchk++;
			last;
		}
	}
#
#--- correcting order ranking. ordr may not go 1, 2, 3 .... it may go 2, 1, 3... (Jul 14, 2015)
#
    if($entry =~ /ordr/i){
        $pordr = $new[$i]
    }
#
#--- these two parameters are added Mar 2011, and older data don't have them; need to have a special treatment
#
	if($entry =~ /MULTIPLE_SPECTRAL_LINES/i || $entry =~ /SPECTRA_MAX_COUNT/i){
		if($mchk == 0){
			$mchk = 10;
		}
	}

	if($mchk >  0){
		print "<tr>\n";
		if($name[$i] =~ /INCLUDE_FLAG/i){
			$lname =lc($name[$i]);
			$sorg  = $org[$i];
			$sorg  =~ s/\s+//g;
			$snew  = $new[$i];
			$snew  =~ s/\s+//g;
			$ddat  = ${$lname};
			$ddat  =~ s/\s+//g;
			if($ddat eq ''){
				${$lname} = 'I';
				$ddat = 'I';
			}
			$spcl_color = 0;
		}else{
#
#---- sepceial case for Mar 2011 parameters (MULTIPLE_SPECTRAL_LINES and SPECTRA_MAX_COUNT)
#
			if($mchk == 10){
				$name[$i] = uc($entry);
				$lname =lc($name[$i]);
				$sorg  = '';
				$snew  = '';
				$ddat  = ${$lname};
				$ddat  =~ s/\s+//g;
				if($ddat =~ /NULL/){
					$ddat = '';
				}
				$spcl_color = 0;
			}else{
				$lname =lc($name[$i]);
				$sorg  = $org[$i];
				$sorg  =~ s/\s+//g;
				$snew  = $new[$i];
				$snew  =~ s/\s+//g;
				$ddat  = ${$lname};
				$ddat  =~ s/\s+//g;
				$spcl_color = 0;
			}

#
#--- aciswin constraint data from database: shifting one for display purpose
#
			if($awin_chk > 0){
				$ltent = lc($tent);
#----- Jul 23 2015 change. this may be modified farther
                if( $it == $ordr[$it-1]){
				    $ddat  = ${$ltent}[$it-1];
                }else{
                    $ddat  = ${$ltent}[$ordr[$it]];
                }
				$ddat  =~ s/\s+//g;
			}

#
#---- special case for time; we need to change the format to mm:dd:yyy:hh:mm:ss
#
			if(($lname =~ /tstart/i || $lname =~ /tstop/i)
				&& ($new_time_form eq 'no')){
				@stemp = split(//,$sorg);
#
#--- checking a format of time
#
				if($stemp[0] =~ /\d/){
					@stemp = split(/:/,$sorg);
					$t_cnt = 0;
					foreach(@stemp){
						$t_cnt++;
					}
					if($t_cnt > 1){
						$sorg = "$stemp[1]:$stemp[0]:$stemp[2]:$stemp[3]:$stemp[4]:$stemp[5]";
						$org[$i] = $sorg;
					}
				}
	
				@stemp = split(//,$snew);
				if($stemp[0] =~ /\d/){
					@stemp = split(/:/,$snew);
					$t_cnt = 0;
					foreach(@stemp){
						$t_cnt++;
					}
					if($t_cnt > 1){
						$snew = "$stemp[1]:$stemp[0]:$stemp[2]:$stemp[3]:$stemp[4]:$stemp[5]";
						$new[$i] = $snew;
					}
				}
			}
		}

		@dchk = split(//,$ddat);
#		@dchk = split(//,$sorg);

		@echk = split(//, $name[$i]);
		$end = pop @echk;
#
#---- special treatment for mainly acis window constratint
#
		if($end =~ /\d/ && $end >= 0){ 
			$comb = "";
			foreach $ent (@echk){
				$comb = "$comb"."$ent";
			}

			#$name[$i] = "acis window chip ordr  $end: $comb";
			$name[$i] = "acis window chip ordr  $pordr: $comb";
			#$name[$i] = "acis window chip set  $pordr: $comb";
		}
				
		if($lname eq 'ra' || $lname eq 'dec'){
#
#--- sub to check and round numbers
#
			chk_frac($sorg);
			$sorg = $output;

			chk_frac($ddat);
			$ddat = $output;
#
#--- color cording sub
#
			$cck = 0;
			color_coding();

		}elsif($lname eq 'dra'){
			$ddat = ${dra};
			unless($ddat =~ /\d/){
				$ddat = ${ra};
				$spcl_color = 1;
			}
			chk_frac($sorg);
			$sorg = $output;
			chk_frac($snew);
			$snew = $output;
			chk_frac($ddat);
			$ddat = $output;
			if($dra_chk == 1){
				$spcl_color = 1;
			}
			$cck = 0;
			color_coding();

		}elsif($lname eq 'ddec'){
			$ddat = ${ddec};
			unless($ddat =~ /\d/){
				$ddat = ${dec};
				$spcl_color = 1;
			}
			$ddat = ${dec};
			chk_frac($sorg);
			$sorg = $output;
			chk_frac($snew);
			$snew = $output;
			chk_frac($ddat);
			$ddat = $output;
			if($ddec_chk == 1){
				$spcl_color = 1;
			}
			$cck = 0;
			color_coding();

		}elsif($dchk[0] =~ /\d/ || $dchk[0] eq '-' || $dchk[0] eq '+'){
			chk_frac($sorg);
			$sorg = $output;
			chk_frac($snew);
			$snew = $output;
			chk_frac($ddat);
			$ddat = $output;
			$cck = 0;
#
#--- if the case of comparing time, we use none digit comparison (added 11/17/08)
#
			if($snew =~ /:/){
				$cck = 1;
			}
			color_coding();

		}else{
			$cck = 1;
			color_coding();
		}
		print "</tr>\n";
	}else{
		@echk = split(//, $entry);
		$end = pop @echk;
		if($end =~ /\d/ && $end > 0){ 
			$comb = "";
			foreach $ent (@echk){
				$comb = "$comb"."$ent";
			}

			$entry = "acis window chip ordr $end: $comb";
		}
		
#
#--- reading the older format where "ordr" is still used as a counter:
#
		if($entry =~ /ORDR/){
			$enum = $entry;
			$enum =~ s/entry //;
			$enum = int($enum)-1;
			
			if($aw_cls == 1){
				print "<tr style='text-align:left'><th>$entry</th><td>&#160;</td><td>&#160;</td><td>&#160;</td></tr>";
			}elsif($ordr[$enum] =~ /\d/){
				print "<tr style='text-align:left'><th>$entry</th><td>$end</td><td>$end</td><td>$ordr[$enum]</td></tr>";
			}else{
				print "<tr style='text-align:left'><th>$entry</th><td>$end</td><td>$end</td><td>&#160;</td></tr>";
			}
		}else{
			print "<tr style='text-align:left'><th>$entry</th><td>&#160;</td><td>&#160;</td><td>&#160;</td></tr>";
		}
		$snew = 1;
	}
}

################################################################
###     chk_frac: check fraction so that you can round number ##
################################################################

sub chk_frac{
        ($input) = @_;
	@val = split(/\./,$input);
	$output = $input;
	if($val[1] =~ /\d/){
		@cfraction = split(//,$val[1]);
		$ncnt = 0;
		foreach(@cfraction){
			$ncnt++;
		}
		$nfraction = '';
		if($cfraction[6] > 4){
			$cfraction[5]++;
			if($cfraction[5] > 9) {
				$cfraction[5] -= 10;
				$cfraction[4]++;
				if($cfraction[4] > 9){
					$cfraction[4] -= 10;
					$cfraction[3]++;
					if($cfraction[3] > 9){
						$cfraction[3] -= 10;
						$cfraction[2]++;
						if($cfraction[2] > 9){
							$cfraction[2] -= 10;
							$cfraction[1]++;
					     		if($cfraction[1] > 9){
								$cfraction[1] -= 10;
								$val[0]++;
							}
						}
					}
				}
			}
		}
		for($k = 0; $k < 6; $k++){
			$nfraction = "$nfraction"."$cfraction[$k]";
		}
		$output = "$val[0]".'.'."$nfraction";
	}
}

#############################################*
### color_coding: html print with color code #
#############################################**

sub color_coding{

#
#--- for digit cases
#
        if($cck == 0){
                if(($sorg == $snew) && ($sorg == $ddat)){
#
#----black
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($snew =~ /\w/){
                        	print "<td>$snew</td>";
			}else{
				print "<td>&#160;</td>";
			}
			if($ddat =~ /\w/){
				print "<td>$ddat</td>\n";
			}else{
				print "<td>&#160;</td>";
			}
                }elsif(($sorg == $ddat) && ($snew eq '')){
#
#----black
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($snew =~ /\w/){
                        	print "<td>$snew</td>\n";
			}else{
				print "<td>&#160;</td>";
			}
			if($ddat =~ /\w/){
                        	print "<td>$ddat</td>\n";
			}else{
				print "<td>&#160;</td>";
			}
			
                }elsif($snew == $ddat){
#
#----green
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($snew =~/\w/){
                        	print "<td>$snew</td>\n";
			}else{
				print "<td>&#160;</td>";
			}
			if($ddat =~/\w/){
                        	print "<td style='background-color:#00AA00'>$ddat<br />\n";
			}else{
                        	print "<td style='background-color:#00AA00'>&#160;<br />\n";
			}
                }elsif(($snew != $ddat) && ($snew =~ /\w/)){
#
#----red
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($lname eq 'acisid'){
				if($snew =~ /\w/){
					print "<td>$snew</td>";
				}else{
					print "<td>&#160;</td>";
				}
				if($ddat =~ /\w/){
					print "<td style='background-color:magenda'>$ddat<br />\n";
				}else{
					print "<td style='background-color:magenda'>&#160;<br />\n";
				}
			}elsif($spcl_color == 0){
                        		print "<td>$snew</td>";
					print "<td style='background-color:red'>$ddat<br />\n";
			}else{
                        		print "<td>$snew</td>";
					print "<td style='background-color:blue'>$ddat<br />\n";
			}
                }elsif(($snew eq '') && ($ddat eq '')){
#
#----red
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($lname eq 'acisid'){
				if($snew =~ /\w/){
					print "<td>$snew</td>";
				}else{
					print "<td>&#160;</td>";
				}
				if($ddat =~ /\w/){
					print "<td style='background-color:magenda'>$ddat<br />\n";
				}else{
					print "<td style='background-color:magenda'>&#160;<br />\n";
				}
			}elsif($spcl_color == 0){
				if($snew =~ /\w/){
                        		print "<td>$snew</td>";
				}else{
					print "<td>&#160;</td>";
				}
				if($ddat =~ /\w/){
					print "<td style='background-color:red'>$ddat<br />\n";
				}else{
					print "<td style='background-clolr:red'>&#160;<br />\n";
				}
			}else{
				if($snew =~/\w/){
                        		print "<td>$snew</td>";
				}else{
					print "<td>&#160;</td>";
				}
				if($ddat =~ /\d/){
					print "<td style='background-color:blue'>$ddat<br />\n";
				}else{
					print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
				}
			}
                }elsif(($sorg != $ddat) && ($snew eq '')){
#
#----fuchsia
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($snew =~ /\w/){
                        	print "<td>$snew</td>";
			}else{
				print "<td>&#160;</td>";
			}
			if($ddat =~ /\w/){
				print "<td style='background-color:fuchsia'>$ddat<br />\n";
			}else{
				print "<td style='background-color:fuchsia'>&#160;<br />\n";
			}
                }else{
#
#----black
#
			if($sorg =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$sorg</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($snew =~ /\w/){	
                        	print "<td>$snew</td>";
			}else{
				print "<td>&#160;</td>";
			}
			if($ddat =~ /\w/){
				print "<td>$ddat<br />\n";
			}else{
				print "<td>&#160;</td>";
			}
                }
#
#----for  words
#
        }else{
                if(($sorg eq $snew) && ($sorg eq $ddat)){
#
#----black
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&#160;</td>";
			}
#			if(${$lname} =~ /\w/){
#				print "<td>${$lname}<br />\n";
			if($ddat =~ /\w/){
				print "<td>$ddat<br />\n";
			}else{
				print "<td>&#160;</td>";
			}
                }elsif(($sorg eq $ddat) && ($snew eq '')){
#
#----black
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&#160;</td>";
			}
#			if(${$lname} =~ /\w/){
#				print "<td>${$lname}<br />\n";
			if($ddat =~ /\w/){
				print "<td>$ddat<br />\n";
			}else{
				print "<td>&#160;</td>";
			}
                }elsif($snew eq $ddat){
#
#----green
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&#160;</td>";
			}
#			if(${$lname} =~ /\w/){
#				print "<td style='background-color:'00AA00'>${$lname}<br />\n";
			if($ddat =~ /\w/){
				print "<td style='background-color:#00AA00'>$ddat<br />\n";
			}else{
				print "<td style='background-color:#00AA00'>&#160;<br />\n";
			}
                }elsif(($snew ne $ddat) && ($snew =~ /\w/)){
#
#----red
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&#160;</td>";
			}
			if(${$lname} =~ /\w/){
				print "<td style='background-color:red'>${$lname}<br />\n";
			}elsif($snew eq 'NULL' && $ddat eq ''){
				print "<td>NULL</td>";
			}else{
				print "<td style='background-color:red'>&#160;<br />\n";
			}
                }elsif(($snew eq '') && ($ddat eq '')){
#
#----red
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&&#160;</td>";
			}
#			if(${$lname} =~ /\w/){
#				print "<td style='background-color:red>${$lname}<br />\n";
			if($ddat =~ /\w/){
				print "<td style='background-color:red'>$ddat<br />\n";
			}else{
				print "<td style='background-color:red'>&#160;<br />\n";
			}
                }elsif(($sorg ne $ddat) && ($snew eq '')){
#
#----fuchsia
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&#160;</td>";
			}
#			if(${$lname} =~ /\w/){
#				print "<td style='background-color:fuchsia>${$lname}<br />\n";
			if($ddat =~ /\w/){
				print "<td style='background-color:fuchsia'>$ddat<br />\n";
			}else{
				print "<td style='background-color:fuchsia'>&#160;<br />\n";
			}
                }else{
#
#----black
#
			if($org[$i] =~ /\w/){
                        	print "<th style='text-align:left'>$name[$i]</th><td>$org[$i]</td>";
			}else{
				print "<th style='text-align:left'>$name[$i]</th><td>&#160;</td>";
			}
			if($new[$i] =~ /\w/){
                        	print "<td>$new[$i]</td>";
			}else{
				print "<td>&#160;</td>";
			}
#			if(${$lname} =~ /\w/){
#				print "<td>${$lname}<br />\n";
			if($ddat =~ /\w/){
				print "<td>$ddat<br />\n";
			}else{
				print "<td>&#160;</td>";
			}
                }
        }
}

#####################################################################################
### mod_time_format: convert and devide input data format			 ###
#####################################################################################

sub mod_time_format{
	@tentry = split(/\W+/, $input_time);
	$ttcnt = 0;
	foreach (@tentry){
		$ttcnt++;
	}

	$hr_add = 0;
	if($tentry[$ttcnt-1] eq 'PM'     || $tentry[$ttcnt-1] eq 'pm'){
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
			$hr = int($hr);
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




################################################################################
### sub read_databases: read out values from databases                       ###
################################################################################

sub read_databases{

#------------------------------------------------
#-------  database username, password, and server
#------------------------------------------------

    $web = $ENV{'HTTP_REFERER'};
    if($web =~ /icxc/){
        $user   = "mtaops_internal_web";
        $passwd =`cat $pass_dir/.targpass_internal`;
    }else{
        $user = "mtaops_public_web";
        $passwd =`cat $pass_dir/.targpass_public`;
    }
	$server="ocatsqlsrv";
	chomp $passwd;

#	$user="browser";
#	$server="sqlbeta";
#   $passwd = `cat $pass_dir/.targpass`;

	@obtemp = split(/\./,$obsid);
	$obsid_base = $obtemp[0];

#--------------------------------------
#-------- open connection to sql server
#--------------------------------------

	my $db = "server=$server;database=axafocat";
	$dsn1 = "DBI:Sybase:$db";
	$dbh1 = DBI->connect($dsn1, $user, $passwd, { PrintError => 0, RaiseError => 1});

#-------------------------------------------
#-----------  get remarks from target table
#-------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select remarks  from target where obsid=$obsid_base));
	$sqlh1->execute();
	($remarks) = $sqlh1->fetchrow_array;
	$sqlh1->finish;

#-------------------------------------------
#--------  get preferences from target table
#-------------------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select preferences  from target where obsid=$obsid_base));
#	$sqlh1->execute();
#	($preferences) = $sqlh1->fetchrow_array;
#	$sqlh1->finish;

#------------------------------------------
#----------  get comments from target table
#------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select mp_remarks  from target where obsid=$obsid_base));
	$sqlh1->execute();
  	($comments) = $sqlh1->fetchrow_array;
	$sqlh1->finish;

#----------------------------------
#--------  get preference comments
#----------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select mp_remarks from target where obsid=$obsid_base));
#	$sqlh1->execute();
#      	($mp_remarks) = $sqlh1->fetchrow_array;
#	$sqlh1->finish; 

#---------------------------------
#---------  get roll_pref comments
#---------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select roll_pref  from target where obsid=$obsid_base));
#	$sqlh1->execute();
#        ($roll_pref) = $sqlh1->fetchrow_array;
#	$sqlh1->finish;

#--------------------------------
#--------  get date_pref comments
#--------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select date_pref from target where obsid=$obsid_base));
#	$sqlh1->execute();
#       ($date_pref) = $sqlh1->fetchrow_array;
#	$sqlh1->finish; 

#----------------------------------
#---------  get coord_pref comments
#----------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select coord_pref  from target where obsid=$obsid_base));
#	$sqlh1->execute();
#        ($coord_pref) = $sqlh1->fetchrow_array;
#	$sqlh1->finish; 

#---------------------------------
#---------  get cont_pref comments
#---------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select cont_pref from target where obsid=$obsid_base));
#	$sqlh1->execute();
#       ($cont_pref) = $sqlh1->fetchrow_array;
#	$sqlh1->finish;

#------------------------------------------
#-------- combine all remarks to one remark 
#------------------------------------------

#	$remark_cont = '';
#	if($roll_pref =~ /\w/){
#        	unless($roll_pref =~ /N\/A/){
#                	$remark_cont ="$remark_cont".'<I><B>Roll preferences:</B></I><BR>'."$roll_pref".'<BR>';
#        	}
#	}
#	if($date_pref =~ /\w/){
#        	unless($data_pref =~ /N\/A/){
#                	$remark_cont ="$remark_cont".'<I><B>Date preferences:</B></I><BR>'."$date_pref".'<BR>';
#        	}
#	}
#	if($coord_pref =~ /\w/){
#        	unless($coord_pref =~ /N\/A/){
#                	$remark_cont ="$remark_cont".'<I><B>Coord preferences:</B></I><BR>'."$coord_pref".'<BR>';
#        	}
#	}
#	if($cont_pref =~ /\w/){
#        	unless($cont_pref =~ /N\/A/){
#                	$remark_cont ="$remark_cont".'<I><B>Cont preferences:</B></I><BR>'."$cont_pref".'<BR>';
#        	}
#	}
#	if($preferences =~ /\w/){
#        	unless($preferences =~ /N\/A/){
#                	$remark_cont ="$remark_cont".'<I><B>Preferences:</B></I><BR>'."$preferences".'<BR>';
#        	}
#	}

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
		spwindow_flag,multitelescope_interval 
	from target where obsid=$obsid_base));

	$sqlh1->execute();
    	@targetdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

#--------------------------------------------------------------------------
#------- fill values from target table
#------- doing this the long way so I can see what I'm doing and make sure
#------- everything is accounted for
#--------------------------------------------------------------------------

	$targid                   = $targetdata[1];
	$seq_nbr                  = $targetdata[2];
	$targname                 = $targetdata[3];
	$obj_flag                 = $targetdata[4];
	$object                   = $targetdata[5];
	$si_mode                  = $targetdata[6];
	$photometry_flag          = $targetdata[7];
	$vmagnitude               = $targetdata[8];
	$ra                       = $targetdata[9];
	$dec                      = $targetdata[10];
	$est_cnt_rate             = $targetdata[11];
	$forder_cnt_rate          = $targetdata[12];
	$y_det_offset             = $targetdata[13];
	$z_det_offset             = $targetdata[14];
	$raster_scan              = $targetdata[15];
	$dither_flag              = $targetdata[16];
	$approved_exposure_time   = $targetdata[17];
	$pre_min_lead             = $targetdata[18];
	$pre_max_lead             = $targetdata[19];
	$pre_id                   = $targetdata[20];
	$seg_max_num              = $targetdata[21];
	$aca_mode                 = $targetdata[22];
	$phase_constraint_flag    = $targetdata[23];
	$proposal_id              = $targetdata[24];
	$acisid                   = $targetdata[25];
	$hrcid                    = $targetdata[26];
	$grating                  = $targetdata[27];
	$instrument               = $targetdata[28];
	$rem_exp_time             = $targetdata[29];
	$soe_st_sched_date        = $targetdata[30];
	$type                     = $targetdata[31];
	$lts_lt_plan              = $targetdata[32];
	$mpcat_star_fidlight_file = $targetdata[33];
	$status                   = $targetdata[34];
	$data_rights              = $targetdata[35];
	$tooid                    = $targetdata[36];
	$description              = $targetdata[37];
	$total_fld_cnt_rate       = $targetdata[38];
	$extended_src             = $targetdata[39];
	$uninterrupt              = $targetdata[40];
	$multitelescope           = $targetdata[41];
	$observatories            = $targetdata[42];
	$tooid                    = $targetdata[43];
	$constr_in_remarks        = $targetdata[44];
	$group_id                 = $targetdata[45];
	$obs_ao_str               = $targetdata[46];
	$roll_flag                = $targetdata[47];
	$window_flag              = $targetdata[48];
	$spwindow                 = $targetdata[49];
	$multitelescope_interval  = $targetdata[50];
#
#--- creating monitor_flag
#
    $monitor_flag = 'N';
    if ($pre_id) {
        $monitor_flag = "Y";
    }
    $sqlh1 = $dbh1->prepare(qq(select distinct pre_id from target where pre_id=$obsid_base));
    $sqlh1->execute();
    $pre_id_match = $sqlh1->fetchrow_array;
    $sqlh1->finish;

    if($pre_id_match){
        $monitor_flag = "Y";
    }
    if ($group_id){
        $monitor_flag = "N";
    }else{
        if($monitor_flag !~ /Y/i){
            undef $pre_min_lead;
            undef $pre_max_lead;
            undef $pre_id;
        }
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
		$sqlh1 = $dbh1->prepare(qq(select ordr from rollreq where ordr=$incl and obsid=$obsid_base));
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

#-----------------------------------------------------------------
#-------- get the rest of the roll requirement data for each order
#-----------------------------------------------------------------
	for($tordr = 1; $tordr <= $roll_ordr; $tordr++){

		$sqlh1 = $dbh1->prepare(qq(select 
			roll_constraint,roll_180,roll,roll_tolerance 
		from rollreq where ordr = $tordr and obsid=$obsid_base));
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
		$sqlh1 = $dbh1->prepare(qq(select ordr from timereq where ordr=$incl and obsid=$obsid_base));
		$sqlh1->execute();
		@timereq_data = $sqlh1->fetchrow_array;
		$sqlh1->finish;
		if($timereq_data[0] eq ''){
			last OUTER;
		}
		$time_ordr = $timereq_data[0];				# here is time order
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
		from timereq where ordr = $tordr and obsid=$obsid_base));
		$sqlh1->execute();
		@timereq_data = $sqlh1->fetchrow_array;
		$sqlh1->finish;

		$window_constraint[$tordr] = $timereq_data[0];
		$tstart[$tordr]            = $timereq_data[1];
		$tstop[$tordr]             = $timereq_data[2];
	}

#-----------------------------------------------------------------
#---------- if it's a too, get remarks and trigger from too table
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
			exp_mode,ccdi0_on,ccdi1_on,ccdi2_on,ccdi3_on,
			ccds0_on, ccds1_on,ccds2_on,ccds3_on,ccds4_on,ccds5_on,bep_pack,
			onchip_sum, onchip_row_count,onchip_column_count,frame_time,
			subarray,subarray_start_row, subarray_row_count,
			duty_cycle, secondary_exp_count,  primary_exp_time,
			eventfilter,eventfilter_lower, eventfilter_higher,
			most_efficient,dropped_chip_count,
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
		$spectra_max_count       = $acisdata[28];

#               $subarray_frame_time    = $acisdata[19];
#               $secondary_exp_time     = $acisdata[23];
#               $bias_request           = $acisdata[27];
#               $frequency              = $acisdata[28];
#               $bias_after             = $acisdata[39];
#               $fep                    = $acisdata[31];
	} else {
    		$exp_mode = "NULL";
    		$ccdi0_on = "NULL";
    		$ccdi1_on = "NULL";
    		$ccdi2_on = "NULL";
    		$ccdi3_on = "NULL";
    		$ccds0_on = "NULL";
    		$ccds1_on = "NULL";
    		$ccds2_on = "NULL";
    		$ccds3_on = "NULL";
    		$ccds4_on = "NULL";
    		$ccds5_on = "NULL";
    		$bep_pack = "NULL";
    		$onchip_sum          = "NULL";
    		$onchip_row_count    = "NULL";
    		$onchip_column_count = "NULL";
    		$frame_time          = "NULL";
    		$subarray            = "NONE";
    		$subarray_start_row  = "NULL";
    		$subarray_row_count  = "NULL";
#   		$subarray_frame_time = "NULL";
    		$duty_cycle          = "NULL";
    		$secondary_exp_count = "NULL";
    		$primary_exp_time    = "NULL";
#   		$secondary_exp_time  = "NULL";
    		$eventfilter         = "NULL";
    		$eventfilter_lower   = "NULL";
    		$eventfilter_higher  = "NULL";
    		$spwindow            = "NULL";
#   		$bias_request        = "NULL";
#   		$frequency           = "NULL";
#   		$bias_after          = "NULL";
    		$most_efficient      = "NULL";
#   		$fep                 = "NULL";
		$dropped_chip_count  = "NULL";
		$multiple_spectral_lines = "NULL";
		$spectra_max_count       = "NULL";
	} 

#	if($standard_chips =~ /YES/i){
#		if($instrument =~ /ACIS-I/i){
#    			$ccdi0_on = "YES";
#    			$ccdi1_on = "YES";
#    			$ccdi2_on = "YES";
#    			$ccdi3_on = "YES";
#    			$ccds0_on = "NULL";
#    			$ccds1_on = "NULL";
#    			$ccds2_on = "YES";
#    			$ccds3_on = "YES";
#    			$ccds4_on = "NULL";
#    			$ccds5_on = "NULL";
#		}elsif($instrument =~ /ACIS-S/i){
#    			$ccdi0_on = "NULL";
#    			$ccdi1_on = "NULL";
#    			$ccdi2_on = "NULL";
#    			$ccdi3_on = "NULL";
#    			$ccds0_on = "YES";
#    			$ccds1_on = "YES";
#    			$ccds2_on = "YES";
#    			$ccds3_on = "YES";
#    			$ccds4_on = "YES";
#    			$ccds5_on = "YES";
#		}
#	}	

#-------------------------------------------------------------------
#-------  get values from aciswin table
#-------  first, get aciswin_id to see whether there are any aciswin param set
#-------------------------------------------------------------------

	 $sqlh1 = $dbh1->prepare(qq(select  aciswin_id  from aciswin where  obsid=$obsid_base));
	 $sqlh1->execute();
	 @aciswindata = $sqlh1->fetchrow_array;
	 $sqlh1->finish;
	 $aciswin_id[0] = $aciswindata[0];
	 $aciswin_id[0] =~ s/\s+//g;


	 if($aciswin_id[0] =~ /\d/){

	       $sqlh1 = $dbh1->prepare(qq(select
		      ordr, start_row, start_column, width, height, lower_threshold,
		      pha_range, sample, chip, include_flag , aciswin_id
	       from aciswin where obsid=$obsid_base));
	       $sqlh1->execute();
	       $j = 0;
	       while(my(@aciswindata) = $sqlh1->fetchrow_array){
		      
		      $ordr[$j]	   = $aciswindata[0];
		      $start_row[$j]       = $aciswindata[1];
		      $start_column[$j]    = $aciswindata[2];
		      $width[$j]	   = $aciswindata[3];
		      $height[$j]	   = $aciswindata[4];
		      $lower_threshold[$j] = $aciswindata[5];

		      if($lower_threshold[$j] > 0.5){
			     $awc_l_th = 1;
		      }

		      $pha_range[$j]       = $aciswindata[6];
		      $sample[$j]          = $aciswindata[7];
		      $chip[$j]	   	   = $aciswindata[8];
		      $include_flag[$j]    = $aciswindata[9];
		      $aciswin_id[$j]      = $aciswindata[10];

		      $j++;
	       }
	       $aciswin_no = $j;

	       $sqlh1->finish;


#		  OUTER:
#		  for($aciswin_no = 1; $aciswin_no < 30; $aciswin_no++){
#			   $test  = $aciswin_id[0] + $aciswin_no;
#			   $sqlh1 = $dbh1->prepare(qq(select aciswin_id from aciswin where aciswin_id = $test  and  obsid=$obsid_base));
#			   $sqlh1->execute();
#			   @aciswindata = $sqlh1->fetchrow_array;
#			   $sqlh1->finish;
#			   if($aciswindata[0] !~ /\d/){
#				    $aciswin_no--;
#				    last OUTER;
#			   }
#			   $aciswin_id[$aciswin_no] = $aciswindata[0];
#		  }
#----------------------------------------------------------------------
#------- get the rest of acis window requirement data from the database
#----------------------------------------------------------------------

#		  $awc_l_th = 0;
#		  for($j = 0; $j < $aciswin_no; $j++){
#			   $sqlh1 = $dbh1->prepare(qq(select
#				    ordr,start_row,start_column,width,height,lower_threshold,
#				    pha_range,sample,chip,include_flag
#			   from aciswin where aciswin_id = $aciswin_id[$j]  and  obsid=$obsid_base));
#
#			   $sqlh1->execute();
#			   @aciswindata = $sqlh1->fetchrow_array;
#			   $sqlh1->finish;
#
#			   $ordr[$j]	        = $aciswindata[0];
#			   $start_row[$j]       = $aciswindata[1];
#			   $start_column[$j]    = $aciswindata[2];
#			   $width[$j]	        = $aciswindata[3];
#			   $height[$j]	        = $aciswindata[4];
#			   $lower_threshold[$j] = $aciswindata[5];
#
#			   if($lower_threshold[$j] > 0.5){
#				    $awc_l_th = 1;
#			   }
#
#			   $pha_range[$j]      = $aciswindata[6];
#			   $sample[$j]	       = $aciswindata[7];
#			   $chip[$j]	       = $aciswindata[8];
#			   $include_flag[$j]   = $aciswindata[9];
#		  }
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
	from phasereq where obsid=$obsid_base));
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
	from dither where obsid=$obsid_base));
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
	from sim where obsid=$obsid_base));
	$sqlh1->execute();
	@simdata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$trans_offset = $simdata[0];
	$focus_offset = $simdata[1];

#---------------------------
#------  get values from soe
#---------------------------

	$sqlh1 = $dbh1->prepare(qq(select soe_roll from soe where obsid=$obsid_base));
	$sqlh1->execute();
	@soedata = $sqlh1->fetchrow_array;
	$sqlh1->finish;

	$rroll_obsr = $soedata[0];

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

#-------------------------------------------------------------
#<<<<<<------>>>>>>  switch to axafusers <<<<<<------>>>>>>>>
#-------------------------------------------------------------

#	$db = "server=$server;database=axafusers";
#	$dsn1 = "DBI:Sybase:$db";
#	$dbh1 = DBI->connect($dsn1, $user, $passwd, { PrintError => 0, RaiseError => 1});

#--------------------------------
#-----  get proposer's last name
#--------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select 
#		last from person_short s,axafocat..prop_info p 
#	where p.ocat_propid=$proposal_id and s.pers_id=p.piid));
#	$sqlh1->execute();
#	@namedata = $sqlh1->fetchrow_array;
#	$sqlh1->finish;
#
#	$PI_name = $namedata[0];

#---------------------------------------------------------------------------
#------- if there is a co-i who is observer, get them, otherwise it's the pi
#---------------------------------------------------------------------------

#	$sqlh1 = $dbh1->prepare(qq(select 
#		coi_contact from person_short s,axafocat..prop_info p 
#	where p.ocat_propid = $proposal_id));
#	$sqlh1->execute();
#	($observerdata) = $sqlh1->fetchrow_array;
#	$sqlh1->finish;
#
#	if ($observerdata =~/N/){
#    		$Observer = $PI_name;
#	} else {
#		$sqlh1 = $dbh1->prepare(qq(select 
#			last from person_short s,axafocat..prop_info p 
#		where p.ocat_propid = $proposal_id and p.coin_id = s.pers_id));
#		$sqlh1->execute();
#		($observerdata) = $sqlh1->fetchrow_array;
#		$sqlh1->finish;
#
#    		$Observer=$observerdata;
#	}

#-------------------------------------------------
#---- Disconnect from the server
#-------------------------------------------------

	$dbh1->disconnect();


#-----------------------------------------------------------------
#------ these ~100 lines are to remove the whitespace from most of
#------ the obscat dump entries.  
#-----------------------------------------------------------------
	$targid                   =~ s/\s+//g; 
	$seq_nbr                  =~ s/\s+//g; 
	$targname                 =~ s/\s+//g; 
	$obj_flag                 =~ s/\s+//g; 
	if($obj_flag =~ /NONE/){
		$obj_flag = "NO";
	}
	$object                   =~ s/\s+//g; 
	$si_mode                  =~ s/\s+//g; 
	$photometry_flag          =~ s/\s+//g; 
	$vmagnitude               =~ s/\s+//g; 
	$ra                       =~ s/\s+//g; 
	$dec                      =~ s/\s+//g; 
	$est_cnt_rate             =~ s/\s+//g; 
	$forder_cnt_rate          =~ s/\s+//g; 
	$y_det_offset             =~ s/\s+//g; 
	$z_det_offset             =~ s/\s+//g; 
	$raster_scan              =~ s/\s+//g; 
	$defocus                  =~ s/\s+//g; 
	$dither_flag              =~ s/\s+//g; 
	$roll                     =~ s/\s+//g; 
	$roll_tolerance           =~ s/\s+//g; 
	$approved_exposure_time   =~ s/\s+//g; 
	$pre_min_lead             =~ s/\s+//g; 
	$pre_max_lead             =~ s/\s+//g; 
	$pre_id                   =~ s/\s+//g; 
	$seg_max_num              =~ s/\s+//g; 
	$aca_mode                 =~ s/\s+//g; 
	$phase_constraint_flag    =~ s/\s+//g; 
	$proposal_id              =~ s/\s+//g; 
	$acisid                   =~ s/\s+//g; 
	$hrcid                    =~ s/\s+//g; 
	$grating                  =~ s/\s+//g; 
	$instrument               =~ s/\s+//g; 
	$rem_exp_time             =~ s/\s+//g; 
	#$soe_st_sched_date       =~ s/\s+//g; 
	$type                     =~ s/\s+//g; 
	#$lts_lt_plan             =~ s/\s+//g; 
	$mpcat_star_fidlight_file =~ s/\s+//g; 
	$status                   =~ s/\s+//g; 
	$data_rights              =~ s/\s+//g; 
	$server_name              =~ s/\s+//g; 
	$hrc_config               =~ s/\s+//g; 
	$hrc_chop_duty_cycle      =~ s/\s+//g; 
	$hrc_chop_fraction        =~ s/\s+//g; 
	$hrc_chop_duty_no         =~ s/\s+//g; 
	$hrc_zero_block           =~ s/\s+//g; 
	$hrc_timing_mode          =~ s/\s+//g;
	$exp_mode                 =~ s/\s+//g; 
	$ccdi0_on                 =~ s/\s+//g; 
	$ccdi1_on                 =~ s/\s+//g; 
	$ccdi2_on                 =~ s/\s+//g; 
	$ccdi3_on                 =~ s/\s+//g; 
	$ccds0_on                 =~ s/\s+//g; 
	$ccds1_on                 =~ s/\s+//g; 
	$ccds2_on                 =~ s/\s+//g; 
	$ccds3_on                 =~ s/\s+//g; 
	$ccds4_on                 =~ s/\s+//g; 
	$ccds5_on                 =~ s/\s+//g; 
	$bep_pack                 =~ s/\s+//g; 
	$onchip_sum               =~ s/\s+//g; 
	$onchip_row_count         =~ s/\s+//g; 
	$onchip_column_count      =~ s/\s+//g; 
	$frame_time               =~ s/\s+//g; 
	$subarray                 =~ s/\s+//g; 
	$subarray_start_row       =~ s/\s+//g; 
	$subarray_row_count       =~ s/\s+//g; 
	$subarray_frame_time      =~ s/\s+//g; 
	$duty_cycle               =~ s/\s+//g; 
	$secondary_exp_count      =~ s/\s+//g; 
	$primary_exp_time         =~ s/\s+//g; 
	$secondary_exp_time       =~ s/\s+//g; 
	$eventfilter              =~ s/\s+//g; 
	$eventfilter_lower        =~ s/\s+//g; 
	$eventfilter_higher       =~ s/\s+//g; 
	$multiple_spectral_lines =~ s/\s+//g;
	$spectra_max_count       =~ s/\s+//g;

	$spwindow                 =~ s/\s+//g; 
	$multitelescope_interval  =~ s/\s+//g;
	$phase_period             =~ s/\s+//g; 
	$phase_epoch              =~ s/\s+//g; 
	$phase_start              =~ s/\s+//g; 
	$phase_end                =~ s/\s+//g; 
	$phase_start_margin       =~ s/\s+//g; 
	$phase_end_margin         =~ s/\s+//g; 
	$PI_name                  =~ s/\s+//g; 
	$proposal_number          =~ s/\s+//g; 
	$trans_offset             =~ s/\s+//g; 
	$focus_offset             =~ s/\s+//g;
	$tooid                    =~ s/\s+//g;
	$description              =~ s/\s+//g;
	$total_fld_cnt_rate       =~ s/\s+//g;
	$extended_src             =~ s/\s+//g;
	$y_amp                    =~ s/\s+//g;
	$y_freq                   =~ s/\s+//g;
	$y_phase                  =~ s/\s+//g;
	$z_amp                    =~ s/\s+//g;
	$z_freq                   =~ s/\s+//g;
	$z_phase                  =~ s/\s+//g;
	$most_efficient           =~ s/\s+//g;
	$fep                      =~ s/\s+//g;
	$timing_mode              =~ s/\s+//g;
	$uninterrupt              =~ s/\s+//g;
	$proposal_joint           =~ s/\s+//g;
	$proposal_hst             =~ s/\s+//g;
	$proposal_noao            =~ s/\s+//g;
	$proposal_xmm             =~ s/\s+//g;
	$roll_obsr                =~ s/\s+//g;
	$multitelescope           =~ s/\s+//g;
	$observatories            =~ s/\s+//g;
	$too_type                 =~ s/\s+//g;
	$too_start                =~ s/\s+//g;
	$too_stop                 =~ s/\s+//g;
	$too_followup             =~ s/\s+//g;
	$roll_flag                =~ s/\s+//g;
	$window_flag              =~ s/\s+//g;
	$constr_in_remarks        =~ s/\s+//g;
	$group_id                 =~ s/\s+//g;
	$obs_ao_str               =~ s/\s+//g;
	$dropped_chip_count       =~ s/\s+//g;

#--------------------------------------------------------------------
#----- roll_ordr, time_ordr, and ordr need extra check for each order
#--------------------------------------------------------------------

	for($k = 1; $k <= $roll_ordr; $k++){
		$roll_constraint[$k]  =~ s/\s+//g; 
		$roll_180[$k]         =~ s/\s+//g; 
		$roll[$k]             =~ s/\s+//g;
		$roll_tolerance[$k]   =~ s/\s+//g; 
		${roll_constraint.$k} = $roll_constraint[$k];
		${roll_180.$k}        = $roll_180[$k];
		${roll.$k}            = $roll[$k];
		${roll_tolerance.$k}  = $roll_tolerance[$k];
	}

	for($k = 1; $k <= $time_ordr; $k++){
		$window_constraint[$k]  =~ s/\s+//g; 
		${window_constraint.$k} = $window_constraint[$k];
	}

	for($k = 0; $k < $aciswin_no; $k++){
		$ordr[$k]             =~ s/\s+//g;
		$chip[$k]             =~ s/\s+//g;
		$include_flag[$k]     =~ s/\s+//g;
		$start_row[$k]        =~ s/\s+//g; 
		$start_column[$k]     =~ s/\s+//g; 
		$width[$k]            =~ s/\s+//g; 
		$height[$k]           =~ s/\s+//g; 
		$lower_threshold[$k]  =~ s/\s+//g; 
		$pha_range[$k]        =~ s/\s+//g; 
		$sample[$k]           =~ s/\s+//g; 

		${ordr.$k}            = $ordr[$k];
		${chip.$k}            = $chip[$k];
		${include_flag.$k}    = $include_flag[$k];
		${start_row.$k}       = $start_row[$k];
		${start_column.$k}    = $start_column[$k];
		${width.$k}           = $width[$k];
		${height.$k}          = $height[$k];
		${lower_threshold.$k} = $lower_threshold[$k];
		${pha_range.$k}       = $pha_range[$k];
		${sample.$k}          = $sample[$k];
	}

#-----------------------------------
#-----------  A FEW EXTRA SETTINGS
#-----------------------------------

	$ra  = sprintf("%3.6f", $ra);		# setting to 6 digit after a dicimal point
	$dec = sprintf("%3.6f", $dec);
	$dra = $ra;
	$ddec= $dec;

#---------------------------------------------------------------------------
#------- time need to be devided into year, month, day, and time for display
#---------------------------------------------------------------------------

	for($k = 1; $k <= $time_ordr; $k++){
		if($tstart[$k] ne ''){
			$input_time       = $tstart[$k];

			mod_time_format();		# sub mod_time_format changes time format

			$start_year[$k]  = $year;
			$start_month[$k] = $month;
			$start_date[$k]  = $day;
			$start_time[$k]  = $time;
			${tstart.$k}     = "$month:$day:$year:$time";
		}
		
		if($tstop[$k] ne ''){
			$input_time = $tstop[$k];

			mod_time_format();

			$end_year[$k]  = $year;
			$end_month[$k] = $month;
			$end_date[$k]  = $day;
			$end_time[$k]  = $time;
			${tstop.$k}    = "$month:$day:$year:$time";
		}
	}

#---------------------------------------------------------------------------------
#------ here are the cases which database values and display values are different.
#---------------------------------------------------------------------------------

	if($multitelescope eq ''){$multitelescope = 'N'}

	if($proposal_joint eq ''){$proposal_joint = 'N/A'}

	if($proposal_hst eq ''){$proposal_hst = 'N/A'}

	if($proposal_noao eq ''){$proposal_noao = 'N/A'}

	if($proposal_xmm eq ''){$proposal_xmm = 'N/A'}

	if($rxte_approved_time eq ''){$rxte_approved_time = 'N/A'}

	if($vla_approved_time eq ''){$vla_approved_time = 'N/A'}

	if($vlba_approved_time eq ''){$vlba_approved_time = 'N/A'}

	
	if($roll_flag eq 'NULL'){$droll_flag = 'NULL'}
	elsif($roll_flag eq '') {$droll_flag = 'NULL'; $roll_flag = 'NULL';}
	elsif($roll_flag eq 'Y'){$droll_flag = 'YES'}
	elsif($roll_flag eq 'N'){$droll_flag = 'NO'}
	elsif($roll_flag eq 'P'){$droll_flag = 'PREFERENCE'}
	
	if($window_flag eq 'NULL'){$dwindow_flag = 'NULL'}
	elsif($window_flag eq '') {$dwindow_flag = 'NULL'; $window_flag = 'NULL';}
	elsif($window_flag eq 'Y'){$dwindow_flag = 'YES'}
	elsif($window_flag eq 'N'){$dwindow_flag = 'NO'}
	elsif($window_flag eq 'P'){$dwindow_flag = 'PREFERENCE'}
	
	if($dither_flag eq 'NULL'){$ddither_flag = 'NULL'}
	elsif($dither_flag eq '') {$ddither_flag = 'NULL'; $dither_flag = 'NULL';}
	elsif($dither_flag eq 'Y'){$ddither_flag = 'YES'}
	elsif($dither_flag eq 'N'){$ddither_flag = 'NO'}
	
	if($uninterrupt eq 'NULL'){$duninterrupt = 'NULL'}
	elsif($uninterrupt eq '') {$duninterrupt = 'NULL'; $uninterrupt = 'NULL';}
	elsif($uninterrupt eq 'N'){$duninterrupt = 'NO'}
	elsif($uninterrupt eq 'Y'){$duninterrupt = 'YES'}
	elsif($uninterrupt eq 'P'){$duninterrupt = 'PREFERENCE'}

	if($photometry_flag eq 'NULL'){$dphotometry_flag = 'NULL'}
	elsif($photometry_flag eq '') {$dphotometry_flag = 'NULL'; $photometry_flag = 'NULL'}
	elsif($photometry_flag eq 'Y'){$dphotometry_flag = 'YES'}
	elsif($photometry_flag eq 'N'){$dphotometry_flag = 'NO'}
	
	for($k = 1; $k <= $time_ordr; $k++){
		if($window_constraint[$k] eq 'Y')      {$dwindow_constraint[$k] = 'CONSTRAINT'}
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

		if($roll_180[$k] eq 'Y')   {$droll_180[$k] = 'YES'}
		elsif($roll_180[$k] eq 'N'){$droll_180[$k] = 'NO'}
		else{$droll_180[$k] = 'NULL'}
	}	

	if($constr_in_remarks eq 'NULL'){$dconstr_in_remarks = 'NULL'}
	elsif($constr_in_remarks eq '') {$dconstr_in_remarks = 'NULL'; $constr_in_remarks = 'NULL'}
	elsif($constr_in_remarks eq 'N'){$dconstr_in_remarks = 'NO'}
	elsif($constr_in_remarks eq 'Y'){$dconstr_in_remarks = 'YES'}

	if($phase_constraint_flag eq 'NULL'){$dphase_constraint_flag = 'NULL'}
	elsif($phase_constraint_flag eq '') {$dphase_constraint_flag = 'NONE'; $phase_constraint_flag = 'NULL'}
	elsif($phase_constraint_flag eq 'N'){$dphase_constraint_flag = 'NONE'}
	elsif($phase_constraint_flag eq 'Y'){$dphase_constraint_flag = 'CONSTRAINT'}
	elsif($phase_constraint_flag eq 'P'){$dphase_constraint_flag = 'PREFERENCE'}

	if($multitelescope eq 'Y')   {$dmultitelescope = 'YES'}
	elsif($multitelescope eq 'N'){$dmultitelescope = 'NO'}
	elsif($multitelescope eq 'P'){$dmultitelescope = 'PREFERENCE'}

	if($hrc_config eq ''){$hrc_config = 'NULL'}

	if($hrc_zero_block eq 'NULL'){$dhrc_zero_block = 'NULL'}
	elsif($hrc_zero_block eq '') {$dhrc_zero_block = 'NULL'; $hrc_zero_block = 'NULL';}
	elsif($hrc_zero_block eq 'Y'){$dhrc_zero_block = 'YES'}
	elsif($hrc_zero_block eq 'N'){$dhrc_zero_block = 'NO'}

	if($hrc_timing_mode eq 'NULL'){$dhrc_timing_mode = 'NULL'}
	elsif($hrc_timing_mode eq '') {$dhrc_timing_mode = 'NO'; $hrc_timing_mode = 'NO';}
	elsif($hrc_timing_mode eq 'Y'){$dhrc_timing_mode = 'YES'}
	elsif($hrc_timing_mode eq 'N'){$dhrc_timing_mode = 'NO'}

#	if($ordr =~ /\W/ || $ordr == '') {
#		$ordr = 1;
#	}

	if($most_efficient eq 'NULL'){$dmost_efficient = 'NULL'}
	elsif($most_efficient eq '') {$most_efficient = 'NULL'; $dmost_efficient  = 'NULL'}
	elsif($most_efficient eq 'Y'){$dmost_efficient = 'YES'}
	elsif($most_efficient eq 'N'){$dmost_efficient = 'NO'}

	if($standard_chips eq 'NULL'){$dstandard_chips = 'NULL'}
	elsif($standard_chips eq '') {$dstandard_chips = 'NULL'; $standard_chips = 'NULL'}
	elsif($standard_chips eq 'Y'){$dstandard_chips = 'YES'}
	elsif($standard_chips eq 'N'){$dstandard_chips = 'NO'}

	if($ccdi0_on eq 'NULL'){$dccdi0_on = 'NULL'}
	elsif($ccdi0_on eq '') {$dccdi0_on = 'NULL'; $ccdi0_on = 'NULL'}
	elsif($ccdi0_on eq 'Y'){$dccdi0_on = 'YES'}
	elsif($ccdi0_on eq 'N'){$dccdi0_on = 'NO'}
	
	if($ccdi1_on eq 'NULL'){$dccdi1_on = 'NULL'}
	elsif($ccdi1_on eq '') {$dccdi1_on = 'NULL'; $ccdi1_on = 'NULL'}
	elsif($ccdi1_on eq 'Y'){$dccdi1_on = 'YES'}
	elsif($ccdi1_on eq 'N'){$dccdi1_on = 'NO'}
	
	if($ccdi2_on eq 'NULL'){$dccdi2_on = 'NULL'}
	elsif($ccdi2_on eq '') {$dccdi2_on = 'NULL'; $ccdi2_on = 'NULL'}
	elsif($ccdi2_on eq 'Y'){$dccdi2_on = 'YES'}
	elsif($ccdi2_on eq 'N'){$dccdi2_on = 'NO'}
	
	if($ccdi3_on eq 'NULL'){$dccdi3_on = 'NULL'}
	elsif($ccdi3_on eq '') {$dccdi3_on = 'NULL'; $ccdi3_on = 'NULL'}
	elsif($ccdi3_on eq 'Y'){$dccdi3_on = 'YES'}
	elsif($ccdi3_on eq 'N'){$dccdi3_on = 'NO'}
	
	if($ccds0_on eq 'NULL'){$dccds0_on = 'NULL'}
	elsif($ccds0_on eq '') {$dccds0_on = 'NULL'; $ccds0_on = 'NULL'}
	elsif($ccds0_on eq 'Y'){$dccds0_on = 'YES'}
	elsif($ccds0_on eq 'N'){$dccds0_on = 'NO'}
	
	if($ccds1_on eq 'NULL'){$dccds1_on = 'NULL'}
	elsif($ccds1_on eq '') {$dccds1_on = 'NULL'; $ccds1_on = 'NULL'}
	elsif($ccds1_on eq 'Y'){$dccds1_on = 'YES'}
	elsif($ccds1_on eq 'N'){$dccds1_on = 'NO'}
	
	if($ccds2_on eq 'NULL'){$dccds2_on = 'NULL'}
	elsif($ccds2_on eq '') {$dccds2_on = 'NULL'; $ccds2_on = 'NULL'}
	elsif($ccds2_on eq 'Y'){$dccds2_on = 'YES'}
	elsif($ccds2_on eq 'N'){$dccds2_on = 'NO'}
	
	if($ccds3_on eq 'NULL'){$dccds3_on = 'NULL'}
	elsif($ccds3_on eq '') {$dccds3_on = 'NULL'; $ccds3_on = 'NULL'}
	elsif($ccds3_on eq 'Y'){$dccds3_on = 'YES'}
	elsif($ccds3_on eq 'N'){$dccds3_on = 'NO'}

	if($ccds4_on eq 'NULL'){$dccds4_on = 'NULL'}
	elsif($ccds4_on eq '') {$dccds4_on = 'NULL'; $ccds4_on = 'NULL'}
	elsif($ccds4_on eq 'Y'){$dccds4_on = 'YES'}
	elsif($ccds4_on eq 'N'){$dccds4_on = 'NO'}
	
	if($ccds5_on eq 'NULL'){$dccds5_on = 'NULL'}
	elsif($ccds5_on eq '') {$dccds5_on = 'NULL'; $ccds5_on = 'NULL'}
	elsif($ccds5_on eq 'Y'){$dccds5_on = 'YES'}
	elsif($ccds5_on eq 'N'){$dccds5_on = 'NO'}
	
	if($duty_cycle eq 'NULL')  {$dduty_cycle = 'NULL'}
	elsif($duty_cycle eq '')   {$dduty_cycle = 'NULL'; $duty_cycle = 'NULL'}
	elsif($duty_cycle eq 'Y')  {$dduty_cycle = 'YES'}
	elsif($duty_cycle eq 'YES'){$dduty_cycle = 'YES'}
	elsif($duty_cycle eq 'N')  {$dduty_cycle = 'NO'}
	elsif($duty_cycle eq 'NO')  {$dduty_cycle = 'NO'}

	if($onchip_sum eq 'NULL'){$donchip_sum = 'NULL'}
	elsif($onchip_sum eq '') {$donchip_sum = 'NULL'; $onchip_sum = 'NULL'}
	elsif($onchip_sum eq 'Y'){$donchip_sum = 'YES'}
	elsif($onchip_sum eq 'N'){$donchip_sum = 'NO'}

	if($eventfilter eq 'NULL'){$deventfilter = 'NULL'}
	elsif($eventfilter eq '') {$deventfilter = 'NULL'; $eventfilter = 'NULL'}
	elsif($eventfilter eq 'Y'){$deventfilter = 'YES'}
	elsif($eventfilter eq 'N'){$deventfilter = 'NO'}

        if($multiple_spectral_lines eq 'NULL') {$dmultiple_spectral_lines = 'NULL'}
        elsif($multiple_spectral_lines eq '')  {$dmultiple_spectral_lines = 'NULL'; $multiple_spectral_lines = 'NULL'}
        elsif($multiple_spectral_lines eq 'Y') {$dmultiple_spectral_lines = 'YES'}
        elsif($multiple_spectral_lines eq 'N') {$dmultiple_spectral_lines = 'NO'}

	if($spwindow eq 'NULL'){$dspwindow = 'NULL'}
	elsif($spwindow eq '' ){$dspwindow = 'NULL'; $spwindow = 'NULL'}
	elsif($spwindow eq 'Y'){$dspwindow = 'YES'}
	elsif($spwindow eq 'N'){$dspwindow = 'NO'}

        if($multiple_spectral_lines eq 'NULL') {$dmultiple_spectral_lines = 'NULL'}
        elsif($multiple_spectral_lines eq '')  {$dmultiple_spectral_lines = 'NULL'; $multiple_spectral_lines = 'NULL'}
        elsif($multiple_spectral_lines eq 'Y') {$dmultiple_spectral_lines = 'YES'}
        elsif($multiple_spectral_lines eq 'N') {$dmultiple_spectral_lines = 'NO'}

        if($spwindow eq 'NULL')    {$dspwindow = 'NULL'}
        elsif($spwindow eq '' )    {$dspwindow = 'NULL'; $spwindow = 'NULL'}
        elsif($spwindow eq 'Y')    {$dspwindow = 'YES'}
        elsif($spwindow eq 'N')    {$dspwindow = 'NO'}

#-----------------------------------------------------------
#----- define several array of parameter names for later use
#-----------------------------------------------------------

#-------------------------
#----- all the param names
#-------------------------

                @paramarray = (
                SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,OBS_AO_STR,TARGNAME,
                SI_MODE,INSTRUMENT,GRATING,TYPE,PI_NAME,OBSERVER,APPROVED_EXPOSURE_TIME, REM_EXP_TIME,
                PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
                PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
                RA,DEC,DRA,DDEC,ROLL_OBSR,Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
                RASTER_SCAN,DITHER_FLAG,UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,VMAGNITUDE,EST_CNT_RATE,
                FORDER_CNT_RATE,
                CONSTR_IN_REMARKS,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,PHASE_START,PHASE_START_MARGIN,
                PHASE_END,PHASE_END_MARGIN,PRE_ID,PRE_MIN_LEAD,PRE_MAX_LEAD,MULTITELESCOPE, OBSERVATORIES,
		MULTITELESCOPE_INTERVAL,
                HRC_CONFIG,HRC_ZERO_BLOCK,HRC_SI_MODE,
                EXP_MODE,BEP_PACK,FRAME_TIME,MOST_EFFICIENT,
                CCDI0_ON, CCDI1_ON, CCDI2_ON, CCDI3_ON, CCDS0_ON, CCDS1_ON, CCDS2_ON, CCDS3_ON,CCDS4_ON, CCDS5_ON,
                SUBARRAY,SUBARRAY_ROW_COUNT,DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
                ONCHIP_SUM,ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
                EVENTFILTER_HIGHER,SPWINDOW_FLAG,
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,                                             #--- added 03/29/11
                TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS, REMARKS,COMMENTS,
                ROLL_ORDR,
                TIME_ORDR,
		ACISWIN_ID,
                ORDR,DROPPED_CHIP_COUNT
#              WINDOW_CONSTRAINT,TSTART,TSTOP,
#              ROLL_CONSTRAINT,ROLL_180,ROLL,ROLL_TOLERANCE,
#              CHIP,INCLUDE_FLAG,START_ROW,START_COLUMN,HEIGHT,WIDTH,
#              LOWER_THRESHOLD,PHA_RANGE,SAMPLE,BIAS_RREQUEST,FREQUENCY,BIAS_AFTER,
#	        SUBARRAY_FRAME_TIME,SECONDARY_EXP_TIME,FEP
                );

                @paramarray2 = (
                SI_MODE,INSTRUMENT,GRATING,TYPE,PI_NAME,OBSERVER,APPROVED_EXPOSURE_TIME, REM_EXP_TIME,
                PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
                PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
                RA,DEC,ROLL_OBSR,Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
                RASTER_SCAN,DITHER_FLAG,UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,VMAGNITUDE,EST_CNT_RATE,
                FORDER_CNT_RATE,
                CONSTR_IN_REMARKS,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,PHASE_START,PHASE_START_MARGIN,
                PHASE_END,PHASE_END_MARGIN,PRE_ID,PRE_MIN_LEAD,PRE_MAX_LEAD,MULTITELESCOPE, OBSERVATORIES,
		MULTITELESCOPE_INTERVAL,
                HRC_CONFIG,HRC_ZERO_BLOCK,HRC_SI_MODE,
                EXP_MODE,BEP_PACK,FRAME_TIME,MOST_EFFICIENT,
                CCDI0_ON, CCDI1_ON, CCDI2_ON, CCDI3_ON, CCDS0_ON, CCDS1_ON, CCDS2_ON, CCDS3_ON,CCDS4_ON, CCDS5_ON,
                SUBARRAY,SUBARRAY_ROW_COUNT,DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,
                ONCHIP_SUM,ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,
                EVENTFILTER_HIGHER,SPWINDOW_FLAG,
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,                                             #--- added 03/29/11
                TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS, REMARKS,COMMENTS,
                ROLL_ORDR,
                TIME_ORDR,
		ACISWIN_ID,
                ORDR,DROPPED_CHIP_COUNT 
#		SUBARRAY_FRAME_TIME,SECONDARY_EXP_TIME
                );

                @gen_paramarray = (
                SI_MODE,INSTRUMENT,GRATING,TYPE,,APPROVED_EXPOSURE_TIME, REM_EXP_TIME,
                PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
                PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,RA,DEC,DRA,DDEC,ROLL_OBSR,Y_DET_OFFSET,
                Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,RASTER_SCAN,DITHER_FLAG,UNINTERRUPT,
                OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,VMAGNITUDE,EST_CNT_RATE,FORDER_CNT_RATE,SPWINDOW_FLAG
                );

		@dither_paramarray = (Y_AMP,Y_FREQ,Y_PHASE,Z_AMP,Z_FREQ, Z_PHASE);

                @const_paramarray = (
                CONSTR_IN_REMARKS,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,PHASE_START,
                PHASE_START_MARGIN,PHASE_END,PHASE_END_MARGIN,
		GROUP_ID,PRE_ID_GROUP,PRE_MIN_LEAD_GROUP,PRE_MAX_LEAD_GROUP,
		MONITOR_FLAG,PRE_ID,PRE_MIN_LEAD,PRE_MAX_LEAD,
                MULTITELESCOPE, OBSERVATORIES,MULTITELESCOPE_INTERVAL
                );

                @hrc_paramarray = (
                HRC_CONFIG,HRC_ZERO_BLOCK,HRC_SI_MODE
                );

                @acis_gen_paramarray = (
                EXP_MODE,BEP_PACK,FRAME_TIME,MOST_EFFICIENT,CCDI0_ON, CCDI1_ON, CCDI2_ON, CCDI3_ON,
                CCDS0_ON, CCDS1_ON, CCDS2_ON, CCDS3_ON,CCDS4_ON, CCDS5_ON,SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
                DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,ONCHIP_SUM,
                ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,EVENTFILTER_HIGHER,
		MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,     #--- added 03/29/11
#               SUBARRAY_FRAME_TIME,SECONDARY_EXP_TIME, BIAS_RREQUEST,FREQUENCY,BIAS_AFTER,
		DROPPED_CHIP_COUNT
                );

                @too_paramarray = (
                TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS
                );

                @time_const_paramarray = (
                WINDOW_CONSTRAINT,TSTART,TSTOP
                );
                @roll_const_paramarray = (
                ROLL_CONSTRAINT,ROLL_180,ROLL,ROLL_TOLERANCE
                );

                @acis_win_const_array = (
                ORDR,CHIP,
#		INCLUDE_FLAG,
		START_ROW,START_COLUMN,HEIGHT,WIDTH,LOWER_THRESHOLD,PHA_RANGE,SAMPLE
                );

#----- all the param names passed not editable in ocat data page

                @passarray = (
                SEQ_NBR,STATUS,OBSID,PROPOSAL_NUMBER,PROPOSAL_TITLE,GROUP_ID,OBS_AO_STR,TARGNAME,
                REM_EXP_TIME,
                PROPOSAL_JOINT,PROPOSAL_HST,PROPOSAL_NOAO,PROPOSAL_XMM,PROPOSAL_RXTE,PROPOSAL_VLA,
                PROPOSAL_VLBA,SOE_ST_SCHED_DATE,LTS_LT_PLAN,
                TOO_TRIG,TOO_TYPE,TOO_START,TOO_STOP,TOO_FOLLOWUP,TOO_REMARKS,
                );

#----- all the param names in acis data

        @acisarray=(EXP_MODE,BEP_PACK,MOST_EFFICIENT,FRAME_TIME,CCDI0_ON,CCDI1_ON,
			CCDI2_ON,CCDI3_ON,CCDS0_ON,CCDS1_ON,CCDS2_ON,CCDS3_ON,CCDS4_ON,CCDS5_ON,
			SUBARRAY,SUBARRAY_START_ROW,SUBARRAY_ROW_COUNT,
			DUTY_CYCLE,SECONDARY_EXP_COUNT,PRIMARY_EXP_TIME,ONCHIP_SUM,
                	ONCHIP_ROW_COUNT,ONCHIP_COLUMN_COUNT,EVENTFILTER,EVENTFILTER_LOWER,EVENTFILTER_HIGHER,
			MULTIPLE_SPECTRAL_LINES, SPECTRA_MAX_COUNT,     #--- added 03/29/11
			DROPPED_CHIP_COUNT
#			SUBARRAY_FRAME_TIME,SECONDARY_EXP_TIME,BIAS_REQUEST,FREQUENCY,BIAS_AFTER,FEP
);

#----- all the param in acis window data

        @aciswinarray=(START_ROW,START_COLUMN,HEIGHT,WIDTH,LOWER_THRESHOLD,
				PHA_RANGE,SAMPLE,ACISWIN_ID,ORDR,CHIP,
#				INCLUDE_FLAG
				);

#----- all the param in general data dispaly

        @genarray=(REMARKS,INSTRUMENT,GRATING,TYPE,RA,DEC,APPROVED_EXPOSURE_TIME,
			Y_DET_OFFSET,Z_DET_OFFSET,TRANS_OFFSET,FOCUS_OFFSET,DEFOCUS,
			RASTER_SCAN,DITHER_FLAG, UNINTERRUPT,OBJ_FLAG,OBJECT,PHOTOMETRY_FLAG,
			VMAGNITUDE,EST_CNT_RATE,FORDER_CNT_RATE,ROLL,ROLL_TOLERANCE,TSTART,
			TSTOP,PHASE_CONSTRAINT_FLAG,PHASE_EPOCH,PHASE_PERIOD,PHASE_START,
			PHASE_START_MARGIN,PHASE_END,PHASE_END_MARGIN,PRE_MIN_LEAD,PRE_MAX_LEAD,
			PRE_ID,HRC_CONFIG,HRC_ZERO_BLOCK,TOOID,TARGNAME,DESCRIPTION,SI_MODE,
			ACA_MODE,EXTENDED_SRC,SEG_MAX_NUM,Y_AMP,Y_FREQ,Y_PHASE,Z_AMP,Z_FREQ,
			Z_PHASE,HRC_CHOP_FRACTION,HRC_CHOP_DUTY_CYCLE,HRC_CHOP_DUTY_NO,
			TIMING_MODE, ROLL_OBSR,MULTITELESCOPE, OBSERVATORIES, ROLL_CONSTRAINT, 
			WINDOW_CONSTRAINT, ROLL_ORDR, TIME_ORDR, ROLL_180,CONSTR_IN_REMARKS);

#-------------------------------
#------ save the original values
#-------------------------------

	foreach $ent (@namearray){	
		$lname = lc ($ent);
		$wname = 'orig_'."$lname";		# for the original value, all variable name start from "orig_"
		${$wname} = ${$lname};
	}

#-------------------------------------
#------------------	special cases
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
		$tstart[$j]      = 'NULL';
		$tstop[$j]       = 'NULL';
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
if($j < 3){
}
	}

#----------------------------------------------
#------ special treatment for roll requirements
#----------------------------------------------

	for($j = 1; $j <= $roll_ordr; $j++){		# make sure that all entries have some values for each order
		if($roll_constraint[$j] eq ''){ $roll_constraint[$j] = 'NULL'}
		if($roll_180[$j] eq ''){$roll_180[$j] = 'NULL'}
	}
	$proll_ordr = $roll_ordr + 1;
	for($j = $proll_ordr; $j < 30; $j++){		# set default values up to order < 30, assuming that
		$roll_constraint[$j] = 'NULL';		# we do not get the order larger than 29
		$roll_180[$j]         = 'NULL';
		$roll[$j]            = 'NULL';
		$roll_tolerance[$j]  = 'NULL';
	}
	for($j = 1; $j < 30; $j++){			# save them as the original values
		$orig_roll_constraint[$j] = $roll_constraint[$j];
		$orig_roll_180[$j]        = $roll_180[$j];
		$orig_roll[$j]            = $roll[$j];
		$orig_roll_tolerance[$j]  = $roll_tolerance[$j];
	}

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
                $chip[$j]          = 'NULL';
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
}


###################################################################################
###################################################################################
###################################################################################

sub conv_lmon_to_ydate{
	($lmon) = @_;
	if($lmon =~ /Jan/i){
		$mydate = 1;
	}elsif($lmon =~ /Feb/i){
		$mydate = 32;
	}elsif($lmon =~ /Mar/i){
		$mydate = 60;
	}elsif($lmon =~ /Apr/i){
		$mydate = 91;
	}elsif($lmon =~ /May/i){
		$mydate = 121;
	}elsif($lmon =~ /Jun/i){
		$mydate = 152;
	}elsif($lmon =~ /Jul/i){
		$mydate = 182;
	}elsif($lmon =~ /Aug/i){
		$mydate = 213;
	}elsif($lmon =~ /Sep/i){
		$mydate = 244;
	}elsif($lmon =~ /Oct/i){
		$mydate = 274;
	}elsif($lmon =~ /Nov/i){
		$mydate = 305;
	}elsif($lmon =~ /Dec/i){
		$mydate = 335;
	}else{
		$mydate = -999;
	}
}
