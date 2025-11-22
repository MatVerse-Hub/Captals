const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying Omega Capitals contracts to testnet...\n");

  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH\n");

  // Deploy OmegaScore Library
  console.log("📚 Deploying OmegaScore library...");
  const OmegaScore = await ethers.getContractFactory("OmegaScore");
  // Note: Libraries don't need deployment for internal functions
  console.log("✅ OmegaScore library ready\n");

  // Deploy OmegaCapitals Token
  console.log("💎 Deploying OmegaCapitals token...");
  const OmegaCapitals = await ethers.getContractFactory("OmegaCapitals");
  const omegaCapitals = await OmegaCapitals.deploy();
  await omegaCapitals.waitForDeployment();
  const omegaAddress = await omegaCapitals.getAddress();
  console.log("✅ OmegaCapitals deployed to:", omegaAddress, "\n");

  // Deploy OmegaGovernance
  console.log("🗳️  Deploying OmegaGovernance...");
  const OmegaGovernance = await ethers.getContractFactory("OmegaGovernance");
  const governance = await OmegaGovernance.deploy(omegaAddress);
  await governance.waitForDeployment();
  const governanceAddress = await governance.getAddress();
  console.log("✅ OmegaGovernance deployed to:", governanceAddress, "\n");

  // Deploy EvidenceNotes
  console.log("📜 Deploying EvidenceNotes NFT...");
  const EvidenceNotes = await ethers.getContractFactory("EvidenceNotes");
  const evidenceNotes = await EvidenceNotes.deploy();
  await evidenceNotes.waitForDeployment();
  const evidenceAddress = await evidenceNotes.getAddress();
  console.log("✅ EvidenceNotes deployed to:", evidenceAddress, "\n");

  // Deploy OmegaPool (example with dummy tokens)
  console.log("💧 Deploying OmegaPool...");
  const OmegaPool = await ethers.getContractFactory("OmegaPool");
  // Using OmegaCapitals as both tokens for demo
  const pool = await OmegaPool.deploy(omegaAddress, omegaAddress);
  await pool.waitForDeployment();
  const poolAddress = await pool.getAddress();
  console.log("✅ OmegaPool deployed to:", poolAddress, "\n");

  // Deploy OmegaFunds
  console.log("🏦 Deploying OmegaFunds...");
  const OmegaFunds = await ethers.getContractFactory("OmegaFunds");
  const luaPayOracle = deployer.address; // Use deployer as oracle for testing
  const omegaFunds = await OmegaFunds.deploy(luaPayOracle);
  await omegaFunds.waitForDeployment();
  const fundsAddress = await omegaFunds.getAddress();
  console.log("✅ OmegaFunds deployed to:", fundsAddress, "\n");

  // Summary
  console.log("=" .repeat(60));
  console.log("📝 DEPLOYMENT SUMMARY");
  console.log("=" .repeat(60));
  console.log("Network:", network.name);
  console.log("\nContract Addresses:");
  console.log("-------------------");
  console.log("OmegaCapitals Token:", omegaAddress);
  console.log("OmegaGovernance:    ", governanceAddress);
  console.log("EvidenceNotes NFT:  ", evidenceAddress);
  console.log("OmegaPool:          ", poolAddress);
  console.log("OmegaFunds:         ", fundsAddress);
  console.log("\n💡 Save these addresses to your .env file!");
  console.log("=" .repeat(60));

  // Generate .env update
  console.log("\n📋 Add to .env:");
  console.log(`OMEGA_CONTRACT_ADDRESS=${omegaAddress}`);
  console.log(`GOVERNANCE_CONTRACT_ADDRESS=${governanceAddress}`);
  console.log(`EVIDENCE_CONTRACT_ADDRESS=${evidenceAddress}`);
  console.log(`POOL_CONTRACT_ADDRESS=${poolAddress}`);
  console.log(`FUNDS_CONTRACT_ADDRESS=${fundsAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
