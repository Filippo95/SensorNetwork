# SensorNetwork (Progetto Ricerca Operativa)

## Il Problema
Sono dati n sensori installati in altrettanti siti. Ogni sensore s riesce a trasmettere dati a qualunque altro sensore entro una distanza ds che dipende dalla morfologia circostante.  Una volta installato un apposito dispositivo in un sito, questo può raccogliere le informazioni da tutti i sensori vicini, e instradarli sulla rete che collega i dispositivi. Noto il costo di un dispositivo e di ogni potenziale collegamenti fra siti, determinare la rete di costo minimo (quanti dispositivi installare e su che nodi e come collegare i nodi) in modo che ogni sensore sia collegato).
Potreste considerare la variante capacitata del problema (i sensori hanno ciascuno una data domanda e i dispositivi possono essere di k tipi diversi, ciascuno con un costo e una capacità massima)

## Analisi
Il problema, secondo la nostra modellazione, è composto sostanzialmente da due problemi principali:
1. Dove installre i concentratori (presso quali sensori)? 
   
2. Come collegare i concentratorri tra di loro per minimizzare il cammino (problema cammino minimo)

### I dispositivi
Cerchiamo quindi di modellare il problema, quindi, ogni sensore è composto da diversi attributi, tra cui:
* latitudine
* longitudine
* portata (in metri)
* send_rate (in messaggi/secondo)  
  
Quindi ogni sensore è definito da un punto sulla mappa che ha un certo raggio di copertura (portata) e invia i messaggi al dispositivo gateway con una certa frequenza.  

Ogni gateway è composto da altrettanti attributi:
* latitudine
* longitudine
* costo
* capacità di elaborazione   

Ogni dispositivo gateway è caratterizzato da un punto sulla mappa quindi un costo di installazione e una capacità di elaborazione, ovvero quanti messaggi al secondo è in grado elaborare.   

Il dispositivo gateway quindi, sarà installato nello stesso punto di un sensore e sarà in grado (potenzialmente) di recepire i dati di tutti i sensori che con il loro raggio di copertura riescono a comunicare con questo dispositivo installato in quella posizione.  
Inoltre bisognerà tenere conto anche della capacità del dispositivo gateway, in quanto limitata, questo costituisce un problema, infatti bisognerà controllare che la capacità necessaria per riceve i dati dei sensori (vicini) sia congrua con la capacità del gateway, in caso contrario bisogna scegliere quali sensori servire.  
Un altro problema da affrontare è la minimizzazione del costo, quindi scegliere il gateway appropriato anche considerando il costo di installazione.  

Al fine di risolvere il problema è stato generato un "catalogo" di gateway, abbiamo inoltre considerato il problema della disponibilità in termini di quantità di gateway, abbiamo ipotizzato di avere diversi modelli di gateway installabili, che si differenziano per costo e capacità e quantità disponibile.   

## Approcci risolutivi
### Primo Aprroccio
Un primo approccio risolutivo del problema è quello che considera l'utilizzo di una greedy, che come best possibili abbia:
* massimizzare il rapporto costo/sensori coperti
* massimizzare il rapporto capacità/costo
* massimizzare lo score, ovvero un punteggio calcolato sulla base del rapporto costo/sensori coperti e ..... *****!!!TODO!!!*****   

La greedy quindi restituisce una soluzione che è l'insieme dei gateway, la scelta dei dispositivi da installare, e il luogo in cui installarli, e quali sensori servire con un certo dispositivo.   
All'interno della greedy vengono quindi affrontati tre problemi:
* dove installare il dispositivo
* quale dispositivo installare
* quali sensori servire 

In un secondo momento, attraverso l'algoritmo di kruskal viene costruito il grafo minimo di copertura (minimum spanning tree), che ci da informazione su come collegare i dispositivi tra di loro, iporizzando che il costo di collegamento tra un dispositivo gateway ed un'altro dipenda solamente dalla distanza in linea d'aria.    

Le soluzioni trovate vengono poi migliorate attraverso algoritmi di ricerca locale come destroy and repair.
### Secondo Approccio (branch develop)
Risolvendo il problema, ci siamo resi conto che la soluzione trovata dalla funzione greedy potrebbe essere in realtà non ottima per il problema del MST, quindi innalzare notevolmente il costo di interconnessione dei dispositivi, anche se la scelta fatta dalla greedy è corretta.   
Questo può capitare in quanto la greedy non ha una visione globale dle problema, ma si limita a risolvere il problema di installazione dei dispositivi.  
A questo punto quindi abbiamo pensato di dare alla greedy una visione più completa del problema che stiamo risolvendo, quindi inserire ad ogni iterazione della greedy il calcolo del MST quindi la greedy valuta ogni sensore da poter installare minimizzando il costo d'installazione del gateway più il costo del MST.   
In questo modo cosidererà anche il problema che l'algoritmo poi andrà a risolvere in un secondo momento.  
Questo però ci porta ad avere un costo computazionale elevatissimo che quindi si avvicina all'enumerazione delle soluzioni, ovvero l'unico modo per risolvere un problema di classe NP-Hard.  
Questo secondo approccio è state implementato al solo scopo di valutare le soluzioni che abbiamo ottenuto con il primo approccio, in modo da fornire una stima ottimistica che si avvicini però il più possibili alla soluzione ottima, in questo modo abbiamo potuto valutare la bontà delle soluzioni ottenute dal primo apporoccio, con un costo computazionale più basso. 

## Risoluzione
Ai fini pratici abbiamo definito cinque classi di dispositivi:
* Classe 0: Capacità 8, costo 6, un dispositivo molto limitato, ma anche molto economico, si pensi a microcontrollori come ad esempio ESP32
* Classe 1: Capacità 15, costo 14, un dispositivo di costo limitato, come potrebbe essere un arduino
* Classe 2: Capacità 25, costo 25, un dispositivo economico ma che garantisce un buon rapporto qualità costo, si pensi tipo ad un raspberyy pi zero
* Classe 3: Capacità 50, costo 75, un dispositivo costoso si ma anche molto potente, si pensi aad un raspberry pi 3
* Classe 4: Capacità 100, costo 175, dispositivo decisamente performante ma ovviamente molto costo come potrebbe essere un jetson nano

Abbiamo supposto che il numero di dispositivi disponibili per ciascuna classe sia maggiore per la Classe 0 e man mano che aumenta il costo diminuisca la disponibilità di tali dispositivi, ad esempio: 
infiniti dispositivi disponibili per la classe 0, 500 per la classe 1, 100 per la classe 2, 20 per la classe 3, 4 per la classe 4. 

A questo punto abbiamo un certo numero di sensori, installati in determinati punti, e un catalogo di dispositivi disponibili in determinate quantità. 
### Greedy
La ricerca greedy quindi ha diversi input, ovvero la lista di sensori da coprire, la lista dei gateway disponibili e lo scenario, order_by e pack_by.
#### Lo Scenario 
Abbiamo definito una struttura dati, chiamata scenario per identificare un dizionario Key->Value, dove per Key abbiamo l'id del sensore e come value una struttura dati contenente:
* Senders: una lista di ID dei sensori che con il loro raggio di copertura possono arrivare a comunicare con il sensore con ID la Key, quindi sarebbero tutti gli ID dei sensori che potrebbero comunicare, se il gateway fosse installato in quel punto, quindi dove è situato il sensore con quell'ID. 
* tot_capacita: un numero che identifica la capacità necessaria per coprire tutti i sensori che potrebbero comunicare con il gateway installato in quella posizione.
* rapp_cap_costo: ovvero il rapporto tra la capacità totale necessaria (tot_capacita) e il costo del gateway migliore (che supporta tale capacità).
* rapp_numsensori_costo: il rapporto tra il numero di sensori che vengono coperti e il costo del dispositivo necessario per coprirli. 
Questo dizionario viene quindi ordinato sulla base di uno degli attributi o rapp_cap_costo oppure rapp_numsensori_costo.   
  

La ricerca Greedy quindi prende in ingresso il parametro order_by che serve per poter ordinare lo scenario che viene calcolato ad ogni iterazione, ovvero dopo aver scelto d'installare un gateway in una certa posizione.   
Il parametro pack_by serve nel momento in cui si decide quali sensori servire con un dato gateway.   
La scelta di quali sensori coprire di configura come un problema di zaino-binario ovvero abbiamo una capacità limitata di "spazio" (capacità del gateway scelto) e un insieme di sensori che possono essere scelti quindi inseriti nello zaino.   
L'obiettivo è quello di occupare tutta la capacità del gateway scelto, inoltre il sensore presso il quale decidiamo d'installare il gateway è sempre coperto.   
A questo punto abbiamo scelto di dare la possibilità di prioritizzare la scelta dei sensori da coprire con il parametro pack_by che può avere due possibili valori:
* capacità: in questo modo andiamo a ordinare la lista dei possibili senders sulla base della send_rate ovvero prioritizziamo i sensori che mandano più dati
* distanza: in questo caso andiamo a ordinare la lista dei possibili senders in base al rapporto send_rate/ distanza quindi prioritizziamo i sensori con send rate più alta e che sono più vicini al gateway installato.    

Una volta determinata la lista ordinata per il criterio scelto dei sensori che possono comunicare con il gateway installato in quella posizione andiamo a scorrerla e quindi a prendere il primo sensore nella lista, controllare se ci sta, se ci sta allora lo eliminiamo da quelli possibili e lo aggiungiamo a quelli coperti.    

Ovviamente questo problema di zaino binario viene risolto solo ne caso in cui la capacità richiesta è maggiore della capacità disponibile, diversamente si servono tutti i sensori che riescono a comunicare con il gateway.    

A questo punto la greedy ha trovato scelto il sensore presso cui installare il gateway grazie all'ordinamento dello scenario, ha trovato il tipo di gateway da utilizzare, di conseguenza ha scelto quali sensori servire con l'opzione pack_by, quindi può popolare la struttura dati che rappresenta la soluzione. 

Riassumendo la greedy:
* per ogni elemento nello scenario:    
    * cerco il gateway in base alla capacità necessaria
    * se la capacità richiesta è > della capacità offerta dal gateway scelto:
        * trovo i sensori serviti con la risoluzione del zaino binario
    * altrimenti:
        * tutti i sensori vengono serviti
    * aggiungo alla soluzione finale la struttura dati con il sensore il gateway installato e i sensori coperti 
    * aggiungo al costo totale il costo d'installazione de gateway selezionato a questa iterazione 
    * tolgo i sensori serviti da quelli ancora da servire 
    * ricalcolo lo scenario
    
La greedy quindi ci restituisce una soluzione che è un dizionario Key->Value in cui value è:
```json
{
 "sensor_id": "id_sensore in cui viene installato",
 "latitudine": "latitudine del sensore",
 "longitudine": "longitudine del sensore",
 "classe": "0 o 1 o 2 o 3 o 4",
 "costo": "costo del gateway",
 "max_capacity": "capacità del gateway",
 "sensor_covered": [ "array di id dei sensori coperti"]
}
```
### Minimum Spanning Tree 
Una volta trovata la soluzione, quindi dove installare i gateways, la seconda parte del problema da risolvere è cercare di collegare questi gateway, minimizzando il costo di collegamento.    
Per affrontare questo problema bisogna innanzitutto chiarire cosa si intend per costo di collegamento tra un gateway e un altro. 
Il costo di collegamento tra un gateway e un altro può essere dovuto a diversi fattori, ovvero il costo dell'infrastruttura di comunicazione, assetto territoriale, ecc. 
Di fatto per semplicità abbiamo definito il costo di collegamento come la distanza tra i due gateway/1000.     

Lo scopo della procedura è quindi trovare un albero di copertura di costo minimo. 
Per realizzare questa procedura abbiamo implementato l'algoritmo di Kruskal, che genera un albero di supporto minimo di un grafo non orientato co archi con costi non negativi.    
La soluzione fornita dall'algoritmo di Kruskal è ottima.      

L'idea su cui si basa è: ordiniamo gli archi in ordine crescente di costo e successivamente li analizziamo singolarmente, si inserisce un arco nella soluzione se non forma cicli con gli archi precedentemente selezionai, se ad ogni passo ci sono archi con lo stesso costo la scelta è indifferente.         

Il costo computazionale dell'algoritmo è nel caso peggiore O(E * log(V)) dove E è il numero di archi ed V il numero di vertici.      

La procedura quindi prevede la costruzione di due strutture vertices ( che contiene i nodi del grafo) e edges (che contiene glia rchi del grafo).   
Ogni arco è quindi descritto da una struttura dati del tipo :
```json
{
  "node_one": "nodo1",
  "node_two": "nodo2",
  "costo": "distanza tra nodo1 e nodo2 / 1000"
}
```
Abbiamo quindi che si crea grafo creando un arco per ogni nodo a ogni nodo per poi "ripulirlo", quindi otteniamo un grafo completamente connesso, per poi rimuovere i duplicati, poichè vogliamo creare un grafo semplice e non un multigrafo.      
Ordiniamo quindi gli archi sulla base del costo.     
Per ogni arco finchè il numero di archi della soluzione è < del numero di vertici -1
* aggiungiamo l'arco alla soluzione
* se la soluzione ha cicli:
    * togliamo l'arco dalla soluzione
* elimino l'arco appena selezionato da quelli ancora da considerare. 

La funzione più impegnativa è sicuramente la funzione che controlla se esistono cicli all'interno della soluzione appena creata.     
Per realizzare la funzione infatti è necessario implementare una visita del grafo, in particolare abbiamo implementato una visita depth-first, in profondità.    
La funzione ha_cicli semplicemente crea una struttura dati vertices_to_visit che contiene tutti i vertici da visitare.    
A questo punto richiama una funzione ricorsiva chiamata depth_first_visit che prende in ingresso la lista dei archi, il vertice di partenza, i vertici visitati, i vertici aperti, i vertici sinistri.    
```python
def depth_first_visit(edge_list, this_vertex, visited_vertices, opened_vertices, vertices_left)
```
Trovo i vertici raggiungibili partendo dal vertice attuale.     
per ogni vertice raggiungibile se non è già stato aperto e se non è il genitore di questo vertice lo aggiungo in testa alla lista dei vertici aperti.    

Verifico che fra i vertici raggiungibili (a parte il genitore ), c'è uno dei vertici già visitati, 
    *   se c'è allora c'è un ciclo. 
    *   altrimenti proseguo in profondità   

Verifico che la lista dei vertici aperti non sia nulla:
* se è non è nulla trovo il prossimo vertice da analizzare e tolgo dai vertici aperti il corrente 
* se è nulla allora verifico che sia di lunghezza 0 
    * sono riuscito a visitare tutti i nodi del grafo e non ho trovato cilici quindi ritorno False
    * assegno il prossimo vertice
    
Richiamo ricorsivamente la stessa funzione con vertice corrente il vertice selezionato come prossimo 

## Controllo ammissibilità 
A questo punto, siamo riusciti a trovare delle soluzioni che però non abbiamo la certezza che siano ammissibili.   
Per chiarire questo abbiamo bisogno di definire i criteri di ammissibilità delle soluzioni, ovvero cos'è che differenzia una soluzione ammissibile da una non ammissibile.     
Una soluzione ammissibile deve:
* Tutti i sensori devono essere coperti da un gateway (un solo gateway)
* La capacità di un gateway non può essere inferiore di quella necessaria per coprire i sensori che gli sono stati assegnati. In altre parole nessun gateway può coprire capacità superiore al proprio massimo    
* un sensore non può essere coperto da più gateway (single demand)
* in un sito può essere installato solo un gateway

Abbiamo quindi implementato un funzione che controlla l'ammissibilità controllando questi criteri:
```python
def controlla_ammisibilita(solution):
    if not tutti_sensori_coperti(solution):
        return False, "Non tutti i sensori sono stati coperti!"
    if not gateway_capacity(solution):
        return False, "Alcuni gateway coprono capacità superiori al loro massimo!"
    if not single_demand(solution):
        return False, "Alcuni sensori sono coperti da più gateway!"
    if not only_one_gw_per_site(solution):
        return False, "Più gateway sono installati nello stesso sito!"
    return True, "OK"
```

## Ricerche locali 
A questo punto, siamo riusciti a trovare delle soluzioni che rispetta i criteri di ammissibilità, ha un alberto di copertura di costo minimo (MST), però può essere ancora migliorata in termini di costo.     
Per fare questo abbiamo utilizzato due tecniche di ricerca locale.
### Large neighborhood search
Questa tecnica si ricerca locale cerca di trovare soluzioni migliori vicine alla soluzione di partenza. L'intorno di una soluzione è l'insieme di soluzioni ammissibili ottenute da modifiche relativamente semplici alla soluzione originale.    
Le strategie di Large Neighborhood Search fanno parte della famiglia di Very Larghe Neighborhood Search, determinano l'intorno tramite una operazione di destroy e di rapair.    
* L'operatore destroy distrugge parte della soluzione corrente, scelta attraverso una procedura non deterministica in modo che la parte modificata vari ad ogni iterazione.
* L'operatore repair assegna alle variabili cancellate un valore che renda la soluzione ammissibile.     

Il tasso % di distruzione caratterizza l'intorno.      
Per questa procedura si ripete per n iterazioni, che definiamo arbitrariamente.    
Di fatto viene distrutta parte della soluzione, il 30% dei gateway vengono rimossi e i sensori serviti da quei gateway dovranno essere riassegnati ad altri gateway.     
La scelta dei gateway da distruggere è basata sul costo, ovvero se consideriamo 100 gateway, allora elimineremo dalla soluzione corrente i 30 gateway più costosi (con costo di installazione più alto).    
Successivamente viene eseguita l'operazione repair, che di fatto esegue la greedy solo sui sensori ancora da assegnare, unendo la parte di soluzione non distrutta alla nuova soluzione parziale possiamo ottenere una soluzione completa, quindi verifichiamo l'ammissibilità.         
Se la soluzione nuova ottenuta ha un costo (costo di installazione dei gateway + Minimum Spannin Tree) minore della soluzione precedente allora  viene considerata la soluzione attuale sulla base della quale verranno costruiti gli eventuali e successivi miglioramenti.      


### Altra
fare prima spanning tree poi fare gateway pag 137


## Rappresentazioni grafiche delle soluzioni
Per aiutarci nella comprensione di cioè che l'algoritmo restituisce, abbiamo utilizzato una libreria python chiamata folium che permette agilmente di creare mappe con grafi e altri elementi grafici.     
Abbiamo quindi creato diverse rappresentazioni:
* i sensori: questa rappresentazione ci permette di visualizzare dove sono posizionati i sensori e il loroo raggio di copeertura. 
  ![alt text](./img/sensors.png)
* la soluzione: possiamo vedere dove vengono posizionati i gateway e quali sensori vengono coperti da un certo gateway. 
  ![alt text](./img/solution.png)
* mst: rappresentiamo il Minimum Spannin Tree
  ![alt text](./img/mst.png)
* full solution: rappresentiamo tutti i sensori collegati ai gateway e i gateway collegati attraverso l'mst. 
  ![alt text](./img/full.png)
* full-difference: rappresentiamo due soluzione complete per verificare come sono cambiate, questa rappresentazione viene utilizzata dopo la ricerca locale per verificare le differenze tra la soluzione originale e la soluzione migliore trovata.           
  ![alt text](./img/difference.png)
## Computazioni



## Conclusioni e Grafici

    


