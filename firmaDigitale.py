from hashlib import blake2b
import sqlite3
import os



def hashFun(tuple):
    m = blake2b(key=b'chiaveSegreta', digest_size=64)
    for tupla in tuple: 
        for attr in tupla:
            temp=str(attr)
            m.update(temp.encode('utf-8'))
    #Fine hashing di tutte le tuple della tabella
    return(m.digest())


def firmaDigitale(pathDb,nomeTabella):
    
    #cntrollo se il db esite
    dbEsiste =os.path.exists(pathDb)
    #Se non esiste lancio un eccezione
    if not dbEsiste:
        raise Exception('Db non esistente')
    
    conn=sqlite3.connect(pathDb)
    c=conn.cursor()
    #select di tutti gli elementi nella tabella
    try:
        c.execute('select * from '+nomeTabella)
        #meglio scrivere direttamente il nome della tabella?
        #O fare dei controlli?
    except:
        #Se tabella non esite lancio eccezione
        raise Exception('Tabella non esistente')
    
    
    tuple=c.fetchall() #rows contiene tutte le tuple della tabella
    conn.close()
    
    return(hashFun(tuple))
    


