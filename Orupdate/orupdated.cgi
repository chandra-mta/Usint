#!/usr/bin/perl
# R. Kilgard, Jan 30/31 2000
# This script generates a dynamic webpage for keeping track of updates to
# target parameters.  
#
# Last Udpate: Jun 28, 2021 (t. isobe: tisobe@cfa.harvard.edu)
#
#

use CGI;

print "Content-type: text/html; charset=utf-8\n\n";

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print "<title>Updated Target List</title>";
print "<style  type='text/css'>";
print "table{text-align:center;margin-left:auto;margin-right:auto;";
print "border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
print "</head>";

print "<body style='color:#000000;background-color:#FFFFE0'>";

read(STDIN,$newinfo,$ENV{'CONTENT_LENGTH'});


print "<h1>Updated Targets List</h1>";
print "<p>This list contains all targets which have been verified as updated.</p>";
print "<p><strong><a href=\"https://cxc.cfa.harvard.edu/cgi-bin/target_search/search.html\">";
print "Chandra Uplink Support Observation Search Form</a></strong></p>";
print "<p><strong><a href=\"https://cxc.cfa.harvard.edu/cus/\">";
print "Chandra Uplink Support Organizational Page</a></strong></p>";


#####
#open (FILE, "</data/udoc1/ocat/updates_table.list");
####open (FILE, "</proj/web-cxc/cgi-gen/mta/Obscat/ocat/updates_table.list");
open (FILE, "</data/mta4/CUS/www/Usint/ocat/updates_table.list");
@revisions = <FILE>;
close (FILE);
#####



print "<table border=1>";
print "<tr><th>OBSID.revision</th><th>General/ACIS edits by</th>";
print "<th>ACIS SI Mode edits by</th><th>HRC SI MODE edits by</th>";
print "<th>Verified by</th></tr>";

#--- because log is appended to, rather than added to...

@revisions= reverse(@revisions);

foreach $line (@revisions){
    chop $line;
    @values         = split ("\t+", $line);
    $obsrev         = $values[0];
    $general_status = $values[1];
    $acis_status    = $values[2];
    $si_mode_status = $values[3];
    $hrc_si_mode_status = $values[4];
    $dutysci_status = $values[5];
    $seqnum         = $values[6];
    $user           = $values[7];

    if ($dutysci_status =~/NA/){
        next;
    }
#
#--- use a file creatiion date as a sign-off date
#
    ($na0,$na1,$na2,$na3,$na4,$na5,$na6,$na7,$na8,$mtime,$na10,$na11,$na12) 
                    = stat "/data/mta4/CUS/www/Usint/ocat/updates/$obsrev";
    ($t0,$t1,$t2,$t3,$t4,$t5,$t6,$t7,$t8) = localtime($mtime);
    $month = $t4 + 1;
    $day   = $t3;
    $year  = $t5 + 1900;
    $ftime ="$month/$day/$year";

    print "<tr>";
    print "<td>";
    print "<a href=\"https://cxc.cfa.harvard.edu/mta/CUS/Usint/chkupdata.cgi\?$obsrev\">";
    print "$obsrev</a><br />";
    print "$seqnum<br />";
    print "$ftime<br />";
    print "$user";
    print "</td>";

    print "<td>$general_status</td>";
    print "<td>$si_mode_status</td>";
    print "<td>$hrc_si_mode_status</td>";
    print "<td><span style='color:#005C00'>$dutysci_status</span></td>";
    print "</tr>";
}
print "</table></body></html>";
