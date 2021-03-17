#!/usr/bin/perl
use DBI;
use CGI qw/:standard :netscape /;

#################################################################################################
#												#
#	insert_person.cgi:  let a user to submit/remove/update too point of contact information #
#												#
#		author: t. isobe (tisobe@cfa.harvard.edu)					#
#												#
#		last update: Apr 24, 2015   	 						#
#												#
#################################################################################################

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


print '<body style="background-color:#FAEBD7; font-family:serif, sans-serif;font-size:12pt; color:black;" >';


print "<h2 style='background:blue;color:#FAEBD7; margin-right:10em'>Input New Contact Information</h2>";

print "<ul style='font-size:90%; margin-right:10em'>";
print '<li>';
print "If you want to <em class='blue'>submit</em> a new contact, please put all information in the fields.";
print 'If a certain information, other than name, is not available, use "NA".';
print 'Then click "Submit Contact Info" button.';
print '</li>';
print '<li>';
print "If you want to <em class='blue'>replace</em> a part of information, put the contact name, and ";
print 'necessary information to appropriate fields, and click "Modify Data" button.';
print '</li> ';
print '<li>';
print "If you want to <em class='blue'>remove</em> a contact, just put the EXACT name in the name field.";
print 'Then click "Remove" button.';
print '</li>';
print '<li>';
print '"Load" button just reloads the contact table below, and "Clear" button ';
print 'clears the new contact inputs.';
print '</li>';
print '</ul>';

#
#--- Input part starts here
#

print start_form();

$submit = param("submit");

#
#---  the submission from the last round tells the php what to do next
#

if($submit =~ /Clear/){
	$name   = '';
	$office = '';
	$cell   = '';
	$home   = '';
	$mail   = '';
	$assign = '';
}elsif($submit =~ /Load Data/){

#
#---	 do nothing... 
#

}else{
    	$name   = param('name');
    	$office = param('office');
    	$cell   = param('cell');
    	$home   = param('home');
    	$mail   = param('mail');
	$assign = param('assign');

	$name   = trim_white($name);
	$office = trim_white($office);
	$cell   = trim_white($cell);
	$home   = trim_white($home);
	$mail   = trim_white($mail);
	$assign = trim_white($assign);

	$name   = sentence_case($name);

	if($office =~ /na/ || $office =~ /n\/a/ || $office =~ /N\/A/){
		$office = 'NA';
	}
	if($cell   =~ /na/ || $cell   =~ /n\/a/ || $cell   =~ /N\/A/){
		$cell   = 'NA';
	}
	if($home   =~ /na/ || $home   =~ /n\/a/ || $home   =~ /N\/A/){
		$home   = 'NA';
	}
	if($mail   =~ /na/ || $mail   =~ /n\/a/ || $mail   =~ /N\/A/){
		$mail   = 'NA';
	}else{
		$mail   = lc($mail);
	}
	if($assign   =~ /na/ || $assign   =~ /n\/a/ || $assign   =~ /N\/A/){
		$assign   = 'NA';
	}
}

#------------------------------------------------

print ' <table style="text-align:left;padding-left:20px;border-width:0px">';
print ' <tr>';
print ' <td>';
print ' <strong>Name</strong>';
print ' </td>';
print ' <td>';
print "<input type='text' name='name' value = '' size=20>";
print ' </td>';
print ' </tr>';

print ' <tr>';
print ' <td>';
print ' <strong>Office Phone</strong>';
print ' </td>';
print ' <td>';
print "<input type='text' name='office' value = '' size=20>";
print ' </td>';
print ' </tr>';

print ' <tr>';
print ' <td>';
print ' <strong>Cell Phone</strong>';
print ' </td>';
print ' <td>';
print "<input type='text' name='cell' value = '' size=20>";
print ' </td>';
print ' </tr>';

print '<tr>';
print ' <td>';
print ' <strong>Home Phone</strong>';
print ' </td>';
print ' <td>';
print "<input type='text' name='home' value = '' size=20>";
print ' </td>';
print ' </tr>';

print ' <tr>';
print ' <td>';
print ' <strong>Mail Address</strong> ';
print ' </td>';
print ' <td>';
print "<input type='text' name='mail' value = '' size=20>";
print ' </td>';
print ' </tr>';

print ' <tr>';
print ' <td>';
print ' <strong>Responsibility<sup>*</sup></strong> ';
print ' </td>';
print ' <td>';
print "<input type='text' name='assign' value = '' size=20>";
print ' </td>';
print ' </tr>';
print ' </table>';

print '<p style="padding-top:10px;padding-bottom:20px">';
print '* Responsibility includes sequence numbers (bottom inclusive, top exclusive), instruments, and targets.';
print '</p>';

print "<input type='submit' value='Load'                name='submit' />";
print "<input type='submit' value='Submit Contact Info' name='submit' />";
print "<input type='submit' value='Modify Data'         name='submit' />";
print "<input type='submit' value='Remove'              name='submit' />";
print "<input type='submit' value='Clear'               name='submit' />";
print '<br />';

#------------------------------------------------

#
#---  the request is to remove the information from the data base
#

if($submit =~ /Remove/){
    	open(FH,"$data_dir/personal_list");
   		$tot = 0;
    	while(<FH>) {
		chomp $_;
		@entry = split(/\<\>/, $_);
		if($name !~ /$entry[0]/ && ($entry[0] ne '') && ($entry[0] ne "\n")){
			$cname[$tot] = $entry[0];
			$save[$tot]  = $_;
			$tot++;
		}
    	}
    	close(FH);

	open(OUT, "> $data_dir/personal_list");
	for ($i=0; $i< $tot; $i++)
  	{
		$line = "$save[$i]";
		print OUT "$line\n";;
  	}
	close(OUT);

#
#--- the request is to submit a new point of contact information or up date the previous info
#

}elsif(
	    (($submit =~ /Submit Contact Info/) 
		&& ($name ne "") && ($office ne "") 
		&& ($cell ne "") && ($home ne "") 
		&& ($mail ne "") && ($assign ne "")
	    ) || (
	     ($submit =~ /Modify Data/)
	    )
     	){
#
#--- check whether PC is already in the database 
#
    	open(FH, "$data_dir/personal_list");
   		$tot = 0;
    	while(<FH>) {
		chomp $_;
		@entry = split(/\<\>/, $_);
		if(($entry[0] ne '') && ($entry[0] ne "\n")){
			$cname[$tot] = $entry[0];
			$save[$tot]  = $_;
			$tot++;
		}
    	}
    	close(FH);

	$chk = 0;
	$loc = 0;
	for($j = 0; $j < $tot; $j++){
		if($name =~ /$cname[$j]/){
			$chk += 1;
			$loc  = $j;
		}
	}


#
#-- here is the case, we need to do a partial upate
#

	if($chk > 0){
		@test = split(/\<\>/, $save[$loc]);
		if(
			   ( ($office !~ /$test[1]/) && ($office ne '') )
			|| ( ($cell   !~ /$test[2]/) && ($cell   ne '') )
		 	|| ( ($home   !~ /$test[3]/) && ($home   ne '') )
			|| ( ($mail   !~ /$test[4]/) && ($mail   ne '') )
			|| ( ($assign !~ /$test[6]/) && ($assign ne '') )
		){
			if($office eq '' || $office =~ /na/i){
				$office = $test[1];
			}
			if($cell   eq '' || $cell =~ /na/i){
				$cell   = $test[2];
			}
			if($home   eq '' || $home =~ /na/i){
				$home   = $test[3];
			}
			if($mail   eq '' || $mail =~ /na/i){
				$mail   = $test[4];
			}
			if($assign eq '' || $assign =~ /na/i){
				$assign = $test[6];
			}

			$sname = $test[5];

			$chk = 0;

#
#--- remove the entry from the database 
#
    			open(FH, "$data_dir/personal_list");
   			$atot = 0;
    			while(<FH>) {
				chomp $_;
				@entry = split(/\<\>/, $_);
				if(($name !~ /$entry[0]/) && ($entry[0] ne '') && ($entry[0] ne "\n")){
					$cname[$atot] = $entry[0];
					$tsave[$atot]  = $_;
					$atot++;
				}
    			}
    			close(FH);
		
#
#--- add back the updated information to the database
#

			open(OUT,">$data_dir/personal_list");
			for ($i=0; $i< $atot; $i++)
  			{
				$line = "$tsave[$i]";
				print OUT "$line\n";
  			}
			close(OUT);
		}
	}

#
#--- here is totally new PC information update case
#

	if($chk == 0){
		open(OUT,">>$data_dir/personal_list");

		$input = "$name<>";
		print OUT "$input";
	
		$input = "$office<>";
		print OUT "$input";
	
		$input = "$cell<>";
		print OUT "$input";
	
		$input = "$home<>";
		print OUT "$input";
	
		$input = "$mail<>";
		print OUT "$input";
	
		if($sname eq ''){
			@btemp = split(/\@/, $mail);
			$sname = $btemp[0];
		}
		$input = "$sname<>";
		print OUT "$input";

		$input = "$assign\n";
		print OUT "$input";
		close(OUT);
	}
}

print end_form;

#----------------------------

print '<hr />';

print '<h2>Current Contact Information</h2>';

print '<table border=1>';

print '<tr>';
print '<th>Contact</th>';
print '<th>Office Phone</th>';
print '<th>Cell Phone</th>';
print '<th>Home Phone</th>';
print '<th>Email</th>';
print '<th>Responsibility</th>';
print '</tr>';


#-----------------------------

open(FH, "$data_dir/personal_list");

while(<FH>) {
	chomp $_;
	@entry = split(/\<\>/, $_);
	print '<tr>';
	if($entry[0] ne ''){
		if($entry[0] =~ /$name/){
			print '<td style="background-color:lime;text-align:center">' ,"$entry[0]", '</td>';
			print '<td style="background-color:lime;text-align:center">' ,"$entry[1]", '</td>';
			print '<td style="background-color:lime">' ,"$entry[2]", '</td>';
			print '<td style="background-color:lime">' ,"$entry[3]", '</td>';
			print '<td style="background-color:lime">' ,"$entry[4]", '</td>';
			print '<td style="background-color:lime">' ,"$entry[6]", '</td>';
		}
		else
		{
			print '<td style="text-align:center" >' ,"$entry[0]", '</td>';
			print '<td style="text-align:center" >' ,"$entry[1]", '</td>';
			print '<td>' ,"$entry[2]", '</td>';
			print '<td>' ,"$entry[3]", '</td>';
			print '<td>' ,"$entry[4]", '</td>';
			print '<td>' ,"$entry[6]", '</td>';
		}
	}
	print '</tr>';
}
close(FH);


#---------------------------------------------------------------------------


print '</table>';

print '<p style="padding-top:20px;padding-bottom:10px">';
print "<a href='https://cxc.cfa.harvard.edu/mta/CUS/Usint/too_contact_schedule.html'>";
print "<strong><em style='background-color:red;color:yellow;'>Back to USINT TOO Point of Contact</em></strong></a>";
print '</p>';

print '<hr />';

print '<p style="padding-top:10px">';
print "<em style='font-size:90%'>";
print 'If you have any questions about this page, please contact: ';
print "<a href='mailto:swolk@head.cfa.harvard.edu'>swolk@head.cfa.harvard.edu</a>.";
print '</em>';
print '</p>';
print "<p style='text-align:right'>";
print "<em style='font-size:85%;'>";
print '<strong>';
print 'This Script Was Last Modified on Oct 30, 2012';
print '</strong>';
print '</em>';
print '</p>';

print '</body>';
print '</html>';






##############################################################################
### sentence_case: make the first letter of each word upper case           ###
##############################################################################

sub sentence_case {
        my ($line, @atemp, $cnt, $lind, $uline);
        ($line) = @_;

        $line = trim_white($line);

        @atemp = split(//, $line);
        $cnt   = 0;
        foreach(@atemp){
                $cnt++;
        }

        $lind = 0;
        for($i = 0; $i < $cnt; $i++){
                if($atemp[$i] eq ' '){
                        $lind = 1;
                        $uline = "$uline".' ';
                }elsif($lind == 1){
                        $ladd  = uc($atemp[$i]);
                        $uline = "$uline"."$ladd";
                        $lind = 0;
                }else{
                        $uline = "$uline". "$atemp[$i]";
                }
        }

        return $uline;
}


##############################################################################
### trim_white: trim leading and trailing white space                      ###
##############################################################################

sub trim_white{
	my ($line, @atemp);

	($line) = @_;
	@atemp  = split(//, $line);
	$line   = '';
#
#--- remove suspicious characters from the input
#
	foreach $ent (@atemp){
		if($ent =~ /\w/ || $ent eq '@' || $ent eq '_' || $ent eq '-' || $ent eq '.' || $ent eq ' '){
			$line = "$line"."$ent";
		}
	}
#
#--- removing white spaces before and after the sring
#

        $line =~ s/^\s+//;
        $line =~ s/\s+$//;

	return $line;
}

