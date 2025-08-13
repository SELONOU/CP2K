while IFS=" " read -r i;
do
g16 <"$i".com> "$i".log
done < files1
