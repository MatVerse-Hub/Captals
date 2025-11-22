const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying Omega Capitals to Polygon Amoy Testnet...\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString(), "\n");

  // Deploy EvidenceNotes
  console.log("📝 Deploying EvidenceNotes...");
  const EvidenceNotes = await hre.ethers.getContractFactory("EvidenceNotes");
  const evidenceNotes = await EvidenceNotes.deploy();
  await evidenceNotes.waitForDeployment();
  const evidenceNotesAddress = await evidenceNotes.getAddress();
  console.log("✅ EvidenceNotes deployed to:", evidenceNotesAddress, "\n");

  // Deploy OmegaPool (using mock USDC address for testnet)
  // For Polygon Amoy, use USDC test token: 0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582
  const USDC_TESTNET = process.env.USDC_TESTNET_ADDRESS || "0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582";

  console.log("🏊 Deploying OmegaPool...");
  const OmegaPool = await hre.ethers.getContractFactory("OmegaPool");
  const omegaPool = await OmegaPool.deploy(USDC_TESTNET);
  await omegaPool.waitForDeployment();
  const omegaPoolAddress = await omegaPool.getAddress();
  console.log("✅ OmegaPool deployed to:", omegaPoolAddress, "\n");

  // Deploy TreasuryVault with 3 signers, 2 required
  console.log("🏦 Deploying TreasuryVault...");
  const signers = [
    deployer.address,
    process.env.TREASURY_SIGNER_2 || deployer.address,
    process.env.TREASURY_SIGNER_3 || deployer.address
  ];
  const TreasuryVault = await hre.ethers.getContractFactory("TreasuryVault");
  const treasuryVault = await TreasuryVault.deploy(signers, 2);
  await treasuryVault.waitForDeployment();
  const treasuryVaultAddress = await treasuryVault.getAddress();
  console.log("✅ TreasuryVault deployed to:", treasuryVaultAddress, "\n");

  // Deploy OmegaGovernance (mock governance token for now)
  const GOVERNANCE_TOKEN = process.env.GOVERNANCE_TOKEN || evidenceNotesAddress;

  console.log("🗳️  Deploying OmegaGovernance...");
  const OmegaGovernance = await hre.ethers.getContractFactory("OmegaGovernance");
  const omegaGovernance = await OmegaGovernance.deploy(GOVERNANCE_TOKEN);
  await omegaGovernance.waitForDeployment();
  const omegaGovernanceAddress = await omegaGovernance.getAddress();
  console.log("✅ OmegaGovernance deployed to:", omegaGovernanceAddress, "\n");

  // Save deployment addresses
  const deploymentData = {
    network: "amoy",
    chainId: 80002,
    deployedAt: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {
      EvidenceNotes: evidenceNotesAddress,
      OmegaPool: omegaPoolAddress,
      TreasuryVault: treasuryVaultAddress,
      OmegaGovernance: omegaGovernanceAddress
    },
    config: {
      usdcToken: USDC_TESTNET,
      governanceToken: GOVERNANCE_TOKEN,
      treasurySigners: signers,
      requiredApprovals: 2
    }
  };

  const deploymentPath = path.join(__dirname, "../backend/abis/deployment-amoy.json");
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentData, null, 2));
  console.log("💾 Deployment data saved to:", deploymentPath, "\n");

  // Export ABIs
  console.log("📦 Exporting ABIs...");
  const artifactsPath = path.join(__dirname, "../contracts/artifacts");
  const abiPath = path.join(__dirname, "../backend/abis");

  const contracts = ["EvidenceNotes", "OmegaPool", "TreasuryVault", "OmegaGovernance"];
  for (const contract of contracts) {
    const artifact = require(path.join(artifactsPath, `core/${contract}.sol/${contract}.json`));
    fs.writeFileSync(
      path.join(abiPath, `${contract}.json`),
      JSON.stringify(artifact.abi, null, 2)
    );
  }
  console.log("✅ ABIs exported\n");

  console.log("🎉 Deployment complete!\n");
  console.log("📋 Summary:");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("EvidenceNotes:    ", evidenceNotesAddress);
  console.log("OmegaPool:        ", omegaPoolAddress);
  console.log("TreasuryVault:    ", treasuryVaultAddress);
  console.log("OmegaGovernance:  ", omegaGovernanceAddress);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

  console.log("🔍 Verify contracts with:");
  console.log(`npx hardhat verify --network amoy ${evidenceNotesAddress}`);
  console.log(`npx hardhat verify --network amoy ${omegaPoolAddress} ${USDC_TESTNET}`);
  console.log(`npx hardhat verify --network amoy ${treasuryVaultAddress} "[${signers.join(',')}]" 2`);
  console.log(`npx hardhat verify --network amoy ${omegaGovernanceAddress} ${GOVERNANCE_TOKEN}\n`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
