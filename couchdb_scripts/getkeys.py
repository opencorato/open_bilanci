import sys
import couchdb
import json
import argparse
from couchdb.design import ViewDefinition
from pprint import pprint

def quadro4_getkeys(doc):
    all_keys = {
        'a':[],
        'b':[],
        'c':[]
    }

    possible_values = {
        'a':['quadro-4-a-impegni','quadro-4-a-impegni-1'],
        'b':['quadro-4-b-pagamenti-in-conto-competenza','quadro-4-b-pagamenti-in-conto-competenza-1'],
        'c':['quadro-4-c-pagamenti-in-conto-residui','quadro-4-c-pagamenti-in-conto-residui-1']
    }

    for titolo_key,titolo_values in possible_values.iteritems():
        for titolo_name in titolo_values:
            if titolo_name in doc['consuntivo']['04'].keys():
                for sottovoce in doc['consuntivo']['04'][titolo_name]['data'].keys():
                    clean_sottovoce = sottovoce.lower().strip()
                    # se presente toglie il carattere - iniziale
                    try:
                        if clean_sottovoce.index('- ') == 0:
                            clean_sottovoce = clean_sottovoce[2:]
                    except ValueError:
                        pass

                    all_keys[titolo_key].append(clean_sottovoce)

    all_keys['a']=sorted(all_keys['a'])
    all_keys['b']=sorted(all_keys['b'])
    all_keys['c']=sorted(all_keys['c'])
    yield ('key', all_keys)



def titoli_getkeys(doc):
    # funzione che raccoglie per tutti i bilanci tutti i nomi
    # dei titoli, quadro per quadro
    ignored_keys =["_rev", "_id"]
    if doc:
        for doc_keys in doc.keys():
            if doc_keys not in ignored_keys:
                tipo_bilancio = doc_keys
                for quadro_n, quadro_v  in doc[tipo_bilancio].iteritems():

                    # genera una chiave che contiene tipo di bilancio, quadro e la voce
                    # il valore 1 ci permette di fare somme con la reduce function _sum()
                    for nome_titolo in quadro_v.keys():
                        yield ([tipo_bilancio,quadro_n,nome_titolo,doc['_id'][:4]],1)



def main(argv):
    parser = argparse.ArgumentParser(description='Get Titolo names and voce labels from bilanci')
    server_name = None
    check_function= None

    accepted_servers = {
        'localhost': {
            'host': 'localhost',
            'port': '5984',
            'user': '',
            'password':'',
            'db_name':'bilanci_raw'

        },
        'staging': {
            'host': 'staging.depp.it',
            'port': '5984',
            'user': 'op',
            'password':'op42',
            'db_name':'bilanci'
        },
    }


    parser.add_argument('--server','-s', dest='server_name', action='store',
                   default='localhost',
                   help='Server name: localhost | staging')

    parser.add_argument("--check-function","-ck", help="check function after synch",
                    action="store_true")

    args = parser.parse_args()
    server_name= args.server_name
    check_function= args.check_function

    if server_name and check_function:
        # costruisce la stringa per la connessione al server aggiungendo user/passw se necessario
        server_string ='http://'
        if accepted_servers[server_name]['user']:
            server_string+=accepted_servers[server_name]['user']+":"
            if accepted_servers[server_name]['password']:
                server_string+=accepted_servers[server_name]['password']+"@"

        server_string+=accepted_servers[server_name]['host']+":"+accepted_servers[server_name]['port']

        print "Connecting to:"+server_string
        # open db connection
        server = couchdb.Server(server_string)
        db = server[accepted_servers[server_name]['db_name']]
        # sync the view
        view = ViewDefinition('tree_getkeys', 'cons_titoli_getkeys', map_fun=titoli_getkeys, reduce_fun='_sum()', language='python')
        view.sync(db)

        if check_function:
            # get view values
            check = db.view('tree_getkeys/cons_titoli_getkeys')




# launches main function
if __name__ == "__main__":
   main(sys.argv[1:])
