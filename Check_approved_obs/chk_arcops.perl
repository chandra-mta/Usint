#!/usr/bin/perl

#########################################################################################
#											#
#	chk_arcops.perl: check arcops list and add to approved list if it is signed off	#
#											#
#		author: t. isobe (tisobe@cfa.harvard.edu)				#
#											#
#		last update: Mar 28, 2012						#
#											#
#########################################################################################


#
#---- if this is usint version, set the following param to 'yes', otherwise 'no'
#

$usint_on = 'yes';                     ##### USINT Version
#$usint_on = 'no';                      ##### USER Version
#$usint_on = 'test_yes';                 ##### Test Version USINT
#$usint_on = 'test_no';                 ##### Test Version USER

#
#---- set a name and email address of a test person
#

$test_user  = 'isobe';
$test_email = 'isobe@head.cfa.harvard.edu';

#$test_user  = 'mta';
#$test_email = 'isobe@head.cfa.harvard.edu';

#$test_user  = 'brad';
#$test_email = 'brad@head.cfa.harvard.edu';

#$test_user  = 'swolk';
#$test_email = 'swolk@head.cfa.harvard.edu';


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
        }elsif($atemp[0]  =~ /mtemp_dir/){
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
#--- if this is a test case, use the first directory, otherwise use the real one
#

if($usint_on =~ /test/i){
        $ocat_dir = $test_dir;
}else{
        $ocat_dir = $rea_dir;
}

#
#--- read updates_table.list
#--- check whether it is signed off
#

open(FH, "$ocat_dir/updates_table.list");

@ut_obsid  = ();

while(<FH>){
	chomp $_;
	@atemp = split(/\t+/, $_);
	@btemp = split(/\./, $atemp[0]);
	push(@ut_obsid, $btemp[0]);
	$status = 'ok';
	if($atemp[4] =~ /NA/i){
		$status = 'no';
	}
	@ctemp = split(/\s+/, $atemp[4]);
	%{ut_data.$btemp[0]} = (status => ["$status"],
			  	user   => ["$ctemp[0]"],
				date   => ["$ctemp[1]"],
				seq_no => ["$atemp[5]"]);
}
close(FH);

#
#--- sort and remove duplicate
#

@temp  = sort{$a<=>$b} @ut_obsid;
$first = shift(@temp);
@new   = ($first);

OUTER:
foreach $ent (@temp){
	foreach $comp (@new){
		if($ent == $comp){
			next OUTER;
		}
	}
	push(@new, $ent);
}

@ut_obsid = @new;

#
#--- read which one is in an arcops list
#

open(FH, "$ocat_dir/arcops_list");
@obsid = ();
while(<FH>){
	chomp $_;
	@atemp = split(/\s+/, $_);
	push(@obsid, $atemp[0]);
	%{date.$atemp[0]} = (date       => ["$atemp[1]"],
			     submitter  => ["$atemp[2]"],
			     targname   => ["$atemp[3]"],
			     instrument => ["$atemp[4]"],
			     grating    => ["$atemp[5]"]
				);
}
close(FH);

#
#--- make a list of signed off obsid
#

@approved_list = ();
foreach $ent (@obsid){
	foreach $comp (@ut_obsid){
		if($ent == $comp){
			if(${ut_data.$ent}{status}[0] =~ /ok/i){
				push(@approved_list, $ent);
			}
		}
	}
}

#
#--- update arcops_list
#

open(OUT, ">$ocat_dir/arcops_list");

OUTER:
foreach $ent (@obsid){
	foreach $comp (@approved_list){
		if($ent == $comp){
			next OUTER;
		}
	}
	print OUT "$ent\t";
	print OUT "${date.$ent}{date}[0]\t";
	print OUT "${date.$ent}{submitter}[0]\t";
	print OUT "${date.$ent}{targname}[0]\t";
	print OUT "${date.$ent}{instrument}[0]\t";
	print OUT "${date.$ent}{grating}[0]\n";
}
close(OUT);
	
#
#--- add to approved
#

open(OUT, ">>$ocat_dir/approved");

foreach $ent (@approved_list){
	print OUT "$ent\t";
	print OUT "${ut_data.$ent}{seq_no}[0]\t";
	print OUT "${ut_data.$ent}{user}[0]\t";
	print OUT "${ut_data.$ent}{date}[0]\n";

	$submitter  = ${date.$ent}{submitter}[0];
	$targname   = ${date.$ent}{targname}[0];
	$instrument = ${date.$ent}{instrument}[0];
	$grating    = ${date.$ent}{grating}[0];

#
#--- sending out acknoldgement email to submitter
#
	send_mail();

}
close(OUT);


##################################################################################
### send_mail: sending email to submitter about the approval of the obsid      ###
##################################################################################

sub send_mail{

#
#--- find USINT person corresponding to this obsid
#

	find_usint();

#
#--- find out email address for this submitter
#

	if($submitter =~ /mta/){
		$submitter_email = $test_email;
	}else{
		open(IN, "$pass_dir/user_email_list");
		OUTER:
		while(<IN>){
			chomp $_;
			@atemp = split(/\s+/, $_);
			if($submitter =~ /$atemp[0]/){
				$submitter_email = $atemp[3];
				last OUTER;
			}
		}
		close(IN);
	}

	open(OUT, ">$temp_dir/arcops_send_email");
	
	print OUT "\n\n\n\n";
	print OUT "Your change request for Obsid: $ent was made and approved for observation.\n\n";
	print OUT "If you have any questions, please contact $usint_mail. \n";
	print OUT "Thank you.\n\n\n";
	print OUT "${ut_data.$ent}{date}[0]\n";

	close(OUT);

	if($usint_on =~ /test/){
		system("cat $temp_dir/arcops_send_email |mailx -s\"Subject: Your Obsid: $ent Is Approved for Observation ($submitter_email)\" $test_email");
	}else{
		system("cat $temp_dir/arcops_send_email |mailx -s\"Subject: Your Obsid: $ent Is Approved for Observation\"  $submitter_email $test_email cus\@head.cfa.harvard.edu");
	}
	system("rm $temp_dir/arcops_send_email");
}

###############################################################################
### find_usint: find an appropriate usint email address for a given obs.    ###
###############################################################################

sub find_usint {
        if($targname    =~ /CAL/i){
                $usint_mail  = 'ldavid@cfa.harvard.edu';
        }elsif($grating =~ /LETG/i){
                $usint_mail  = 'jdrake@cfa.harvard.edu bwargelin@cfa.harvard.edu';
        }elsif($grating =~ /HETG/i){
                $usint_mail  = 'nss@space.mit.edu  hermanm@spce.mit.edu';
        }elsif($inst    =~ /HRC/i){
                $usint_mail  = 'juda@cfa.harvard.edu vkashyap@cfa.harvard.edu';
        }else{
                if($seq_nbr < 290000){
                        $usint_mail = 'swolk@cfa.harvard.edu';
                }elsif($seq_nbr > 300000 && $seq_nbr < 490000){
                        $usint_mail = 'nadams@cfa.harvard.edu';
                }elsif($seq_nbr > 500000 && $seq_nbr < 590000){
                        $usint_mail = 'plucinsk@cfa.harvard.edu';
                }elsif($seq_nbr > 600000 && $seq_nbr < 690000){
                        $usint_mail = 'jdepasquale@cfa.harvard.edu';
                }elsif($seq_nbr > 700000 && $seq_nbr < 790000){
                        $usint_mail = 'emk@cfa.harvard.edu';
                }elsif($seq_nbr > 800000 && $seq_nbr < 890000){
                        $usint_mail = 'maxim@cfa.harvard.edu';
                }elsif($seq_nbr > 900000 && $seq_nbr < 990000){
                        $usint_mail = 'das@cfa.harvard.edu';
                }
        }
}

