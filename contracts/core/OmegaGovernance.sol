// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title OmegaGovernance
 * @dev Governance contract for Omega Capitals ecosystem
 * Implements proposal creation, voting, and execution
 */
contract OmegaGovernance is Ownable, ReentrancyGuard {
    IERC20 public omegaToken;

    enum ProposalState {
        Pending,
        Active,
        Defeated,
        Succeeded,
        Executed,
        Cancelled
    }

    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 startTime;
        uint256 endTime;
        ProposalState state;
        mapping(address => bool) hasVoted;
        mapping(address => uint256) votes;
    }

    // Proposal ID counter
    uint256 public proposalCount;

    // Proposal ID to Proposal
    mapping(uint256 => Proposal) public proposals;

    // Voting parameters
    uint256 public votingPeriod = 3 days;
    uint256 public proposalThreshold = 1000 * 10**18; // 1000 OMEGA to propose
    uint256 public quorumPercentage = 4; // 4% quorum

    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string title,
        uint256 startTime,
        uint256 endTime
    );
    event VoteCast(
        address indexed voter,
        uint256 indexed proposalId,
        bool support,
        uint256 votes
    );
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCancelled(uint256 indexed proposalId);

    constructor(address _omegaToken) {
        require(_omegaToken != address(0), "Invalid token address");
        omegaToken = IERC20(_omegaToken);
    }

    /**
     * @dev Create a new proposal
     * @param title Proposal title
     * @param description Proposal description
     * @return proposalId The created proposal ID
     */
    function createProposal(
        string memory title,
        string memory description
    ) external returns (uint256 proposalId) {
        require(
            omegaToken.balanceOf(msg.sender) >= proposalThreshold,
            "Insufficient tokens to propose"
        );
        require(bytes(title).length > 0, "Title required");
        require(bytes(description).length > 0, "Description required");

        proposalCount++;
        proposalId = proposalCount;

        Proposal storage newProposal = proposals[proposalId];
        newProposal.id = proposalId;
        newProposal.proposer = msg.sender;
        newProposal.title = title;
        newProposal.description = description;
        newProposal.startTime = block.timestamp;
        newProposal.endTime = block.timestamp + votingPeriod;
        newProposal.state = ProposalState.Active;

        emit ProposalCreated(
            proposalId,
            msg.sender,
            title,
            newProposal.startTime,
            newProposal.endTime
        );

        return proposalId;
    }

    /**
     * @dev Cast a vote on a proposal
     * @param proposalId Proposal ID
     * @param support True for yes, false for no
     */
    function castVote(uint256 proposalId, bool support) external nonReentrant {
        require(proposalId > 0 && proposalId <= proposalCount, "Invalid proposal");

        Proposal storage proposal = proposals[proposalId];

        require(proposal.state == ProposalState.Active, "Proposal not active");
        require(block.timestamp < proposal.endTime, "Voting period ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");

        uint256 votes = omegaToken.balanceOf(msg.sender);
        require(votes > 0, "No voting power");

        proposal.hasVoted[msg.sender] = true;
        proposal.votes[msg.sender] = votes;

        if (support) {
            proposal.forVotes += votes;
        } else {
            proposal.againstVotes += votes;
        }

        emit VoteCast(msg.sender, proposalId, support, votes);
    }

    /**
     * @dev Execute a succeeded proposal
     * @param proposalId Proposal ID
     */
    function executeProposal(uint256 proposalId) external nonReentrant {
        require(proposalId > 0 && proposalId <= proposalCount, "Invalid proposal");

        Proposal storage proposal = proposals[proposalId];

        require(proposal.state == ProposalState.Active, "Proposal not active");
        require(block.timestamp >= proposal.endTime, "Voting still active");

        // Calculate quorum
        uint256 totalSupply = omegaToken.totalSupply();
        uint256 quorum = (totalSupply * quorumPercentage) / 100;
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes;

        if (totalVotes < quorum) {
            proposal.state = ProposalState.Defeated;
        } else if (proposal.forVotes > proposal.againstVotes) {
            proposal.state = ProposalState.Succeeded;
            // In production, execute proposal actions here
            proposal.state = ProposalState.Executed;
            emit ProposalExecuted(proposalId);
        } else {
            proposal.state = ProposalState.Defeated;
        }
    }

    /**
     * @dev Cancel a proposal (only proposer or owner)
     * @param proposalId Proposal ID
     */
    function cancelProposal(uint256 proposalId) external {
        require(proposalId > 0 && proposalId <= proposalCount, "Invalid proposal");

        Proposal storage proposal = proposals[proposalId];

        require(
            msg.sender == proposal.proposer || msg.sender == owner(),
            "Not authorized"
        );
        require(proposal.state == ProposalState.Active, "Proposal not active");

        proposal.state = ProposalState.Cancelled;
        emit ProposalCancelled(proposalId);
    }

    /**
     * @dev Get proposal details
     * @param proposalId Proposal ID
     */
    function getProposal(uint256 proposalId) external view returns (
        uint256 id,
        address proposer,
        string memory title,
        string memory description,
        uint256 forVotes,
        uint256 againstVotes,
        uint256 startTime,
        uint256 endTime,
        ProposalState state
    ) {
        require(proposalId > 0 && proposalId <= proposalCount, "Invalid proposal");

        Proposal storage proposal = proposals[proposalId];

        return (
            proposal.id,
            proposal.proposer,
            proposal.title,
            proposal.description,
            proposal.forVotes,
            proposal.againstVotes,
            proposal.startTime,
            proposal.endTime,
            proposal.state
        );
    }

    /**
     * @dev Check if an address has voted on a proposal
     */
    function hasVoted(uint256 proposalId, address voter) external view returns (bool) {
        return proposals[proposalId].hasVoted[voter];
    }

    /**
     * @dev Update voting period
     */
    function setVotingPeriod(uint256 newPeriod) external onlyOwner {
        require(newPeriod >= 1 days && newPeriod <= 30 days, "Invalid period");
        votingPeriod = newPeriod;
    }

    /**
     * @dev Update proposal threshold
     */
    function setProposalThreshold(uint256 newThreshold) external onlyOwner {
        require(newThreshold > 0, "Threshold must be positive");
        proposalThreshold = newThreshold;
    }

    /**
     * @dev Update quorum percentage
     */
    function setQuorumPercentage(uint256 newQuorum) external onlyOwner {
        require(newQuorum > 0 && newQuorum <= 100, "Invalid quorum");
        quorumPercentage = newQuorum;
    }
}
