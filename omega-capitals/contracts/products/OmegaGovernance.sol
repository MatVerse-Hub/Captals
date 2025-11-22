// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../libraries/OmegaScore.sol";

/**
 * @title OmegaGovernance
 * @dev Governance system for Omega Capitals protocol
 * Voting power weighted by Ω-Score and token holdings
 */
contract OmegaGovernance is Ownable {
    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 startBlock;
        uint256 endBlock;
        bool executed;
        bool canceled;
        mapping(address => bool) hasVoted;
        mapping(address => bool) voteChoice;  // true = for, false = against
    }

    struct Voter {
        uint256 omegaScore;
        uint256 tokenBalance;
        uint256 votingPower;
        uint256 lastUpdateBlock;
    }

    // State variables
    IERC20 public governanceToken;
    mapping(uint256 => Proposal) public proposals;
    mapping(address => Voter) public voters;
    uint256 public proposalCounter;

    uint256 public votingPeriod = 17280;  // ~3 days (assuming 15s blocks)
    uint256 public proposalThreshold = 1000 ether;  // Min tokens to propose
    uint256 public quorumVotes = 10000 ether;  // Min votes to pass

    // Events
    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        string title,
        uint256 startBlock,
        uint256 endBlock
    );
    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        bool support,
        uint256 votingPower
    );
    event ProposalExecuted(uint256 indexed proposalId);
    event ProposalCanceled(uint256 indexed proposalId);
    event VoterRegistered(address indexed voter, uint256 omegaScore, uint256 votingPower);

    constructor(address _governanceToken) Ownable(msg.sender) {
        governanceToken = IERC20(_governanceToken);
    }

    /**
     * @dev Register voter with Ω-Score
     * @param cvar CVaR metric
     * @param beta Beta metric
     * @param err5m ERR5m metric
     * @param idem Idempotency metric
     */
    function registerVoter(
        uint256 cvar,
        uint256 beta,
        uint256 err5m,
        uint256 idem
    ) external {
        uint256 omegaScore = OmegaScore.compute(cvar, beta, err5m, idem);
        uint256 tokenBalance = governanceToken.balanceOf(msg.sender);

        // Voting power = tokens * (1 + Ω/1000)
        // Higher Ω-Score multiplies voting power
        uint256 votingPower = (tokenBalance * (1000 + omegaScore)) / 1000;

        voters[msg.sender] = Voter({
            omegaScore: omegaScore,
            tokenBalance: tokenBalance,
            votingPower: votingPower,
            lastUpdateBlock: block.number
        });

        emit VoterRegistered(msg.sender, omegaScore, votingPower);
    }

    /**
     * @dev Create new proposal
     */
    function propose(
        string memory title,
        string memory description
    ) external returns (uint256) {
        require(
            governanceToken.balanceOf(msg.sender) >= proposalThreshold,
            "Below proposal threshold"
        );

        uint256 proposalId = ++proposalCounter;
        Proposal storage proposal = proposals[proposalId];

        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.title = title;
        proposal.description = description;
        proposal.startBlock = block.number;
        proposal.endBlock = block.number + votingPeriod;
        proposal.executed = false;
        proposal.canceled = false;

        emit ProposalCreated(
            proposalId,
            msg.sender,
            title,
            proposal.startBlock,
            proposal.endBlock
        );

        return proposalId;
    }

    /**
     * @dev Cast vote on proposal
     * @param proposalId Proposal ID
     * @param support true = for, false = against
     */
    function castVote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(block.number >= proposal.startBlock, "Voting not started");
        require(block.number <= proposal.endBlock, "Voting ended");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        require(!proposal.canceled, "Proposal canceled");

        Voter storage voter = voters[msg.sender];
        require(voter.votingPower > 0, "Not registered or zero power");

        proposal.hasVoted[msg.sender] = true;
        proposal.voteChoice[msg.sender] = support;

        if (support) {
            proposal.forVotes += voter.votingPower;
        } else {
            proposal.againstVotes += voter.votingPower;
        }

        emit VoteCast(proposalId, msg.sender, support, voter.votingPower);
    }

    /**
     * @dev Execute passed proposal
     */
    function execute(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");
        require(block.number > proposal.endBlock, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(!proposal.canceled, "Proposal canceled");

        uint256 totalVotes = proposal.forVotes + proposal.againstVotes;
        require(totalVotes >= quorumVotes, "Quorum not reached");
        require(proposal.forVotes > proposal.againstVotes, "Proposal defeated");

        proposal.executed = true;

        emit ProposalExecuted(proposalId);
    }

    /**
     * @dev Cancel proposal (only proposer or owner)
     */
    function cancel(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(
            msg.sender == proposal.proposer || msg.sender == owner(),
            "Not authorized"
        );
        require(!proposal.executed, "Already executed");
        require(!proposal.canceled, "Already canceled");

        proposal.canceled = true;

        emit ProposalCanceled(proposalId);
    }

    /**
     * @dev Get proposal state
     */
    function getProposalState(uint256 proposalId)
        external
        view
        returns (
            string memory state,
            uint256 forVotes,
            uint256 againstVotes,
            uint256 totalVotes
        )
    {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "Proposal does not exist");

        forVotes = proposal.forVotes;
        againstVotes = proposal.againstVotes;
        totalVotes = forVotes + againstVotes;

        if (proposal.canceled) {
            state = "Canceled";
        } else if (proposal.executed) {
            state = "Executed";
        } else if (block.number <= proposal.endBlock) {
            state = "Active";
        } else if (totalVotes < quorumVotes) {
            state = "Failed (Quorum)";
        } else if (forVotes <= againstVotes) {
            state = "Defeated";
        } else {
            state = "Succeeded";
        }
    }

    /**
     * @dev Update governance parameters
     */
    function setVotingPeriod(uint256 newPeriod) external onlyOwner {
        votingPeriod = newPeriod;
    }

    function setProposalThreshold(uint256 newThreshold) external onlyOwner {
        proposalThreshold = newThreshold;
    }

    function setQuorumVotes(uint256 newQuorum) external onlyOwner {
        quorumVotes = newQuorum;
    }

    /**
     * @dev Get voter info
     */
    function getVoterInfo(address voter)
        external
        view
        returns (uint256 omegaScore, uint256 tokenBalance, uint256 votingPower)
    {
        Voter storage v = voters[voter];
        return (v.omegaScore, v.tokenBalance, v.votingPower);
    }
}
