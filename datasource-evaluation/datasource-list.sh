#!/bin/bash
#Busca os dados através do Holmes-Admin para verificar se existem Datasources duplicados;
cd ..
./holmes-admin get stats > stats
sleep 30
#Gera dois arquivos com base no resultado obtido através do Holmes;
cat stats |grep "insert into" |awk '{print$3}' |sort > stats.new && cat stats |grep "insert into" |awk '{print$3}' |sort |uniq > stats.uniq
#Avalia as diferenças entre os arquivos;
diff stats.new stats.uniq > stats.final
#diff stats.new stats.uniq >> stats.final #Linha de diff para forçar o funcionamento do script criando o arquivo stats.final manualmente com conteúdo aleatório
if [ -s stats.final ]
then
	cp mail	msg
	cat stats.final >> msg
	#/usr/sbin/sendmail -t < msg
	#rm -f stats stats.new stats.uniq msg stats.final
else
	#rm -f stats stats.new stats.uniq stats.final
fi 
