#!/home/ascds/DS.release/bin/perl

#################################################################################################################
#														#
#	create_schedule_table.perl: create a html page from a given schedule					#
#														#
#		author: t. isobe (tisobe@cfa.harvard.edu)							#
#														#
#		last update: Jun 13, 2019									#
#														#
#################################################################################################################

#
#---- set directory paths : updated to read from a file (02/25/2011): this is user cus version
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
        }elsif($atemp[0]  =~ /ctemp_dir/){
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
#--- read a list of too persons' information
#

open(FH, "$data_dir/personal_list");

@name   = ();
@office = ();
@cell   = ();
@home   = ();
@mail   = ();
$pcnt   = 0;

while(<FH>){
	chomp $_;
	@atemp = split(/<>/, $_);
	push(@name,   $atemp[0]);
	push(@office, $atemp[1]);
	push(@cell,   $atemp[2]);
	push(@home,   $atemp[3]);
	push(@mail,   $atemp[4]);
	$pcnt++;
}
close(FH);

#
#--- find today's date
#

($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
$year = 1900 + $year;
$mon++;

#
#--- read schedule list
#

open(FH, "$data_dir/schedule");

@charge  = ();
@mstart  = ();
@dstart  = ();
@mend    = ();
@dend    = ();
@period  = ();
$scnt    = 0;
$mark    = 0;

while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	push(@charge, $atemp[0]);
	$lmon = change_month_format($atemp[1]);
	push(@mstart, $lmon);
	push(@dstart, $atemp[2]);
	$lmon = change_month_format($atemp[4]);
	push(@mend,   $lmon);
	push(@dend,   $atemp[5]);

	$start = $atemp[1];
	$end   = $atemp[4];
	$now   = 0;
	if($start == 12 && $end == 1){
		if($mon == $start){
			if($mday >= $atemp[2]){
				$now = 1;
				$mark = $scnt;
			}
		}elsif($mon == $end){
			if($mday <= $atemp[5]){
				$now = 1;
				$mark = $scnt;
			}
		}
	}elsif($mon >= $start &&  $mon <= $end){
		if($start == $end){
			if($mday >= $atemp[2] && $mday <= $atemp[5]){
				$now = 1;
				$mark = $scnt;
			}
		}else{
			if($mon == $start){
				if($mday >= $atemp[2]){
					$now = 1;
					$mark = $scnt;
				}
			}else{
				if($mday <= $atemp[5]){
					$now = 1;
					$mark = $scnt;
				}
			}
		}
	}
	push(@period, $now);
	$scnt++;
}
close(FH);

open(OUT, "> $cus_dir/too_contact_schedule.html");
print OUT '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">',"\n";
print OUT '<html>', "\n";
print OUT '<head>',"\n";
print OUT '<title>USINT TOO Point of Contact</title>' ,"\n";
#print OUT "<link rel=\"stylesheet\" type=\"text/css\" href='http://asc.harvard.edu/mta/REPORTS/Template/mta_monthly.css' />","\n";

print OUT '<style type="text/css">',"\n";
print OUT 'hr {color:sienna}',"\n";
print OUT 'p {margin-left:20px}',"\n";
print OUT 'body{   background-color:#FAEBD7;',"\n";
print OUT '        font-family:     serif, sans-serif, Verdana, Helvetica, Arial;',"\n";
print OUT '        font-size:       12pt;',"\n";
print OUT '//      text-align:      justify;',"\n";
print OUT '//      color:           #FFF8DC;',"\n";
print OUT '        margin:          20px;',"\n";
print OUT '        padding:         10px;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT 'table{',"\n";
print OUT '//      color:          #FFFACD;',"\n";
print OUT '        font-size:      95%;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT 'p{',"\n";
print OUT '//        color:          #FFFACD;',"\n";
print OUT '        margin-left:    10px;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT 'p.center{',"\n";
print OUT '        text-align:     center;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT 'a:link    {color:       #FF0000}  /* unvisited link */',"\n";
print OUT 'a:visited {color:       #FFFF22}  /* visited link */',"\n";
print OUT 'a:hover   {color:       #FF00FF}  /* mouse over link */',"\n";
print OUT 'a:active  {color:       #0000FF}  /* selected link */',"\n";
print OUT "\n";
print OUT 'h1{',"\n";
print OUT '        text-align:     center;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT 'h1, h2, h3, h4{',"\n";
print OUT '//        color:          #FFFACD;',"\n";
print OUT '        font-style:     oblique;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT 'h2.center{',"\n";
print OUT '        text-align:     center;',"\n";
print OUT '}',"\n";
print OUT "\n";
print OUT "\n";
print OUT '</style>',"\n";

print OUT '</head>',"\n";
print OUT '<body>',"\n";


print OUT '<h2 style="background-color:blue; color:#FAEBD7">USINT TOO Point of Contact</h2>', "\n";

print OUT '<br />',"\n";

print OUT '<p>',"\n";
print OUT '<strong>The current USINT TOO Point of Contact is indicated by <em style="background-color:lime;color:lime">Lime</em> color</strong>.',"\n";
print OUT '</p>',"\n";
print OUT '<p>',"\n";
print OUT 'Shifts run midnight plus <em>&#949;</em> on start day to midnight minus <em>&#949;</em> on last day.',"\n";
print OUT '</p>',"\n";

print OUT '<p>', "\n";
print OUT 'The TOO POC becomes the responsible scientist for all bare ACIS TOO/DDTs', "\n";
print OUT 'APPROVED DURING their on-duty period. Grating and HRC observations are', "\n";
print OUT 'assigned to instrument specialists as are solar system and Crab observations,', "\n";
print OUT 'with the exception of cases where a grating is used primarily to reduce', "\n";
print OUT 'the source event rate (see below) and the observer has minimal interest in the', "\n";
print OUT 'dispersed spectrum. Those not-really-grating observations will remain under', "\n";
print OUT 'the management of the TOO POC and not the instrument specialist.', "\n";
print OUT '</p>', "\n";
print OUT '<p>', "\n";
print OUT 'Inserting the LETG reduces the source rate by a factor of ~8 at wavelengths', "\n";
print OUT 'longer than ~8 Ang (0th order vs no-grating), and by a factor of 3-10 for', "\n";
print OUT 'the HETG; the higher value is for a very soft source (E<2 keV) and the', "\n";
print OUT 'lower value for hard sources (E>4 keV). Use PIMMS for more detailed estimates.', "\n";
print OUT '</p>', "\n";

print OUT '<br />',"\n";
print OUT '<br />',"\n";



print OUT '<table border=1, cellpadding=4, cellspacing=4>',"\n";
print OUT '<tr>',"\n";
print OUT '<th>Period</th><th>Name</th><th>Office Phone</th><th>Cell Phone</th><th>Home Phone</th><th>Email</th>',"\n";
print OUT '</tr>',"\n";

#
#--- if there are too many listing before the current period
#--- skip them.
#

$sub = 0;
if($mark > 4){
	$sub = $mark - 4;
}
$chk   = 0;
$alert = 0;

OUTER:
for($i = 0; $i < $scnt; $i++){
	if($i < $sub){
		next OUTER;
	}

	if($period[$i] == 1){
		print OUT "<tr style='color:blue; background-color:lime'>", "\n";
		$current = $i;
		$person_in_charge = $charge[$i];
		$chk = 1;
	}else{
		print OUT '<tr>',"\n";
	}
	print OUT "<th>$mstart[$i] $dstart[$i] - $mend[$i] $dend[$i]</th>","\n";
	print OUT "<td style='text-align:center'>$charge[$i]</td>","\n";

#
#--- check whether unassigned period is coming soon or not.
#
	if($chk > 0){
		if($chk < 4 && $charge[$i] =~ /TBD/i){
			$alert = $i;
			$chk   = 0;
		}
		$chk++;
	}
		
	OUTER:
	for($j = 0; $j < $pcnt; $j++){
		if($charge[$i] eq $name[$j]){
			if($i == $current){
				$info_current = $j;
			}
			last OUTER;
		}
	}
	print OUT "<td style='text-align:center'>$office[$j]</td>","\n";
	print OUT "<td>$cell[$j]</td>","\n";
	print OUT "<td>$home[$j]</td>","\n";
	if($period[$i] == 1){
		print OUT "<td><a href='mailto:$mail' style='color:blue'>$mail[$j]</a></td>","\n";
	}else{
		print OUT "<td><a href='mailto:$mail'>$mail[$j]</a></td>","\n";
	}
	print OUT "</tr>","\n";
}

print OUT "</table>","\n";

print OUT '<br />',"\n";
print OUT '<a href="https://cxc.cfa.harvard.edu/mta/CUS/Usint/insert_person.cgi" style="color:red">Update Contact List</a>',"\n";
print OUT '<br />',"\n";
print OUT '<a href="https://cxc.cfa.harvard.edu/mta/CUS/Usint/schedule_submitter.cgi" style="color:red">Update Schedule</a>',"\n";
print OUT '<br />',"\n";


print OUT "<br /><br />","\n";
print OUT "<hr />","\n";
print OUT "<p style='font-size:90%'>","\n";
print OUT "<em>\n";
print OUT "Last Update: $mon/$mday/$year<br /><br />","\n";
print OUT "If you have any questions about this page, please email to: <a href='mailto:swolk\@head.cfa.harvard.edu'>swolk\@head.cfa.harvard.edu</a>\n";
print OUT "</em>\n";
print OUT "</p>\n";

print OUT '</body>',"\n";
print OUT '</html>',"\n";

close(OUT);

#####system("chmod 777 $cus_dir/too_contact_schedule.html");
system("chmod 755 $cus_dir/too_contact_schedule.html");

open(OUT, ">  $temp_dir/temp_email");

print OUT "The current USINT TOO-POC is $charge[$current]:\n";
print OUT "\tOffice Phone:\t$office[$info_current]\n";
print OUT "\tCell   Phone:\t$cell[$info_current]\n";
print OUT "\tHome   Phone:\t$home[$info_current]\n";
print OUT "\tMail   Phone:\t$mail[$info_current]\n\n";

$next      = $current + 1;

OUTER:
for($j = 0; $j < $pcnt; $j++){
	if($charge[$next] eq $name[$j]){
		$info_next = $j;
		last OUTER;
	}
}

print OUT "From Midnight $mstart[$next] $dstart[$next] to $mend[$next] $dend[$next]  ";
print OUT "the TOO-POC will be $charge[$next]:\n";
print OUT "\tOffice Phone:\t$office[$info_next]\n";
print OUT "\tCell   Phone:\t$cell[$info_next]\n";
print OUT "\tHome   Phone:\t$home[$info_next]\n";
print OUT "\tMail   Phone:\t$mail[$info_next]\n\n";

print OUT "If you have any questions about this email, please contact to Scott Wolk ";
print OUT "(swolk\@head.cfa.harvard.edu), as no one will read email sent to the account.\n";
close(OUT);


if($wday == 5){
	system("cat $temp_dir/temp_email | mailx -s\"Subject: USINT TOO Point of Contact Updated\n\" isobe\@head.cfa.harvard.edu");
	system("cat $temp_dir/temp_email | mailx -s\"Subject: USINT TOO Point of Contact Updated\n\" swolk\@head.cfa.harvard.edu");
	system("cat $temp_dir/temp_email | mailx -s\"Subject: USINT TOO Point of Contact Updated\n\" $mail[$info_next]");

}
system("rm $temp_dir/temp_email");

#
#--- if the POC is not assigned two weeks from this period, sent out email to alert Scott
#

#
#--- check whether the notice was sent out the last 24 hrs; if so, don't send it again till later
#

$tdelta = 883699179;            #--- difference between 1970 base and 1998 base

$icheck = ` ls $temp_dir`;

if($icheck =~ /poc_alerted_time/){
	open(FH, "$temp_dir/poc_alerted_time");
	while(<FH>){
		chomp $_;
		$prevsec = $_;
	}
	close(FH);
	
	$cinsec = time() - $tdelta;
	
	$diff   = $cinsec - $prevsec;
	
	if($diff > 86400){
		$send_alert = 1;
	}else{
		$send_alert = 0;
	}
}else{
	$cinsec = time() - $tdelta;
	$send_alert = 1;
}

if($alert > 1 && $send_alert > 0){

	open(OUT, ">$temp_dir/poc_alerted_time");
	print OUT "$cinsec\n";
	close(OUT);

	open(OUT, "> $temp_dir/temp_email_alert");
	print OUT "TOO Point of Contact for the following period has not been assigned yet.\n\n";
	print OUT "\t$mstart[$alert] $dstart[$alert] - $mend[$alert] $dend[$alert]\n\n";
	print OUT "Please assign a person using: \n\n";
	print OUT 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/schedule_submitter.cgi',"\n\n";
	print OUT "as soon as possible.\n";
	close(OUT);

	system("cat $temp_dir/temp_email_alert |mailx -s\"Subject: USINT TOO Point of Contact Needs an Assignment\n\" isobe\@head.cfa.harvard.edu ");
	system("cat $temp_dir/temp_email_alert |mailx -s\"Subject: USINT TOO Point of Contact Needs an Assignment\n\" -cisobe\@head.cfa.harvard.edu swolk\@head.cfa.harvard.edu cus\@head.cfa.harvard.edu");
	system("rm $temp_dir/temp_email_alert");
}

#
#--- create a file for dian hall to read
#

open(IN , "$data_dir/this_week_person_in_charge");
OUTER:
while(<IN>){
	chomp $_;
	if($_ !~ /#/){
		@atemp = split(/\,/, $_);
		$cemail = $atemp[4];
		last OUTER;
	}
}
close(IN);
	
open(OUT , ">$data_dir/this_week_person_in_charge");
for($i = 0; $i < $pcnt; $i++){
	if($name[$i] !~ /$person_in_charge/){
		print OUT "#";
	}else{
		$too_poc = $mail[$i];		#--- used below
	}

	print OUT "$name[$i]",',';
	print OUT "$office[$i]",',';
	print OUT "$cell[$i]",',';
	print OUT "$home[$i]",',';
	print OUT "$mail[$i]\n";
}
close(OUT);

if($cemail !~ /$too_poc/){
	open(OUT2, "> $temp_dir/temp_email2");
	print OUT2 "Hi\n";
	print OUT2 "Your TOO point of contact duty just started. Please check the schedule: \n\n";
	print OUT2 "\thttps://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html\n\n";
	print OUT2 "If you have any questions, please contact: Scott Wolk (swolk\@head.cfa.harvard.edu) as soon as possible.\n";
	close(OUT2);

        system("cat $temp_dir/temp_email2 | mailx -s\"Subject:  TOO Point of Contact Duty: Second  Notification to:$too_poc\n\" isobe\@head.cfa.harvard.edu swolk\@head.cfa.harvard.edu");

        system("cat $temp_dir/temp_email2 | mailx -s\"Subject:  TOO Point of Contact Duty: Second  Notification\n\" -ccus\@head.cfa.harvard.edu $too_poc");

	system("rm $temp_dir/temp_email2");
}
	
#
#--- create a file for Daniel Patnaude use .... this function is taken over by write_this_week_too_poc.py
#

#system("chmod 777 /home/mta/TOO-POC");
#open(OUT, ">/home/mta/TOO-POC");
#print OUT "$too_poc\n";
#close(OUT);


###################################################################################################r
####################################################################################################
####################################################################################################

sub change_mon_lett_to_digit{
	my($month, $dmon);
	($month) = @_;
	if($month =~ /Jan/i){
		$dmon = 1;
	}elsif($month =~ /Feb/i){
		$dmon = 2;
	}elsif($month =~ /Mar/i){
		$dmon = 3;
	}elsif($month =~ /Apr/i){
		$dmon = 4;
	}elsif($month =~ /May/i){
		$dmon = 5;
	}elsif($month =~ /Jun/i){
		$dmon = 6;
	}elsif($month =~ /Jul/i){
		$dmon = 7;
	}elsif($month =~ /Aug/i){
		$dmon = 8;
	}elsif($month =~ /Sep/i){
		$dmon = 9;
	}elsif($month =~ /Oct/i){
		$dmon = 10;
	}elsif($month =~ /Nov/i){
		$dmon = 11;
	}elsif($month =~ /Dec/i){
		$dmon = 12;
	}

	return $dmon;
}


############################################################
### change_month_format: change month format             ###
############################################################

sub change_month_format{
        my ($month, $omonth);
        ($month) = @_;
        if($month =~ /\d/){
                if($month == 1){
                        $omonth = 'January';
                }elsif($month == 2){
                        $omonth = 'February';
                }elsif($month == 3){
                        $omonth = 'March';
                }elsif($month == 4){
                        $omonth = 'April';
                }elsif($month == 5){
                        $omonth = 'May';
                }elsif($month == 6){
                        $omonth = 'June';
                }elsif($month == 7){
                        $omonth = 'July';
                }elsif($month == 8){
                        $omonth = 'August';
                }elsif($month == 9){
                        $omonth = 'September';
                }elsif($month == 10){
                        $omonth = 'October';
                }elsif($month == 11){
                        $omonth = 'November';
                }elsif($month == 12){
                        $omonth = 'December';
                }
        }else{
                if($month =~ /jan/i){
                        $omonth = 1;
                }elsif($month =~ /feb/i){
                        $omonth = 2;
                }elsif($month =~ /mar/i){
                        $omonth = 3;
                }elsif($month =~ /apr/i){
                        $omonth = 4;
                }elsif($month =~ /may/i){
                        $omonth = 5;
                }elsif($month =~ /jun/i){
                        $omonth = 6;
                }elsif($month =~ /jul/i){
                        $omonth = 7;
                }elsif($month =~ /aug/i){
                        $omonth = 8;
                }elsif($month =~ /sep/i){
                        $omonth = 9;
                }elsif($month =~ /oct/i){
                        $omonth = 10;
                }elsif($month =~ /nov/i){
                        $omonth = 11;
                }elsif($month =~ /dec/i){
                        $omonth = 12;
                }
        }
        return $omonth;
}

