import ctypes
import json
import sys
import threading
import time
import requests
from blocknative.stream import Stream
from web3 import Web3
import os

configExample = {
    "RPC": "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
    "privateKey": ["", ""],
    "blocknativeKey": "",
    "barkKey": "",
    "maxGasPrice": 50,
    "maxGasLimit": 1000000,
    "follow": {
        "0x8888887a5e2491fec904d90044e6cd6c69f1e71c": {"start": 0, "end": 24},
        "0x555555B63d1C3A8c09FB109d2c80464685Ee042B": {"start": 18, "end": 6},
        "0x99999983c70de9543cdc11dB5DE66A457d241e8B": {"start": 8, "end": 20}
    },
    "blacklist": ["Ape", "Bear", "Duck", "Pixel", "Not", "Okay", "Woman", "Baby", "Goblin", "Ai"]
}
std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)


def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool


# reset white
def resetColor():
    set_cmd_text_color(0x0c | 0x0a | 0x09)


def print_green(message):
    stime = time.strftime("%m-%d %H:%M:%S", time.localtime())
    set_cmd_text_color(0x0a)
    sys.stdout.write(f'[{stime}] {message}\n')
    resetColor()


def print_red(message):
    stime = time.strftime("%m-%d %H:%M:%S", time.localtime())
    set_cmd_text_color(0x0d)
    sys.stdout.write(f'[{stime}] {message}\n')
    resetColor()


def print_blue(message):
    stime = time.strftime("%m-%d %H:%M:%S", time.localtime())
    set_cmd_text_color(0x0b)
    sys.stdout.write(f'[{stime}] {message}\n')
    resetColor()


def print_yellow(message):
    stime = time.strftime("%m-%d %H:%M:%S", time.localtime())
    set_cmd_text_color(0x0e)
    sys.stdout.write(f'[{stime}] {message}\n')
    resetColor()


def bark(info, data):
    if barkKey != '':
        requests.get('https://api.day.app/' + barkKey + '/' + info + '?url=' + data)


def getMethodName(methodSignature):
    try:
        if methodSignature in methodNameList:
            return methodNameList[methodSignature]
        res = requests.get('https://www.4byte.directory/api/v1/signatures/?hex_signature=' + methodSignature)
        if res.status_code == 200:
            methodName = res.json()['results'][0]['text_signature'].split('(')[0].lower()
            print_yellow(res.json()['results'][0]['text_signature'])
            if 'mint' in methodName:
                methodNameList[methodSignature] = True
                return True
        methodNameList[methodSignature] = False
        return False
    except:
        return False


def isBlackList(_to):
    try:
        NFTcon = w3.eth.contract(address=_to, abi=[nameabi])
        name = NFTcon.functions.name().call()
        for black in blacklist:
            if black.lower() in name.lower():
                print_yellow(name + "黑名单，跳过")
                return False
    except:
        print_yellow('获取NFT名称失败，跳过')
        return False
    return True


def isMintTime(_from):
    for _follow in follows:
        if _follow.lower() == _from.lower():
            starttime = int(follows[_follow]['start'])
            endtime = int(follows[_follow]['end'])
            tm_hour = time.localtime().tm_hour
            if tm_hour >= starttime or tm_hour < endtime:
                pass
            else:
                print_yellow("非Mint时间，跳过")
                return False
    return True


def minttx(_account, _privateKey, _inputData, _from_address, _to_address, _gasPrice, _maxFeePerGas, _maxPriorityFeePerGas):
    _inputData = _inputData.replace(_from_address[2:].lower(), _account.address[2:].lower())
    transaction = {
        'from': _account.address,
        'chainId': chainId,
        'to': _to_address,
        'gas': 2000000,
        'nonce': w3.eth.getTransactionCount(_account.address),
        'data': _inputData
    }
    if _gasPrice > 10000:
        transaction['gasPrice'] = _gasPrice
    else:
        transaction['maxFeePerGas'] = _maxFeePerGas
        transaction['maxPriorityFeePerGas'] = _maxPriorityFeePerGas
    try:
        estimateGas = w3.eth.estimateGas(transaction)
        if estimateGas > maxGasLimit:
            print_yellow('超过gasLimit上限，跳过')
            return
        transaction['gas'] = estimateGas
        signed = w3.eth.account.sign_transaction(transaction, _privateKey)
        new_raw = signed.rawTransaction.hex()
        tx_hash = w3.eth.sendRawTransaction(new_raw)
        print_green("mint交易发送成功" + w3.toHex(tx_hash))
        freceipt = w3.eth.waitForTransactionReceipt(tx_hash, 600)
        if freceipt.status == 1:
            print_green("mint成功")
            bark('mint成功', 'https://cn.etherscan.com/tx/' + w3.toHex(tx_hash))
        else:
            print_green("mint失败")
            bark('mint失败', 'https://cn.etherscan.com/tx/' + w3.toHex(tx_hash))
    except Exception as e:
        print_yellow('预测失败，跳过:' + str(e))
        return


async def txn_handler(txn, unsubscribe):
    to_address = txn['to']
    from_address = txn['from']
    to_address = w3.toChecksumAddress(to_address)
    gasPrice = 0
    maxFeePerGas = 0
    maxPriorityFeePerGas = 0
    if 'gasPrice' in txn:
        gasPrice = int(txn['gasPrice']) + 1000000
    else:
        maxFeePerGas = int(txn['maxFeePerGas'])
        maxPriorityFeePerGas = int(txn['maxPriorityFeePerGas']) + 1000000
    inputData = txn['input']
    value = txn['value']
    print_yellow(from_address + "监控到新交易")
    if not isMintTime(from_address):
        return
    if value != '0':
        print_yellow("非免费，跳过")
        return
    if to_address in mintadd:
        print_yellow("mint过，跳过")
        return
    if not getMethodName(inputData[:10]):
        print_yellow('可能不是mint交易,跳过')
        return
    if not isBlackList(to_address):
        return
    if gasPrice > maxGasPrice or maxFeePerGas > maxGasPrice:
        print_yellow('gasPrice过高,跳过')
        return
    mintadd.append(_to_address)
    for index in range(len(accounts)):
        threading.Thread(target=minttx, args=(accounts[index], privateKeys[index], inputData, from_address, to_address, gasPrice, maxFeePerGas, maxPriorityFeePerGas)).start()


def main():
    while True:
        try:
            stream = Stream(blocknativeKey)
            filters = [{"status": "pending"}]
            print_blue(str(len(accounts)) + '个地址开始监控')
            print_blue('开始监控')
            for _follow in follows:
                stream.subscribe_address(_follow, txn_handler, filters)
            stream.connect()
        except Exception as e:
            print_red(str(e))
            time.sleep(10)


if __name__ == '__main__':
    if not os.path.exists('config.json'):
        print_blue('请先配置config.json')
        file = open('config.json', 'w')
        file.write(json.dumps(configExample))
        file.close()
        time.sleep(10)
    try:
        file = open('config.json', 'r')
        config = json.loads(file.read())
        RPC = config['RPC']
        privateKeys = config['privateKey']
        if type(privateKeys) == str:
            privateKeys = [privateKeys]
            file = open('config.json', 'w')
            config['privateKey'] = privateKeys
            file.write(json.dumps(config))
            file.close()
        if 'blacklist' in config:
            blacklist = config['blacklist']
        else:
            blacklist = []
            file = open('config.json', 'w')
            config['blacklist'] = ["Ape", "Bear", "Duck", "Pixel", "Not", "Okay", "Woman", "Baby", "Goblin", "Ai"]
            file.write(json.dumps(config))
            file.close()
        blocknativeKey = config['blocknativeKey']
        barkKey = config['barkKey']
        follows = config['follow']
        nameabi = {
            'inputs': [],
            'name': 'name',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view',
            'type': 'function'
        }
        if type(follows) == list:
            print_red('请重新配置follow起始时间，配置文件模板已更新')
            followsDict = {}
            for follow in follows:
                followsDict[follow] = {'start': 0, 'end': 24}
            config['follow'] = followsDict
            file = open('config.json', 'w')
            file.write(json.dumps(config))
            file.close()
            time.sleep(10)
        else:
            w3 = Web3(Web3.HTTPProvider(RPC))
            maxGasPrice = config['maxGasPrice']
            maxGasPrice = w3.toWei(maxGasPrice, 'gwei')
            maxGasLimit = int(config['maxGasLimit'])
            chainId = w3.eth.chainId
            accounts = []
            for privateKey in privateKeys:
                accounts.append(w3.eth.account.privateKeyToAccount(privateKey))
            mintadd = []
            methodNameList = {}
            main()
    except Exception as e:
        print_red(str(e))
        time.sleep(10)
