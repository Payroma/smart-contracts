from provider import config, w3
import os
import sys
import json


def run():
    global abi, bytecode, contract

    # Validation
    try:
        contract_name = sys.argv[1]
        constructor_args = eval(sys.argv[2])
        contract_file_name = sys.argv[3]
    except IndexError:
        raise KeyError(
            """Unexpected Parameters EX: deploy.py ContractName "('ConstructorArgs1')" FileName.sol"""
        )

    # Initialize
    public_key = config['owner']['publicKey']
    private_key = config['owner']['privateKey']
    build_dir = os.path.join('build', contract_name)
    with open(os.path.join(build_dir, 'compiled.json')) as file:
        compiled_sol = json.load(file)['contracts'][contract_file_name][contract_name]
        abi = compiled_sol['abi']
        bytecode = compiled_sol['evm']['bytecode']['object']

    # Deploy
    w3.eth.default_account = public_key
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    data = contract.constructor(*constructor_args).buildTransaction()
    data.update({'nonce': w3.eth.get_transaction_count(public_key)})
    signed_txn = w3.eth.account.sign_transaction(data, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract = w3.eth.contract(tx_receipt.contractAddress, abi=abi)

    # Debugging
    print(f"""
    Contract Name: {contract_name}
    Constructor Args: {constructor_args}
    -------------
    Owner: {w3.eth.default_account}
    TX Hash: {tx_hash.hex()}
    Contract Address: {tx_receipt.contractAddress}
    """)


abi = None
bytecode = None
contract = None
run()
