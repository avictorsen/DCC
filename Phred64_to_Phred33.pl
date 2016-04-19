#!/usr/bin/perl -w
use strict;
no warnings;
my $file = $ARGV[0];
my $count = 1;
my $cmd;
my $check1; my $check2;
my $ungzipfile;

open (OUTPUT, ">temp.txt") || die "Cannot open output file";
#if gziped
my $response = `file $file`;
if ($response =~ /gzip/){
	print "$file is gzipped\n";
	if ($file =~ /\.gz$/){
		$ungzipfile = $file;
		$ungzipfile =~ s/\.gz$//;
	}
	$check1 =`zcat $file 2>/dev/null | head -3000 2>/dev/null | grep -c -m 20 "a"`;
	$check2 =`zcat $file 2>/dev/null | head -3000 2>/dev/null | grep -c -m 20 "e"`;
}
else{
	$check1 =`cat $file 2>/dev/null | head -3000 2>/dev/null | grep -c -m 20 "a"`;
	$check2 =`cat $file 2>/dev/null | head -3000 2>/dev/null | grep -c -m 20 "e"`;

}
if ($check1 > 15 && $check2 > 15){
	if ($response =~ /gzip/){
		`gzip -df $file`;
	        print "processing gzipped file: $file\n";
		open (INPUT, "<".$ungzipfile) || die "Cannot open input file";
	}
	else{
	        print "processing $file\n";
		open (INPUT, "<".$file) || die "Cannot open input file";
	}
	while(<INPUT>){
		my $line = $_;
		if($count % 4 == 0) {# only look at every 4th line
			if ($line =~ /[J-h]/){
				$line =~ s/[(\;\<\>\=\?]/\!/g; # incase solexa
				$line =~ tr/@-~/!-~/; # for converting to Phred+33
			}
		}
		print OUTPUT $line;
		$count++;
	}
	#if gzipped
	if ($response =~ /gzip/){
		`mv temp.txt $ungzipfile`;
		`gzip -f $ungzipfile`;
	}
	else{
		`mv temp.txt $file`;
	}
print "Done!\n";
}

