from web3 import Web3
from data.utils import *


def delegate_arb(key, src_chain):
    function_name = inspect.stack()[0][3]
    cprint(f'>>> start {function_name}: {src_chain}')

    try:
        rpc = check_rpc(src_chain)['rpc']
        web3 = Web3(Web3.HTTPProvider(rpc))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        my_address = web3.eth.account.from_key(key).address
   
        contract = web3.eth.contract(address=delegate_token_contracts[src_chain], abi=TOKEN_ABI)
        delegator_address = delegator[src_chain]

        function = contract.functions.delegate(delegator_address)
        maxPriorityFeePerGas, maxFeePerGas = getFeePerGas(src_chain, web3)
        contract_txn = function.build_transaction({
                        'from': my_address,
                        'value': 0,
                        'nonce': web3.eth.get_transaction_count(my_address),
                        'maxFeePerGas': maxFeePerGas,
                        'maxPriorityFeePerGas': maxPriorityFeePerGas,
                })
        signed_txn = web3.eth.account.sign_transaction(contract_txn, private_key=key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        pritnt_status_tx(function_name, src_chain, tx_hash, key)
    except Exception as error:
            cprint(f'>>> Exception {function_name} {src_chain}: {error}', 'red')

def run():
    with open("private_keys.txt", "r") as f:
        KEYS = [row.strip() for row in f]

    chain = CHAIN_FOR_DELEGATE
    i = 0
    for key in KEYS:
        
        rpc = check_rpc(chain)['rpc']
        scan = check_rpc(chain)['scan']
        web3 = Web3(Web3.HTTPProvider(rpc))
        my_address = web3.eth.account.from_key(key).address

        i = i + 1
        cprint(f'{i}. {scan}/address/{my_address} :', 'magenta')

        try:  
            delegate_arb(key, chain)
            sleeping(SLEEP_MIN, SLEEP_MAX)
        except Exception as error:
            cprint(f'Something went wrong: {error}', 'red')

if __name__ == "__main__":
    cprint(f'Ты получишь мега иксы в 2024 году    https://t.me/slow_rich', 'blue')
    cprint(f'Ты получишь мега иксы в 2024 году    https://t.me/slow_rich', 'blue')
    cprint(f'Ты получишь мега иксы в 2024 году    https://t.me/slow_rich', 'blue')
    run()
    cprint(f'Бычка уже рядом. ZKF по 1$ !!!       https://t.me/slow_rich', 'blue')
    cprint(f'Бычка уже рядом. ZKF по 1$ !!!       https://t.me/slow_rich', 'blue')
    cprint(f'Бычка уже рядом. ZKF по 1$ !!!       https://t.me/slow_rich', 'blue')

   