import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from hashlib import sha256
from textwrap import dedent
import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transaction = []
        self.nodes = set()
        

        #Cria o bloco genesis
        self.new_block(previous_hash = 1, proof = 100)



    def register_node(self, address):
        """
        adciona um novo nó para lista de nó.
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)



    def valid_chain(self, chain):
        """
        determina se o blockchain é valido
        param chain: <list> um blockchain
        return bool
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print (f'{last_block}')
            print (f'{block}')
            print ("\n-----------\n")
            # checa se o hash do bloco esta correto
            if block['previous_hash'] != self.hash(last_block):
                return False

            #chegando se a prova de trabalho é correto
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        

        return True


    def resolve_conflicts(self):

        """
        essa parte serve para resolver conflitos
        substituindo nossos nós por nós mais longos
        """
        neighbours = self.nodes
        new_chain = None
        #procurando hash mais longos
        max_length = len(self.chain)
        #verifica os nós de todos blocos
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                #verificar se comprimento é longo e se os blocos são validos
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        #
        if new_chain:
            self.chain = new_chain
            return True

        return False
        



    def new_block(self, proof, previous_hash = None):
        #Cria um novo bloco e adiciona ao blockChain
        """
        proof: <int> a prova dada pelo algoritmo Prova do trabalho
        previous_has:(opt)<str> o hash do bloco anterior
        return: <dict> novo bloco
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])

        }

        #redifini a lista atual de transações
        self.current_transaction = []

        self.chain.append(block)
        return block


    @property
    def last_block(self):
    #devolve o ultimobloco
        return self.chain[-1] 



    def new_transaction(self, sender, recipient, amount):
        #adciona uma nova transação a lista
        """
        Cria uma nova transação que entra no ultimo bloco
        parametro 'sender': <str> é o endereço do remetente
        'recipient': <str> endereço do destinatario
        'amount': <int> valor da transação
        return <int> o indice do bloco que realizara a transação
        """
        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1
        

    @staticmethod
    def hash(block):
        #hash do bloco.
        """
        Cria um SHA-256 que é op Hash do bloco
        param block: <dict> Block
        return: <str>
        """
        #Devemos ter certeza que o dicionario esta ordenado ou teremos hash inconsistentes
        block_string = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        encontra um numero p tal que a hash é pp que contem 4 zeros, onde p é o hash anterior
        p é a prova anterior, e p é a nova prova
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof +=1
        
        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova verifica se contem 4 zeros

        param last_proof: <int> uma prova anterior
        param proof: <int> prova atual
        return: <bool> se estiver correto retorna True se não retorna False
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
        

#instancia do nó
app = Flask(__name__)


#gerra um endereço global para o nó
node_identifier = str(uuid4()).replace('-', '')


#instancia do blackchain
blockchain = Blockchain()
    

@app.route('/mine', methods = ['GET'])
def mine():
    #recuperamos a ultima prova para pegar a proxima prova
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #devemos  receber uma recompensa por minerar
    # remedente 0 para indicar que extraiu uma nova moeda
    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block forged",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/transaction/new', methods = ['GET'])
def new_transaction():
    values = request.get_json()

    #checa que o requirimento são no Post
    required = ['sender', 'recipient', 'amount']
    if not all (k in values for k in required):
        return "Missing values", 400

    #criando uma nova transação
    index = blockchain.new_transaction(values['sender'], values ['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods = ['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200



@app.route('/nodes/register', methods = ['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods = ['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200



if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default = 5000, type = int, help = 'port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host = '0.0.0.0', port = 5000)
