const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("OmegaCapitals Token", function () {
  let omegaCapitals;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const OmegaCapitals = await ethers.getContractFactory("OmegaCapitals");
    omegaCapitals = await OmegaCapitals.deploy();
    await omegaCapitals.waitForDeployment();
  });

  it("Should have correct name and symbol", async function () {
    expect(await omegaCapitals.name()).to.equal("Omega Capitals Token");
    expect(await omegaCapitals.symbol()).to.equal("OMEGA");
  });

  it("Should mint initial supply to owner", async function () {
    const ownerBalance = await omegaCapitals.balanceOf(owner.address);
    expect(ownerBalance).to.be.gt(0);
  });

  it("Should allow updating omega score", async function () {
    const assetAddress = addr1.address;
    const params = {
      psi: 8500,
      theta: 9200,
      cvar: 500,
      pole: 8800
    };

    await omegaCapitals.updateOmegaScore(assetAddress, params);
    const score = await omegaCapitals.getOmegaScore(assetAddress);
    expect(score).to.be.gt(0);
  });

  it("Should burn tokens", async function () {
    const burnAmount = ethers.parseEther("100");
    const initialBalance = await omegaCapitals.balanceOf(owner.address);

    await omegaCapitals.burn(burnAmount);
    const finalBalance = await omegaCapitals.balanceOf(owner.address);

    expect(finalBalance).to.equal(initialBalance - burnAmount);
  });
});

describe("EvidenceNotes NFT", function () {
  let evidenceNotes;
  let owner;
  let addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    const EvidenceNotes = await ethers.getContractFactory("EvidenceNotes");
    evidenceNotes = await EvidenceNotes.deploy();
    await evidenceNotes.waitForDeployment();
  });

  it("Should have correct name and symbol", async function () {
    expect(await evidenceNotes.name()).to.equal("Omega Evidence Note");
    expect(await evidenceNotes.symbol()).to.equal("OENOTE");
  });

  it("Should mint evidence note", async function () {
    const evidenceHash = "QmTest123";
    const amount = ethers.parseEther("100");

    await evidenceNotes.mintEvidenceNote(
      addr1.address,
      evidenceHash,
      amount,
      "OmegaFund"
    );

    const totalSupply = await evidenceNotes.totalSupply();
    expect(totalSupply).to.equal(1);
  });

  it("Should prevent transfer of soulbound NFT", async function () {
    const evidenceHash = "QmTest456";
    const amount = ethers.parseEther("50");

    await evidenceNotes.mintEvidenceNote(
      addr1.address,
      evidenceHash,
      amount,
      "OmegaFund"
    );

    // Try to transfer (should fail)
    await expect(
      evidenceNotes.transferFrom(addr1.address, owner.address, 1)
    ).to.be.revertedWith("EvidenceNotes: Soulbound tokens cannot be transferred");
  });
});

describe("OmegaGovernance", function () {
  let governance;
  let omegaToken;
  let owner;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();

    const OmegaCapitals = await ethers.getContractFactory("OmegaCapitals");
    omegaToken = await OmegaCapitals.deploy();
    await omegaToken.waitForDeployment();

    const OmegaGovernance = await ethers.getContractFactory("OmegaGovernance");
    governance = await OmegaGovernance.deploy(await omegaToken.getAddress());
    await governance.waitForDeployment();
  });

  it("Should create proposal", async function () {
    await governance.createProposal(
      "Test Proposal",
      "This is a test proposal"
    );

    const proposalCount = await governance.proposalCount();
    expect(proposalCount).to.equal(1);
  });

  it("Should update voting parameters", async function () {
    const newPeriod = 7 * 24 * 60 * 60; // 7 days
    await governance.setVotingPeriod(newPeriod);

    const votingPeriod = await governance.votingPeriod();
    expect(votingPeriod).to.equal(newPeriod);
  });
});
