from flask import Flask, render_template, request, redirect, url_for, session, flash
from web3_utils import mint_ticket, buy_ticket, get_user_tickets, get_primary_market_tickets_onchain, safe_checksum_address,g_uri
import requests
import os
from flask import jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

"""
常用指令
npx hardhat run scripts/deploy.js --network sepolia
"""

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

#一级市场票
def get_primary_market_tickets():
    return get_primary_market_tickets_onchain()

#二级市场票
def get_secondary_market_tickets():
    fake_tickets_for_sale_secondary = []
    """
    待实现
    """
    return fake_tickets_for_sale_secondary

#初始化入口界面
@app.route("/")
def index():
    return render_template("index.html")

#进入购票/我的票务界面
@app.route('/my_tickets')
def my_tickets():
    user_address = request.args.get('address')
    try:
        checksum_address = safe_checksum_address(user_address)
        tickets = get_user_tickets(checksum_address)
        return render_template(
            'my_tickets.html',
            tickets=tickets,
            tickets_for_sale_primary=get_primary_market_tickets(),#web3里的onchain函数
            tickets_for_sale_secondary=get_secondary_market_tickets()
        )
    except Exception as e:
        print("获取用户票务信息失败:", e)
        return "无效地址或无法加载票券", 400

#购票功能
@app.route('/buy_ticket/<int:token_id>', methods=['POST'])
def buy_ticket_route(token_id):
    try:
        data = request.get_json()
        buyer_address = data.get('buyer_address')

        acc = {
            "0x35439095de5fc8B1b809A178a2dfC07C6440F439":"dea0f25d4a2d8edd1cdae3648cb11ac07cff5e7425943200adb9b757d37d0e01",
            "0xCe427f33A70C9730066b122a29CD77150E2994d9":"4aa032769dbfb720323d5177a9984e175883f2b27aed573ad8ea063cac6eb147",
        }

        checksum_address = safe_checksum_address(buyer_address)
        private_key = acc[checksum_address]
        tx_receipt = buy_ticket(checksum_address, private_key, token_id)

        return jsonify({"success": True, "tx_hash": tx_receipt.transactionHash.hex()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

#管理员入口，即官方铸造门票界面
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        to = request.form["to"]
        uri = request.form["uri"]

        response = requests.get(g_uri)
        if response.status_code == 200:
            metadata = response.json()
            price_eth = float(metadata.get("price", 0.0))  # 从JSON中读取ETH单位的价格
        else:
            print(f"无法获取元数据，状态码: {response.status_code}")

        try:
            tx_receipt = mint_ticket(to, g_uri, price_eth)
            # 解析tokenId，ethers日志里topics索引和格式可能要根据你实际合约事件调整
            token_id = int(tx_receipt['logs'][0]['topics'][3].hex(), 16)
            # POST后直接渲染页面并显示铸造成功信息
            return render_template("admin.html", minted=True, token_id=token_id, uri=uri)
        except Exception as e:
            flash(f"铸造失败: {str(e)}")

    # GET请求或者POST出错时，正常渲染表单
    return render_template("admin.html")

#转售功能（待实现）
@app.route('/resell_ticket/<int:token_id>', methods=['POST'])
def resell_ticket(token_id):
    # 把这张票设置为“可售”，加入在售市场
    user_id = session.get('user_id')
    success = mark_ticket_for_sale(user_id, token_id)
    if success:
        flash("已成功上架该票券进行转售！")
    else:
        flash("转售失败，可能你不是票的拥有者。")
    return redirect(url_for('my_tickets'))


if __name__=="__main__":
    app.run(debug=True)