
import random
from termcolor import cprint
import time
import json
from decimal import Decimal
from web3 import Web3, Account
from web3.middleware import geth_poa_middleware
from loguru import logger
import inspect
from tqdm import tqdm
import math

from data.config import *

with open('data/abi_token.json', "r") as file:
    TOKEN_ABI = json.load(file)


def sleepForAWhile(min,max,log=True):
    sleepT=random.randint(min,max)
    if (log):
        cprint(f">>> sleep  time = {sleepT}")
    time.sleep(sleepT)

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

def round_to(num, digits=3):
    try:
        if num == 0: return 0
        scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
        if scale < digits: scale = digits
        return round(num, scale)
    except: return num

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

RPCS = [
    {'chain': 'ETH',        'chain_id': 1,      'rpc': 'https://rpc.ankr.com/eth',               'scan': 'https://etherscan.io',                'token': 'ETH'},
    {'chain': 'OPTIMISM',   'chain_id': 10,     'rpc': 'https://rpc.ankr.com/optimism',          'scan': 'https://optimistic.etherscan.io',     'token': 'ETH'},
    {'chain': 'ARBITRUM',   'chain_id': 42161,  'rpc': 'https://arb1.arbitrum.io/rpc',           'scan': 'https://arbiscan.io',                 'token': 'ETH'},
]

def check_rpc(chain):
    for elem in RPCS:
        if elem['chain'] == chain:
            RPC = elem['rpc']
            chainId = elem['chain_id']
            scan = elem['scan']
            token = elem['token']

            return {
                'rpc': RPC, 'chain_id': chainId, 'scan': scan, 'token': token
            }
        

def getFeePerGas(chain, web3):
    maxPriorityFeePerGas = web3.eth.max_priority_fee
    if (chain == 'ARBITRUM'):                                                     maxPriorityFeePerGas = web3.to_wei('0', 'gwei')
    if (chain == 'OPTIMISM'):                                                     maxPriorityFeePerGas = web3.eth.max_priority_fee
        
    maxFeePerGas = web3.eth.gas_price + maxPriorityFeePerGas
    if (chain == 'ARBITRUM'): maxFeePerGas = web3.eth.gas_price + web3.to_wei('0.035', 'gwei')
    if (chain == 'OPTIMISM'): maxFeePerGas = web3.eth.gas_price + web3.to_wei('0.00000005', 'gwei')

    return maxPriorityFeePerGas, maxFeePerGas


def check_status_tx(chain, tx_hash):
    counter = 0
    while True:
        try:
            data = check_rpc(chain)
            rpc_chain = data['rpc']
            web3        = Web3(Web3.HTTPProvider(rpc_chain))
            status_     = web3.eth.get_transaction_receipt(tx_hash)
            status      = status_["status"]
            if status in [0, 1]:
                return status
            time.sleep(1)
        except Exception as error:
            counter = counter +1 
            if (counter > TIME_OUT_LIMIT):
                logger.error(f'{chain} chain timeout. Skip this chain')
                return -1
            # logger.info(f'{counter} error, try again : {error}')
            time.sleep(1)
    
def  pritnt_status_tx(function_name, chain, tx_hash, key):
    status = check_status_tx(chain, tx_hash.hex())
    scan = check_rpc(chain)['scan']
    if status == 1:
        logger.success(f"{function_name} | {scan}/tx/{tx_hash.hex()}")
    else:
        logger.error(f"{function_name} | tx is failed | {scan}/tx/{tx_hash.hex()}")
    return status



def sign_tx(web3, contract_txn, privatekey):

    signed_tx = web3.eth.account.sign_transaction(contract_txn, privatekey)
    raw_tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash = web3.to_hex(raw_tx_hash)
    return raw_tx_hash


def wait_normal_gas(normal_gas):
    gas_is_high = True
    while gas_is_high:
        eth_web3 = Web3(Web3.HTTPProvider(check_rpc('ETH')['rpc']))
        gas_price = eth_web3.eth.gas_price
        gas_price_gwei = round(eth_web3.from_wei(gas_price, 'gwei'))
        cprint(f'gas_price: {gas_price_gwei}. Normal price for script: {normal_gas}')
        if (gas_price_gwei <= normal_gas):
            gas_is_high = False
            continue
        time.sleep(30)