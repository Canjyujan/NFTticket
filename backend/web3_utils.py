from web3 import Web3
import json
import requests
from datetime import datetime

# 连接本地网络
ALCHEMY_URL = "https://eth-sepolia.g.alchemy.com/v2/5tpz7PZO0DYLj8G3DXzwz8hDDlc2HNT5"
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
print("🔗 Alchemy连接状态：", w3.is_connected())
g_uri = "http://127.0.0.1:5000/static/metadata/ticket3.json"
# 自动读取部署后的地址
with open("deployedAddress.json", "r") as f:
    deployed_info = json.load(f)
contract_address = Web3.to_checksum_address(deployed_info["TicketNFT"])
# 部署合约后的地址，转换为checksum地址
# 合约 ABI
with open("artifacts/contracts/TicketNFT.sol/TicketNFT.json", encoding="utf-8") as f:
    abi = json.load(f)["abi"]

# 合约实例
contract = w3.eth.contract(address=contract_address, abi=abi)
# 默认管理员账户(hardhat node启动时生成的第一个账户Account0)
admin_address = "0x35439095de5fc8B1b809A178a2dfC07C6440F439"
private_key = "dea0f25d4a2d8edd1cdae3648cb11ac07cff5e7425943200adb9b757d37d0e01"

def mint_ticket(to, uri, price_eth):
    nonce = w3.eth.get_transaction_count(admin_address)
    price_wei = w3.to_wei(price_eth, 'ether')
    token_uri = g_uri#铸造票时传入的元数据
    txn = contract.functions.mintTicket(to, token_uri, price_wei).build_transaction({
        'from': admin_address,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt

#购票
def buy_ticket(buyer_address, private_key, ticket_id):
    # 获取账户nonce
    nonce = w3.eth.get_transaction_count(buyer_address)
    # 从合约读取当前票价（单位wei）
    ticket_info = contract.functions.tickets(ticket_id).call()
    price_wei = ticket_info[2]

    # 构建交易
    txn = contract.functions.buyTicket(ticket_id).build_transaction({
        'from': buyer_address,
        'nonce': nonce,
        'value': price_wei,
        'gas': 300000,
        'gasPrice': w3.to_wei('20', 'gwei'),
    })

    # 签名交易
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    # 发送交易
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # 等待交易确认
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def get_user_tickets(user_address):
    tickets = []

    try:
        user_address = safe_checksum_address(user_address)

        result = contract.functions.getUserTickets(user_address).call()

        for ticket in result:
            token_id = ticket[0]
            uri = ticket[1]
            price = ticket[2]
            price_eth = Web3.from_wei(price, 'ether')
            is_for_sale = ticket[3]

            response = requests.get(uri)
            if response.status_code == 200:
                metadata = response.json()
                tickets.append({
                    "token_id": token_id,
                    "event": metadata.get("event", "未知活动"),
                    "date": metadata.get("date", "未知时间"),
                    "price": price_eth,#这里显示的是“我的票”的价格
                    "image": metadata.get("image", ""),
                    "description": metadata.get("description", ""),
                    "uri": uri,
                    "is_for_sale": is_for_sale
                })
            else:
                print(f"无法访问 tokenURI: {uri}")
    except Exception as e:
        print(f"获取用户票务信息失败: {str(e)}")
    return tickets

def safe_checksum_address(address: str) -> str:
    #安全地将以太坊地址转换为checksum格式，若无效或转换失败则抛出异常
    if not address:
        raise ValueError("地址不能为空")
    if not Web3.is_address(address):
        raise ValueError(f"无效以太坊地址: {address}")
    return Web3.to_checksum_address(address)


def get_primary_market_tickets_onchain():
    try:
        token_ids = contract.functions.getResaleTickets().call()
        tickets = []

        for ticket in token_ids:
            token_id = ticket[0]
            token_uri = contract.functions.tokenURI(token_id).call()
            response = requests.get(token_uri)
            if response.status_code == 200:
                metadata = response.json()
                ticket_info = contract.functions.getTicket(token_id).call()
                price_wei = ticket_info[2]  # 票价 wei

                tickets.append({
                    "token_id": token_id,
                    "event": metadata.get("event", "未知活动"),
                    "date": metadata.get("date", "未知时间"),
                    "price": Web3.from_wei(price_wei, 'ether'),
                    "image": metadata.get("image", ""),
                    "description": metadata.get("description", ""),
                    "uri": token_uri
                })

        return tickets
    except Exception as e:
        print(f"获取链上票券失败: {str(e)}")
        return []


