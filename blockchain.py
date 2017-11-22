import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
from hashlib import sha256

import requests
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transaction = []
        

        #Cria o bloco genesis
        self.new_block(previous_hash = 1, proof = 100)

    def new_block(self, proof, previous_hash = None):
        #Cria um novo bloco e adiciona ao Chain
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


    @property
    def last_block(self):
    #devolve o ultimobloco
        return self.chain[-1] 
