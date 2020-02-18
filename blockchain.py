import hashlib
import json
import requests
from textwrap import dedent
from urllib.parse import urlparse
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
        'index': len(self.chain) + 1,
        'timestamp': time(),
        'transactions': self.current_transactions,
        'proof': proof,
        'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender, receiver, amount):
        self.current_transactions.append({
        'sender': sender,
        'receiver': receiver,
        'amount': amount
        })

        return self.last_block['index'] + 1


    def proof_of_work(self, last_proof, last_block):
        proof = 0
        while self.valid_proof(last_proof, proof, self.hash(last_block)) is False:
            proof += 1
        return proof

    def register_nodes(self, address):
        node_url = urlparse(address)
        if node_url.netloc:
            self.nodes.add(node_url.netloc)
        elif node_url.path:
            self.nodes.add(node_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print("Last block: ".format(last_block))
            print("Block: ".format(block))
            print('-'*40)

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof'], self.hash(last_block)):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for nodes in neighbours:
            response = requests.get("http://{}/chain".format(nodes))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        valid if the hash contains 4 leading 0's
        """
        correct = f'{last_proof}{proof}{last_hash}'.encode()
        correct_hash = hashlib.sha256(correct).hexdigest()
        return correct_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
