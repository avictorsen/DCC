#!bin/bash
for filename in $1/*.regionPeak.gz; do
    echo "processing $filename..."
    zcat $filename | awk '{
        FS="\t";
        if ($3 ~ /e/){
            $3 = sprintf("%d",$3);
        };
        if ($2 ~ /e/){
            $2 = sprintf("%d",$2);
        };
        if ($1 ~ /dmel_mito/){$1 = "chrM";}
        else{$1 = "chr"$1;};
        print $0;
        }' OFS="\t" > $filename.temp2
    bedtools sort -i $filename.temp2 > $filename.temp3
    bedtools slop -i $filename.temp3 -g ./encValData/dm3/chrom.sizes -b 0 >> $filename.temp4
    bedtools sort -i $filename.temp4 > $filename.temp5
    ./bedToBigBed -type=bed6+4 $filename.temp5 ./encValData/dm3/chrom.sizes "${filename%%.gz}.bb"
    cat $filename.temp5 | gzip -c > $filename
    rm $filename.temp*
    echo " $filename converted to BigBed"
done
