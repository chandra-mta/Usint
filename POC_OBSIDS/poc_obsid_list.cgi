#!/usr/bin/perl

use DBI;
#use DBD::Sybase;
use CGI qw/:standard :netscape /;

#############################################################################
#												                            #
#	poc_obsid_list.cgi: display obsid list for a given poc 					#
#												                            #
#		author: t. isobe (tisobe@cfa.harvard.edu)					        #
#												                            #
#		last update: Jan 05, 2017							                #
#												                            #
#############################################################################

#
#---- set directory pathes
#

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
#--- read database
#

@usint_list  = ();
@seqno_list  = ();
@obsid_list  = ();
@status_list = ();
@person_list = ();
@ao_list     = ();
@date_list   = ();
$total = 0;

open(FH, "$data_dir/too_list");
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@usint_list,  $atemp[0]);
	push(@seqno_list,  $atemp[1]);
	push(@obsid_list,  $atemp[2]);
	push(@status_list, $atemp[3]);
	push(@person_list, $atemp[4]);
	push(@ao_list,     $atemp[5]);
	push(@date_list,   $atemp[6]);
	$total++;
}
close(FH);


open(FH, "$data_dir/ddt_list");
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@usint_list,  $atemp[0]);
	push(@seqno_list,  $atemp[1]);
	push(@obsid_list,  $atemp[2]);
	push(@status_list, $atemp[3]);
	push(@person_list, $atemp[4]);
	push(@ao_list,     $atemp[5]);
	push(@date_list,   $atemp[6]);
	$total++;
}
close(FH);



@ousint_list  = ();
@oseqno_list  = ();
@oobsid_list  = ();
@ostatus_list = ();
@operson_list = ();
@oao_list     = ();
@odate_list   = ();
$ototal = 0;

open(FH, "$data_dir/new_obs_list");
OUTER:
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	if($_ =~ /too/i || $_ =~ /ddt/i){
		%{ao.$atemp[2]} = (ao =>["$atemp[5]"]);
		next OUTER;
	}

	push(@ousint_list,  $atemp[0]);
	push(@oseqno_list,  $atemp[1]);
	push(@oobsid_list,  $atemp[2]);
	push(@ostatus_list, $atemp[3]);
	push(@operson_list, $atemp[4]);
	push(@oao_list,     $atemp[5]);
	push(@odate_list,   $atemp[6]);
	$ototal++;
}
close(FH);


@nusint_list  = ();
@nseqno_list  = ();
@nobsid_list  = ();
@nstatus_list = ();
@nperson_list = ();
@nao_list     = ();
@ndate_list   = ();
$ntotal = 0;

open(FH, "$data_dir/obs_in_30days");
OUTER:
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	if($_ =~ /too/i || $_ =~ /ddt/i){
		%{ao.$atemp[2]} = (ao =>["$atemp[5]"]);
		next OUTER;
	}

	push(@nusint_list,  $atemp[0]);
	push(@nseqno_list,  $atemp[1]);
	push(@nobsid_list,  $atemp[2]);
	push(@nstatus_list, $atemp[3]);
	push(@nperson_list, $atemp[4]);
	push(@nao_list,     $atemp[5]);
	push(@ndate_list,   $atemp[6]);
	$ntotal++;
}
close(FH);

#
#--- read the name of user, if it is supplied from the outside 
#

$name_temp  = $ARGV[0];

#
#--- here we start html/cgi
#

print header(-type => 'text/html; charset=utf-8');
print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print "<title>A List Of Observations For A Given POC ID</title>";
print "<style  type='text/css'>";
print "table{border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
print "</head>";

print  '<body style="background-color:#FAEBD7; font-family:serif, sans-serif;font-size:12pt; color:black;" >';


print '<h2 style="background-color:blue; color:#FAEBD7">A List Of Observations For A Given POC ID</h2>';

print '<div style="text-align:right"><a href="https://cxc.cfa.harvard.edu/cus/"><strong>Back to USINT Page</strong></a></div>';
print '<div style="text-align:right"><a href="https://cxc.cfa.harvard.edu/mta/CUS/Usint/obsid_usint_list.cgi">';
print '<strong>Go to "USINT Contact For A Given OBSID/Sequence Number" Page</strong></a></div>';


print start_form();

$contact = param("poc");
if($contact eq ''){
	$contact      = $name_temp;
}

if($contact =~ /Malgosia Sobolewska/)   {$poc = 'msobolewska'}
elsif($contact =~ /CAL/)             {$poc = 'cal'}
elsif($contact =~ /Jean Connelly/)   {$poc = 'jeanconn'}
elsif($contact =~ /Dan Schwartz/)    {$poc = 'das'}
elsif($contact =~ /HETG/)            {$poc = 'hetg'}
elsif($contact =~ /Jeremy Drake/)    {$poc = 'jd'}
elsif($contact =~ /Scott Wolk/)      {$poc = 'sjw'}
elsif($contact =~ /HRC/)             {$poc = 'hrc'}
elsif($contact =~ /Ping Zhao/)       {$poc = 'ping'}
elsif($contact =~ /Paul Plucinsky/)  {$poc = 'ppp'}
elsif($contact =~ /LETG/)            {$poc = 'letg'}
elsif($contact =~ /Brad Spitzbart/)  {$poc = 'brad'}


print '<h3>Please choose POC to display the list of observations</h3>';


print '<table style="border-width:0px">';

print '<tr>';
#print '<td style="text-align:center">';
#print '<input type="submit" name="poc" value="Nancy Adams Wolk">';
#print '</td>';
#print '<td style="text-align:center">';
#print '<input type="submit" name="poc" value="Brad Spitzbart">';
#print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="Malgosia Sobolewska">';
print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="CAL">';
print '</td>';
print '</tr>';

print '<tr>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="Jean Connelly">';
print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="Dan Schwartz">';
print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="HETG">';
print '</td>';
print '</tr>';

print '<tr>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="Paul Plucinsky">';
print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="Scott Wolk">';
print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="HRC">';
print '</td>';
print '</tr>';


print '<tr>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="Ping Zhao">';
print '</td>';
print '<td style="text-align:center">';
print '<input type="submit" name="poc" value="LETG">';
print '</td>';
print '<td>&#160;</td>';
print '</tr>';

print '</table>';


if($poc ne '' && $poc !~ /\s+/){
 
	print "<div style='padding-left:40px'>";
	print "<h3>POC: $contact</h3>";

	OUTER:
	for($k = 0; $k < $ptot; $k++){
		if($id[$k] =~ /$poc/){
			print '<table border=1>';
			print '<tr>';
			if($poc =~ /hrc/i || $poc =~ /cal/i || $poc =~ /hetg/i || $poc =~ /letg/i){
				print "<th>Name</th>";
			}
			print '<th>Office Phone</th><th>Cell Phone</th><th>Home Phone</th><th>Email</th></tr>';
			print '<tr>';

			if($poc =~ /hrc/i || $poc =~ /cal/i || $poc =~ /hetg/i || $poc =~ /letg/i){
				print "<td style='text-align:center'>$name[$k]</td>";
			}

			print "<td style='text-align:center'>$o_tel[$k]",'</td>';
			print "<td style='text-align:center'>$h_tel[$k]",'</td>';
			print "<td style='text-align:center'>$c_tel[$k]",'</td>';
			print "<td style='text-align:center'><a href='mailto:$email[$k]'>$email[$k]</a>",'</td>';
			print '</tr>';
			print '</table>';
			last OUTER;
		}
	}

	print "<p style='padding-top:20px;padding-bottom:20px'>";
	print "DDT/TOO observations are indicated by <em style='color:lime;background-color:lime'>color</em>, and all other observations<br />";
	print "scheduled in the next 30 days are indicated by <em style='color:#ADFF2F;background-color:#ADFF2F'>color</em>.";
	print "</p>";

	print "<table border=1> ";
	print "<tr>";
	print "<th>OBSID</th>";
	print "<th>Seq #</th>";
	print "<th>Status</th>";
	print "<th>Type</th>";
	print "<th>AO #</th>";
	print "<th>Scheduled Date</th>";
	print "</tr>";

	if($total > 0){
		print '<tr><td colspan=6>&#160;</td></tr>';
	}

	$chk = 0;
	for($i = 0; $i < $total; $i++){
		if($person_list[$i] =~ /$poc/){
			print "<tr bgcolor=lime>";
			print "<td style='text-align:center'><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details\&obsid=$obsid_list[$i]' target='_blank'>$obsid_list[$i]</a></td>";
			print "<td style='text-align:center'><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&obsid=$obsid_list[$i]' target='_blank'>$seqno_list[$i]</a></td>";
			print "<td style='text-align:center'>$status_list[$i]</td>";
			$type = uc($usint_list[$i]);
			print "<td style='text-align:center'><strong style='color:red'>$type</strong></td>";
			print "<td style='text-align:center'>${ao.$obsid_list[$i]}{ao}[0]</td>";
			print "<td style='text-align:center'>$date_list[$i]</td>";
			print "</tr>";
			$chk++;
		}
	}

	if($chk == 0){
		print '<tr><td colspan=6 style="text-align:center">No DDT/TOO Observation</td</tr>';
	}
	print '<tr><td colspan=6>&#160;</td</tr>';

	@chkobs = ();
	$chk    = 0;
	for($i = 0; $i < $ntotal; $i++){
		if($nperson_list[$i] =~ /$poc/){
			print "<tr sytle='background-color:#ADFF2F'>";
			print "<td style='text-align:center'><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details\&obsid=$nobsid_list[$i]' target='_blank'>$nobsid_list[$i]</a></td>";
			print "<td style='text-align:center'><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&obsid=$nobsid_list[$i]' target='_blank'>$nseqno_list[$i]</a></td>";
			print "<td  style='text-align:center'>$nstatus_list[$i]</td>";
			print "<td style='text-align:center'>$nusint_list[$i]</td>";
			print "<td style='text-align:center'>$nao_list[$i]</td>";
			print "<td style='text-align:center'>$ndate_list[$i]</td>";
			print "</tr>";
			push(@chkobs, $nobsid_list[$i]);
			$chk++;
		}
	}
	if($chk > 0){
		print '<tr><td colspan=6 style="text-align:center">&#160;</td></tr>';
	}



	$chk = 0;
	OUTER:
	for($i = 0; $i < $ototal; $i++){
		if($operson_list[$i] =~ /$poc/){
			foreach $ent(@chkobs){
				if($oobsid_list[$i] =~ /$ent/){
					next OUTER;
				}
			}
			print "<tr>";
			print "<td style='text-align:center'><a href='https://cda.harvard.edu/chaser/startViewer.do\?menuItem=details\&obsid=$oobsid_list[$i]' target='_blank'>$oobsid_list[$i]</a></td>";
			print "<td style='text-align:center'><a href='https://cda.cfa.harvard.edu/chaser/startViewer.do\?menuItem=sequenceSummary&obsid=$oobsid_list[$i]' target='_blank'>$oseqno_list[$i]</a></td>";
			if($ostatus_list[$i] =~ /unobserved/)  {$color = '#F0E68C'}
			elsif($ostatus_list[$i] =~ /scheduled/){$color = '#7FFF00'}
			elsif($ostatus_list[$i] =~ /observed/) {$color = '#00FFFF'}
			print "<td bgcolor=$color style='text-align:center'>$ostatus_list[$i]</td>";
			print "<td style='text-align:center'>$ousint_list[$i]</td>";
			print "<td style='text-align:center'>$oao_list[$i]</td>";
			print "<td style='text-align:center'>$odate_list[$i]</td>";
			print "</tr>";
			$chk++;
		}
	}
	if($chk == 0){
		print '<tr><td colspan=6 style="text-align:center">No Observation Assigned</td</tr>';
	}

	print "</table>";
	print '</div>';
}

print end_form();

print '<hr />';
print "<p style='font-size:80%'><em>";
print 'If you have any questions about this site, please contact: <a href="mailto:swolk@head.cfa.harvard.edu">swolk@head.cfa.harvard.edu</a>';
print "</em></p>";
print "<p style='font-size:80%;text-align:right'>";
print "<em>";
print 'Last Update: Oct 30, 2012';
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
		$mup = 'sjw';
	}elsif($seqno >= 500000 && $seqno < 600000){
		$mup = 'ppp';
	}elsif($seqno >= 600000 && $seqno < 700000){
		$mup = 'ping';
	}elsif($seqno >= 700000 && $seqno < 800000){
		$mup = 'brad';
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

#	$db_user = "browser";
#	$db_passwd =`cat $pass_dir/.targpass`;

    $web = $ENV{'HTTP_REFERER'};
    if($web =~ /icxc/){
        $db_user   = "mtaops_internal_web";
        $db_passwd =`cat $pass_dir/.targpass_internal`;
    }else{
        $db_user = "mtaops_public_web";
        $db_passwd =`cat $pass_dir/.targpass_public`;
    }

	$server  = "ocatsqlsrv";
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
			group_id,pre_id,pre_min_lead,pre_max_lead,grating,type,instrument,obs_ao_str
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


