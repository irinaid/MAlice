#!/bin/bash

OIFS=$IFS;
IFS="|";

simple=../../malice_examples/archaeology/*.alice;
simple_array=($simple);

for ((i=0; i<${#simple_array[@]}; ++i));
do
	echo -e "\n\n\n";	
	echo $(echo ${simple_array[$i]});
	echo -e "\n";
	echo $(python main.py ${simple_array[$i]});
	echo $(nasm -f elf64 written.asm);
	echo $(gcc -m64 -o written written.o);
	echo $(./written);
	echo -e "compared to:";
	echo $(MAlice ${simple_array[$i]} --exe);
done

#restore delimiter
IFS=$OIFS;
