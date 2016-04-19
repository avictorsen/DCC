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
    gzip -c $filename.temp2 > $filename
    rm $filename.temp*
done
