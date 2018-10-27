import json
from requests import get, post
import time
import ast
from math import sqrt
from pprint import pprint


"""
Basic Blockchain Functions
"""
def getBlockchain(URL, HTTP_PORT):
    op = "blocks"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    res = get(target)
    return res

def addNewBlock(URL, HTTP_PORT, req=None):
    op = "mineBlock"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    if req == None:
        res = post(target)
    else:
        headers = {'Content-type': 'application/json'}
        data = {"data": req}
        res = post(target, data=json.dumps(data), headers=headers)

    return res

def getPeers(URL, HTTP_PORT):
    op = "peers"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    res = get(target)
    return res

def addPeer(URL, HTTP_PORT, req=None):
    op = "addPeer"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    headers = {'Content-type': 'application/json'}
    data = {"peer": req}
    res = post(target, data=json.dumps(data), headers=headers)
    return res

def stopNode(URL, HTTP_PORT):
    op = "stop"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    res = post(target)
    return res

def getAddress(URL, HTTP_PORT):
    op = "address"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    res = get(target)
    return res

def deleteWallet(URL, HTTP_PORT):
    op = "deleteWallet"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    res = post(target)
    return res


"""
Voting Systems
"""
def voting(URL, HTTP_PORT, req=None):
    op = "voting"
    target = URL + ":" + str(HTTP_PORT) + '/' + op

    headers = {'Content-type': 'application/json'}
    data = {
        "receiver": req[0],
        "amount": req[1]
    }
    res = post(target, data=json.dumps(data), headers=headers)
    return res

def getBalance(URL, HTTP_PORT, address):
    utxo = 0

    res = getBlockchain(URL, HTTP_PORT)
    blockchain = ast.literal_eval(res.text)

    for block in blockchain:
        tx = block['data']
        try:
            vote = tx['vote']
        except:
            continue

        amount = vote['amount']
        receiver = vote['receiver']
        sender = vote['sender']

        if receiver == address:
            utxo += amount
        elif sender == address:
            utxo -= amount

    return utxo

def getLinearVoting(URL, HTTP_PORT, address):
    tot = 0

    res = getBlockchain(URL, HTTP_PORT)
    blockchain = ast.literal_eval(res.text)

    for block in blockchain:
        tx = block['data']
        try:
            vote = tx['vote']
        except:
            continue

        amount = vote['amount']
        receiver = vote['receiver']
        # sender = vote['sender']

        if receiver == address:
            tot += amount  # floor

    return tot

def getQuadraticVoting(URL, HTTP_PORT, address):
    tot = 0

    res = getBlockchain(URL, HTTP_PORT)
    blockchain = ast.literal_eval(res.text)

    for block in blockchain:
        tx = block['data']
        try:
            vote = tx['vote']
        except:
            continue

        amount = vote['amount']
        receiver = vote['receiver']
        # sender = vote['sender']

        if receiver == address:
            tot += int(sqrt(amount))  # floor

    return tot


"""
Scenario 1: Linear voting
# 6001: admin node  # distribute votes
# 6002: policy A    # parity multi-sig wallet restore
# 6003: policy B    # do not restore
# 6004: policy C    # postpone voting
# 6005: citizen 1   # A >  B > C: who has lost little money
# 6006: citizen 2   # A >= C > B: who has lost money, but not too much
# 6007: citizen 3   # A >  C > B: who has lost a lot of money 
# 6008: citizen 4   # B >= C > A: not a victim
# 6009: citizen 5   # B >= C > A: not a victim
# 6010: citizen 6   # B >= C > A: not a victim
# 6011: citizen 7   # B >= C > A: not a victim
# 6012: citizen 8   # B >= C > A: not a victim
# 3 / 5 / 0
"""
def scenario_1():
    URL = "http://127.0.0.1"  # (only) local environment

    """
    STEP 1: construct a network
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6002, 6013):
        res = addPeer(URL, HTTP_PORT, req="ws://127.0.0.1:" + str(peer))


    end_time = time.time()

    time.sleep(0.5)  # wait
    res = getPeers(URL, HTTP_PORT)
    print("> STEP 1", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(ast.literal_eval(res.text)))

    """
    STEP 2: get public address
    """
    start_time = time.time()

    addresses = {}

    # execution code
    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = getAddress(URL, HTTP_PORT)
        addresses[P2P_PORT] = (ast.literal_eval(res.text)['address'])

    end_time = time.time()

    print("> STEP 2", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(addresses))

    """
    STEP 3: distribute votes
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6005, 6013):
        res = voting(URL, HTTP_PORT, (addresses[peer], 1))  # Linear Voting

    end_time = time.time()

    balances = {}
    for peer in range(6005, 6013):
        utxo = getBalance(URL, HTTP_PORT, addresses[peer])
        balances[peer] = utxo

    print("> STEP 3", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(balances))

    """
    STEP 4: voting
    # rule-based
    """
    start_time = time.time()

    HTTP_PORT = 3005; P2P_PORT = 6005                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 1))  # A >  B > C: who has lost little money
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3006; P2P_PORT = 6006                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 1))  # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3007; P2P_PORT = 6007                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 1))  # A >  C > B: who has lost a lot of money
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3008; P2P_PORT = 6008                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 1))  # B >= C > A: not a victim
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3009; P2P_PORT = 6009                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 1))  # B >= C > A: not a victim
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3010; P2P_PORT = 6010                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 1))  # B >= C > A: not a victim
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3011; P2P_PORT = 6011                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 1))  # B >= C > A: not a victim
    time.sleep(0.5)                                     # wait

    HTTP_PORT = 3012; P2P_PORT = 6012                   # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 1))  # B >= C > A: not a victim
    time.sleep(0.5)                                     # wait

    end_time = time.time()

    print("> STEP 4", end="")
    print("[" + str(round(((end_time - start_time) - 0.5 * 8) * 1000, 2)) + "ms]")

    """
    STEP 5: get results
    # voting results
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    tots = {}
    for peer in range(6002, 6005):
        tot = getLinearVoting(URL, HTTP_PORT, addresses[peer])
        tots[peer] = tot

    end_time = time.time()

    print("> STEP 5", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(tots))

    """
    STEP 6: get blockchain
    # blocks
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    res = getBlockchain(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 6", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + res.text)

    """
    STEP 7: stop peers
    """
    start_time = time.time()

    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = stopNode(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 7", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]")


"""
Scenario 2: Quadratic Voting
# 27 / 35 / 42
"""
def scenario_2():
    URL = "http://127.0.0.1"  # (only) local environment

    """
    STEP 1: construct a network
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6002, 6013):
        res = addPeer(URL, HTTP_PORT, req="ws://127.0.0.1:" + str(peer))


    end_time = time.time()

    time.sleep(0.5)  # wait
    res = getPeers(URL, HTTP_PORT)
    print("> STEP 1", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(ast.literal_eval(res.text)))

    """
    STEP 2: get public address
    """
    start_time = time.time()

    addresses = {}

    # execution code
    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = getAddress(URL, HTTP_PORT)
        addresses[P2P_PORT] = (ast.literal_eval(res.text)['address'])

    end_time = time.time()

    print("> STEP 2", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(addresses))

    """
    STEP 3: distribute votes
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6005, 6013):
        res = voting(URL, HTTP_PORT, (addresses[peer], 100))  # Quadratic Voting: 100s

    end_time = time.time()

    balances = {}
    for peer in range(6005, 6013):
        utxo = getBalance(URL, HTTP_PORT, addresses[peer])
        balances[peer] = utxo

    print("> STEP 3", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(balances))

    """
    STEP 4: voting
    # rule-based
    """
    start_time = time.time()

    HTTP_PORT = 3005; P2P_PORT = 6005                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # A >  B > C: who has lost little money
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3006; P2P_PORT = 6006                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3007; P2P_PORT = 6007                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # A >  C > B: who has lost a lot of money
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3008; P2P_PORT = 6008                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3009; P2P_PORT = 6009                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3010; P2P_PORT = 6010                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3011; P2P_PORT = 6011                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3012; P2P_PORT = 6012                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    end_time = time.time()

    print("> STEP 4", end="")
    print("[" + str(round(((end_time - start_time) - 0.5 * 14) * 1000, 2)) + "ms]")

    """
    STEP 5: get results
    # voting results
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    tots = {}
    for peer in range(6002, 6005):
        tot = getQuadraticVoting(URL, HTTP_PORT, addresses[peer])
        tots[peer] = tot

    end_time = time.time()

    print("> STEP 5", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(tots))

    """
    STEP 6: get blockchain
    # blocks
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    res = getBlockchain(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 6", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + res.text)

    """
    STEP 7: stop peers
    """
    start_time = time.time()

    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = stopNode(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 7", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]")


"""
Scenario 3: Quadratic + Tradable Voting
# citizen 4 -> citizen 3, 100
# 31 / 28 / 35  : fail
"""
def scenario_3():
    URL = "http://127.0.0.1"  # (only) local environment

    """
    STEP 1: construct a network
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6002, 6013):
        res = addPeer(URL, HTTP_PORT, req="ws://127.0.0.1:" + str(peer))


    end_time = time.time()

    time.sleep(0.5)  # wait
    res = getPeers(URL, HTTP_PORT)
    print("> STEP 1", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(ast.literal_eval(res.text)))

    """
    STEP 2: get public address
    """
    start_time = time.time()

    addresses = {}

    # execution code
    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = getAddress(URL, HTTP_PORT)
        addresses[P2P_PORT] = (ast.literal_eval(res.text)['address'])

    end_time = time.time()

    print("> STEP 2", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(addresses))

    """
    STEP 3: distribute votes
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6005, 6013):
        res = voting(URL, HTTP_PORT, (addresses[peer], 100))  # Quadratic Voting: 100s

    end_time = time.time()

    balances = {}
    for peer in range(6005, 6013):
        utxo = getBalance(URL, HTTP_PORT, addresses[peer])
        balances[peer] = utxo

    print("> STEP 3", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(balances))

    """
    STEP 4: voting
    # rule-based
    """
    start_time = time.time()

    # trading
    HTTP_PORT = 3008; P2P_PORT = 6008                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6007], 100))    # citizen 4 -> citizen 3
    time.sleep(0.5)                                         # wait

    # voting
    HTTP_PORT = 3005; P2P_PORT = 6005                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # A >  B > C: who has lost little money
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3006; P2P_PORT = 6006                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3007; P2P_PORT = 6007                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 200))    # A >  C > B: who has lost a lot of money
    time.sleep(0.5)                                         # wait

    # HTTP_PORT = 3008; P2P_PORT = 6008                       # set PORT
    # res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    # time.sleep(0.5)                                         # wait
    # res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    # time.sleep(0.5)                                         # wait

    HTTP_PORT = 3009; P2P_PORT = 6009                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3010; P2P_PORT = 6010                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3011; P2P_PORT = 6011                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3012; P2P_PORT = 6012                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    end_time = time.time()

    print("> STEP 4", end="")
    print("[" + str(round(((end_time - start_time) - 0.5 * 14) * 1000, 2)) + "ms]")

    """
    STEP 5: get results
    # voting results
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    tots = {}
    for peer in range(6002, 6005):
        tot = getQuadraticVoting(URL, HTTP_PORT, addresses[peer])
        tots[peer] = tot

    end_time = time.time()

    print("> STEP 5", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(tots))

    """
    STEP 6: get blockchain
    # blocks
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    res = getBlockchain(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 6", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + res.text)

    """
    STEP 7: stop peers
    """
    start_time = time.time()

    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = stopNode(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 7", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]")


"""
Scenario 4: Quadratic + Tradable Voting
# citizen 4 -> citizen 3, 100
# citizen 5 -> citizen 3, 30
# citizen 6 -> citizen 3, 4
# citizen 7 -> citizen 3, 4
# citizen 8 -> citizen 3, 4
# expectation   : 31 / 23 / 30
# real          : 31 / 27 / 30  : success
# citizen 3 bought 142 votes 
"""
def scenario_4():
    URL = "http://127.0.0.1"  # (only) local environment

    """
    STEP 1: construct a network
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6002, 6013):
        res = addPeer(URL, HTTP_PORT, req="ws://127.0.0.1:" + str(peer))


    end_time = time.time()

    time.sleep(0.5)  # wait
    res = getPeers(URL, HTTP_PORT)
    print("> STEP 1", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(ast.literal_eval(res.text)))

    """
    STEP 2: get public address
    """
    start_time = time.time()

    addresses = {}

    # execution code
    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = getAddress(URL, HTTP_PORT)
        addresses[P2P_PORT] = (ast.literal_eval(res.text)['address'])

    end_time = time.time()

    print("> STEP 2", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(addresses))

    """
    STEP 3: distribute votes
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6005, 6013):
        res = voting(URL, HTTP_PORT, (addresses[peer], 100))  # Quadratic Voting: 100s

    end_time = time.time()

    balances = {}
    for peer in range(6005, 6013):
        utxo = getBalance(URL, HTTP_PORT, addresses[peer])
        balances[peer] = utxo

    print("> STEP 3", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(balances))

    """
    STEP 4: voting
    # rule-based
    """
    start_time = time.time()

    # trading
    HTTP_PORT = 3008; P2P_PORT = 6008                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6007], 100))    # citizen 4 -> citizen 3
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3009; P2P_PORT = 6009                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6007], 30))     # citizen 5 -> citizen 3
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3010; P2P_PORT = 6010                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6007], 4))      # citizen 6 -> citizen 3
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3011; P2P_PORT = 6011                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6007], 4))      # citizen 7 -> citizen 3
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3012; P2P_PORT = 6012                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6007], 4))      # citizen 8 -> citizen 3
    time.sleep(0.5)                                         # wait

    # voting
    HTTP_PORT = 3005; P2P_PORT = 6005                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # A >  B > C: who has lost little money
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3006; P2P_PORT = 6006                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3007; P2P_PORT = 6007                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 200))    # A >  C > B: who has lost a lot of money
    time.sleep(0.5)                                         # wait

    # HTTP_PORT = 3008; P2P_PORT = 6008                       # set PORT
    # res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    # time.sleep(0.5)                                         # wait
    # res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    # time.sleep(0.5)                                         # wait

    HTTP_PORT = 3009; P2P_PORT = 6009                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 36))     # B >= C > A: not a victim  # not 35
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 34))     # B >= C > A: not a victim  # not 35
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3010; P2P_PORT = 6010                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 49))     # B >= C > A: not a victim  # not 48
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 47))     # B >= C > A: not a victim  # not 48
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3011; P2P_PORT = 6011                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 49))     # B >= C > A: not a victim  # not 48
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 47))     # B >= C > A: not a victim  # not 48
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3012; P2P_PORT = 6012                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 49))     # B >= C > A: not a victim  # not 48
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 47))     # B >= C > A: not a victim  # not 48
    time.sleep(0.5)                                         # wait

    end_time = time.time()

    print("> STEP 4", end="")
    print("[" + str(round(((end_time - start_time) - 0.5 * 18) * 1000, 2)) + "ms]")

    """
    STEP 5: get results
    # voting results
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    tots = {}
    for peer in range(6002, 6005):
        tot = getQuadraticVoting(URL, HTTP_PORT, addresses[peer])
        tots[peer] = tot

    end_time = time.time()

    print("> STEP 5", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(tots))

    """
    STEP 6: get blockchain
    # blocks
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    res = getBlockchain(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 6", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + res.text)

    """
    STEP 7: stop peers
    """
    start_time = time.time()

    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = stopNode(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 7", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]")


"""
Scenario 5: Quadratic Voting + Suborn
# citizen 4 suborns citizen 3
# 37 / 28 / 35  : success
# citizen 3 bought only 100 votes
"""
def scenario_5():
    URL = "http://127.0.0.1"  # (only) local environment

    """
    STEP 1: construct a network
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6002, 6013):
        res = addPeer(URL, HTTP_PORT, req="ws://127.0.0.1:" + str(peer))


    end_time = time.time()

    time.sleep(0.5)  # wait
    res = getPeers(URL, HTTP_PORT)
    print("> STEP 1", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(ast.literal_eval(res.text)))

    """
    STEP 2: get public address
    """
    start_time = time.time()

    addresses = {}

    # execution code
    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = getAddress(URL, HTTP_PORT)
        addresses[P2P_PORT] = (ast.literal_eval(res.text)['address'])

    end_time = time.time()

    print("> STEP 2", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(addresses))

    """
    STEP 3: distribute votes
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    for peer in range(6005, 6013):
        res = voting(URL, HTTP_PORT, (addresses[peer], 100))  # Quadratic Voting: 100s

    end_time = time.time()

    balances = {}
    for peer in range(6005, 6013):
        utxo = getBalance(URL, HTTP_PORT, addresses[peer])
        balances[peer] = utxo

    print("> STEP 3", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(balances))

    """
    STEP 4: voting
    # rule-based
    """
    start_time = time.time()

    HTTP_PORT = 3005; P2P_PORT = 6005                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # A >  B > C: who has lost little money
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3006; P2P_PORT = 6006                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # A >= C > B: who has lost money, but not too much
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3007; P2P_PORT = 6007                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # A >  C > B: who has lost a lot of money
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3008; P2P_PORT = 6008                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6002], 100))    # but A  # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3009; P2P_PORT = 6009                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3010; P2P_PORT = 6010                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3011; P2P_PORT = 6011                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    HTTP_PORT = 3012; P2P_PORT = 6012                       # set PORT
    res = voting(URL, HTTP_PORT, (addresses[6003], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait
    res = voting(URL, HTTP_PORT, (addresses[6004], 50))     # B >= C > A: not a victim
    time.sleep(0.5)                                         # wait

    end_time = time.time()

    print("> STEP 4", end="")
    print("[" + str(round(((end_time - start_time) - 0.5 * 13) * 1000, 2)) + "ms]")

    """
    STEP 5: get results
    # voting results
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    tots = {}
    for peer in range(6002, 6005):
        tot = getQuadraticVoting(URL, HTTP_PORT, addresses[peer])
        tots[peer] = tot

    end_time = time.time()

    print("> STEP 5", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + str(tots))

    """
    STEP 6: get blockchain
    # blocks
    """
    start_time = time.time()

    # set PORT
    HTTP_PORT = 3001
    P2P_PORT = 6001

    # execution code
    res = getBlockchain(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 6", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]", end="")
    print(": " + res.text)

    """
    STEP 7: stop peers
    """
    start_time = time.time()

    for peer in range(6001, 6013):
        # set PORT
        HTTP_PORT = peer - 3000  # 3001~
        P2P_PORT = peer

        res = stopNode(URL, HTTP_PORT)

    end_time = time.time()

    print("> STEP 7", end="")
    print("[" + str(round((end_time - start_time) * 1000, 2)) + "ms]")


if __name__ == '__main__':
    """
    res = getBlockchain()                       # pprint(ast.literal_eval(res.text)[0]['data'])
                                                # pprint(ast.literal_eval(res.text)[1]['data']['vote']['amount'])
    res = addNewBlock(req="Anything")           # print(res.text)
    res = getPeers()                            # pprint(ast.literal_eval(res.text)[0])
    res = addPeer(req="ws://127.0.0.1:6003")    # print(res.text)
    res = stopNode()                            # pprint(ast.literal_eval(res.text)['msg'])
    res = getAddress()                          # print(ast.literal_eval(res.text)['address'])
    res = deleteWallet()                        # print(res.text)
    res = voting(("addr", 50))                  # print(res.text)
    
    utxo = getBalance("A")                      # print(utxo)
    tot = getLinearVoting("A")                  # print(tot)
    tot = getQuadraticVoting("A")               # print(tot)
    """
    time.sleep(2)  # ready...

    """
    simulation
    """
    # scenario_1()
    # scenario_2()
    # scenario_3()
    # scenario_4()
    # scenario_5()
