#!/usr/bin/perl -w
use strict;
use Carp;

#
# This script generates .htpasswd and .htgroup files for use with
# a .htaccess. It generates entries from the system passwd maps
# for all users in the 'cal' group. It also has a means for
# adding non-system usernames and passwords, or for using a
# password different than that found in the system maps.
# See %additional_users below.
#
# by Pete Ratzlaff
# August, 1999
#

################################################################################
#
# BEGINNING OF CONFIGURATION SECTION
#
################################################################################

# If errors encountered while running, email sent to following address.
# empty string -> no email sent
#my $email_contact = 'swolk@cfa.harvard.edu';
my $email_contact = 'tisobe@cfa.harvard.edu';

# Files to generate, parameters therein. These should agree with the parameters
# in your .htaccess
my $htpasswd = '.htpasswd';
my $htgroup = '.htgroup';
my $htgroup_name = 'cal_users';

# List of groups for which all users' passwords are automatically
# put into .htpasswd
#my @auto_groups = qw( cal );
my @auto_groups = qw( mtagroup  );

# Usernames whose passwords are in the local maps, but are not in
# any of @auto_groups
my @additional_system_users = 	
	qw( 
           arots
           aldcroft
	   bmg
           bradw
           cjf
           donnelly
	   das
           ems
           harris
           hermanm
           isobe
	   jem
           jdrake
           jvrtilek
           lpd
           mattison
           mta
           mtadude
           nss
           pgreen
           plucinsk
           rac
           rkilgard
           royceb
           slane
           pslane
           swolk
           wrf
           wilton
           wink
           wrf
           jnichols
           jpbrown
           dmh
	   mccolml
	   nadams
	   belinda
	   fds
	   elvis
	   wrf
	   harris
	   kraft
	   karovska
	   jvrtilek
	   azezas
	   frh
	   ems
	   alexey
	   ssm
	   andreap
	   evans
	   pepi
	   graessle
	   kaaret
	   fap
	   aneta
	   rsmith
	   houck
	   pjonker
           kashyap
	   wise
	   vikhlinin
	   nevans
           aprestwich
	   gaensler
           mtorres
           shami
           mazzotta
	   devans
	   dgarcia
	   jclee
	   jlgalache
	   josh
	   jeno
           bhouse
	   antonell
	   gokas
	   heidi
           srandall
           patnaude
           gshattow
           kkingsbury
	   ht
	   jhagler
	   zhao
	   gregg
	   jeanconn
	   gaetz
	   edgar
           fcivano
           dfoight
           acarlton
           gokas
           wyman
           etingle
           jgreen
           erule
           twhalen
           cegrant
           cgrant
           jwing
           atran
           jzuhone
           abogdan
           rdabrusc
           emcclain
           malgosia
           rmontez
            rpete
            dj
            dcastro
            mprovost
	  ); 

# Users not in above groups on local system. Can also be used to give
# a user a password which is different than that found in the 
# system passwd map. Keys are usernames, values are corresponding
# crypt()ed passwords. Example is given for user "someuser", password "pie".
my %additional_users = (
		 #
		 #     AO5 entries
                 #      'fkb'           => 'LcvJC7XfodCeM',
                 #      'mwb'           => 'LcZK7E.sBRFFE',
                 #      'niel'          => 'Lc1C.3KwHC1dg',
                 #      'gkosta'        => 'LcSbmj2WHmmmo',
                 #      'cgrant'        => 'LcGCPQ1bUf9E6',
                 #      'mnowak'        => 'Lcit2WYE41xis',
                 #      'divas'         => 'Lc0FOm7gmR8D2',
                 #      'townsley'      => 'LcrypI0Kr9e72',
                 #      'vanspeybroeck' => 'Lcu1OOmLX3ktk',
                 #      'houck'         => 'LcgPS5FwKFzSM',
		 #    AO6 entries 	
                 #       'niel'          => 'Lc1C.3KwHC1dg',
                 #       'jsa'           => 'Lcbue0zLb.VKc',
                 #       'crc'           => 'LcG7O8.4I5ADM',
                 #       'chartas'       => 'LcVu1SngF2JWc',
                 #       'bdf'           => 'LcsXMqIB2UGqQ',
                 #       'elling'        => 'LcPVD7lsTctk6',
                 #       'edf'           => 'LcsfkzQMRgink',
                 #       'agarmire'      => 'LclaExi3hAt6E',
                 #       'agarmire'      => 'LcqaVn2q4aMnU',
                 #       'garmire'       => 'LcqaVn2q4aMnU',
                 #       'jcg'           => 'LccHWZK.SSDZ2',
                 #       'mario'         => 'LcoEBgjBKpDY.',
                 #       'j.kaastra'     => 'LcN61pWW5ASzM',
                 #       'green'         => 'Lcxwkxgg.wJ1Q',
                 #      'jlee'          => 'LcN61pWW5ASzM',
                 #       'jlee'          => 'Lc8GnBPY6S4vU',
                 #       'm.mendez'      => 'LcaDKE81CzenM',
                 #       'park'          => 'LcySxl7Kc.PqQ',
                 #       'pavlov'        => 'Lc.v6fRnya77U',
                 #       'predehl'       => 'Lcatkka8o6yj2',
                 #       'tsujimot'      => 'LcDZwn9Dr.eG2',
                 #       'l.m.kuiper'    => 'Lc.A8K3DHe8yk',
                 #       'nbrandt'       => 'Lc1C.3KwHC1dg',
                 #       'jschmitt'      => 'LcPffAaw7/DKI',
                 #       'rudy'          => 'LcoVU9DysmPbQ',
                 #       'chrisr'        => 'LcQKyGIUqluTM',
                 #       'chrisv'        => 'Lc96Lr1oBDLDE',
                 #       'jairwin'       => 'LcXTnkVfQU.3M',
                 #       'daniel'        => 'Lc9kQOhoA10.c',
                 #       'ron.elsner'    => 'LchhbyUFoQ9IE',
                 #       'gfossati'      => 'LcpQ.YBbEXeyI',
                 #       'cls7i'         => 'LcOwPPVitK4cI',
                 #       'acf'           => 'LccAVCZ/gOZkg',
                 #       'leighly'       => 'LcHTcFZbVtmbk',
                 #       'rwr'           => 'Lc9XY.Vrwq3Gs',
		 #	'wqd'           => 'LcyqjCQygMmxU',
		 #	'mwb'		=> 'Lc/8MXRwE9eg2',
		 #   AO7 entries
                 #       'dph'          => 'LcNUTB0h2VrOw',
                        'crc'          => 'LcG7O8.4I5ADM',
		#   AO 7 gto list
                #       'chartas'          => 'LcVu1SngF2JWc',
                #       'jsa'          => 'Lcbue0zLb.VKc',
                #       'divas'          => 'LcP8mJyhT3QOg',
                #       'l.m.kuiper'          => 'Lc.A8K3DHe8yk',
                #         'm.mendez'          => 'LcaDKE81CzenM',
                #         'web'          => 'LcvcNk0AxO1cw',
                #         'pavlov'          => 'Lc.v6fRnya77U',
                #         'divas'          => 'LccELwoEnfYos',
                #         'park'          => 'LcySxl7Kc.PqQ',
                #         'niel'          => 'Lc1C.3KwHC1dg',
                #         'skomossa'          => 'LcAdzmgT2dwcE',
                #         'chartas'          => 'LcVu1SngF2JWc',
                #         'jsa'          => 'Lcbue0zLb.VKc',
                #         'l.m.kuiper'          => 'Lc.A8K3DHe8yk',
                #         'jeanz'          => 'LcspEvKDXqWz.',
		#   AO7 exp list
                #        'stelzer'          => 'LcsNkEqnWZCjI',
                #        'spravdo'          => 'LckET2waWbvlY',
                #        'wqd'          => 'LcyqjCQygMmxU',
                #        'doug.swartz'          => 'Lccihsx7eepGs',
                #       'web'          => 'LcCABxKTYuSvI',
                #       'm.mendez'          => 'LcaDKE81CzenM',
                #       'jeanz'          => 'LcXl4f.xfI4pU',
                #       'pavlov'          => 'Lc.v6fRnya77U',
                #       'niel'          => 'Lc1C.3KwHC1dg',
                #       'skomossa'          => 'LcAYHDpsjZFhI',
                #       'park'          => 'LcySxl7Kc.PqQ',
                #       'guedel'          => 'LcFLyTbQrrSvA',
                #       'townsley'          => 'LcRcG6GydLaaE',
                #       'gkosta'          => 'LcaBFNitZ6IGg',
                #       'anderson'          => 'LcmUyH2Cg.r4.',
                #        'park'          => 'LcySxl7Kc.PqQ',
		#   test user name
			'special'	=> 'LcFEphwZD5Cmw',
			'nschulz'          => 'Lcz0XTU4kVtDg',
       #    special addition     
			'bwilkes'          => 'rRSLFjskkhjJI'
			);

################################################################################
#
# END OF CONFIGURATION SECTION
#
################################################################################

my @ERRORS; # error stack

# get NIS maps for local system
my @system_groups = `ypcat group`;
@system_groups or
    add_error("error getting group map from NIS"),
    sudden_death();
my @system_passwd = `ypcat passwd`;
@system_passwd or
    add_error("error getting passwd map from NIS"),
    sudden_death();

my %users; # all users going into $htpasswd

# Get usernames and passwords from each group
#
# First time through loop, also process users in @additional_system_users
#
my $first_time = 1;
foreach my $group (@auto_groups) {
    # we need one match...
    my @tmp = grep(/^${group}:/,@system_groups) or
	add_error("group '$group' not found on local system"),
	sudden_death();
    # ...and only one match
    @tmp == 1 or
	add_error("group '$group' had ${\(scalar @tmp)} matches on local system (yuck!)"),
	sudden_death();

    # get comma-separated list of users in this group
    my $group_line = $tmp[0];
    $group_line =~ /^$group:\*:\d+:(.*)$/ or
	add_error("users could not be extracted from group '$group'"),
	sudden_death();
	
    my @users = split ',', $1;
    if ($first_time) {
	push @users, @additional_system_users;
	$first_time = 0;
    }
    foreach my $user (@users) {
	next if exists $users{$user}; # Is user already added?

	# we need one match...
	my @tmp = grep(/^${user}:/,@system_passwd) or
#		       add_error("user '$user' from group '$group' not found on local system"),
			next;
#		       sudden_death();
	# ...and only one match
	@tmp == 1 or
#	    add_error("user '$user' had ${\(scalar @tmp)} matches on local system (yuck!)"),
		next;
#	    sudden_death();

	my $user_line = $tmp[0];
	$user_line =~ /^$user:(.*?):/ or
#	    add_error("password could not be extracted for user '$user'"),
		next;
#	    sudden_death();

	# finally, add user to hash
	$users{$user} = $1;
    }
}

# add additional usernames and passwords
foreach my $user (keys %additional_users) {
    exists $users{$user} and
	add_error("using non-system password for user '$user'");
    $users{$user} = $additional_users{$user};
}

# write files
write_htgroup($htgroup,$htgroup_name,keys %users) or
    add_error("error writing htgroup file, program terminating"),
    sudden_death();
write_htpasswd($htpasswd,%users) or
    add_error("error writing htpasswd file, program terminating"),
    sudden_death();

# clean up, go home
report_errors();

exit 0;

# write htgroup file
sub write_htgroup {
    my $MNAME = _mname();
    my $file = shift;
    my $group_name = shift;
    my @users = @_;

    my $content = $group_name.': '.join(' ',@users);
    open(FH,">$file") or
	add_error("$MNAME: could not open file '$file': $!"),
	return 0;
    print FH $content,"\n";
    close FH;

    system("chmod 744 $file") == 0 or
	add_error("$MNAME: could not change permissions on file '$file'");
    #system("chgrp cal $file") == 0 or
#	add_error("$MNAME: could not change group on file '$file'");

    return 1;
}

# write htpasswd file
sub write_htpasswd {
    my $MNAME = _mname();
    my $file = shift;
    my %users = @_;

    open(FH,">$file") or
	add_error("$MNAME: could not open file '$file': $!"),
	return 0;

    foreach my $user (keys %users) {
	print FH "$user:$users{$user}\n";
    }
    close FH;

    system("chmod 744 $file") == 0 or
	add_error("$MNAME: could not change permissions on file '$file'");
    #system("chgrp cal $file") == 0 or
#	add_error("$MNAME: could not change group on file '$file'");

    return 1;
}

# just add an error message to the error stack
sub add_error {
    foreach (@_) {
	push @ERRORS, "$0: $_";
    }
    return 1;
}

# Die a horrible death. Well, not really. Maybe just email some error
# messages to the appropriate person and quit.
sub sudden_death {
    Carp::cluck("uh oh");

    my $MNAME = _mname();
    add_error("$MNAME: program died prematurely");
    report_errors();
    exit 1;
}

# mail error message to appropriate address
sub report_errors {
    if (@ERRORS) {
	if ($email_contact) {
	    my $message = join("\n",@ERRORS);
	    my $command = "cat <<EOP | mail -s \"$0 had errors\" $email_contact\n$message\nEOP";
	    system($command);
	}
	else {
	    carp "errors found, no email contact to send them to";
	}
    }
    return 1;
}

sub _mname {
    return (caller 1)[3];
}

