#!bin/bash
for filename in $1/*.bam; do
    echo "processing $filename..."
    samtools view -h $filename > $filename.sam
    awk -F, '{
        FS="\t";
        if ($0 ~ /^@/){
            sub(/v1/,"",$0);
            print $0;
        }
        else{
            if ($3 ~ /chrUn/){
              sub(/v1/,"",$3)}
            print $0;
        }
    }' OFS="\t" $filename.sam > $filename.temp.sam
    samtools view -Sbh $filename.temp.sam > $filename
    echo " $filename now lacks \"v1\" in chrom name"
done
