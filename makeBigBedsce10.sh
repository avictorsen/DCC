#!bin/bash
#usage : sh makeBigBeds.sh <directory name>
#converts all bed files in directory $1 to bigBeds
for filename in $1/*.regionPeak.gz; do
    echo "processing $filename..."
    zcat $filename >>  $filename.temp
    echo 'track name=' $filename > $filename.temp2
    bedtools slop -i $filename.temp -g ../../encValData/ce10/chrom.sizes -b 0 >> $filename.temp2
    gzip -c $filename.temp2 > $filename
    #rm $filename.temp*
    echo " $filename converted to BigBed"
done
