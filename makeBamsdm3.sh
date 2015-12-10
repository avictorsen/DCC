#!bin/bash
for filename in $1/*.bam; do
    echo "processing $filename..."
    samtools view -h $filename > $filename.sam
    awk -F, '{
        FS="\t";
        if ($0 ~ /^@/){
            sub(/SN\:/,"SN:chr",$0);
            sub(/dmel_mitochondrion_genome/,"M",$0);
            sub(/Mitochondrial/,"M",$0);
            print $0;
        }
        else{
            if ($3~/dmel_mito/){$3="chrM";}
            else if ($3 ~ /Mitochondrial/){$3="chrM";}
            else if ($3 ~ /\*/){;}
            else{$3 = "chr"$3;}
            print $0;
        }
    }' OFS="\t" $filename.sam > $filename.temp.sam
    samtools view -Sbh $filename.temp.sam > $filename
    echo " $filename now contains \"chr\""
done
