const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying Omega Capitals to Polygon Mainnet...\n");
  console.log("⚠️  WARNING: Deploying to MAINNET - Real funds will be used!\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.provider.getBalance(deployer.address)).toString(), "\n");

  // Confirm deployment
  if (!process.env.CONFIRM_MAINNET_DEPLOY) {
    console.error("❌ Set CONFIRM_MAINNET_DEPLOY=true to proceed with mainnet deployment");
    process.exit(1);
  }

  // Deploy EvidenceNotes
  console.log("📝 Deploying EvidenceNotes...");
  const EvidenceNotes = await hre.ethers.getContractFactory("EvidenceNotes");
  const evidenceNotes = await EvidenceNotes.deploy();
  await evidenceNotes.waitForDeployment();
  const evidenceNotesAddress = await evidenceNotes.getAddress();
  console.log("✅ EvidenceNotes deployed to:", evidenceNotesAddress, "\n");

  // USDC Mainnet: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 (native USDC)
  // Or new USDC: 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359
  const USDC_MAINNET = process.env.USDC_MAINNET_ADDRESS || "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359";

  console.log("🏊 Deploying OmegaPool...");
  const OmegaPool = await hre.ethers.getContractFactory("OmegaPool");
  const omegaPool = await OmegaPool.deploy(USDC_MAINNET);
  await omegaPool.waitForDeployment();
  const omegaPoolAddress = await omegaPool.getAddress();
  console.log("✅ OmegaPool deployed to:", omegaPoolAddress, "\n");

  // Deploy TreasuryVault with multisig signers
  console.log("🏦 Deploying TreasuryVault...");
  const signers = [
    process.env.TREASURY_SIGNER_1 || deployer.address,
    process.env.TREASURY_SIGNER_2 || deployer.address,
    process.env.TREASURY_SIGNER_3 || deployer.address,
    process.env.TREASURY_SIGNER_4 || deployer.address,
    process.env.TREASURY_SIGNER_5 || deployer.address
  ];
  const requiredApprovals = parseInt(process.env.TREASURY_REQUIRED_APPROVALS || "3");

  const TreasuryVault = await hre.ethers.getContractFactory("TreasuryVault");
  const treasuryVault = await TreasuryVault.deploy(signers, requiredApprovals);
  await treasuryVault.waitForDeployment();
  const treasuryVaultAddress = await treasuryVault.getAddress();
  console.log("✅ TreasuryVault deployed to:", treasuryVaultAddress, "\n");

  // Deploy OmegaGovernance
  const GOVERNANCE_TOKEN = process.env.GOVERNANCE_TOKEN || evidenceNotesAddress;

  console.log("🗳️  Deploying OmegaGovernance...");
  const OmegaGovernance = await hre.ethers.getContractFactory("OmegaGovernance");
  const omegaGovernance = await OmegaGovernance.deploy(GOVERNANCE_TOKEN);
  await omegaGovernance.waitForDeployment();
  const omegaGovernanceAddress = await omegaGovernance.getAddress();
  console.log("✅ OmegaGovernance deployed to:", omegaGovernanceAddress, "\n");

  // Save deployment addresses
  const deploymentData = {
    network: "polygon",
    chainId: 137,
    deployedAt: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {
      EvidenceNotes: evidenceNotesAddress,
      OmegaPool: omegaPoolAddress,
      TreasuryVault: treasuryVaultAddress,
      OmegaGovernance: omegaGovernanceAddress
    },
    config: {
      usdcToken: USDC_MAINNET,
      governanceToken: GOVERNANCE_TOKEN,
      treasurySigners: signers,
      requiredApprovals: requiredApprovals
    }
  };

  const deploymentPath = path.join(__dirname, "../backend/abis/deployment-mainnet.json");
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

  console.log("🎉 Mainnet Deployment complete!\n");
  console.log("📋 Summary:");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log("EvidenceNotes:    ", evidenceNotesAddress);
  console.log("OmegaPool:        ", omegaPoolAddress);
  console.log("TreasuryVault:    ", treasuryVaultAddress);
  console.log("OmegaGovernance:  ", omegaGovernanceAddress);
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");

  console.log("🔍 Verify contracts on PolygonScan:");
  console.log(`npx hardhat verify --network polygon ${evidenceNotesAddress}`);
  console.log(`npx hardhat verify --network polygon ${omegaPoolAddress} ${USDC_MAINNET}`);
  console.log(`npx hardhat verify --network polygon ${treasuryVaultAddress} "[${signers.join(',')}]" ${requiredApprovals}`);
  console.log(`npx hardhat verify --network polygon ${omegaGovernanceAddress} ${GOVERNANCE_TOKEN}\n`);

  console.log("⚠️  IMPORTANT: Update .env with contract addresses and restart backend!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
