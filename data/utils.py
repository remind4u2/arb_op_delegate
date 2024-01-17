import requests
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

def token_to_wei(token_amount, decimal_factor):
    return int(token_amount * 10**decimal_factor)

def token_from_wei(token_amount, decimal_factor):
    if (token_amount == 0):
        return 0
    return round(Decimal(token_amount / 10**decimal_factor), 8)

def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty/ int("".join((["1"]+ ["0"]*decimal)))

def sleepForAWhile(min,max,log=True):
    sleepT=random.randint(min,max)
    if (log):
        cprint(f">>> sleep  time = {sleepT}")
    time.sleep(sleepT)

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

def prices():
    currency_price = []
    response = requests.get(url=f'https://api.gateio.ws/api/v4/spot/tickers')
    currency_price.append(response.json())
    return currency_price

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
    {'chain': 'BSC',        'chain_id': 56,     'rpc': 'https://rpc.ankr.com/bsc',               'scan': 'https://bscscan.com',                 'token': 'BNB'},
    {'chain': 'MATIC',      'chain_id': 137,    'rpc': 'https://rpc.ankr.com/polygon',           'scan': 'https://polygonscan.com',             'token': 'MATIC'},
    {'chain': 'ARBITRUM',   'chain_id': 42161,  'rpc': 'https://arb1.arbitrum.io/rpc',           'scan': 'https://arbiscan.io',                 'token': 'ETH'},
    {'chain': 'AVAXC',      'chain_id': 43114,  'rpc': 'https://avalanche.public-rpc.com',       'scan': 'https://snowtrace.io',                'token': 'AVAX'},
    {'chain': 'NOVA',       'chain_id': 42170,  'rpc': 'https://rpc.ankr.com/arbitrumnova',      'scan': 'https://nova.arbiscan.io',            'token': 'ETH'},
    {'chain': 'FTM',        'chain_id': 250,    'rpc': 'https://rpc.ankr.com/fantom',            'scan': 'https://ftmscan.com',                 'token': 'FTM'},
    {'chain': 'CORE',       'chain_id': 1116,   'rpc': 'https://rpc.coredao.org',                'scan': 'https://scan.coredao.org',            'token': 'CORE'},
    {'chain': 'METIS',      'chain_id': 1088,   'rpc': 'https://andromeda.metis.io/?owner=1088', 'scan': 'https://andromeda-explorer.metis.io', 'token': 'METIS'},
    {'chain': 'GNOSIS',     'chain_id': 100,    'rpc': 'https://rpc.ankr.com/gnosis',            'scan': 'https://gnosisscan.io',               'token': 'XDAI'},
    {'chain': 'CELO',       'chain_id': 42220,  'rpc': 'https://rpc.ankr.com/celo',              'scan': 'https://celoscan.io',                 'token': 'CELO'},
    {'chain': 'HARMONY',    'chain_id': 1666600000,  'rpc': 'https://rpc.ankr.com/harmony',      'scan': 'https://explorer.harmony.one',        'token': 'ONE'},
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
        
def check_balance(privatekey, rpc_chain, symbol_chain):
    try:
            
        web3 = Web3(Web3.HTTPProvider(rpc_chain))
        account = web3.eth.account.from_key(privatekey)
        balance = web3.eth.get_balance(web3.to_checksum_address(account.address))
        humanReadable = web3.from_wei(balance,'ether')

        price = 1
        try:
            currency_price = prices()
            for currency in currency_price[0]:
                if currency['currency_pair'] == f'{symbol_chain}_USDT':
                    price = Decimal(currency['last'])
        except: 
            price = 300

        gas = web3.eth.gas_price
        gasPrice = decimalToInt(gas, 18)

        balance = round(Decimal(humanReadable), 8)
        balance_in_usdt = round(Decimal(Decimal(humanReadable)*Decimal(price)), 6)
        # if (balance > 0):
            # cprint(f'balance: {balance} {symbol_chain}; {balance_in_usdt} USDT')
        return balance, balance_in_usdt


    except Exception as error:
        cprint(f'error : {error}', 'yellow')
        0, 0

def getFeePerGas(chain, web3):
    maxPriorityFeePerGas = web3.eth.max_priority_fee
    if (chain == 'AVAXC'):                                                        maxPriorityFeePerGas = web3.to_wei('1.5', 'gwei')
    if (chain == 'ARBITRUM'):                                                     maxPriorityFeePerGas = web3.to_wei('0', 'gwei')
    if (chain == 'OPTIMISM'):                                                     maxPriorityFeePerGas = web3.eth.max_priority_fee
    if (chain == 'NOVA'):                                                         maxPriorityFeePerGas = web3.to_wei('0', 'gwei')
    if (chain == 'MATIC' and maxPriorityFeePerGas < web3.to_wei('30', 'gwei')):    maxPriorityFeePerGas = web3.to_wei('31', 'gwei')
        
    maxFeePerGas = web3.eth.gas_price + maxPriorityFeePerGas
    if (chain == 'AVAXC'):    maxFeePerGas = web3.eth.gas_price + web3.to_wei('10', 'gwei')
    if (chain == 'ARBITRUM'): maxFeePerGas = web3.eth.gas_price + web3.to_wei('0.035', 'gwei')
    if (chain == 'OPTIMISM'): maxFeePerGas = web3.eth.gas_price + web3.to_wei('0.00000005', 'gwei')
    if (chain == 'NOVA'):     maxFeePerGas = web3.eth.gas_price + web3.to_wei('0.0035', 'gwei')
    if (chain == 'MATIC'):    maxFeePerGas = web3.eth.gas_price + web3.to_wei('200', 'gwei')

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

def add_gas_price(web3, contract_txn):

    try:
        gas_price = web3.eth.gas_price
        contract_txn['gasPrice'] = int(gas_price * random.uniform(1.01, 1.02))
    except Exception as error: 
        logger.error(error)

    return contract_txn

def add_gas_limit(web3, contract_txn):

    try:
        # value = contract_txn['value']
        # contract_txn['value'] = 0
        pluser = [1.02, 1.05]
        gasLimit = web3.eth.estimate_gas(contract_txn)
        contract_txn['gas'] = int(gasLimit * random.uniform(pluser[0], pluser[1]))
        # logger.info(f"gasLimit : {contract_txn['gas']}")
    except Exception as error: 
        contract_txn['gas'] = random.randint(2000000, 3000000)
        # logger.info(f"estimate_gas error : {error}. random gasLimit : {contract_txn['gas']}")

    # contract_txn['value'] = value
    return contract_txn


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