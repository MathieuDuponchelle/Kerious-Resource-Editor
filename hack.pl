#! /usr/bin/perl

# gphx-cutout.pl --- cut out multiple subjects from scans.

# Copyright (C) 2008 John J Foerch <jjfoerch@earthlink.net>

# Author: John J Foerch <jjfoerch@earthlink.net>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

use strict;
use warnings;

use Image::Magick;

## get input and output filenames from command line
##
my $in = $ARGV[0];
my $out = $ARGV[1];

my $i = 0;

## set up parameters
##
my $scannerbedshave="0x0";
my $bgcolor="white";
my $bgcolorfuzz="25%";
my $samplestep="8";

open (MYFILE, '>lol');

$SIG{'INT'} = sub {close (MYFILE); exit(0);};

my $original = Image::Magick->new;
$original->Read($in);

my $flatbg = $original->Clone;

## compute subjectcolor and xcolor
##
my $c1 = Image::Magick->new(size=>'1x1');
$c1->Read("xc:$bgcolor");
my @c = $c1->GetPixel(x=>0, y=>0, normalize=>0);
$bgcolor = 'rgb('.join(',',splice(@c,0,3)).')';
$c1->Negate();
@c = $c1->GetPixel(x=>0, y=>0, normalize=>0);
my $subjectcolor = 'rgb('.join(',',splice(@c,0,3)).')';
my $c2 = $c1->Fx(expression=>'u == 0 ? 0.01 : u - 0.01', channel=>'red');
@c = $c2->GetPixel(x=>0, y=>0, normalize=>0);
my $xcolor = 'rgb('.join(',',splice(@c,0,3)).')';
undef $c1;
undef $c2;

## get width and height
##
my $wid = $flatbg->Get('width');
my $hei = $flatbg->Get('height');


## 1. create flatbg image.  In this image, we try to remove the
##    scannerbed edges, and remove any variation in our backdrop to
##    create a uniform background color around the subject(s).  We
##    also replace any pixels of subjectcolor by xcolor, so that
##    we can safely use subjectcolor as a key.
##
$flatbg->Shave(geometry=>$scannerbedshave);
$flatbg->Border(geometry=>$scannerbedshave, bordercolor=>$bgcolor);
$flatbg->Set(fuzz=>$bgcolorfuzz);
$flatbg->Opaque(color=>$bgcolor, fill=>$bgcolor);
$flatbg->Set(fuzz=>0);
$flatbg->Opaque(color=>$subjectcolor, fill=>$xcolor);




## 2. iterate over the prepared flatbg by samplestep, looking for
##    non-background pixels.  When one is found, generate a silhouette
##    image from flatbg, and use composition to cut that silhouette
##    out of a copy of the original image.  Then modify flatbg
##    in-place, coloring the subject we just extracted with the
##    background color, so it cannot be found again.
##
my $n = 0;
my $outfile;
for (my $y = $samplestep; $y < $hei; $y+=$samplestep) {
  for (my $x = $samplestep; $x < $wid; $x+=$samplestep) {
    @c = $flatbg->GetPixel(x=>$x, y=>$y, normalize=>0);
    my $color = 'rgb('.join(',',splice(@c,0,3)).')';
    if ($color eq $bgcolor) { next; }

    if ($out =~ /^(.*)%d(.*)$/) {
      $outfile = $1 . $n . $2;
    } elsif ("$out" =~ /^(.*?)\.(.*)$/) {
      # $outfile = replace . with -$n. in $out
      $outfile = $1 . "-$n." . $2;
    } else {
      $outfile=$out;
    }

    my $subject = $flatbg->Clone();
    $subject->Draw(bordercolor=>$bgcolor, fill=>$subjectcolor,
                   primitive=>'color', points=>"$x,$y",
                   method=>'filltoborder');
    $subject->Draw(bordercolor=>$subjectcolor, fill=>$bgcolor,
                   primitive=>'color', points=>"0,0",
                   method=>'filltoborder');
    $subject->Trim;

    print MYFILE ($subject->Get('width') . ' ' . $subject->Get('height') . ' ' . $subject->Get('page.x') . ' ' . $subject->Get('page.y') . "\n");

    ## fill this subject's area with the background in flatbg.
    ##
    $flatbg->Draw(bordercolor=>$bgcolor, fill=>$bgcolor,
                  primitive=>'color', points=>"$x,$y",
                  method=>'filltoborder');
			   ##$i++;
			   ##printf("%d\n", $i);
    $n++;
  }
}
close (MYFILE);
