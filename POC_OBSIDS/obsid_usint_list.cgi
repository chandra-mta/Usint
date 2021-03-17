#!/usr/bin/env /usr/bin/perl 

BEGIN
{
#    $ENV{SYBASE} = "/soft/SYBASE_OCS15.5";
    $ENV{SYBASE} = "/soft/SYBASE15.7";
}

use DBI;
use DBD::Sybase;
use CGI qw/:standard :netscape /;


#################################################################################################
#												#
#	obsid_usint_list.cgi: display who is in charge for a give obsid/seq #			#
#												#
#		author: t. isobe (tisobe@cfa.harvard.edu)					#
#												#
#		last update: Jan 04, 2017							#
#												#
#################################################################################################

#
#---- set directory paths : updated to read from a file (02/25/2011)
#

#open(IN, '/data/udoc1/ocat/Info_save/dir_list');
#open(IN, './ocat/Info_save/dir_list');
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
        }elsif($atemp[0]  =~ /too_dir/){
                $data_dir = $atemp[1];
        }elsif($atemp[0]  =~ /ocat_dir/){
                $real_dir = $atemp[1];
        }elsif($atemp[0]  =~ /test_dir/){
                $test_dir = $atemp[1];
        }elsif($atemp[0]  =~ /cus_dir/){
                $cus_dir  = $atemp[1];
        }
}
close(IN);


#
#--- read usint person list
#

open(FH, "$data_dir/usint_personal");
@id     = ();
@name   = ();
@o_tel  = ();
@h_tel  = ();
@c_tel  = ();
@email  = ();
$ptot   = 0;
while(<FH>){
	chomp $_;
	@atemp = split(/:/, $_);
	push(@id,    $atemp[0]);
	push(@name,  $atemp[1]);
	push(@o_tel, $atemp[2]);
	push(@h_tel, $atemp[3]);
	push(@c_tel, $atemp[4]);
	push(@email, $atemp[5]);
	$ptot++;
}
close(FH);

#
#--- read database: the entries in ddt and too could be duplicated in 
#--- 		    new_obs_list, but that does not harm any operation.
#

@usint_list  = ();
@seqno_list  = ();
@obsid_list  = ();
@status_list = ();
@person_list = ();
@date_list   = ();
$total       = 0;

@susint_list  = ();
@sseqno_list  = ();
@sobsid_list  = ();
@sstatus_list = ();
@sperson_list = ();
@sdate_list   = ();
$stotal       = 0;

@nusint_list  = ();
@nseqno_list  = ();
@nobsid_list  = ();
@nstatus_list = ();
@nperson_list = ();
@ndate_list   = ();
$ntotal       = 0;

open(FH, "$data_dir/ddt_list");
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@usint_list,  $atemp[0]);
	push(@seqno_list,  $atemp[1]);
	push(@obsid_list,  $atemp[2]);
	push(@status_list, $atemp[3]);
	push(@person_list, $atemp[4]);
	push(@date_list,   $atemp[6]);
	$total++;

	push(@susint_list,  $atemp[0]);
	push(@sseqno_list,  $atemp[1]);
	push(@sobsid_list,  $atemp[2]);
	push(@sstatus_list, $atemp[3]);
	push(@sperson_list, $atemp[4]);
	push(@sdate_list,   $atemp[6]);
	$stotal++;
}
close(FH);


open(FH, "$data_dir/too_list");
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@usint_list,  $atemp[0]);
	push(@seqno_list,  $atemp[1]);
	push(@obsid_list,  $atemp[2]);
	push(@status_list, $atemp[3]);
	push(@person_list, $atemp[4]);
	push(@date_list,    $atemp[6]);
	$total++;

	push(@susint_list,  $atemp[0]);
	push(@sseqno_list,  $atemp[1]);
	push(@sobsid_list,  $atemp[2]);
	push(@sstatus_list, $atemp[3]);
	push(@sperson_list, $atemp[4]);
	push(@sdate_list,   $atemp[6]);
	$stotal++;
}
close(FH);


open(FH, "$data_dir/new_obs_list");
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@usint_list,  $atemp[0]);
	push(@seqno_list,  $atemp[1]);
	push(@obsid_list,  $atemp[2]);
	push(@status_list, $atemp[3]);
	push(@person_list, $atemp[4]);
	push(@date_list,   $atemp[6]);
	$total++;
}
close(FH);


open(FH, "$data_dir/obs_in_30days");
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@nusint_list,  $atemp[0]);
	push(@nseqno_list,  $atemp[1]);
	push(@nobsid_list,  $atemp[2]);
	push(@nstatus_list, $atemp[3]);
	push(@nperson_list, $atemp[4]);
	push(@ndate_list,   $atemp[6]);
	$ntotal++;
}
close(FH);



#
#--- here we start html/cgi
#

print header(-type => 'text/html; charset=utf-8');

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print "<title>USINT Contact Finder</title>";
print "<style  type='text/css'>";
print "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
print "</head>";

print  '<body style="background-color:#FAEBD7; font-family:serif, sans-serif;font-size:12pt; color:black;" >';


print '<h2 style="background-color:blue; color:#FAEBD7">USINT Contact For A Given OBSID/Sequence Number</h2>';
print '<div style="text-align:right"><a href="https://cxc.cfa.harvard.edu/cus/"><strong>Back to USINT Page</strong></a></div>';
print '<div style="text-align:right"><a href="https://cxc.cfa.harvard.edu/mta/CUS/Usint/poc_obsid_list.cgi">';
print '<strong>Go to "A List Of Observations For A Given POC ID" Page</strong></a></div>';


print start_form();

$check = param('Check');
$disp  = param('disp');
if($check =~ /DDT/){
	$disp = 0;
}

if($check =~ /Submit/){
	$input_no = param('input_no');
	$input_no =~ s/\s+//g;
	$disp     = 0;
}elsif($check =~ /Scheduled/i){
	$disp = 10;
}elsif($disp > 5){
	$input_no = '';
	OUTER:
	for($k = 0; $k < $ptot; $k++){
		$cname = $name[$k];
		if($cname =~ /br/){
			@etemp = split(/\</, $cname);
			$cname = $etemp[0];
		}
#		if($check =~ /$name[$k]/){
		if($check =~ /$cname/){
			$p_name = $name[$k];
			$p_o_tel = $o_tel[$k];
			$p_h_tel = $h_tel[$k];
			$p_c_tel = $c_tel[$k];
			$p_email = $email[$k];
			last OUTER;
		}
	}
}else{
	$input_no = '';
	$disp     = 1;
	OUTER:
	for($k = 0; $k < $ptot; $k++){
		if($check =~ /$name[$k]/){
			$p_name = $name[$k];
			$p_o_tel = $o_tel[$k];
			$p_h_tel = $h_tel[$k];
			$p_c_tel = $c_tel[$k];
			$p_email = $email[$k];
			$disp = 2;
			last OUTER;
		}
	}
}

print '<table style="border-width:0px">';

print '<tr>';
print '<th style="text-align:left">Type OBSID or Seqence Number, and click "Submit"<br />';
print 'to find who is POC for the observation</th> ';
print "<td style='text-align:center'><input type='text' size='10' name='input_no' value='$input_no'>";
print '<input type="submit" name="Check" value="Submit"></td>';
print '</tr>';

print '<tr>';
print '<th style="text-align:left">Show Approved  DDT/TOO List </th> ';
print '<td style="text-align:center"><input type="submit" name="Check" value="DDT/TOO List"></td>';
print '</tr>';
print '<tr>';
print '<th style="text-align:left">Show Observation Scheduled in the Next 30 days </th>';
print '<td style="text-align:center"><input type="submit" name="Check" value="Scheduled List"></td>';
print '</tr>';
print '</table>';

print '<div style="padding-bottom:40px"></div>';

if($input_no =~ /\d/){
	$chk = 0;
	if($input_no >= 100000){
		OUTER:
		for($i = 0; $i < $total; $i++){
			if($seqno_list[$i] == $input_no){
				$usint = $usint_list[$i];
				$obsid = $obsid_list[$i];
				$seqno = $input_no;
				$status= $status_list[$i];
				$person= $person_list[$i];
				$sts   = $date_list[$i];
				$chk   = 1;
				last OUTER;
			}
		}
	}else{
		OUTER:
		for($i = 0; $i < $total; $i++){
			if($obsid_list[$i] == $input_no){
				$usint = $usint_list[$i];
				$seqno = $seqno_list[$i];
				$obsid = $input_no;
				$status= $status_list[$i];
				$person= $person_list[$i];
				$sts   = $date_list[$i];
				$chk   = 1;
				last OUTER;
			}
		}
	}


	if($chk == 0){
		if($input_no >= 100000){
			print "<h3 style='color:red'>No observation with Sequence Number: $input_no is in this AO cycle, ";
			print "<br />or the observation is not approved yet.</h3>";
		}else{
			print "<h3 style='color:red'>No observation with ObsId: $input_no is in this AO cycle, ";
			print "<br />or the observation is  not approved yet.</h3>";
		}
	}else{
	
		find_group();

		if($person =~ /ppp/ && $obs_ao_str > 11){
			$person = 'jeanconn';
		}

		if($person =~ /TBD/i || $person eq ''){
			$pos = 14;
		}else{
			OUTER:
			for($k = 0; $k < $ptot; $k++){
				if($id[$k] =~ /$person/){
					$pos = $k;
					last OUTER;
				}
			}
		}
	
		print "<h3>Contact for <div style='color:#20B2AA'>";
		print "ObsID: <a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details&amp;obsid=$obsid'  target='_blank'>$obsid</a> / ";
		print "Sequene Number: <a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&obsid=$obsid' target='_blank'>$seqno</a>";
		if($sts ne ''){
			print " ($status -- <em style='font-size:80%'>$sts</em>) </div>",' </h3>';
		}else{
			print " ($status) </div>",' </h3>';
		}
	
		if($type =~ /too/i || $type =~ /ddt/i){
			$utype = uc($type);
			print "<h4 style='color:#FF00FF'>This Is  $utype Observation ",'</h4>';
		}
	
		if($usint eq '' && ($status =~ /scheduled/ || $status =~ /unobserved/)){
			print '<h3>USINT person is not assigned for this observation yet.</h3>';
		}else{
			print '<table>';
			print '<tr><th>Name</th><th>Office Phone</th><th>Cell Phone</th><th>Home Phone</th><th>Email</th></tr>';
			print '<tr>';


			$user = $name[$pos];
			if($user =~ /Norbert/){
				$user = 'HETG';
			}elsif($user =~ /Kashyap/){
				$user = 'HRC';
			}elsif($user =~ /Wargelin/){
				$user = 'LETG';
			}elsif($user =~ /Larry/){
				$user = 'CAL';
			}

			print "<td style='text-align:center'><a href='https://cxc.cfa.harvard.edu/mta/CUS/Usint/poc_obsid_list.cgi\?$user'>$name[$pos]</a>", '</td>';
			print "<td style='text-align:center'>$o_tel[$pos]",'</td>';
			print "<td style='text-align:center'>$h_tel[$pos]",'</td>';
			print "<td style='text-align:center'>$c_tel[$pos]",'</td>';
			print "<td style='text-align:center'><a href='mailto:$email[$pos]'>$email[$pos]</a>",'</td>';
			print '</tr>';
			print '</table>';

			print "<p style='font-size:80%'>If you like to see all observations under <em>$name[$pos]</em>, please click the name above.</p>";
		}
	
		print '<div style="padding-bottom:20px"></div>';
		$cnt1 = 0;
		foreach (@group_obsid){
			$cnt1++;
		}
	
		$cnt2 = 0;
		foreach (@monitor_series){
			$cnt2++;
		}
		if($cnt1 > 0 || $cnt2 > 0){
			print '<h3>Related OBSIDs </h3>';
	
			if($cnt1 > 0){
				print '<table style="border-width:0px">';
				print '<tr>';
				print '<th colspan=4>Grouped Observation</th></tr>';
				print '<tr><th>ObsID</th><th>Seq. No</th><th>Status</th><th>Scheduled Date</th></tr>';
				foreach $ent (@group_obsid){
					OUTER:
					for($i = 0; $i < $total; $i++){
						if($obsid_list[$i] == $ent){
							$usint = $usint_list[$i];
							$seqno = $seqno_list[$i];
							$obsid = $input_no;
							$status= $status_list[$i];
							$person= $person_list[$i];
							$sts   = $date_list[$i];
							$chk   = 1;
							last OUTER;
						}
					}
					print "<tr><td><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details&amp;obsid=$ent' target='_blank'>$ent</a></td>";
					print "<td><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&amp;obsid=$ent' target='_blank'>$seqno</a></td>";
					print "<td>$status</td><td>$sts</td></tr>";
				}
				print '</table>';
				print '<br /><br />';
			}

			if($cnt2 > 0){
				print '<table style="border-width:0px">';
				print '<tr><th colspan=4>Monitoring Observation</th></tr>';
				print '<tr><th>ObsID</th><th>Seq. No</th><th>Status</th><th>Scheduled Date</th></tr>';
				foreach $ent (@monitor_series){
					OUTER:
					for($i = 0; $i < $total; $i++){
						if($obsid_list[$i] == $ent){
							$usint = $usint_list[$i];
							$seqno = $seqno_list[$i];
							$obsid = $input_no;
							$status= $status_list[$i];
							$person= $person_list[$i];
							$sts   = $date_list[$i];
							$chk   = 1;
							last OUTER;
						}
					}
					print "<tr><td><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details&amp;obsid=$ent' target='_blank'>$ent</a></td>";
					print "<td><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&amp;obsid=$ent' target='_blank'>$seqno</a></td>";
					print "<td style='text-align:center' >$status</td><td>$sts</td></tr>";
				}
				print '</table>';
				print '<div style="padding-bottom:20px"></div>';
			}
		}		
	}
}elsif($disp > 0 && $disp < 10){


	print "<h3>USINT responsible for approved DDT/TOO </h3>";
	print "<h4> This is either an instrument specialist or the bare ACIS support person on duty at the time the proposal was APPROVED. </h4>";

	if($disp > 1){
		print "<h3>Contact Information</h3>";
		print "<table border=1 style='paddinig-top:30px'>";
		print "<tr>";
		print "<th>Name</th><th>Office Tel</th><th>Home Tel</th><th>Cell Phone</th><th>Email</th>";
		print "</tr><tr>";

		$user = $p_name;
		if($user =~ /Norbert/){
			$user = 'HETG';
		}elsif($user =~ /Kashyap/){
			$user = 'HRC';
		}elsif($user =~ /Wargelin/){
			$user = 'LETG';
		}elsif($user =~ /Larry/){
			$user = 'CAL';
		}

		print "<td style='text-align:center'><a href='https://cxc.cfa.harvard.edu/mta/CUS/Usint/poc_obsid_list.cgi\?$user'>$p_name</a></td>";
		print "<td style='text-align:center'>$p_o_tel</td>";
		print "<td style='text-align:center'>$p_h_tel</td>";
		print "<td style='text-align:center'>$p_c_tel</td>";
		print "<td style='text-align:center'><a href='mailto:$p_email'>$p_email</a></td>";
		print "</tr>";
		print "</table>";
		print "<p style='font-size:80%;padding-bottom:20px'>If you like to see all observations under <em>$p_name</em>, please click the name above.</p>";
	}


	print '<p>Click POC name to display the contact information.</p>';

	print "<table border=1>";
	print "<tr>";
	print "<th>Type</th>";
	print "<th>OBSID</th>";
	print "<th>Seq #</th>";
	print "<th>Status</th>";
	print "<th>POC</th>";
	print "<th>Obs Date</th>";
	print "</tr>";

	for($i = 0; $i < $stotal; $i++){
		print "<tr>";
		$type = uc($susint_list[$i]);
		print "<td style='text-align:center'>$type</td>";
		print "<td style='text-align:center'><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details&amp;obsid=$sobsid_list[$i]' target='_blank'>$sobsid_list[$i]</a></td>";
		print "<td style='text-align:center'><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&amp;obsid=$sobsid_list[$i]'  target='_blank'>$sseqno_list[$i]</a></td>";
		print "<td style='text-align:center'>$sstatus_list[$i]</td>";

		OUTER:
		for($k = 0; $k < $ptot; $k++){
			if($sperson_list[$i] =~ /$id[$k]/){
				$poc_name = $name[$k];
				$poc_email= $email[$k];
				last OUTER;
			}
		}

		$pnam = $poc_name;
		if($pnam =~ /br/){
			$pnam =~ s/\<br\>/ \/ /;
		}
		print "<td style='text-align:center'><input type='submit' name='Check' value='$pnam'></td>";
		print "<td>$sdate_list[$i]</td>";
		print "</tr>";
	}

	print "</table>";


}elsif($check =~ /Scheduled/ || $disp > 5){

		print '<h3>Observations Scheduled in the Next 30 Days</h3>';

		if($p_name ne ''){
			print "<h3>Contact Information</h3>";
			print "<table border=2 cellpadding=5 cellspacing=5 style='paddinig-top:30px'>";
			print "<tr>";
			print "<th>Name</th><th>Office Tel</th><th>Home Tel</th><th>Cell Phone</th><th>Email</th>";
			print "</tr><tr>";

			$user = $p_name;
			if($user =~ /Norbert/){
				$user = 'HETG';
			}elsif($user =~ /Kashyap/){
				$user = 'HRC';
			}elsif($user =~ /Wargelin/){
				$user = 'LETG';
			}elsif($user =~ /Larry/){
				$user = 'CAL';
			}

			print "<td style='text-align:center'><a href='https://cxc.cfa.harvard.edu/mta/CUS/Usint/poc_obsid_list.cgi\?$user'>$p_name</a></td>";
			print "<td style='text-align:center'>$p_o_tel</td>";
			print "<td style='text-align:center'>$p_h_tel</td>";
			print "<td style='text-align:center'>$p_c_tel</td>";
			print "<td style='text-align:center'><a href='mailto:$p_email'>$p_email</a></td>";
			print "</tr>";
			print "</table>";
			print "<p style='font-size:80%;padding-bottom:20px'>If you like to see all observations under <em>$p_name</em>, please click the name above.</p>";
		}

		print "<table border=2 cellpadding=5 cellspacing=5>";
		print "<tr>";
		print "<th>Type</th>";
		print "<th>OBSID</th>";
		print "<th>Seq #</th>";
		print "<th>Status</th>";
		print "<th>POC</th>";
		print "<th>Obs Date</th>";
		print "</tr>";

		print hidden(-name=>'disp', -override=>"$disp", -value=>"$disp");

		for($i = 0; $i < $ntotal; $i++){
			print "<tr>";
			$type = uc($nusint_list[$i]);
			print "<td style='text-align:center'>$type</td>";
			print "<td><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details&amp;obsid=$nobsid_list[$i]' target='_blank'>$nobsid_list[$i]</a></td>";
			print "<td><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&amp;obsid=$nobsid_list[$i]' target='_blank'>$nseqno_list[$i]</a></td>";

#			print "<td style='text-align:center'><a href='https://cxc.cfa.harvard.edu/cgi-gen/target_param.cgi\?$nobsid_list[$i]' target='_blank'>$nobsid_list[$i]</a></td>";
#			print "<td style='text-align:center'><a href='https://cxc.cfa.harvard.edu/cgi-gen/mp/target.cgi\?$nseqno_list[$i]'   target='_blank'>$nseqno_list[$i]</a></td>";
			print "<td style='text-align:center'>$nstatus_list[$i]</td>";
	
			OUTER:
			for($k = 0; $k < $ptot; $k++){
				if($nperson_list[$i] =~ /$id[$k]/){
					$poc_name = $name[$k];
					$poc_email= $email[$k];
					last OUTER;
				}
			}

			$pnam = $poc_name;
			if($pnam =~ /br/){
				$pnam =~ s/\<br\>/ \/ /;
			}
			print "<td style='text-align:center'><input type='submit' name='Check' value='$pnam'></a></td>";
			print "<td>$ndate_list[$i]</td>";
			print "</tr>";
		}
		print'</table>';
}
	
print end_form();

print "<div style='padding-top:20px;padding-bottom:10px'>";
print '<hr />';
print "</div>";
print "<p style='font-size:80%'><em>";
print 'If you have any questions about this site, please contact: <a href="mailto:swolk@head.cfa.harvard.edu">swolk@head.cfa.harvard.edu</a>';
print "</em></p>";
print "<p style='font-size:80%;text-align:right'><em>";
print 'Last Update: Oct 06, 2010';
print '</em></p>';

print "</body>";
print "</html>";

###########################################################################################
###########################################################################################
###########################################################################################

sub match_usint_person{

	if($type    =~ /cal/i){
		$mup = 'cal';
	}elsif($grating =~ /letg/i){
		$mup = 'letg';
	}elsif($grating =~ /hetg/i){
		$mup = 'hetg';
	}elsif($instrument =~ /hrc/i){
		$mup = 'hrc';
	}elsif($seqno >= 100000 && $seqno < 300000){
		$mup = 'sjw';
	}elsif($seqno >= 300000 && $seqno < 500000){
		$mup = 'nraw';
	}elsif($seqno >= 500000 && $seqno < 600000){
		$mup = 'ppp';
	}elsif($seqno >= 600000 && $seqno < 700000){
		$mup = 'ping';
	}elsif($seqno >= 700000 && $seqno < 800000){
		$mup = 'emk';
	}elsif($seqno >= 800000 && $seqno < 900000){
		$mup = 'mm';
	}elsif($seqno >= 900000 && $seqno < 1000000){
		$mup = 'das';
	}
}

###########################################################################################
### find_group: find related obsids                                                     ###
###########################################################################################

sub find_group {

#------------------------------------------------
#-------  database username, password, and server
#------------------------------------------------

	$db_user = "browser";
	$server  = "ocatsqlsrv";

	$db_passwd =`cat $pass_dir/.targpass`;
	chomp $db_passwd;

#--------------------------------------
#-------- open connection to sql server
#--------------------------------------

	my $db = "server=$server;database=axafocat";
	$dsn1  = "DBI:Sybase:$db";
	$dbh1  = DBI->connect($dsn1, $db_user, $db_passwd, { PrintError => 0, RaiseError => 1});


#
#--- find a group_id etc
#

#------------------------------------------------------
#---------------  get stuff from target table, clean up
#------------------------------------------------------

	$sqlh1 = $dbh1->prepare(qq(select
			group_id,pre_id,pre_min_lead,pre_max_lead,grating,type,instrument,obs_ao_str,
			soe_st_sched_date,lts_lt_plan
	from target where obsid=$obsid));

	$sqlh1->execute();
	@targetdata   = $sqlh1->fetchrow_array;
        $sqlh1->finish;

	$group_id     = $targetdata[0];
	$pre_id       = $targetdata[1];
	$pre_min_lead = $targetdata[2];
	$pre_max_lead = $targetdata[3];
	$grating      = $targetdata[4];
	$type         = $targetdata[5];
	$instrument   = $targetdata[6];
	$obs_ao_str   = $targetdata[7];
	$soe_st_sched_date = $targetdata[8];
	$lts_lt_plan  = $targetdata[9];

	$group_id     =~ s/\s+//g;
	$pre_id       =~ s/\s+//g;
	$pre_min_lead =~ s/\s+//g;
	$pre_max_lead =~ s/\s+//g;
	$grating      =~ s/\s+//g;
	$type         =~ s/\s+//g;
	$instrument   =~ s/\s+//g;
	$obs_ao_str   =~ s/\s+//g;

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
			$group_obsid = join( @group_obsid);
			if($usint_on =~ /test/){
				@group       = (@group, "<a href=\"$test_http\/ocatdata2html.cgi\?$group_obsid\">$group_obsid<\/a> ");
			}else{
				@group       = (@group, "<a href=\"$usint_http\/ocatdata2html.cgi\?$group_obsid\">$group_obsid<\/a> ");
			}
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


##############################################################################################
### find_obs_date: extract obs starting date from mit web site                             ###
##############################################################################################

sub find_obs_date{
	system("/opt/local/bin/lynx -source https://acis.mit.edu/cgi-bin/get-obsid\?id=$obs_id > $temp_dir/zfind_bos_date");
	open(IN, "$temp_dir/zfind_bos_date");
	$chk = 0;
	OUTER:
	while(<IN>){
		if($chk > 0){
			@dtemp = split(/\<tt\>/, $_);
			@ftemp = split(/\</, $dtemp[1]);
			$date  = $ftemp[0];
			last OUTER;
		}
		if($_ =~ /Start Date:/){
			$chk = 1;
		}
	}
	close(IN);
	system("rm $temp_dir/zfind_bos_date");
	
	@dtemp = split(/\s+/, $date);
	@ftemp = split(/-/,   $dtemp[0]);
	
	if($ftemp[1] == 1){
		$mon = "Jan";
	}elsif($ftemp[1] == 2){
		$mon = "Feb";
	}elsif($ftemp[1] == 3){
		$mon = "Mar";
	}elsif($ftemp[1] == 4){
		$mon = "Apr";
	}elsif($ftemp[1] == 5){
		$mon = "May";
	}elsif($ftemp[1] == 6){
		$mon = "Jun";
	}elsif($ftemp[1] == 7){
		$mon = "Jul";
	}elsif($ftemp[1] == 8){
		$mon = "Aug";
	}elsif($ftemp[1] == 9){
		$mon = "Sep";
	}elsif($ftemp[1] == 10){
		$mon = "Oct";
	}elsif($ftemp[1] == 11){
		$mon = "Nov";
	}elsif($ftemp[1] == 12){
		$mon = "Dec";
	}
	
	@etemp = split(/:/, $dtemp[1]);
	$part = 'AM';
	$time = $etemp[0];
	if($etemp[0] > 12){
		$part = 'PM';
		if($etemp[0] > 12){
			$time = $etemp[0] - 12;
		}
	}
	
	$time = "$time:$etemp[1]"."$part";
	
	$date = "$mon $ftemp[2] $ftemp[0] $time";
}
