const hre = require("hardhat");
const { ethers } = hre;
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("👤 Deploying contracts with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "ETH");

  const TicketNFT = await ethers.getContractFactory("TicketNFT");
  const ticketNFT = await TicketNFT.deploy();
  await ticketNFT.waitForDeployment();

  console.log("✅ Contract deployed at:", ticketNFT.target);

  const addresses = { TicketNFT: ticketNFT.target };
  const outputPath = path.join(__dirname, "..", "deployedAddress.json");
  fs.writeFileSync(outputPath, JSON.stringify(addresses, null, 2));
  console.log("📦 Contract address saved to deployedAddress.json");
}

main().catch(console.error);


/*
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("👤 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", (await deployer.getBalance()).toString());

  const NFTicket = await ethers.getContractFactory("NFTicket");
  const nfticket = await NFTicket.deploy(); // 若有构造函数参数请传入
  await nfticket.deployed();

  console.log("📦 NFTicket deployed to:", nfticket.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});


*/