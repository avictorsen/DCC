#!bin/bash
#usage : sh makeBigWigs.sh <directory name>
#converts all wig files in directory $1 to bigWigss
for filename in $1/*.wig; do
    echo "processing $filename..."
    awk -F, '{
        FS="\t";
        if ($1 ~ /^CHROMOSOME_/){
            sub(/CHROMOSOME\_/,"chr",$1);
            sub(/MtDNA/,"M",$1);
            print $0;
        }
        else{
            print $0;
        }
    }' OFS="\t" $filename > $filename.temp.wig
    mv $filename.temp.wig $filename
    echo " $filename now contains \"chr\""

    # -clip option to issue warning messages rather than dying if wig file contains items off end of chromosome.
    # some wig files had chr3RHet extending more than listed in chrom.sizes
    ./wigToBigWig -clip $filename /home/avictorsen/DCC/encValData/WS245/chrom.sizes "${filename%%.wig}.bw"
    #echo " $filename converted to BigWig"
done

