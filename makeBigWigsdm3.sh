#!bin/bash
#usage : sh makeBigWigs.sh <directory name>
#converts all wig files in directory $1 to bigWigss
for filename in $1/*.wig; do
    echo "processing $filename..."
    awk -F, '{
        FS=" ";
        if ($1~/dmel_mito/ && NR>1){$1="chrM";}
        else if (NR>1){$1 = "chr"$1;}
        else{;}
        print $0;
    }' OFS=" " $filename > $filename.temp
    #added to try some problematic wigs,  usually jsut use wigToBigWig
    #tail -n +2 $filename.temp | sed 's/ /\t/g' | bedtools sort -i - > $filename.temp2
    #bedtools slop -i $filename.temp2 -g ./encValData/dm3/chrom.sizes -b 0 > $filename.temp3
    #awk -F, '{FS="\t"}{if ($3<$2){;}else {print $0}}' OFS="\t" $filename.temp3 > $filename.temp4
    #bedtools sort -i $filename.temp4 > $filename.temp5
    #./bedGraphToBigWig $filename.temp5 ./encValData/dm3/chrom.sizes ${filename%.wig}.bw
    # -clip option to issue warning messages rather than dying if wig file contains items off end of chromosome.
    # some wig files had chr3RHet extending more than listed in chrom.sizes
    ./wigToBigWig -clip $filename.temp ./encValData/dm3/chrom.sizes "${filename%%.wig}.bw"
    #echo " $filename converted to BigWig"
done

