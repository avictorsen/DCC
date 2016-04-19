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
    # -clip option to issue warning messages rather than dying if wig file contains items off end of chromosome.
    # some wig files had chr3RHet extending more than listed in chrom.sizes
    ./wigToBigWig -clip $filename.temp ./encValData/dm3/chrom.sizes "${filename%%.wig}.bw"
    #echo " $filename converted to BigWig"
    
done

