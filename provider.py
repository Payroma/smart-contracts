from web3 import Web3
import json


config = json.load(open('config.json'))
w3 = Web3(Web3.HTTPProvider(config['network']['rpc']))

if not w3.isConnected():
    raise ConnectionError("( %s ) Provider is disconnected" % config['network']['rpc'])
