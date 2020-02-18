import blockchain
import hashlib
import json
import requests
from textwrap import dedent
from urllib.parse import urlparse
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request, url_for, render_template

"""
Create html pages
"""


app = Flask(__name__)

node_id = str(uuid4()).replace('-','')

blockchain = blockchain.Blockchain()

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('/layouts/main.html', title = "HOME")

@app.route('/mine', methods=['GET', 'POST'])
def mine():
    req = request.form.get('mine')

    lt_block = blockchain.last_block
    lt_proof = lt_block['proof']
    proof = blockchain.proof_of_work(lt_proof, lt_block)

    blockchain.new_transaction(sender='0', receiver=node_id, amount=1)

    previous_hash = blockchain.hash(lt_block)
    block = blockchain.new_block(proof, previous_hash)


    response = {
    'message': "Block created",
    'index': block['index'],
    'proof': block['proof'],
    'previous_hash': block['previous_hash']
    }
    return render_template('/mine.html', response=response)

@app.route('/new-transaction', methods=["GET", "POST"])
def new_tran():
    return render_template("/new-transaction.html")


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    val = request.form

    required = ['sender', 'receiver', 'amount']
    if not all(k in val for k in required):
        return "Enter all the information required", 400

    index = blockchain.new_transaction(val['sender'], val['receiver'], val['amount'])

    response = {
    'message': 'Transaction will be added to Block {}'.format(index)
    }
    return render_template('/new-transaction.html' ,message=response['message'])


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
    'message':'Valid Chain',
    'chain': blockchain.chain,
    'length': len(blockchain.chain)
    }
    return render_template('/chain.html', message=response['message'], chain=response['chain'],
                            chain_length=response['length'], len=len(response['chain']))

@app.route('/register-node', methods=['GET'])
def reg_node():
    return render_template('register-node.html')

@app.route('/node/register', methods=['POST'])
def register_nodes():
    val = request.form

    nodes = val['register']
    nodes = str(nodes)
    if nodes == None:
        return "Error: Provide a valid list of nodes !!", 400

    blockchain.register_nodes(nodes)

    response = {
    'message': "New node has been added !!",
    'total_nodes': list(blockchain.nodes)
    }
    return render_template('register-node.html',response=response)

@app.route('/node/resolve', methods=['GET'])
def resolve():
    resolved = blockchain.resolve_conflicts()
    if resolved:
        response = {
        'message': "Valid chain",
        'chain': blockchain.chain
        }
    else:
        response = {
        'message': "Valid chain",
        'chain': blockchain.chain
        }

    return render_template('/chain.html',message=response['message'], chain=response['chain'],
                            chain_length=len(response['chain']), len=len(response['chain']))




if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
