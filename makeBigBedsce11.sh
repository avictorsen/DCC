#!bin/bash
for filename in $1/*.regionPeak.gz; do
    echo "processing $filename"
    zcat $filename > $filename.temp
    awk -F, '{
        FS="\t";
        gsub(/CHROMOSOME\_/,"chr",$1);
        gsub(/MtDNA/,"M",$1);
        if ($3 ~ /e/){
            $3 = sprintf("%d",$3);
        };
        if ($2 ~ /e/){
            $2 = sprintf("%d",$2);
        };
        print $0;
    }' OFS="\t" $filename.temp > $filename.temp2
    bedtools sort -i $filename.temp2 > $filename.temp3
    bedtools slop -i $filename.temp3 -g ./encValData/ce11/chrom.sizes -b 0 > $filename.temp4
    bedtools sort -i $filename.temp4 > $filename.temp5
    ./bedToBigBed -type=bed6+4 $filename.temp5 ./encValData/ce11/chrom.sizes "${filename%%.gz}.bb"
    cat $filename.temp5 | gzip -c > $filename
    rm $filename.temp*
    echo " $filename converted to BigBed"
done
