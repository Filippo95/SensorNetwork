# SensorNetwork (Progetto Ricerca Operativa)

## Il Problema
Sono dati n sensori installati in altrettanti siti. ogni sensore s riesce a trasmettere dati a qualunque altro sensore entro una distanza ds che dipende dalla morfologia circostante.  Una volta installato un apposito dispositivo in un sito, questo può raccogliere le informazioni da tutti i sensori vicini, e instradarli sulla rete che collega i dispositivi. Noto il costo di un dispositivo e di ogni potenziale collegamenti fra siti, deeterminare la retee di costo minimo (qnauti dispositivi installare e su che nodi e come collegare i nodi) in modo che ogni sensore sia collegato).
Potreste considerare la variante capacitata del problema (i sensori hanno ciascuno una data domanda e i dispositivi possono essere di k tipi diversi, ciascuno con un costo e una capacità massima)

## Analisi
Il problema  è composto sostanzialmente da due problemi principali:
1. Dove installre i concentratori (presso quali sensori)? 
   
2. Come collegare i concentratorri tra di loro per minimizzare il cammino (problema cammino minimo)

### I dispositivi
Ogni sensore è composto da diversi attributi, tra cui:
* latitudine
* longitudine
* portata (in metri)
* send_rate (in messaggi/secondo)  
  
Quindi ogni sensore è definito da un punto sulla mappa che ha un certo raggio di copertura (portata) e invia i messaggi al dispositivo gateway con una certa frequenza.  

Ogni gaateway è composto da altrettanti attributi:
* latitudine
* longitudine
* costo
* capacità di elaborazione   

Ogni dispositivo gateway è caratterizzato da un punto sulla mappa quindi un costo di installazione e una cpacità di elaborazione, ovvero quanti messaggi al secondo è in grado elaborare.   

Il dispositivo gateway quindi, sarà installato nello stesso punto di un sensore e sarà in grado di recepire i dati di tutti i sensori che con il loro raggio di copertura riescono a comunicare con questo dispositivo installato in quella posizione.  
Inoltre bisognerà tenere conto anche della capacità del dispositivo gateway, in quanto limitata, questo costituisce un problema, infatti bisognerà controllare che la capacità necessaria per riceve i dati dei sensori (vicini) sia congrua con la capacità del gateway, in caso contrario bisogna scegliere quali sensori servire.  
Un'altro problema da affrontare è la minimizzazione del costo, quindi scegliere il gateway appropriato anche considerando il costo di installazione.  

Al fine di risolvere il problema è stato generato un "catalogo" di gateway, abbiamo inoltre considerato il problema della disponibilità in termini di quantità di gateway, bbiamo ipotizzato di avere diveresi modelli di gateway installabili, che si differenziano per costo e capacità e quantità disponibile.   

## Approcci risolutivi
### Primo Aprroccio
Un primo approccio risolutivo del problema è quello che consideera l'utilizzo di una greedy, che come best possibili abbia:
* massimizzare il rapporto costo/sensori coperti
* massimizzare il rapporto capacità/costo
* massimizzare lo score, ovvero un punteggio calcolaato sulla base del rapporto costo/sensori coperti e ..... *****!!!TODO!!!*****   

La greedy quindi restituisce una soluzione che è l'insieme dei gateway,  la scelta dei dispositivi da installare, e il luogo in cui installarli, e quali sensori servire con un certo dispositivo.   
All'interno della greedy vengono quindi affrontati tre problemi:
* dove installare il dispositivo
* quale dispositivo installare
* quali sensori servire 

In un secondo momento, attraverso l'algoritmo di kruskal viene costruito il grafo minimo di copertura (minimum spanning tree), che ci da informazione su come collegare i dispositivi tra di loro, iporizzando che il costo di collegamento tra un dispositivo gateway ed un'altro dipenda solamente dalla distanza in linea d'aria.    

Le soluzioni trovate vengono poi migliorate attraverso algostimi di ricerca locaale come:
### Secondo Approccio
Risolvendo il problema, ci siamo resi conto che la soluzione trovata dalla funzione greedy potrebbe essere in realtà non ottima per il problema del MST, quindi innalzare notevolmente il costo di interconnessione dei dispositivi, anche se la scelta fatta dalla greedy è corretta.   
Questo può capitare in quanto la greedy non ha una visione globale dle problema, ma si limita a risolvere il problema di installazione dei dispositivi.  
A questo punto quindi abbiamo pensato di dare alla greedy una visione più completa del problema che stiamo risolvendo, quindi inserire ad ogni iterazione della greedy il calcolo del MST quindi la greedy valuta ogni sensore da poter installare minimizzando il costo di installazione del gateway più il costo del MST.   
In questo modo cosidererà anche il problema che l'algoritmo poi andrà a risolvere in un secondo momento.  
Questo però ci porta ad avere un costo computazionale elevatissimo che quindi si avvicina all'enumerazione delle soluzioni, ovvero l'unico modo per risolvere un problema di classe NP-Hard.  
Questo secondo approccio è state implementato al solo scopo di valutare le soluzioni che abbiamo ottenuto con il primo approccio, in modo da fornire una stima ottimistica che si avvicini però il più possibili alla soluzione ottima, in quesot modo abbiamo potuto valutare la bontà delle soluzioni ottenute dal primo apporccio, con un costo computazionale più basso. 

## L'Algoritmo 



