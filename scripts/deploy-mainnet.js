const { ethers } = require("hardhat");

async function main() {
  console.log("⚠️  MAINNET DEPLOYMENT - Please confirm all settings!\n");

  // Safety check
  if (network.name !== "polygon") {
    throw new Error("This script is for Polygon mainnet only!");
  }

  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "MATIC");

  if (balance < ethers.parseEther("1")) {
    throw new Error("Insufficient balance for deployment!");
  }

  console.log("\n⏳ Waiting 10 seconds before deployment...");
  await new Promise(resolve => setTimeout(resolve, 10000));

  // Deploy contracts (same as testnet)
  console.log("\n🚀 Starting deployment...\n");

  const OmegaCapitals = await ethers.getContractFactory("OmegaCapitals");
  const omegaCapitals = await OmegaCapitals.deploy();
  await omegaCapitals.waitForDeployment();
  console.log("✅ OmegaCapitals:", await omegaCapitals.getAddress());

  const OmegaGovernance = await ethers.getContractFactory("OmegaGovernance");
  const governance = await OmegaGovernance.deploy(await omegaCapitals.getAddress());
  await governance.waitForDeployment();
  console.log("✅ OmegaGovernance:", await governance.getAddress());

  const EvidenceNotes = await ethers.getContractFactory("EvidenceNotes");
  const evidenceNotes = await EvidenceNotes.deploy();
  await evidenceNotes.waitForDeployment();
  console.log("✅ EvidenceNotes:", await evidenceNotes.getAddress());

  const OmegaFunds = await ethers.getContractFactory("OmegaFunds");
  const luaPayOracle = process.env.LUA_PAY_ORACLE || deployer.address;
  const omegaFunds = await OmegaFunds.deploy(luaPayOracle);
  await omegaFunds.waitForDeployment();
  console.log("✅ OmegaFunds:", await omegaFunds.getAddress());

  console.log("\n🎉 Mainnet deployment complete!");
  console.log("⚠️  Remember to verify contracts on PolygonScan!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
