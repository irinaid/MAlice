file="$1"
file=${file%.*}

python main.py $file".alice"
nasm -f elf64 $file".asm"
if [ $# == 2 ]
then
   if [ "$2" == "--show-assembly" ]; then
      echo "$(cat $file.asm)"
   fi
else
   gcc -m64 -o $file $file".o"
fi
rm $file".o"
rm $file".asm"
