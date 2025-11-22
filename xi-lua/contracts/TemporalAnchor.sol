// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title TemporalAnchor
 * @dev Proof of Semantic Existence (PoSE) with Thermodynamic Priority
 *
 * Core Concept:
 * - Each idea/artifact gets an immutable timestamp + content hash
 * - Priority is determined by ENERGY COST (gas paid)
 * - The more gas paid, the higher the thermodynamic priority
 * - Reversal becomes exponentially impossible over time
 *
 * Formula for Consensus Cost:
 *   ΣE_i = Σ(gas_i × gasPrice_i) for all i in history
 *
 * To reverse priority after N blocks:
 *   Required energy ≈ exp(λ·N) where λ = difficulty factor
 *
 * This creates "informational singularity" - past a certain threshold,
 * reversing history requires more energy than exists in the universe.
 *
 * Part of Ξ-LUA v2.0 SuperProject
 */

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract TemporalAnchor is Ownable, ReentrancyGuard {

    // ═══════════════════════════════════════════════════════════
    // STRUCTS & EVENTS
    // ═══════════════════════════════════════════════════════════

    /**
     * @dev Anchor represents a single proof of existence
     */
    struct Anchor {
        bytes32 contentHash;        // SHA-256 hash of content
        address creator;            // Who created this anchor
        uint256 timestamp;          // Block timestamp
        uint256 blockNumber;        // Block number (for irreversibility calc)
        uint256 energyCost;         // Gas cost paid (thermodynamic weight)
        uint256 cumulativeEnergy;   // Total energy up to this point
        string metadataURI;         // Optional metadata (IPFS, etc.)
        bool exists;                // Existence flag
    }

    /**
     * @dev Priority claim for competing anchors
     */
    struct PriorityClaim {
        uint256 anchorId;           // Which anchor
        uint256 energyStaked;       // Energy staked for priority
        uint256 claimTime;          // When priority was claimed
    }

    // Events
    event AnchorCreated(
        uint256 indexed anchorId,
        bytes32 indexed contentHash,
        address indexed creator,
        uint256 energyCost,
        uint256 timestamp
    );

    event PriorityStaked(
        uint256 indexed anchorId,
        address indexed staker,
        uint256 energyStaked,
        uint256 newCumulativeEnergy
    );

    event ConsensusReached(
        uint256 indexed anchorId,
        uint256 finalEnergy,
        uint256 irreversibilityScore
    );

    // ═══════════════════════════════════════════════════════════
    // STATE VARIABLES
    // ═══════════════════════════════════════════════════════════

    // Mapping: anchorId => Anchor
    mapping(uint256 => Anchor) public anchors;

    // Mapping: contentHash => anchorId (first to claim)
    mapping(bytes32 => uint256) public hashToAnchor;

    // Mapping: anchorId => list of priority claims
    mapping(uint256 => PriorityClaim[]) public priorityClaims;

    // Counter for anchor IDs
    uint256 public nextAnchorId = 1;

    // Total cumulative energy in the system
    uint256 public totalSystemEnergy = 0;

    // Minimum energy cost to create anchor (prevents spam)
    uint256 public minimumEnergyCost = 0.0001 ether;  // ~0.0001 MATIC

    // Difficulty factor λ for irreversibility calculation
    // Higher λ = faster exponential growth of reversal cost
    uint256 public difficultyFactor = 100;  // blocks per e-fold

    // ═══════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════

    constructor() Ownable(msg.sender) {
        // Initialize with genesis anchor (anchor #0)
        anchors[0] = Anchor({
            contentHash: keccak256("GENESIS_XI_LUA_V2"),
            creator: msg.sender,
            timestamp: block.timestamp,
            blockNumber: block.number,
            energyCost: 0,
            cumulativeEnergy: 0,
            metadataURI: "ipfs://genesis",
            exists: true
        });

        emit AnchorCreated(0, keccak256("GENESIS_XI_LUA_V2"), msg.sender, 0, block.timestamp);
    }

    // ═══════════════════════════════════════════════════════════
    // CORE FUNCTIONS
    // ═══════════════════════════════════════════════════════════

    /**
     * @dev Create a new temporal anchor (Proof of Semantic Existence)
     * @param _contentHash SHA-256 hash of the content/idea
     * @param _metadataURI Optional metadata URI (IPFS, etc.)
     * @return anchorId The ID of the newly created anchor
     *
     * Energy cost (msg.value) determines thermodynamic priority:
     * - Higher energy = stronger claim to existence
     * - Energy accumulates over time, making reversal exponentially harder
     */
    function createAnchor(
        bytes32 _contentHash,
        string memory _metadataURI
    )
        external
        payable
        nonReentrant
        returns (uint256)
    {
        require(_contentHash != bytes32(0), "Content hash cannot be empty");
        require(msg.value >= minimumEnergyCost, "Insufficient energy cost");

        uint256 anchorId = nextAnchorId++;
        uint256 energyCost = msg.value;
        uint256 cumulativeEnergy = totalSystemEnergy + energyCost;

        // Create anchor
        anchors[anchorId] = Anchor({
            contentHash: _contentHash,
            creator: msg.sender,
            timestamp: block.timestamp,
            blockNumber: block.number,
            energyCost: energyCost,
            cumulativeEnergy: cumulativeEnergy,
            metadataURI: _metadataURI,
            exists: true
        });

        // Record first claim to this hash (if not already claimed)
        if (hashToAnchor[_contentHash] == 0) {
            hashToAnchor[_contentHash] = anchorId;
        }

        // Update total system energy
        totalSystemEnergy = cumulativeEnergy;

        emit AnchorCreated(anchorId, _contentHash, msg.sender, energyCost, block.timestamp);

        return anchorId;
    }

    /**
     * @dev Stake additional energy to increase priority
     * @param _anchorId The anchor to boost
     *
     * Anyone can stake energy to boost an anchor's priority.
     * This creates a "thermodynamic marketplace" for ideas.
     */
    function stakePriority(uint256 _anchorId)
        external
        payable
        nonReentrant
    {
        require(anchors[_anchorId].exists, "Anchor does not exist");
        require(msg.value > 0, "Must stake non-zero energy");

        // Record priority claim
        priorityClaims[_anchorId].push(PriorityClaim({
            anchorId: _anchorId,
            energyStaked: msg.value,
            claimTime: block.timestamp
        }));

        // Update cumulative energy
        anchors[_anchorId].cumulativeEnergy += msg.value;
        totalSystemEnergy += msg.value;

        emit PriorityStaked(_anchorId, msg.sender, msg.value, anchors[_anchorId].cumulativeEnergy);
    }

    /**
     * @dev Calculate irreversibility score for an anchor
     * @param _anchorId The anchor to check
     * @return score The irreversibility score (higher = more irreversible)
     *
     * Formula:
     *   score = cumulativeEnergy × exp(λ × blocksPassed)
     *
     * Where:
     *   λ = 1 / difficultyFactor
     *   blocksPassed = current block - anchor block
     *
     * As blocks pass, the exponential term grows, making reversal
     * exponentially more expensive.
     */
    function calculateIrreversibility(uint256 _anchorId)
        public
        view
        returns (uint256)
    {
        require(anchors[_anchorId].exists, "Anchor does not exist");

        Anchor memory anchor = anchors[_anchorId];
        uint256 blocksPassed = block.number - anchor.blockNumber;

        // Approximation: exp(x) ≈ 1 + x + x²/2 for small x
        // For larger x, this saturates to max uint256 (effectively infinite)
        uint256 lambda = difficultyFactor;  // In blocks per e-fold

        // Calculate exponential factor (capped to prevent overflow)
        uint256 expFactor;
        if (blocksPassed > lambda * 10) {
            // After 10 e-folds, consider it "infinite"
            expFactor = type(uint256).max / (anchor.cumulativeEnergy + 1);
        } else {
            // Linear approximation for small values
            expFactor = 1 + (blocksPassed * 1e18) / lambda;
        }

        // Score = energy × exp(blocks/λ)
        uint256 score = (anchor.cumulativeEnergy * expFactor) / 1e18;

        return score;
    }

    /**
     * @dev Get anchor details
     */
    function getAnchor(uint256 _anchorId)
        external
        view
        returns (
            bytes32 contentHash,
            address creator,
            uint256 timestamp,
            uint256 blockNumber,
            uint256 energyCost,
            uint256 cumulativeEnergy,
            string memory metadataURI,
            uint256 irreversibilityScore
        )
    {
        require(anchors[_anchorId].exists, "Anchor does not exist");

        Anchor memory anchor = anchors[_anchorId];

        return (
            anchor.contentHash,
            anchor.creator,
            anchor.timestamp,
            anchor.blockNumber,
            anchor.energyCost,
            anchor.cumulativeEnergy,
            anchor.metadataURI,
            calculateIrreversibility(_anchorId)
        );
    }

    /**
     * @dev Get first anchor for a given content hash
     */
    function getFirstAnchor(bytes32 _contentHash)
        external
        view
        returns (uint256)
    {
        return hashToAnchor[_contentHash];
    }

    /**
     * @dev Get number of priority claims for an anchor
     */
    function getPriorityClaimCount(uint256 _anchorId)
        external
        view
        returns (uint256)
    {
        return priorityClaims[_anchorId].length;
    }

    // ═══════════════════════════════════════════════════════════
    // ADMIN FUNCTIONS
    // ═══════════════════════════════════════════════════════════

    /**
     * @dev Update minimum energy cost (only owner)
     */
    function setMinimumEnergyCost(uint256 _newCost) external onlyOwner {
        minimumEnergyCost = _newCost;
    }

    /**
     * @dev Update difficulty factor (only owner)
     */
    function setDifficultyFactor(uint256 _newFactor) external onlyOwner {
        require(_newFactor > 0, "Difficulty must be > 0");
        difficultyFactor = _newFactor;
    }

    /**
     * @dev Withdraw accumulated funds (only owner)
     *
     * Note: This doesn't affect anchor validity.
     * Anchors remain immutable regardless of fund withdrawal.
     */
    function withdraw() external onlyOwner nonReentrant {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");

        (bool success, ) = owner().call{value: balance}("");
        require(success, "Withdrawal failed");
    }

    /**
     * @dev Emergency pause (not implemented - anchors are always valid)
     *
     * Temporal anchors cannot be paused or deleted.
     * They exist forever once created.
     * This is by design - truth cannot be paused.
     */

    // ═══════════════════════════════════════════════════════════
    // UTILITY FUNCTIONS
    // ═══════════════════════════════════════════════════════════

    /**
     * @dev Get contract stats
     */
    function getStats()
        external
        view
        returns (
            uint256 totalAnchors,
            uint256 totalEnergy,
            uint256 minEnergyCost,
            uint256 difficulty
        )
    {
        return (
            nextAnchorId - 1,
            totalSystemEnergy,
            minimumEnergyCost,
            difficultyFactor
        );
    }

    receive() external payable {
        // Accept direct payments as "belief energy" in the system
        totalSystemEnergy += msg.value;
    }
}
