#!bin/bash
for filename in $1/*.regionPeak.gz; do
    echo "processing $filename..."
    zcat $filename > $filename.temp
    bedtools sort -i $filename.temp > $filename.temp2
    bedtools slop -i $filename.temp2 -g ./encValData/ce10/chrom.sizes -b 0 >> $filename.temp3
    bedtools sort -i $filename.temp3 > $filename.temp4
    bedToBigBed -type=bed6+4 $filename.temp4 ./encValData/ce10/chrom.sizes "${filename%%.gz}.bb"
    gzip -c $filename.temp4 > $filename
    rm $filename.temp*
    echo " $filename converted to BigBed"
done
