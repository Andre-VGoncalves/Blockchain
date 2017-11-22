import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.current_transaction = []
        self.chain = []

        #Cria o bloco genesis
        self.new_block(previous_hash = 1, proof = 100)

    def new_block(self):
        #Cria um novo bloco e adiciona ao Chain
        pass

    
    def new_transaction(self):
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
        pass


    @property
    def last_block(self)
    #devolve o ultimo bloco
        pass