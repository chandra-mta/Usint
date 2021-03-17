#!/opt/local/bin/perl

#################################################################################################################
#														#
#	send_tpoc_duty.perl: send out POC duty notification a day before the duty starts			#
#														#
#		author: t. isobe (tisobe@cfa.harvard.edu)							#
#														#
#		last update: Mar 27, 2013									#
#														#
#################################################################################################################

$temp_dir = '/data/mta4/www/CUS/Usint/Temp/';            #--- a temporary file is created in this directory

#
#---- set directory paths : updated to read from a file (02/25/2011)	this is user: cus version
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
#--- find today's date
#

($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = localtime(time);
$year = 1900 + $year;
$mon++;

#
#--- find tomorrow's y date
#

$tyday = $yday + 2;

#
#--- check whether tomorrow is the next yeaer or not; if so, modify date
#

$chk   = 4.0 * int(0.25 * $year);

$base = 365;
if($chk == $year){
	$base = 366;
}

if($tyday > $base){
	$year++;
	$tyday = 1;
}


#
#--- read schedule list
#

open(FH, "$data_dir/schedule");

$new = 0;
OUTER:
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	$smon  = $atemp[1];
	$sday  = $atemp[2];
	$syear = $atemp[3];
	$syday = find_ydate($syear, $smon, $sday);
	if($syday == $tyday && $syear == $year){
		$new = 1;
		$person = $atemp[0];
		last OUTER;
	}
}
close(FH);

#
#--- if a new schedule starts tomorrow, send out email to the poc
#

if($new > 0){

#
#--- read a list of too persons' information
#

	open(FH, "$data_dir/personal_list");

	OUTER:
	while(<FH>){
		chomp $_;
		@atemp = split(/<>/, $_);
		if($person =~ /$atemp[0]/i){
			$too_poc = $atemp[4];			#--- email address
			last OUTER;
		}
	}
	close(FH);

	open(OUT2, "> $temp_dir/temp_email2");
	print OUT2 "Hi\n";
	print OUT2 "According to TOO-POC schedule, ";
	print OUT2 "your TOO point of contact duty is starting tomorrow at mid-night (0:00 hr, local time). Pleaes check the schedule: \n\n";
	print OUT2 "\thttps://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html\n\n";
	print OUT2 "If there are any schedule conflicts or schedule mistakes, please contact ";
	print OUT2 "Scott Wolk (swolk\@head.cfa.harvard.edu) as soon as possible.\n";
	close(OUT2);

        system("cat $temp_dir/temp_email2 | mailx -s\"Subject:  TOO Point of Contact Duty Notification:$too_poc\n\" isobe\@head.cfa.harvard.edu");

        system("cat $temp_dir/temp_email2 | mailx -s\"Subject:  TOO Point of Contact Duty Notification\n\" -ccus\@head.cfa.harvard.edu $too_poc");
	system("rm $temp_dir/temp_email2");
}
	

##################################################
### find_ydate: change month/day to y-date     ###
##################################################

sub find_ydate {

##################################################
#       Input   $tyear: year
#               $tmonth: month
#               $tday:   day of the month
#
#       Output  $ydate: day from Jan 1<--- returned
##################################################

        my($tyear, $tmonth, $tday, $ydate, $chk);
        ($tyear, $tmonth, $tday) = @_;

        if($tmonth == 1){
                $ydate = $tday;
        }elsif($tmonth == 2){
                $ydate = $tday + 31;
        }elsif($tmonth == 3){
                $ydate = $tday + 59;
        }elsif($tmonth == 4){
                $ydate = $tday + 90;
        }elsif($tmonth == 5){
                $ydate = $tday + 120;
        }elsif($tmonth == 6){
                $ydate = $tday + 151;
        }elsif($tmonth == 7){
                $ydate = $tday + 181;
        }elsif($tmonth == 8){
                $ydate = $tday + 212;
        }elsif($tmonth == 9){
                $ydate = $tday + 243;
        }elsif($tmonth == 10){
                $ydate = $tday + 273;
        }elsif($tmonth == 11){
                $ydate = $tday + 304;
        }elsif($tmonth == 12 ){
                $ydate = $tday + 334;
        }
        $chk = 4 * int (0.25 * $tyear);
        if($chk == $tyear && $tmonth > 2){
                $ydate++;
        }
        return $ydate;
}

