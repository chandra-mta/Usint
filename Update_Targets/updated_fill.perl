#!/usr/bin/perl

#################################################################################
#                                       										#
#	updated_fill.perl: fill updated.cgi Save_month_html/*                       #
#										                                        #
#		modified by T. Isobe (tisobe@cfa.harvard.edu)			                #
#										                                        #
#	    last update: Mar 19, 2020					                            #
#										                                        #
#										                                        #
#################################################################################

###################################################################
#
#---- set directory paths 
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
        }elsif($atemp[0]  =~ /cus_dir/){
                $cus_dir  = $atemp[1];
        }
}
close(IN);

$ocat_dir = $real_dir;

$html = 'https://cxc.cfa.harvard.edu/mta/CUS/Usint/';

###################################################################

#
#--- check current time, date
#
($t0, $t1, $t2, $t3, $t4, $t5, $t6, $t7, $t8) = localtime(time);
$month = $t4 + 1;
$day   = $t3;
$year  = $t5 + 1900;

$start_year = $year - 3:
		
#
#--- extract data we need from updates_table.list
#
get_data();

$idiff = $year - $start_year + 1;

for($iyear = $start_year; $iyear < $year + 1; $iyear++) {
	for($dmon = 1; $dmon < 13; $dmon++){
		$amon = $dmon;
		if($dmon < 10){
			$amon = '0'."$dmon";
		}
#
#--- change month in digit to letter
#
		mon_digit_lett();

		$file_name = "$lmon".'_'."$iyear".'.html';

		for($i = 0; $i < $idiff; $i++){
#
#--- print out the past data
#
			if($i < $idiff -1){
				$name      = "$amon".'_'."$iyear";
				@data_list = @{$name};

				print_month_html();

			}elsif($i >= $idiff -1){
				if($dmon > $month){
#--- do nothing here.	
				}else{
#
#--- update the current data
#
					$name = "$amon".'_'."$iyear";
					if($dmon == $month && $iyear == $year){
						@data_list = reverse(@{$name});
					}else{
						$name      = "$amon".'_'."$iyear";
						@data_list = @{$name};
					}

					print_month_html();
				}
			}
		}
	}
}

###############################################################################
### check_last_update: check whether the data is updated in the last 24 hrs ###
###############################################################################

sub check_last_update{
	($chsec, $chmin, $chhour, $chmday, $chmon, $chyear, $chwday, $chyday, $chisdst)= localtime(time);
	
	$tyear = $chyear + 1900;
	$tyday = $chyday + 1;
	$tsecd = 3600 * $chhour + 60 * $chmin + $chsec;

	conv_time_1998();

	$update_date = $t1998;

	open(FH, "$cus_dir/Save_month_html/last_update");
	
	while(<FH>){
        	chomp $_;
        	$last_update = $_;
	}
	close(FH);
	$must_update = 0;
	$time_limit  = $last_update + 86400;     #---  update if it passed more than 24 hrs

	if($update_date > $time_limit){
        	open(OUT,">$cus_dir/Save_month_html/last_update");
        	print OUT "$update_date\n";
        	close(OUT);
        	$must_update++;
	}
}

####################################################################
### cov_time_1998: change date (yyyy:ddd) to sec from 01/01/1998  ##
####################################################################

sub conv_time_1998 {

        $totyday = 365*($tyear - 1998);
        if($tyear > 2000){
                $totyday++;
        }
        if($tyear > 2004){
                $totyday++;
        }
        if($tyear > 2008){
                $totyday++;
        }
        if($tyear > 2012){
                $totyday++;
        }
        if($tyear > 2016){
                $totyday++;
        }
        if($tyear > 2020){
                $totyday++;
        }
        if($tyear > 2024){
                $totyday++;
        }

        $ttday = $totyday + $tyday;
        $t1998 = 86400 * $ttday + $tsecd;
}

###############################################################################
### mon_digit_lett: change month in digit into month in letters             ###
###############################################################################

sub mon_digit_lett {
	if($dmon == 1){
		$lmon = 'Jan';
	}elsif($dmon == 2){
		$lmon = 'Feb';
	}elsif($dmon == 3){
		$lmon = 'Mar';
	}elsif($dmon == 4){
		$lmon = 'Apr';
	}elsif($dmon == 5){
		$lmon = 'May';
	}elsif($dmon == 6){
		$lmon = 'Jun';
	}elsif($dmon == 7){
		$lmon = 'Jul';
	}elsif($dmon == 8){
		$lmon = 'Aug';
	}elsif($dmon == 9){
		$lmon = 'Sep';
	}elsif($dmon == 10){
		$lmon = 'Oct';
	}elsif($dmon == 11){
		$lmon = 'Nov';
	}elsif($dmon == 12){
		$lmon = 'Dec';
	}
}
	
###############################################################################
### get_data: extract data from updates_table.list                          ###
###############################################################################

sub get_data {
	open (FILE, "<$ocat_dir/updates_table.list");
	@revisions = <FILE>;
	close (FILE);

	@list_of_entry = ();
	foreach $line (@revisions){
    		chop $line;
    		@values         = split (/\t/, $line);
		$dutysci_status = $values[4];
		@atemp          = split(/ /,  $dutysci_status);
		@vdate          = split(/\//, $atemp[1]);
		$vdate[0];
		if($vdate[2] == 99){
			$vdate[2] = 1999;
		}else{
			$vdate[2] += 2000;
		}
		$name = "$vdate[0]".'_'."$vdate[2]";

		push(@{$name},       $line);
		push(@list_of_entry, $name);
	}

#
#--- remove duplicate
#
	$first = shift(@list_of_entry);
	@test = ("$first");
	OUTER:
	foreach $ent (@list_of_entry){
		foreach $comp (@test){
			if($ent eq $comp){
				next OUTER;
			}
		}
		push(@test, $ent);
	}

	foreach $ent (@test){
		@test_data = @{$ent};

#
#--- sort the data by date
#
		sort_line_by_date();

		@{$ent} = @new_list;
	}
}

###############################################################################
### print_month_html: print indivisual month output html page               ###
###############################################################################

sub print_month_html {
		
	open(OUT, ">$cus_dir/Save_month_html/$file_name");

	print OUT "<!DOCTYPE html>\n";
	print OUT "<html>\n";
	print OUT "<head>\n";
	print OUT "<title>Updated Target List  $lmon/$iyear</title>\n";
	print OUT "<meta http-equiv='Content-Type' content='text/html; charset=utf-8' />\n";
	print OUT "<style  type='text/css'>\n";
	print OUT "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}\n";
	print OUT "a:link {color:blue;}\n";
	print OUT "a:visited {color:teal;}\n";
	print OUT "</style>\n";
	print OUT "</head>\n";

	print OUT "<body style='color:#000000;background-color:#FFFFE0'>\n";

	
	print OUT "<h1>Updated Targets List</h1>";
	print OUT "\n";
	print OUT "<p>This list contains all targets which have been verified as updated in $lmon $iyear.</p>";
	print OUT "\n";
	print OUT "<strong>Back to:</strong> \n";
	print OUT "<ul>\n";
	print OUT "<li><a href=\"https://cxc.cfa.harvard.edu/mta/CUS/Usint/search.html\"><strong>Chandra Uplink Support Observation Search Form</strong></a></li>";
	print OUT "\n";
	print OUT "<li><a href=\"https://cxc.cfa.harvard.edu/mta/CUS/\"><strong>Chandra Uplink Support Organizational Page</strong></a></li>";
	print OUT "\n";
	print OUT "<li><a href=\"https://cxc.cfa.harvard.edu/mta/CUS/Usint/updated.cgi\"><strong>Back to Updated Targets List top page</strong></a></li>\n";
	print OUT "</ul>\n";
	print OUT "\n";
	
	print OUT "<table border=1>";
	print OUT "\n";
	print OUT "<tr><th>OBSID.revision</th><th>general obscat edits by</th><th>ACIS obscat edits by</th><th>SI MODE edits by</th><th>Verified by</th></tr>";
	print OUT "\n";
	
	foreach $line (@data_list){
    		@values         = split ("\t", $line);
    		$obsrev         = $values[0];
    		$general_status = $values[1];
    		$acis_status    = $values[2];
    		$si_mode_status = $values[3];
    		$dutysci_status = $values[4];
    		$seqnum         = $values[5];
    		$user           = $values[6];

	    	($na0, $na1, $na2, $na3, $na4, $na5, $na6, $na7, $na8, $mtime, $na10, $na11, $na12) = stat "/data/mta4/CUS/www/Usint/ocat/updates/$obsrev";
    		($t0, $t1, $t2, $t3, $t4, $t5, $t6, $t7, $t8) = localtime($mtime);
    		$mmonth = $t4 + 1;
    		$mday   = $t3;
    		$myear  = $t5 + 1900;
    		$ftime  = "$mmonth/$mday/$myear";

    		unless ($dutysci_status =~/NA/){
			print OUT "<tr>";
			print OUT "\n";
			print OUT "<td><a href=\"https://icxc.harvard.edu/uspp/updates/$obsrev\">$obsrev</a><br />$seqnum<br />$ftime<br />$user</td>";
			print OUT "\n";
			print OUT "<td>$general_status</td><td>$acis_status</td><td>$si_mode_status</td><td style='color=#005C00'>$dutysci_status</td></tr>";
			print OUT "\n";
		
    		}
	}
	print OUT "</table>";
	print OUT "\n";

	print OUT "<p style='padding-top:20px;padding-bottom:20px'><strong><a href=\"https://cxc.cfa.harvard.edu/mta/CUS/Usint/updated.cgi\">Back to Updated Targets List top page</a></strong>";
	print OUT "\n";

	print OUT "</body></html>";
	print OUT "\n";
	close(OUT);

#	system("chmod 775      $cus_dir/Save_month_html/$file_name");
#	system("chown mta      $cus_dir/Save_month_html/$file_name");
#	system("chgrp mtagroup $cus_dir/Save_month_html/$file_name");
}


#############################################################################
### sort_line_by_date: sort the data by date for the specific data format ###
#############################################################################

sub sort_line_by_date {
	$count     = 0;
	@comp_list = ();
	foreach $line (@test_data) {
		@values         = split (/\t/, $line);
		$dutysci_status = $values[4];
		@atemp          = split(/ /,$dutysci_status);
		@vdate          = split(/\//,$atemp[1]);
		$xname          = "$vdate[1]".'_'."$count";

		%{$xname} = (
				line => ["$line"]
			    );
		$count++;
		push(@comp_list, $xname);
	}
	@comp_list = sort{$a <=> $b} @comp_list;

	@new_list = ();
	foreach $xent (@comp_list) {
		push(@new_list, ${$xent}{line}[0]);
	}
}
		
