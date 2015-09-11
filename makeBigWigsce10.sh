#!bin/bash
#usage : sh makeBigWigs.sh <directory name>
#converts all wig files in directory $1 to bigWigss
for filename in $1/*.wig; do
    echo "processing $filename..."
    # -clip option to issue warning messages rather than dying if wig file conta            ins items off end of chromosome.
    # some wig files had chr3RHet extending more than listed in chrom.sizes
    wigToBigWig -clip $filename /raid/modencode/DCC/fileupload/encValData/ce10/c            hrom.sizes "${filename%%.wig}.bw"
    #echo " $filename converted to BigWig"
done

