from argparse import ArgumentParser
from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()
node_id = str(uuid4()).replace('-', '')

@app.route('/test', methods=['GET'])
def test_proof():
    return str(blockchain.proof_of_work(100000))

@app.route('/transactions/new', mdddddethods=['POST'])
def new_transaction():
    value = request.get_json()
    required = ["sender", "recipient", "amount"]
    if value is None or not all(k in value for k in required):
        return 'Missing value', 400
    index = blockchain.new_transactions(value['sender'], value['recipient'], value['amount'])
    response = {
        "message": f'Transcation will be added to Block {index}'
    }
    return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transactions(sender='0', recipient=node_id, amount=1)
    block = blockchain.new_block(proof, None)
    response = {
        "message": "New Block Forged",
        "index": block['index'],
        "transactions": block['transactions'],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"]
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    value = request.get_json()
    nodes = value.get("nodes")
    if nodes is None:
        return "supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        "message": "new node added",
        "total_nodes": list(blockchain.nodes)
    }
    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            "message": "chain has been replaced",
            "new_chain": blockchain.chain
        }
    else:
        response = {
            "message": "chain is authoritative",
            "new_chain": blockchain.chain
        }
    return jsonify(response), 200

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
