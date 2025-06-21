# 🎟️ NFTticket - 基于区块链的门票管理系统

NFTticket是一个基于以太坊区块链（Sepolia测试网）的去中心化门票管理平台，支持 NFT 门票的铸造、购买、转售（待实现）与展示，解决传统票务中的伪造、黄牛和票据追踪难题。

## 📖 项目简介

本系统结合 Web3 技术和智能合约，允许主办方以 NFT 形式发行门票，并通过区块链保障门票的唯一性和可验证性。用户可通过前端界面购票、查看已购票，并将其转售（待实现）至二级市场。

## 🚀 项目功能

- 👮 管理员功能：
  - NFT 门票铸造
  - 门票发售与价格设定

- 🙋 用户功能：
  - 浏览主售与二级市场门票
  - 连接钱包进行购票与转售
  - 查看“我的门票”信息（含票据编号、所属活动等）

## 💻 技术栈

- 前端：Flask + Jinja2 + HTML/CSS
- 后端：Python + Web3.py
- 区块链：Solidity 合约部署至 Sepolia 测试网
- 工具：Hardhat、MetaMask、Truffle（可选）

## 🛠️ 快速开始

```bash
# 克隆项目
git clone https://github.com/Canjyujan/NFTticket.git
cd NFTticket

# 启动后端（需先部署智能合约）
python app.py
