#!bin/bash
for filename in $1/*.bam; do
    echo "processing $filename..."
    samtools view -h $filename > $filename.sam
    awk -F, '{
        FS="\t";
        if ($0 ~ /^@/){
            sub(/SN\:CHROMOSOME\_/,"SN:chr",$0);
            sub(/MtDNA/,"M",$0);
            sub(/Mitochondrial/,"M",$0);
            print $0;
        }
        else{
            if ($3~/MtDNA/){$3="chrM";}
            else if ($3 ~ /\*/){;}
            else if ($3 ~ /CHROMOSOME\_/){sub(/CHROMOSOME\_/,"chr",$3);}
            else {;}
            print $0;
        }
    }' OFS="\t" $filename.sam > $filename.temp.sam
    samtools view -Sbh $filename.temp.sam > $filename
    echo " $filename now contains \"chr\""
done


