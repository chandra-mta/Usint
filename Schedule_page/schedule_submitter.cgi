#!/usr/bin/perl
use CGI qw/:standard :netscape /;

#####################################################################################
#														                            #
#	schedule_submitter.cgi: create TOO Point of Contact Update Input Table		    #
#														                            #
#		author: t. isobe (tisobe@cfa.harvard.edu)							        #
#														                            #
#		last update: Sep 21, 2021									                #
#														                            #
#####################################################################################

#
#---- set directory paths : updated to read from a file (02/25/2011)
#


#open(IN, '/data/udoc1/ocat/Info_save/dir_list');
#open(IN, '/data/udoc1/ocat/Test/Info_save/dir_list');
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
#--- read who is the contact currently listed as contact persons
#

@person = (' ');
open(FH, "$data_dir/personal_list");

while(<FH>){
	chomp $_;
	@atemp = split(/<>/, $_);
	push(@person, $atemp[0]);
}
close(FH);

#
#--- for record keeping convenience, add a person to be determined.
#

push(@person, 'TBD');

#
#--- find today's date/time
#

$tdelta = 883699179; 		#--- difference between 1970 base and 1998 base


$now = time;
($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($now);

$tmonth = $umon + 1;
$tday   = $umday;
$tyear  = $uyear + 1900;
$tftime = "$tmonth/$tday/$tyear";
$tinsec = $now - $tdelta; 

#
#--- last month
#

$month_ago = (time - 2592000);
($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($month_ago);

$lmonth = $umon + 1;
$lday   = $umday;
$lyear  = $uyear + 1900;
$lftime = "$lmonth/$lday/$lyear";
$linsec = $month_ago - $tdelta;

#
#--- here we start html/cgi
#

print header(-type => 'text/html');
print start_html(-bgcolor=>"white", -title=>'Schedule Submission Form');

print  '<body style="background-color:#FAEBD7; font-family:serif, sans-serif;font-size:12pt; color:black;" >',"\n";

print  "<h2 style='background-color:blue; color:#FAEBD7; margin-right:4em;'>Schedule Submitter</h2>\n";


print '<div style="text-align:right;padding-right:8em">';
print '<a href="https://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html">';
print '<strong><em style="background-color:red;color:yellow;">Back to USINT TOO Point of Contact</em></strong></a>',"\n";
print '</div>';

print "<p>This website is out of date and will cause issues if used. Please use: <a href='https://cxc.cfa.harvard.edu/wsgi/cus/usint/scheduler/index'>https://cxc.cfa.harvard.edu/wsgi/cus/usint/scheduler/index</a></p>";

print  "<p><strong>Periods which do not start on Monday or end on Sunday are marked by <em style='color:#87CEEB;background-color:#87CEEB'>blue</em>.</strong></p>\n";

print "<p style='padding-right:10em'><strong>If there is a cell marked with ","\n";
print "<em style='color:red;background-color:red'>red</em>, ","\n";
print "there is a gap between the ending date and the next starting date. Please correct the problem ";
print "(check not only the date, but the month and the year).</strong></p>","\n";

print "<p style='padding-right:10em'><strong>If you need to add an extra raw, first unlock a raw which is located ";
print "one above where you want to add the new raw. After the page is reloaded, click 'Add' button. Similarly, if ";
print "you want to delete a raw, first unlock the raw, and then, after the page is reloaded, click 'Delete' button.</p>";

print "<p style='padding-right:10em'><strong>Before updating the entry, please sign in your user name in the 'Assigned By' ";
print "column so that other people can identify who modified the entry later.</p>";

print "<p style='padding-right:10em'><strong><em style='color:orange'>IMPORTANT</em>: After click 'Update', or 'Unlock', ";
print "please do not click any other buttons until the page is completely reloaded.</strong></p>"; 

print '<a href="https://cxc.cfa.harvard.edu/cus/PeoplePhones.txt"><strong><em style="background-color:red;color:yellow;">POC phone numbers</em></strong></a>';
print  '<br /><br />',"\n";

print '<br />',"\n";

#
#--- form loop starts here!
#

print start_form();

@unsigned_warning  = ();
$unsigned_cnt      = 0;

#
#--- if the update is submitted, update the schedule database
#

$test    = param('test');		#--- this tells whether data are already read in or not. (entire schedule data)
$ent_cnt = param('total');		#--- total # of entires

if($test eq ''){
	$upate = '';
}else{
	$update    = param('submit');
}


if($update =~ /Submit Updates/i || $update =~ /Update/i){
#
#--- check whether someone just upated the schedule or not, if so, tell the user and load the new schedule
#
	$test2 = `cat $data_dir/schedule`;
	$test  =~s/\s+//g;
	$test2 =~s/\s+//g;
	if($test eq $test2){

		update_database();	#--- sub to update schedule database
	}else{
		print "<em style='font-size:100%;color:red; padding-right:8em'>";
		print "Sorry, but someone just updated the schedule while you are editting.";
		print " Please check the schedule below (automatically updated), and modify it if needed. ";
		print "If you just reloaded the page using the browser button, please ignore this message.";
		print "<br />";
		print "</em><br />";
	}

}else{
#
#--- if a user unlocked the previously entired data, keep the record about it
#
	@unlock_list = ();
	@affected    = ();
	$uchk        = 0;
	for($j = 0; $j < $ent_cnt; $j++){
		$name   = 'unlock'."$j";
		$unlock = param("$name");
		if($unlock eq 'Unlock'){
			push(@unlock_list, $j);
			$key  = 'name'."$j";
			$user =  param("$key");
			push(@affected, $user);
			$uchk++;
	
			$nfield = 'unlock'."$j";
			print "<input type='hidden' name='$nfield' value='Unlock' />";
		}
	}
#
#--- if a user wants to add another raw under the indicated one, do so
#
	for($j = 0; $j < $ent_cnt; $j++){
		$name   = 'add'."$j";
		$addraw = param("$name");
		if($addraw eq 'Add'){

			add_line_on_database();

		}
	}
#
#--- if a user wants to delete a raw, do so
#
	for($j = 0; $j < $ent_cnt; $j++){
		$name   = 'cut'."$j";
		$cutraw = param("$name");
		if($cutraw eq 'Delete'){

			cut_line_on_database();

		}
	}
}

if($unsigned_cnt > 0){
	print "<em style='font-size:100%;color:red; padding-right:8em'>";
	print "You did not sign off the entry (entries) you assigned, and the changes were not made. ";
	print "Please check the raw makred by a red frame, and make the chnage again.";
	print " Then sign the 'Assign By' column before clicking a 'Update' button.</p> ";
}


#
#--- read the already filled date
#

print '<input type="submit" name="submit" value="Submit Updates">',"\n";
print '<br />',"\n";
print '<br />',"\n";
print '<table border=1 cellpadding=5 cellpsapcing=5>',"\n";
print '<tr><th>Contact</th><th colspan=3>Start Date</th><th colspan=3>Finish Date</th><th>Assigned By</th><th colspan=2>Status</th></tr>',"\n";
print '<tr><th>&#160  </th><th>Month</th><th>Day</th><th>Year</th><th>Month</th><th>Day</th><th>Year</th><th>&#160</th><th colspan=2>&#160</th></tr>',"\n";

$total   = 0;		#---- this is a counter of entries

#
#--- just in a case the database was erased in some reason, put back the backup version to the current location.
#

$test = `cat $data_dir/schedule`;
$temp = $test;
$temp =~ s/\s+//g;
if($temp eq ''){
	system("cp $data_dir/schedule~ $data_dir/schedule");
	$test = `cat $data_dir/schedule`;
}

print  "<input type='hidden' name='test' value='$test' />","\n";
open(FH, "$data_dir/schedule");

$h_cnt = 0;     #--- counting how many record will not shown from the schedule.

OUTER:
while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	$total++;

#
#--- begining of the period
#
	$ydate    = find_ydate($atemp[3], $atemp[1], $atemp[2]);
	$ts_insec = cnv_time_to_t1998($atemp[3], $ydate, 0, 0, 0 );

#
#--- if there is the gap between the last period and the this period, warn the fact
#
	$s_warning = 0;
	if($tl_insec =~ /\d/){
		$diff =  $ts_insec - $tl_insec;
		if($diff > 86400){
			$s_warning = 2;
		}
	}

#
#--- ending of the period
#

	$ydate    = find_ydate($atemp[6], $atemp[4], $atemp[5]);
	$tl_insec = cnv_time_to_t1998($atemp[6], $ydate, 0 , 0 , 0);

#
#--- check whether the date starting is monday and the date ending is sunday. if not put warning.
#
	$wtest = $ts_insec + $tdelta;
	($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($wtest);
	if($uwday != 1){
		if($s_warning == 0){
			$s_warning = 1;
		}
	}
	$wtest = $tl_insec + $tdelta;
	($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($wtest);
	$e_warning = 0;
	if($uwday != 0){
		$e_warning = 1;
	}

#
#--- if the date is more than a month ago, do not print on the table
#

	if($ts_insec < $linsec){
		$nfield = 'name'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[0]' />","\n";

		$nfield = 'smonth'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[1]' />","\n";
		$nfield = 'sday'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[2]' />","\n";
		$nfield = 'syear'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[3]' />","\n";

		$nfield = 'emonth'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[4]' />","\n";
		$nfield = 'eday'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[5]' />","\n";
		$nfield = 'eyear'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[6]' />","\n";
		$nfield = 'signoff'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[7]' />","\n";
		$h_cnt++;
		next OUTER;
	}

#
#--- if the date is before the current period, make it none editable
#

	if($ts_insec < $tinsec){
		print "<tr style='background-color:#B8860B'><td>$atemp[0]</td>\n";
		$lmonth = change_month_format($atemp[1]);
		print "<td>$lmonth</td>\n";
		print "<td>$atemp[2]</td>\n";
		print "<td>$atemp[3]</td>\n";
		$lmonth = change_month_format($atemp[4]);
		print "<td>$lmonth</td>\n";
		print "<td>$atemp[5]</td>\n";
		print "<td>$atemp[6]</td>\n";
		print "<td style='text-align:center'>$atemp[7]</td>\n";
		print "<td style='text-align:center'>Closed</td><td>&#160</td></tr>\n";
		
		$nfield = 'name'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[0]' />","\n";

		$nfield = 'smonth'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[1]' />","\n";
		$nfield = 'sday'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[2]' />","\n";
		$nfield = 'syear'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[3]' />","\n";

		$nfield = 'emonth'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[4]' />","\n";
		$nfield = 'eday'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[5]' />","\n";
		$nfield = 'eyear'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[6]' />","\n";
		$nfield = 'signoff'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[7]' />","\n";
		next OUTER;
	}

#
#--- if the someone already signed up for the period, lock it.
#
	$chk = 0;
	TOUTER:
	foreach $test (@unlock_list){
		if($test == $total){
			$chk = 1;
			last TOUTER;
		}
	}

	$warn1 = 0;
	UOUT:
	for($ic = 0; $ic < $unsigned_cnt; $ic++){ 
		if($unsigned_warning[$ic] == $total){
			$warn1++;
			last UOUT;
		}
	}

	if($s_warning != 2 && $chk == 0 && $atemp[0] =~ /\w/ && $warn1 == 0 && $atemp[0] !~ /TBD/i){
		if($warn1 == 0){
			print "<tr style='background-color:#DEB887'><td>$atemp[0]</td>\n";
		}else{
			print "<tr style='background-color:red'><td>$atemp[0]</td>\n";
		}

		$lmonth = change_month_format($atemp[1]);
		print "<td>$lmonth</td>\n";

		if($s_warning == 1){
			print "<td style='background-color:#87CEEB'>$atemp[2]</td>\n";
		}elsif($s_warning == 2){
			print "<td style='background-color:red'>$atemp[2]</td>\n";
		}else{
			print "<td>$atemp[2]</td>\n";
		}

		print "<td>$atemp[3]</td>\n";
		$lmonth = change_month_format($atemp[4]);
		print "<td>$lmonth</td>\n";

		if($e_warning == 1){
			print "<td style='background-color:#87CEEB'>$atemp[5]</td>\n";
		}else{
			print "<td>$atemp[5]</td>\n";
		}

		print "<td>$atemp[6]</td>\n";
		print "<td style='text-align:center'>$atemp[7]</td>\n";

		$nfield = 'unlock'."$total";
		print "<td><input type='submit' name='$nfield' value='Unlock' /></td><td>&#160</td></tr>\n";
		

		$nfield = 'name'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[0]' />","\n";
		$nfield = 'smonth'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[1]' />","\n";
		$nfield = 'sday'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[2]' />","\n";
		$nfield = 'syear'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[3]' />","\n";

		$nfield = 'emonth'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[4]' />","\n";
		$nfield = 'eday'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[5]' />","\n";
		$nfield = 'eyear'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[6]' />","\n";
		$nfield = 'signoff'."$total";
		print  "<input type='hidden' name='$nfield' value='$atemp[7]' />","\n";
		next OUTER;
	}

#
#--- contact
#
	if($warn1 == 0){
		print "<tr>\n";
	}else{
		print "<tr style='background-color:red'>\n";
	}

	$nfield = 'name'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	foreach $ent (@person){
		if($ent =~ /$atemp[0]/ && $atemp[0] =~ /\w/){
			print  "<option selected>$ent</option>","\n";
		}elsif($atemp[0] !~ /\w/ && $ent !~ /\w/){
			print "<option selected></option>","\n";
		}else{
			print  "<option> $ent</option>","\n";
		}
	}
	print  '</select>',"\n";
	print  '</td>',"\n";

#
#--- start month
#
	$nfield = 'smonth'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	if($atemp[1] == 1){
		print  '<option selected> January</option>',"\n";
	}else{
		print  '<option> January</option>',"\n";
	}
	if($atemp[1] == 2){
		print  '<option selected> February</option>',"\n";
	}else{
		print  '<option> February</option>',"\n";
	}
	if($atemp[1] == 3){
		print  '<option selected> March</option>',"\n";
	}else{
		print  '<option> March</option>',"\n";
	}
	if($atemp[1] == 4){
		print  '<option selected> April</option>',"\n";
	}else{
		print  '<option> April</option>',"\n";
	}
	if($atemp[1] == 5){
		print  '<option selected> May</option>',"\n";
	}else{
		print  '<option> May</option>',"\n";
	}
	if($atemp[1] == 6){
		print  '<option selected> June</option>',"\n";
	}else{
		print  '<option> June</option>',"\n";
	}
	if($atemp[1] == 7){
		print  '<option selected> July</option>',"\n";
	}else{
		print  '<option> July</option>',"\n";
	}
	if($atemp[1] == 8){
		print  '<option selected> August</option>',"\n";
	}else{
		print  '<option> August</option>',"\n";
	}
	if($atemp[1] == 9){
		print  '<option selected> September</option>',"\n";
	}else{
		print  '<option> September</option>',"\n";
	}
	if($atemp[1] == 10){
		print  '<option selected> October</option>',"\n";
	}else{
		print  '<option> October</option>',"\n";
	}
	if($atemp[1] == 11){
		print  '<option selected> November</option>',"\n";
	}else{
		print  '<option> November</option>',"\n";
	}
	if($atemp[1] == 12){
		print  '<option selected> December</option>',"\n";
	}else{
		print  '<option> December</option>',"\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";
#
#--- start day
#
	$nfield = 'sday'."$total";

	if($s_warning == 1){
		print  "<td style='background-color:#87CEEB'><input type='text' name='$nfield' value='$atemp[2]' size=5 /></td>","\n";
	}elsif($s_warning == 2){
		print  "<td style='background-color:red'><input type='text' name='$nfield' value='$atemp[2]' size=5 /></td>","\n";
	}else{
		print  "<td><input type='text' name='$nfield' value='$atemp[2]' size=5 /></td>","\n";
	}
#
#--- start year
#
	$nfield = 'syear'."$total";

	print  '<td>';
	print  "<select name='$nfield'>","\n";
#	if($atemp[3] == 2009){
#		print  '<option selected> 2009</option>',"\n";
#	}else{
#		print  '<option> 2009</option>',"\n";
#	}
#	if($atemp[3] == 2010){
#		print  '<option selected> 2010</option>',"\n";
#	}else{
#		print  '<option> 2010</option>',"\n";
#	}
#	if($atemp[3] == 2011){
#		print  '<option selected> 2011</option>',"\n";
#	}else{
#		print  '<option> 2011</option>',"\n";
#	}
#	if($atemp[3] == 2012){
#		print  '<option selected> 2012</option>',"\n";
#	}else{
#		print  '<option> 2012</option>',"\n";
#	}
#	if($atemp[3] == 2013){
#		print  '<option selected> 2013</option>',"\n";
#	}else{
#		print  '<option> 2013</option>',"\n";
#	}
#	if($atemp[3] == 2014){
#		print  '<option selected> 2014</option>',"\n";
#	}else{
#		print  '<option> 2014</option>',"\n";
#	}
#	if($atemp[3] == 2015){
#		print  '<option selected> 2015</option>',"\n";
#	}else{
#		print  '<option> 2015</option>',"\n";
#	}
#	if($atemp[3] == 2016){
#		print  '<option selected> 2016</option>',"\n";
#	}else{
#		print  '<option> 2016</option>',"\n";
#	}
#	if($atemp[3] == 2017){
#		print  '<option selected> 2017</option>',"\n";
#	}else{
#		print  '<option> 2017</option>',"\n";
#	}
	if($atemp[3] == 2018){
		print  '<option selected> 2018</option>',"\n";
	}else{
		print  '<option> 2018</option>',"\n";
	}
	if($atemp[3] == 2019){
		print  '<option selected> 2019</option>',"\n";
	}else{
		print  '<option> 2019</option>',"\n";
	}
	if($atemp[3] == 2020){
		print  '<option selected> 2020</option>',"\n";
	}else{
		print  '<option> 2020</option>',"\n";
	}
	if($atemp[3] == 2021){
		print  '<option selected> 2021</option>',"\n";
	}else{
		print  '<option> 2021</option>',"\n";
	}
	if($atemp[3] == 2022){
		print  '<option selected> 2022</option>',"\n";
	}else{
		print  '<option> 2022</option>',"\n";
	}
	if($atemp[3] == 2023){
		print  '<option selected> 2023</option>',"\n";
	}else{
		print  '<option> 2023</option>',"\n";
	}
	if($atemp[3] == 2024){
		print  '<option selected> 2024</option>',"\n";
	}else{
		print  '<option> 2024</option>',"\n";
	}
	if($atemp[3] == 2025){
		print  '<option selected> 2025</option>',"\n";
	}else{
		print  '<option> 2025</option>',"\n";
	}
	print  '</select>';
	print  '</td>';
	
#
#--- end month
#
	$nfield = 'emonth'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	if($atemp[4] == 1){
		print  '<option selected> January</option>',"\n";
	}else{
		print  '<option> January</option>',"\n";
	}
	if($atemp[4] == 2){
		print  '<option selected> February</option>',"\n";
	}else{
		print  '<option> February</option>',"\n";
	}
	if($atemp[4] == 3){
		print  '<option selected> March</option>',"\n";
	}else{
		print  '<option> March</option>',"\n";
	}
	if($atemp[4] == 4){
		print  '<option selected> April</option>',"\n";
	}else{
		print  '<option> April</option>',"\n";
	}
	if($atemp[4] == 5){
		print  '<option selected> May</option>',"\n";
	}else{
		print  '<option> May</option>',"\n";
	}
	if($atemp[4] == 6){
		print  '<option selected> June</option>',"\n";
	}else{
		print  '<option> June</option>',"\n";
	}
	if($atemp[4] == 7){
		print  '<option selected> July</option>',"\n";
	}else{
		print  '<option> July</option>',"\n";
	}
	if($atemp[4] == 8){
		print  '<option selected> August</option>',"\n";
	}else{
		print  '<option> August</option>',"\n";
	}
	if($atemp[4] == 9){
		print  '<option selected> September</option>',"\n";
	}else{
		print  '<option> September</option>',"\n";
	}
	if($atemp[4] == 10){
		print  '<option selected> October</option>',"\n";
	}else{
		print  '<option> October</option>',"\n";
	}
	if($atemp[4] == 11){
		print  '<option selected> November</option>',"\n";
	}else{
		print  '<option> November</option>',"\n";
	}
	if($atemp[4] == 12){
		print  '<option selected> December</option>',"\n";
	}else{
		print  '<option> December</option>',"\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";
#
#--- end day
#
	$nfield = 'eday'."$total","\n";

	if($e_warning == 1){
		print  "<td style='background-color:#87CEEB'><input type='text' name='$nfield' value='$atemp[5]' size =5 /></td>","\n";
	}else{
		print  "<td><input type='text' name='$nfield' value='$atemp[5]' size =5 /></td>","\n";
	}
#
#--- end year
#
	$nfield = 'eyear'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
#	if($atemp[6] == 2009){
#		print  '<option selected> 2009</option>',"\n";
#	}else{
#		print  '<option> 2009</option>',"\n";
#	}
#	if($atemp[6] == 2010){
#		print  '<option selected> 2010</option>',"\n";
#	}else{
#		print  '<option> 2010</option>',"\n";
#	}
#	if($atemp[6] == 2011){
#		print  '<option selected> 2011</option>',"\n";
#	}else{
#		print  '<option> 2011</option>',"\n";
#	}
#	if($atemp[6] == 2012){
#		print  '<option selected> 2012</option>',"\n";
#	}else{
#		print  '<option> 2012</option>',"\n";
#	}
#	if($atemp[6] == 2013){
#		print  '<option selected> 2013</option>',"\n";
#	}else{
#		print  '<option> 2013</option>',"\n";
#	}
#	if($atemp[6] == 2014){
#		print  '<option selected> 2014</option>',"\n";
#	}else{
#		print  '<option> 2014</option>',"\n";
#	}
#	if($atemp[6] == 2015){
#		print  '<option selected> 2015</option>',"\n";
#	}else{
#		print  '<option> 2015</option>',"\n";
#	}
#	if($atemp[6] == 2016){
#		print  '<option selected> 2016</option>',"\n";
#	}else{
#		print  '<option> 2016</option>',"\n";
#	}
#	if($atemp[6] == 2017){
#		print  '<option selected> 2017</option>',"\n";
#	}else{
#		print  '<option> 2017</option>',"\n";
#	}
	if($atemp[6] == 2018){
		print  '<option selected> 2018</option>',"\n";
	}else{
		print  '<option> 2018</option>',"\n";
	}
	if($atemp[6] == 2019){
		print  '<option selected> 2019</option>',"\n";
	}else{
		print  '<option> 2019</option>',"\n";
	}
	if($atemp[6] == 2020){
		print  '<option selected> 2020</option>',"\n";
	}else{
		print  '<option> 2020</option>',"\n";
	}
	if($atemp[6] == 2021){
		print  '<option selected> 2021</option>',"\n";
	}else{
		print  '<option> 2021</option>',"\n";
	}
	if($atemp[6] == 2022){
		print  '<option selected> 2022</option>',"\n";
	}else{
		print  '<option> 2022</option>',"\n";
	}
	if($atemp[6] == 2023){
		print  '<option selected> 2023</option>',"\n";
	}else{
		print  '<option> 2023</option>',"\n";
	}
	if($atemp[6] == 2024){
		print  '<option selected> 2024</option>',"\n";
	}else{
		print  '<option> 2024</option>',"\n";
	}
	if($atemp[6] == 2025){
		print  '<option selected> 2025</option>',"\n";
	}else{
		print  '<option> 2025</option>',"\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";

	$nfield = 'signoff'."$total";
	print  "<td style='text-align:center'><input type='text' size='10' name='$nfield' value=' '></td>", "\n";
	print  '<td style="text-align:center"><input type="submit" name="submit" value="Update"></td>';
	$nfield = 'add'."$total";
	$nfield2= 'cut'."$total";
	print  "<td style='text-align:center'><input type='submit' name='$nfield' value='Add'>";
	print  "<input type='submit' name='$nfield2' value='Delete'></td>";

	print  '</tr>',"\n";


}
close(FH);
$total++;
 

#-------------------------------------


#
#--- now a blank part starts: first one is special, since it may not be correctly joined
#

$newstart = $tl_insec + 86400 + $tdelta;
($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($newstart);
$smonth = $umon + 1;
$sday   = $umday;
$syear  = $uyear + 1900;
$s_warning = 0;
if($uwday != 1){
	$s_warning = 1;
}

$newend = $tl_insec + 7 * 86400 + $tdelta;
($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($newend);

if($uwday != 0){
        if($uwday <= 4){
                $newend = $tl_insec + (7 - $uwday) * 86400 + $tdelta;
                ($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($newend);
        }else{
                $newend = $tl_insec + (14 - $uwday) * 86400 + $tdelta;
                ($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($newend);
        }
}

$emonth = $umon + 1;
$eday   = $umday;
$eyear  = $uyear + 1900;
$e_warning = 0;

if($uwday != 0){
	$e_warning = 1;
}
	
$warn1 = 0;
UOUT:
for($ic = 0; $ic < $unsigned_cnt; $ic++){ 
	if($unsigned_warning[$ic] == $total){
		$warn1++;
		last UOUT;
	}
}


#
#--- contact
#
	if($warn1 == 0){
		print "<tr>\n";
	}else{
		print "<tr style='background-color:red'>\n";
	}

	$nfield = 'name'."$total";
#	print  "<td><input type='text' name='$nfield' value='' /></td>","\n";


	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	print "<option selected></option>","\n";
	foreach $ent (@person){
		print  "<option> $ent</option>","\n";
	}
	print  '</select>',"\n";

#
#--- start month
#
	$nfield = 'smonth'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	if($smonth == 1){
		print  '<option selected> January</option>',"\n";
	}else{
		print  '<option> January</option>',"\n";
	}
	if($smonth == 2){
		print  '<option selected> February</option>',"\n";
	}else{
		print  '<option> February</option>',"\n";
	}
	if($smonth == 3){
		print  '<option selected> March</option>',"\n";
	}else{
		print  '<option> March</option>',"\n";
	}
	if($smonth == 4){
		print  '<option selected> April</option>',"\n";
	}else{
		print  '<option> April</option>',"\n";
	}
	if($smonth == 5){
		print  '<option selected> May</option>',"\n";
	}else{
		print  '<option> May</option>',"\n";
	}
	if($smonth == 6){
		print  '<option selected> June</option>',"\n";
	}else{
		print  '<option> June</option>',"\n";
	}
	if($smonth == 7){
		print  '<option selected> July</option>',"\n";
	}else{
		print  '<option> July</option>',"\n";
	}
	if($smonth == 8){
		print  '<option selected> August</option>',"\n";
	}else{
		print  '<option> August</option>',"\n";
	}
	if($smonth == 9){
		print  '<option selected> September</option>',"\n";
	}else{
		print  '<option> September</option>',"\n";
	}
	if($smonth == 10){
		print  '<option selected> October</option>',"\n";
	}else{
		print  '<option> October</option>',"\n";
	}
	if($smonth == 11){
		print  '<option selected> November</option>',"\n";
	}else{
		print  '<option> November</option>',"\n";
	}
	if($smonth == 12){
		print  '<option selected> December</option>',"\n";
	}else{
		print  '<option> December</option>',"\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";
#
#--- start day
#
	$nfield = 'sday'."$total";

	if($s_warning == 1){
		print  "<td style='background-color:#87CEEB'><input type='text' name='$nfield' value='$sday' size=5 /></td>","\n";
	}else{
		print  "<td><input type='text' name='$nfield' value='$sday' size=5 /></td>","\n";
	}
#
#--- start year
#
	$nfield = 'syear'."$total";

	print  '<td>';
	print  "<select name='$nfield'>","\n";
#	if($syear == 2009){
#		print  '<option selected> 2009</option>',"\n";
#	}else{
#		print  '<option> 2009</option>',"\n";
#	}
#	if($syear == 2010){
#		print  '<option selected> 2010</option>',"\n";
#	}else{
#		print  '<option> 2010</option>',"\n";
#	}
#	if($syear == 2011){
#		print  '<option selected> 2011</option>',"\n";
#	}else{
#		print  '<option> 2011</option>',"\n";
#	}
#	if($syear == 2012){
#		print  '<option selected> 2012</option>',"\n";
#	}else{
#		print  '<option> 2012</option>',"\n";
#	}
#	if($syear == 2013){
#		print  '<option selected> 2013</option>',"\n";
#	}else{
#		print  '<option> 2013</option>',"\n";
#	}
#	if($syear == 2014){
#		print  '<option selected> 2014</option>',"\n";
#	}else{
#		print  '<option> 2014</option>',"\n";
#	}
#	if($syear == 2015){
#		print  '<option selected> 2015</option>',"\n";
#	}else{
#		print  '<option> 2015</option>',"\n";
#	}
#	if($syear == 2016){
#		print  '<option selected> 2016</option>',"\n";
#	}else{
#		print  '<option> 2016</option>',"\n";
#	}
#	if($syear == 2017){
#		print  '<option selected> 2017</option>',"\n";
#	}else{
#		print  '<option> 2017</option>',"\n";
#	}
	if($syear == 2018){
		print  '<option selected> 2018</option>',"\n";
	}else{
		print  '<option> 2018</option>',"\n";
	}
	if($syear == 2019){
		print  '<option selected> 2019</option>',"\n";
	}else{
		print  '<option> 2019</option>',"\n";
	}
	if($syear == 2020){
		print  '<option selected> 2020</option>',"\n";
	}else{
		print  '<option> 2020</option>',"\n";
	}
	if($syear == 2021){
		print  '<option selected> 2021</option>',"\n";
	}else{
		print  '<option> 2021</option>',"\n";
	}
	if($syear == 2022){
		print  '<option selected> 2022</option>',"\n";
	}else{
		print  '<option> 2022</option>',"\n";
	}
	if($syear == 2023){
		print  '<option selected> 2023</option>',"\n";
	}else{
		print  '<option> 2023</option>',"\n";
	}
	if($syear == 2024){
		print  '<option selected> 2024</option>',"\n";
	}else{
		print  '<option> 2024</option>',"\n";
	}
	if($syear == 2025){
		print  '<option selected> 2025</option>',"\n";
	}else{
		print  '<option> 2025</option>',"\n";
	}
	print  '</select>';
	print  '</td>';
	
#
#--- end month
#
	$nfield = 'emonth'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	if($emonth == 1){
		print  '<option selected> January</option>',"\n";
	}else{
		print  '<option> January</option>',"\n";
	}
	if($emonth == 2){
		print  '<option selected> February</option>',"\n";
	}else{
		print  '<option> February</option>',"\n";
	}
	if($emonth == 3){
		print  '<option selected> March</option>',"\n";
	}else{
		print  '<option> March</option>',"\n";
	}
	if($emonth == 4){
		print  '<option selected> April</option>',"\n";
	}else{
		print  '<option> April</option>',"\n";
	}
	if($emonth == 5){
		print  '<option selected> May</option>',"\n";
	}else{
		print  '<option> May</option>',"\n";
	}
	if($emonth == 6){
		print  '<option selected> June</option>',"\n";
	}else{
		print  '<option> June</option>',"\n";
	}
	if($emonth == 7){
		print  '<option selected> July</option>',"\n";
	}else{
		print  '<option> July</option>',"\n";
	}
	if($emonth == 8){
		print  '<option selected> August</option>',"\n";
	}else{
		print  '<option> August</option>',"\n";
	}
	if($emonth == 9){
		print  '<option selected> September</option>',"\n";
	}else{
		print  '<option> September</option>',"\n";
	}
	if($emonth == 10){
		print  '<option selected> October</option>',"\n";
	}else{
		print  '<option> October</option>',"\n";
	}
	if($emonth == 11){
		print  '<option selected> November</option>',"\n";
	}else{
		print  '<option> November</option>',"\n";
	}
	if($emonth == 12){
		print  '<option selected> December</option>',"\n";
	}else{
		print  '<option> December</option>',"\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";
#
#--- end day
#
	$nfield = 'eday'."$total","\n";

	if($e_warning == 1){
		print  "<td style='background-color:#87CEEB'><input type='text' name='$nfield' value='$eday' size =5 /></td>","\n";
	}else{
		print  "<td><input type='text' name='$nfield' value='$eday' size =5 /></td>","\n";
	}
#
#--- end year
#
	$nfield = 'eyear'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
#	if($eyear == 2009){
#		print  '<option selected> 2009</option>',"\n";
#	}else{
#		print  '<option> 2009</option>',"\n";
#	}
#	if($eyear == 2010){
#		print  '<option selected> 2010</option>',"\n";
#	}else{
#		print  '<option> 2010</option>',"\n";
#	}
#	if($eyear == 2011){
#		print  '<option selected> 2011</option>',"\n";
#	}else{
#		print  '<option> 2011</option>',"\n";
#	}
#	if($eyear == 2012){
#		print  '<option selected> 2012</option>',"\n";
#	}else{
#		print  '<option> 2012</option>',"\n";
#	}
#	if($eyear == 2013){
#		print  '<option selected> 2013</option>',"\n";
#	}else{
#		print  '<option> 2013</option>',"\n";
#	}
#	if($eyear == 2014){
#		print  '<option selected> 2014</option>',"\n";
#	}else{
#		print  '<option> 2014</option>',"\n";
#	}
#	if($eyear == 2015){
#		print  '<option selected> 2015</option>',"\n";
#	}else{
#		print  '<option> 2015</option>',"\n";
#	}
#	if($eyear == 2016){
#		print  '<option selected> 2016</option>',"\n";
#	}else{
#		print  '<option> 2016</option>',"\n";
#	}
#	if($eyear == 2017){
#		print  '<option selected> 2017</option>',"\n";
#	}else{
#		print  '<option> 2017</option>',"\n";
#	}
	if($eyear == 2018){
		print  '<option selected> 2018</option>',"\n";
	}else{
		print  '<option> 2018</option>',"\n";
	}
	if($eyear == 2019){
		print  '<option selected> 2019</option>',"\n";
	}else{
		print  '<option> 2019</option>',"\n";
	}
	if($eyear == 2020){
		print  '<option selected> 2020</option>',"\n";
	}else{
		print  '<option> 2020</option>',"\n";
	}
	if($eyear == 2021){
		print  '<option selected> 2021</option>',"\n";
	}else{
		print  '<option> 2021</option>',"\n";
	}
	if($eyear == 2022){
		print  '<option selected> 2022</option>',"\n";
	}else{
		print  '<option> 2022</option>',"\n";
	}
	if($eyear == 2023){
		print  '<option selected> 2023</option>',"\n";
	}else{
		print  '<option> 2023</option>',"\n";
	}
	if($eyear == 2024){
		print  '<option selected> 2024</option>',"\n";
	}else{
		print  '<option> 2024</option>',"\n";
	}
	if($eyear == 2025){
		print  '<option selected> 2025</option>',"\n";
	}else{
		print  '<option> 2025</option>',"\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";

	$nfield = 'signoff'."$total";
	print  "<td style='text-align:center'><input type='text' size='10' name='$nfield' value=' '></td>", "\n";
	print  '<td style="text-align:center"><input type="submit" name="submit" value="Update"></td>';
	$nfield = 'add'."$total";
	$nfield2= 'cut'."$total";
	print  "<td style='text-align:center'><input type='submit' name='$nfield' value='Add'>";
	print  "<input type='submit' name='$nfield2' value='Delete'></td>";
	print  '</tr>',"\n";

$total++;

#--------------------------------------------------------------

#
#--- Add several unassigned raws so that total # of the raws will cover 6 month periods
#

#$upper = 41 - $total + $h_cnt;
$upper = 52 - $total + $h_cnt;              #--- added 04/10/19

for($j = 0; $j < $upper; $j++){

        $newstart = $newend + 86400;
        ($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($newstart);
        $smonth = $umon + 1;
        $sday   = $umday;
        $syear  = $uyear + 1900;
	$s_warning = 0;
	if($uwday != 1){
		$s_warning = 1;
	}

        $newend = $newend + 604800;
        ($usec, $umin, $uhour, $umday, $umon, $uyear, $uwday, $uyday, $uisdst)= localtime($newend);
        $emonth = $umon + 1;
        $eday   = $umday;
        $eyear  = $uyear + 1900;
	$e_warning = 0;
	if($uwday != 0){
		$e_warning = 1;
	}

        print  '<tr>',"\n";

#
	
	$warn1 = 0;
	UOUT:
	for($ic = 0; $ic < $unsigned_cnt; $ic++){ 
		if($unsigned_warning[$ic] == $total){
			$warn1++;
			last UOUT;
		}
	}

#
#--- contact
#
	if($warn1 == 0){
		print "<tr>\n";
	}else{
		print "<tr style='background-color:red'>\n";
	}

        $nfield = 'name'."$total";

	print  '<td>',"\n";
	print  "<select name='$nfield'>","\n";
	print  "<option selected> </option>","\n";
	foreach $ent (@person){
		print  "<option> $ent</option>","\n";
	}
	print  '</select>',"\n";
	print  '</td>',"\n";

#
#--- start month
#
        $nfield = 'smonth'."$total";

        print  '<td>',"\n";
        print  "<select name='$nfield'>","\n";
        if($smonth == 1){
                print  '<option selected> January</option>',"\n";
        }else{
                print  '<option> January</option>',"\n";
        }
        if($smonth == 2){
                print  '<option selected> February</option>',"\n";
        }else{
                print  '<option> February</option>',"\n";
        }
        if($smonth == 3){
                print  '<option selected> March</option>',"\n";
        }else{
                print  '<option> March</option>',"\n";
        }
        if($smonth == 4){
                print  '<option selected> April</option>',"\n";
        }else{
                print  '<option> April</option>',"\n";
        }
        if($smonth == 5){
                print  '<option selected> May</option>',"\n";
        }else{
                print  '<option> May</option>',"\n";
        }
        if($smonth == 6){
                print  '<option selected> June</option>',"\n";
        }else{
                print  '<option> June</option>',"\n";
        }
        if($smonth == 7){
                print  '<option selected> July</option>',"\n";
        }else{
                print  '<option> July</option>',"\n";
        }
        if($smonth == 8){
                print  '<option selected> August</option>',"\n";
        }else{
                print  '<option> August</option>',"\n";
        }
        if($smonth == 9){
                print  '<option selected> September</option>',"\n";
        }else{
                print  '<option> September</option>',"\n";
        }
        if($smonth == 10){
                print  '<option selected> October</option>',"\n";
        }else{
                print  '<option> October</option>',"\n";
        }
        if($smonth == 11){
                print  '<option selected> November</option>',"\n";
        }else{
                print  '<option> November</option>',"\n";
        }
        if($smonth == 12){
                print  '<option selected> December</option>',"\n";
        }else{
                print  '<option> December</option>',"\n";
        }
        print  '</select>',"\n";
        print  '</td>',"\n";
#
#--- start day
#
        $nfield = 'sday'."$total";

	if($s_warning == 1){
        	print  "<td style='background-color:#87CEEB'><input type='text' name='$nfield' value='$sday' size=5 /></td>","\n";
	}else{
        	print  "<td><input type='text' name='$nfield' value='$sday' size=5 /></td>","\n";
	}
#
#--- start year
#
        $nfield = 'syear'."$total";

        print  '<td>',"\n";
        print  "<select name='$nfield'>","\n";
#        if($syear == 2009){
#                print  '<option selected> 2009</option>',"\n";
#        }else{
#                print  '<option> 2009</option>',"\n";
#        }
#        if($syear == 2010){
#                print  '<option selected> 2010</option>',"\n";
#        }else{
#                print  '<option> 2010</option>',"\n";
#        }
#        if($syear == 2011){
#                print  '<option selected> 2011</option>',"\n";
#        }else{
#                print  '<option> 2011</option>',"\n";
#        }
#        if($syear == 2012){
#                print  '<option selected> 2012</option>',"\n";
#        }else{
#                print  '<option> 2012</option>',"\n";
#        }
#        if($syear == 2013){
#                print  '<option selected> 2013</option>',"\n";
#        }else{
#                print  '<option> 2013</option>',"\n";
#        }
#        if($syear == 2014){
#                print  '<option selected> 2014</option>',"\n";
#        }else{
#                print  '<option> 2014</option>',"\n";
#        }
#        if($syear == 2015){
#                print  '<option selected> 2015</option>',"\n";
#        }else{
#                print  '<option> 2015</option>',"\n";
#        }
#        if($syear == 2016){
#                print  '<option selected> 2016</option>',"\n";
#        }else{
#                print  '<option> 2016</option>',"\n";
#        }
#        if($syear == 2017){
#                print  '<option selected> 2017</option>',"\n";
#        }else{
#                print  '<option> 2017</option>',"\n";
#        }
        if($syear == 2018){
                print  '<option selected> 2018</option>',"\n";
        }else{
                print  '<option> 2018</option>',"\n";
        }
        if($syear == 2019){
                print  '<option selected> 2019</option>',"\n";
        }else{
                print  '<option> 2019</option>',"\n";
        }
        if($syear == 2020){
                print  '<option selected> 2020</option>',"\n";
        }else{
                print  '<option> 2020</option>',"\n";
        }
        if($syear == 2021){
                print  '<option selected> 2021</option>',"\n";
        }else{
                print  '<option> 2021</option>',"\n";
        }
        if($syear == 2022){
                print  '<option selected> 2022</option>',"\n";
        }else{
                print  '<option> 2022</option>',"\n";
        }
        if($syear == 2023){
                print  '<option selected> 2023</option>',"\n";
        }else{
                print  '<option> 2023</option>',"\n";
        }
        if($syear == 2024){
                print  '<option selected> 2024</option>',"\n";
        }else{
                print  '<option> 2024</option>',"\n";
        }
        if($syear == 2025){
                print  '<option selected> 2025</option>',"\n";
        }else{
                print  '<option> 2025</option>',"\n";
        }
        print  '</select>',"\n";
        print  '</td>';

#
#--- end month
#
        $nfield = 'emonth'."$total";

        print  '<td>',"\n";
        print  "<select name='$nfield'>","\n";
        if($emonth == 1){
                print  '<option selected> January</option>',"\n";
        }else{
                print  '<option> January</option>',"\n";
        }
        if($emonth == 2){
                print  '<option selected> February</option>',"\n";
        }else{
                print  '<option> February</option>',"\n";
        }
        if($emonth == 3){
                print  '<option selected> March</option>',"\n";
        }else{
                print  '<option> March</option>',"\n";
        }
        if($emonth == 4){
                print  '<option selected> April</option>',"\n";
        }else{
                print  '<option> April</option>',"\n";
        }
        if($emonth == 5){
                print  '<option selected> May</option>',"\n";
        }else{
                print  '<option> May</option>',"\n";
        }
        if($emonth == 6){
                print  '<option selected> June</option>',"\n";
        }else{
                print  '<option> June</option>',"\n";
        }
        if($emonth == 7){
                print  '<option selected> July</option>',"\n";
        }else{
                print  '<option> July</option>',"\n";
        }
        if($emonth == 8){
                print  '<option selected> August</option>',"\n";
        }else{
                print  '<option> August</option>',"\n";
        }
        if($emonth == 9){
                print  '<option selected> September</option>',"\n";
        }else{
                print  '<option> September</option>',"\n";
        }
        if($emonth == 10){
                print  '<option selected> October</option>',"\n";
        }else{
                print  '<option> October</option>',"\n";
        }
        if($emonth == 11){
                print  '<option selected> November</option>',"\n";
        }else{
                print  '<option> November</option>',"\n";
        }
        if($emonth == 12){
                print  '<option selected> December</option>',"\n";
        }else{
                print  '<option> December</option>',"\n";
        }
        print  '</select>',"\n";
        print  '</td>',"\n";
#
#--- end day
#
        $nfield = 'eday'."$total";

	if($e_warning == 1){
        	print  "<td style='background-color:#87CEEB'><input type='text' name='$nfield' value='$eday' size=5 /></td>","\n";
	}else{
        	print  "<td><input type='text' name='$nfield' value='$eday' size=5 /></td>","\n";
	}
#
#--- end year
#
        $nfield = 'eyear'."$total";

        print  '<td>',"\n";
        print  "<select name='$nfield'>","\n";
#        if($eyear == 2009){
#                print  '<option selected> 2009</option>',"\n";
#        }else{
#                print  '<option> 2009</option>',"\n";
#        }
#        if($eyear == 2010){
#                print  '<option selected> 2010</option>',"\n";
#        }else{
#                print  '<option> 2010</option>',"\n";
#        }
#        if($eyear == 2011){
#                print  '<option selected> 2011</option>',"\n";
#        }else{
#                print  '<option> 2011</option>',"\n";
#        }
#        if($eyear == 2012){
#                print  '<option selected> 2012</option>',"\n";
#        }else{
#                print  '<option> 2012</option>',"\n";
#        }
#        if($eyear == 2013){
#                print  '<option selected> 2013</option>',"\n";
#        }else{
#                print  '<option> 2013</option>',"\n";
#        }
#        if($eyear == 2014){
#                print  '<option selected> 2014</option>',"\n";
#        }else{
#                print  '<option> 2014</option>',"\n";
#        }
#        if($eyear == 2015){
#                print  '<option selected> 2015</option>',"\n";
#        }else{
#                print  '<option> 2015</option>',"\n";
#        }
#        if($eyear == 2016){
#                print  '<option selected> 2016</option>',"\n";
#        }else{
#                print  '<option> 2016</option>',"\n";
#        }
#        if($eyear == 2017){
#                print  '<option selected> 2017</option>',"\n";
#        }else{
#                print  '<option> 2017</option>',"\n";
#        }
        if($eyear == 2018){
                print  '<option selected> 2018</option>',"\n";
        }else{
                print  '<option> 2018</option>',"\n";
        }
        if($eyear == 2019){
                print  '<option selected> 2019</option>',"\n";
        }else{
                print  '<option> 2019</option>',"\n";
        }
        if($eyear == 2020){
                print  '<option selected> 2020</option>',"\n";
        }else{
                print  '<option> 2020</option>',"\n";
        }
        if($eyear == 2021){
                print  '<option selected> 2021</option>',"\n";
        }else{
                print  '<option> 2021</option>',"\n";
        }
        if($eyear == 2022){
                print  '<option selected> 2022</option>',"\n";
        }else{
                print  '<option> 2022</option>',"\n";
        }
        if($eyear == 2023){
                print  '<option selected> 2023</option>',"\n";
        }else{
                print  '<option> 2023</option>',"\n";
        }
        if($eyear == 2024){
                print  '<option selected> 2024</option>',"\n";
        }else{
                print  '<option> 2024</option>',"\n";
        }
        if($eyear == 2025){
                print  '<option selected> 2025</option>',"\n";
        }else{
                print  '<option> 2025</option>',"\n";
        }
        print  '</select>',"\n";
        print  '</td>',"\n";

	$nfield = 'signoff'."$total";
	print  "<td style='text-align:center'><input type='text' size='10' name='$nfield' value=' '></td>", "\n";
	print  '<td style="text-align:center"><input type="submit" name="submit" value="Update"></td>';
	$nfield = 'add'."$total";
	$nfield2= 'cut'."$total";
	print  "<td style='text-align:center'><input type='submit' name='$nfield' value='Add'>";
	print  "<input type='submit' name='$nfield2' value='Delete'></td>";
        print  '</tr>',"\n";
        $total++;
}

print  '</table>',"\n";
print  '<br /><br />',"\n";

print hidden(-name=>'total', -value=>"$total");
print '<input type="submit" name="submit" value="Submit Updates">',"\n";

print  '<br /><br />',"\n";
print '<a href="https://cxc.cfa.harvard.edu/cus/PeoplePhones.txt"><strong><em style="background-color:red;color:yellow;">POC phone numbers</em></strong></a>';
print  '<br /><br />',"\n";
print '<br />',"\n";

print '<hr />',"\n";

print '<br />',"\n";
print '<em style="font-size:90%">',"\n";
print 'If you have any questions about this page, please contact:',"\n";
print '<a href="mailto:bwargelin@head.cfa.harvard.edu">bwargelin@head.cfa.harvard.edu</a>.',"\n";
print '</em>',"\n";

print  '</form>',"\n";
print  '</body>',"\n";
print  '</html>',"\n";


##################################################################
### update_database: update too pc schedule database update    ###
##################################################################

sub update_database{

#
#--- read the original schedule and save it
#

	@orig_schedule = ();
	$ototal        = 0;
	open(IN, "$data_dir/schedule");

	while(<IN>){
		chomp $_;
		push(@orig_schedule, $_);
		$ototal++;
	}
	close(IN);

	@unsigned_warning  = ();
	$unsigned_cnt      = 0;
#
#--- create backup copy
#

	system("mv $data_dir/schedule $data_dir/schedule~");

#
#--- # of data line in the new table
#
	$total = param('total');

	@save_line = ();
	$c_cnt     = 0;
	$d_cnt     = 0;
#
#--- get data
#
	OUTER:
	for($j = 0; $j < $total; $j++){
		$pname  = 'name'."$j";
		$name   = param("$pname");
		$pname  = 'smonth'."$j";
		$lmonth = param("$pname");
		if($lmonth =~ /\d/){
			$smonth = $lmonth;
		}else{
			$smonth = change_month_format($lmonth);
		}
		$pname  = 'sday'."$j";
		$sday   = param("$pname");
		$pname  = 'syear'. "$j";
		$syear  = param("$pname");
		$pname  = 'emonth'."$j";
		$lmonth = param("$pname");
		if($lmonth =~ /\d/){
			$emonth = $lmonth;
		}else{
			$emonth = change_month_format($lmonth);
		}
		$pname  = 'eday'."$j";
		$eday   = param("$pname");
		$pname  = 'eyear'."$j";
		$eyear  = param("$pname");

		$pname  = 'signoff'."$j";
		$signoff= param("$pname");

		$c_cnt++;

		if($name !~ /\w/){
			if($smonth eq '' && $sday eq '' && $emonth eq '' && $eday eq ''){
				next OUTER;
			}
		}else{
			$d_cnt = $c_cnt;
		}


		if($name !~ /TBD/ && $name =~ /\w/ && $signoff !~ /\w/){
			$line = $orig_schedule[$j-1];
			if($line !~ /\w/){
				$line = "TBD\t$smonth\t$sday\t$syear\t$emonth\t$eday\t$eyear\t$signoff";
			}
			push(@unsigned_warning, $j);
			$unsigned_cnt++;
		}elsif($name =~ /TBD/ && $signoff =~ /\w/){
			$line = $orig_schedule[$j-1];
		}elsif($name !~ /\w/ && $signoff =~ /\w/){
			$line = $orig_schedule[$j-1];
		}else{
			$line = "$name\t$smonth\t$sday\t$syear\t$emonth\t$eday\t$eyear\t$signoff";
		}
		push(@save_line, $line);
	}
#
#--- remove a couple of unwanted lines from the new data set, and add some info.
#
	
	@temp_save = ();

	@rtemp   = reverse(@save_line);
	@cleaned = ();
	$rchk    = 0;
	$ncnt    = 0;
	FOUTER:
	foreach $ent (@rtemp){
		@atemp = split(/\t+/, $ent);
#
#--- any lines after the last real entry (the name of a person in charge), are dropped.
#
		if($rchk == 0){
			if($atemp[0] !~ /\w/){
				next FOUTER;
			}elsif($atemp[0] =~ /TBD/i){
				next FOUTER;
			}else{
				$rchk++;
				push(@cleaned, $ent);
				$ncnt++;
			}
		}else{
#
#--- if there a blank name between two real names, put TBD as a name
#

			if($atemp[0] !~ /\w/){
				$ent = "TBD\t$atemp[1]\t$atemp[2]\t$atemp[3]\t$atemp[4]\t$atemp[5]\t$atemp[6]";
			}
			push(@cleaned, $ent);
			$ncnt++;
		}
	}
	@rcleaned  = reverse(@cleaned);
	@save_line = @rcleaned;
	$d_cnt     = $ncnt;


	open(OUT, ">$data_dir/schedule");

	@modified = ();
	@new      = ();
	$mcnt     = 0;
	@newassign= ();
	@nacnt    = 0;
	$k = 0;
	FOUT:
	for($j = 0; $j < $d_cnt; $j++){

#
#--- printing out to the database
#

		print OUT "$save_line[$j]\n";

#
#--- checking what were modified/added
#
		if($k < $ototal){
			if($save_line[$j] !~ $orig_schedule[$k]){
				if($orig_schedule[$k] =~ /TBD/ || $orig_schedule[$k] !~ /\w/){
					push(@newassign, $save_line[$j]);
					$nacnt++;
				}else{
					push(@modified, $orig_schedule[$k]);
					push(@new,      $save_line[$j]);
					$mcnt++;
				}
			}
		}else{
			if($save_line[$j] !~ /TBD/i){
				push(@newassign, $save_line[$j]);
				$nacnt++;
			}
		}
		$k++;
	}
	close(OUT);
#	system("chmod 777 $data_dir/schedule");
#
#--- create time stamp, copy it to Logs directory
#
	$cinsec = time() - $tdelta;
	$cname  = "$data_dir".'/Logs/schedule.'."$cinsec";
	system("cp $data_dir/schedule $cname");
#	system("chmod 777 $data_dir/Logs/schedule*");
#
#--- update the html table
#
	system("cd $cus_dir/; /opt/local/bin/perl $cus_dir/create_schedule_table.perl");
#
#--- send out email to affected person, if their schedule changed
#
	if($mcnt > 0 || $nacnt > 0){
		open(IN, "$data_dir/personal_list");
		@plist  = ();
		@email  = ();
		$pcnt   = 0;
		while(<IN>){
			chomp $_;
			@ltemp = split(/<>/, $_);
			push(@plist,  $ltemp[0]);
			push(@email,  $ltemp[4]);
			$pcnt++;
		}
		close(IN);
	}
#
#--- if any information is modified from the previous entry, send out email
#
	if($mcnt > 0){
		TOUT:
		for($k = 0; $k < $mcnt; $k++){
			
			@mtemp = split(/\t+/, $new[$k]);
			FOUT:
			for($j = 0; $j < $pcnt; $j++){
				if($mtemp[0] =~ /$plist[$j]/){
					$contact1 = $email[$j];
					last FOUT;
				}
			}
			
			@mtemp = split(/\t+/, $modified[$k]);
			FOUT:
			for($j = 0; $j < $pcnt; $j++){
				if($mtemp[0] =~ /$plist[$j]/){
					$contact2 = $email[$j];
					last FOUT;
				}
			}

			@ntemp = split(/\t+/, $new[$k]);

			open(OUT, ">$temp_dir/zztemp");
			print OUT "TOO contact schedule was modified, and your scheduled date was affected:\n";
			print OUT "ORIGINAL: $modified[$k]\n";
			print OUT "NEW:      $new[$k]\n\n";
			print OUT "Please check:\n";
			print OUT ' https://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html',"\n";
			print OUT "or go to:\n";
			print OUT ' https://cxc.cfa.harvard.edu/mta/CUS/Usint/schedule_submitter.cgi',"\n\n";
			print OUT "and re-adjust the schedule, if needed.\n\n";
			print OUT "This change was made by $ntemp[7].\n\n";
			print OUT "If you have any quesitons about the scheduling, please contact\n";
			print OUT "$mail_line"."Brad Wargelin: bwargelin\@head.cfa.harvard.edu\n";
			close(OUT);

			system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Change: $contact1<->$contact2\" -rcus\@head.cfa.harvard.edu msobolewska\@cfa.harvard.edu");

			if($contact1 eq $contact2){
				$contact2 = '';
			}

			if($contact1 =~ /\w/ && $contact2 =~ /\w/){
				system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Change\" -rcus\@head.cfa.harvard.edu -ccus\@head.cfa.harvard.edu bwargelin\@head.cfa.harvard.edu $contact1 $contact2");
			}elsif($cotact1 =~ /\w/ && $contact2 !~ /\w/){
				system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Change\" -rcus\@head.cfa.harvard.edu -ccus\@head.cfa.harvard.edu bwargelin\@head.cfa.harvard.edu $contact1");
			}elsif($cotact1 !~ /\w/ && $contact2 =~ /\w/){
				system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Change\" -rcus\@head.cfa.harvard.edu -ccus\@head.cfa.harvard.edu bwargelin\@head.cfa.harvard.edu $contact2");
			}

			system("rm $temp_dir/zztemp");

		}
	}

#
#--- if a new data raw is added, remind the use for it
#
	if($nacnt > 0){
		TOUT:
		for($k = 0; $k < $nacnt; $k++){

			@mtemp = split(/\t+/, $newassign[$k]);
			if($mtemp[0] =~ /TBD/i || $mtemp[0] !~ /\w/){
				next TOUT;
			}

			FOUT:
			for($j = 0; $j < $pcnt; $j++){
				if($mtemp[0] =~ /$plist[$j]/){
					$contact1 = $email[$j];
					last FOUT;
				}
			}

			open(OUT, ">$temp_dir/zztemp");
			print OUT "TOO contact schedule was updated, and you are assigned to:\n";
			print OUT "          $newassign[$k]\n\n";
			print OUT "Please check:\n";
			print OUT ' https://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html',"\n";
			print OUT "or go to:\n";
			print OUT ' https://cxc.cfa.harvard.edu/mta/CUS/Usint/schedule_submitter.cgi',"\n\n";
			print OUT "and re-adjust the schedule, if needed.\n\n";
			print OUT "This assignment was made by $mtemp[7].\n\n";
			print OUT "If you have any quesitons about the scheduling, please contact\n";
			print OUT "$mail_line"."Brad Wargelin: bwargelin\@head.cfa.harvard.edu\n";
			close(OUT);

			system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Updated: $contact1\" -rcus\@head.cfa.harvard.edu msobolewska\@cfa.harvard.edu");
			system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Updated\" -rcus\@head.cfa.harvard.edu -ccus\@head.cfa.harvard.edu bwargelin\@head.cfa.harvard.edu $contact1");

			system("rm $temp_dir/zztemp");
		}
	}
}


################################################################################################################
### add_line_on_database: adding an extra schedule line on the schedule database                             ###
################################################################################################################

sub add_line_on_database{

	$rno = $j -1;

#
#--- read the original schedule and save it
#

	@mod_schedule = ();
	$atotal        = 0;
	open(IN, "$data_dir/schedule");

	while(<IN>){
		chomp $_;
		push(@mod_schedule, $_);
		if($atotal == $rno){
			@ftemp = split(/\t+/, $_);
			$line  = "TBD\t$ftemp[1]\t$ftemp[2]\t$ftemp[3]\t$ftemp[4]\t$ftemp[5]\t$ftemp[6]\t$ftemp[7]";
			push(@mod_schedule, $line);
		}
		$atotal++;
	}
	close(IN);
#
#--- create backup copy
#

	system("mv $data_dir/schedule $data_dir/schedule~");

#
#--- update schedule database
#
	open(OUT, ">$data_dir/schedule");
	foreach $line (@mod_schedule){
		print OUT "$line\n";
	}
	close(OUT);
#	system("chmod 777 $data_dir/schedule");
}




################################################################################################################
### cut_line_on_database: deleating a line  from the schedule database                                       ###
################################################################################################################

sub cut_line_on_database{

	$rno = $j -1;

#
#--- read the original schedule and save it
#

	@mod_schedule = ();
	@cut_affected = ();
	$ctotal        = 0;
	$cchk          = 0;
	open(IN, "$data_dir/schedule");

	NOUTER:
	while(<IN>){
		chomp $_;
		if($ctotal == $rno){
			$ctotal++;
			$cchk++;
			push(@cut_affected, $_);
			next NOUTER;
		}
		push(@mod_schedule, $_);
		$ctotal++;
	}
	close(IN);
#
#--- create backup copy
#

	system("mv $data_dir/schedule $data_dir/schedule~");

#
#--- update schedule database
#
	open(OUT, ">$data_dir/schedule");
	foreach $line (@mod_schedule){
		print OUT "$line\n";
	}
	close(OUT);
#	system("chmod 777 $data_dir/schedule");

	if($cchk > 0){
		open(IN, "$data_dir/personal_list");
		@plist  = ();
		@email  = ();
		$pcnt   = 0;
		while(<IN>){
			chomp $_;
			@ltemp = split(/<>/, $_);
			push(@plist,  $ltemp[0]);
			push(@email,  $ltemp[4]);
			$pcnt++;
		}

		TOUT:
		for($m = 0; $m < $cchk; $m++){

			@mtemp = split(/\t+/, $cut_affected[$m]);
			if($mtemp[0] =~ /TBD/i || $mtemp[0] !~ /\w/){
				next TOUT;
			}

			FOUT:
			for($n = 0; $n < $pcnt; $n++){
				if($mtemp[0] =~ /$plist[$n]/){
					$contact1 = $email[$n];
					last FOUT;
				}
			}

			open(OUT, ">$temp_dir/zztemp");
			print OUT "TOO contact schedule was updated, and your assignment for: \n";
			print OUT "          $cut_affected[$m]\n\n";
			print OUT "was canceled, and removed from the schedule. Please check:\n";
			print OUT ' https://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html',"\n";
			print OUT "or go to:\n";
			print OUT ' https://cxc.cfa.harvard.edu/mta/CUS/Usint/schedule_submitter.cgi',"\n\n";
			print OUT "and re-adjust the schedule, if needed.\n\n";
			print OUT "This assignment was made by $mtemp[7].\n\n";
			print OUT "If you have any quesitons about the scheduling, please contact\n";
			print OUT "$mail_line"."Brad Wargelin: bwargelin\@head.cfa.harvard.edu\n";
			close(OUT);

			system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Updated: $contact1\" -rcus\@head.cfa.harvard.edu msobolewska\@cfa.harvard.edu");
			system("cat $temp_dir/zztemp|mailx -s\"Subject: TOO Schedule Updated\" -rcus\@head.cfa.harvard.edu -ccus\@head.cfa.harvard.edu bwargelin\@head.cfa.harvard.edu $contact1");

			system("rm $temp_dir/zztemp");
		}
	}
}



##################################################################
### cnv_time_to_t1998: change time format to sec from 1998.1.1 ###
##################################################################

sub cnv_time_to_t1998{

#######################################################
#       Input   $year: year
#               $ydate: date from Jan 1
#               $hour:$min:$sec:
#
#       Output  $t1998<--- returned
#######################################################

        my($totyday, $totyday, $ttday, $t1998);
        my($year, $ydate, $hour, $min, $sec);
        ($year, $ydate, $hour, $min, $sec) = @_;

        $totyday = 365*($year - 1998);
        if($year > 2000){
                $totyday++;
        }
        if($year > 2004){
                $totyday++;
        }
        if($year > 2008){
                $totyday++;
        }
        if($year > 2012){
                $totyday++;
        }
        if($year > 2016){
                $totyday++;
        }
        if($year > 2020){
                $totyday++;
        }
        if($year > 2024){
                $totyday++;
        }
        if($year > 2028){
                $totyday++;
        }
        if($year > 2032){
                $totyday++;
        }
        if($year > 2036){
                $totyday++;
        }

        $ttday = $totyday + $ydate - 1;
        $t1998 = 86400 * $ttday  + 3600 * $hour + 60 * $min +  $sec;

        return $t1998;
}


##############################################################################
### time1998_to_ydate: change sec from 1998 to year:ydate:hh:mm:ss         ###
##############################################################################

sub time1998_to_ydate{

        my ($date, $time, $chk, $year, $month, $hour, $min, $sec);

        ($date) = @_;

        $in_day   = $date/86400;
        $day_part = int ($in_day);

        $rest     = $in_day - $day_part;
        $in_hr    = 24 * $rest;
        $hour     = int ($in_hr);

        $min_part = $in_hr - $hour;
        $in_min   = 60 * $min_part;
        $min      = int ($in_min);

        $sec_part = $in_min - $min;
        $sec      = int(60 * $sec_part);

        OUTER:
        for($year = 1998; $year < 2100; $year++){
                $tot_yday = 365;
                $chk = 4.0 * int(0.25 * $year);
                if($chk == $year){
                        $tot_yday = 366;
                }
                if($day_part < $tot_yday){
                        last OUTER;
                }
                $day_part -= $tot_yday;
        }

        $day_part++;
        if($day_part < 10){
                $day_part = '00'."$day_part";
        }elsif($day_part < 100){
                $day_part = '0'."$day_part";
        }

        if($hour < 10){
                $hour = '0'."$hour";
        }

        if($min  < 10){
                $min  = '0'."$min";
        }

        if($sec  < 10){
                $sec  = '0'."$sec";
        }

        $time = "$year:$day_part:$hour:$min:$sec";

        return($time);
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


#####################################################################
### ch_ydate_to_mon_date: change ydate to month and date          ###
#####################################################################

sub ch_ydate_to_mon_date {

        $tadd = 0;
        $chk = 4.0 * int(0.25 * $tyear);
        if($chk == $tyear){
                $tadd = 1;
        }
        if($tday < 32){
                $mon = '01';
                $mday = $tday;
        }

        if($tday > 31){
                if($tadd == 0){
                        if($tday <60){
                                $mon = '02';
                                $mday = $tday - 31;
                        }elsif($tday < 91){
                                $mon = '03';
                                $mday = $tday - 59;
                        }elsif($tday < 121){
                                $mon = '04';
                                $mday = $tday - 90;
                        }elsif($tday < 152){
                                $mon = '05';
                                $mday = $tday - 120;
                        }elsif($tday < 182){
                                $mon = '06';
                                $mday = $tday - 151;
                        }elsif($tday < 213){
                                $mon = '07';
                                $mday = $tday - 181;
                        }elsif($tday < 244){
                                $mon = '08';
                                $mday = $tday - 212;
                        }elsif($tday < 274){
                                $mon = '09';
                                $mday = $tday - 243;
                        }elsif($tday < 305){
                                $mon = '10';
                                $mday = $tday - 273;
                        }elsif($tday < 335){
                                $mon = '11';
                                $mday = $tday - 304;
                        }else{
                                $mon = '12';
                                $mday = $tday - 334;
                        }
                }else{
                        if($tday <61){
                                $mon = '02';
                                $mday = $tday - 31;
                        }elsif($tday < 92){
                                $mon = '03';
                                $mday = $tday - 60;
                        }elsif($tday < 122){
                                $mon = '04';
                                $mday = $tday - 91;
                        }elsif($tday < 153){
                                $mon = '05';
                                $mday = $tday - 121;
                        }elsif($tday < 183){
                                $mon = '06';
                                $mday = $tday - 152;
                        }elsif($tday < 214){
                                $mon = '07';
                                $mday = $tday - 182;
                        }elsif($tday < 245){
                                $mon = '08';
                                $mday = $tday - 213;
                        }elsif($tday < 275){
                                $mon = '09';
                                $mday = $tday - 244;
                        }elsif($tday < 306){
                                $mon = '10';
                                $mday = $tday - 274;
                        }elsif($tday < 336){
                                $mon = '11';
                                $mday = $tday - 305;
                        }else{
                                $mon = '12';
                                $mday = $tday - 335;
                        }
                }
        }
        $mday = int ($mday);
        if($mday < 10){
                $mday = '0'."$mday";
        }
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

