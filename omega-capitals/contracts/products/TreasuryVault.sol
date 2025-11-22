// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title TreasuryVault
 * @dev Multi-sig treasury for Omega Capitals protocol fees and governance funds
 */
contract TreasuryVault is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct Proposal {
        uint256 id;
        address recipient;
        uint256 amount;
        address token;
        string description;
        uint256 approvals;
        uint256 executedAt;
        bool executed;
        mapping(address => bool) hasApproved;
    }

    // State variables
    mapping(address => bool) public signers;
    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCounter;
    uint256 public requiredApprovals;
    uint256 public signerCount;

    // Events
    event SignerAdded(address indexed signer);
    event SignerRemoved(address indexed signer);
    event ProposalCreated(uint256 indexed proposalId, address recipient, uint256 amount);
    event ProposalApproved(uint256 indexed proposalId, address indexed signer);
    event ProposalExecuted(uint256 indexed proposalId, address recipient, uint256 amount);
    event FundsReceived(address indexed from, uint256 amount, address token);

    modifier onlySigner() {
        require(signers[msg.sender], "Not a signer");
        _;
    }

    constructor(address[] memory _signers, uint256 _requiredApprovals) Ownable(msg.sender) {
        require(_signers.length >= _requiredApprovals, "Invalid threshold");
        require(_requiredApprovals > 0, "Threshold must be > 0");

        for (uint256 i = 0; i < _signers.length; i++) {
            address signer = _signers[i];
            require(signer != address(0), "Invalid signer");
            require(!signers[signer], "Duplicate signer");

            signers[signer] = true;
            emit SignerAdded(signer);
        }

        signerCount = _signers.length;
        requiredApprovals = _requiredApprovals;
    }

    /**
     * @dev Create withdrawal proposal
     */
    function createProposal(
        address recipient,
        uint256 amount,
        address token,
        string memory description
    ) external onlySigner returns (uint256) {
        require(recipient != address(0), "Invalid recipient");
        require(amount > 0, "Zero amount");

        uint256 proposalId = ++proposalCounter;

        Proposal storage proposal = proposals[proposalId];
        proposal.id = proposalId;
        proposal.recipient = recipient;
        proposal.amount = amount;
        proposal.token = token;
        proposal.description = description;
        proposal.approvals = 0;
        proposal.executed = false;

        emit ProposalCreated(proposalId, recipient, amount);
        return proposalId;
    }

    /**
     * @dev Approve proposal
     */
    function approveProposal(uint256 proposalId) external onlySigner {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(!proposal.executed, "Already executed");
        require(!proposal.hasApproved[msg.sender], "Already approved");

        proposal.hasApproved[msg.sender] = true;
        proposal.approvals++;

        emit ProposalApproved(proposalId, msg.sender);

        // Auto-execute if threshold reached
        if (proposal.approvals >= requiredApprovals) {
            _executeProposal(proposalId);
        }
    }

    /**
     * @dev Execute approved proposal
     */
    function _executeProposal(uint256 proposalId) internal nonReentrant {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.approvals >= requiredApprovals, "Insufficient approvals");
        require(!proposal.executed, "Already executed");

        proposal.executed = true;
        proposal.executedAt = block.timestamp;

        if (proposal.token == address(0)) {
            // Native token (ETH/MATIC)
            require(address(this).balance >= proposal.amount, "Insufficient balance");
            payable(proposal.recipient).transfer(proposal.amount);
        } else {
            // ERC20 token
            IERC20(proposal.token).safeTransfer(proposal.recipient, proposal.amount);
        }

        emit ProposalExecuted(proposalId, proposal.recipient, proposal.amount);
    }

    /**
     * @dev Add new signer (requires owner)
     */
    function addSigner(address signer) external onlyOwner {
        require(signer != address(0), "Invalid signer");
        require(!signers[signer], "Already a signer");

        signers[signer] = true;
        signerCount++;

        emit SignerAdded(signer);
    }

    /**
     * @dev Remove signer (requires owner)
     */
    function removeSigner(address signer) external onlyOwner {
        require(signers[signer], "Not a signer");
        require(signerCount > requiredApprovals, "Cannot remove - would break threshold");

        signers[signer] = false;
        signerCount--;

        emit SignerRemoved(signer);
    }

    /**
     * @dev Update approval threshold
     */
    function setRequiredApprovals(uint256 newThreshold) external onlyOwner {
        require(newThreshold > 0 && newThreshold <= signerCount, "Invalid threshold");
        requiredApprovals = newThreshold;
    }

    /**
     * @dev Get proposal approval status
     */
    function hasApproved(uint256 proposalId, address signer) external view returns (bool) {
        return proposals[proposalId].hasApproved[signer];
    }

    /**
     * @dev Get token balance
     */
    function getBalance(address token) external view returns (uint256) {
        if (token == address(0)) {
            return address(this).balance;
        }
        return IERC20(token).balanceOf(address(this));
    }

    /**
     * @dev Receive ETH/MATIC
     */
    receive() external payable {
        emit FundsReceived(msg.sender, msg.value, address(0));
    }
}
