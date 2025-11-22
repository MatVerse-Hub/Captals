// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "../libraries/OmegaScore.sol";

/**
 * @title OmegaCapitals
 * @dev Core ERC20 token for the Omega Capitals ecosystem
 */
contract OmegaCapitals is ERC20, Ownable, ReentrancyGuard {
    using OmegaScore for OmegaScore.ScoreParams;

    // Asset Omega Scores
    mapping(address => uint256) public omegaScores;

    // Asset parameters for score calculation
    mapping(address => OmegaScore.ScoreParams) public assetParams;

    // Whitelisted assets
    mapping(address => bool) public whitelistedAssets;

    // Events
    event OmegaScoreUpdated(address indexed asset, uint256 newScore);
    event AssetWhitelisted(address indexed asset, bool status);

    constructor() ERC20("Omega Capitals Token", "OMEGA") {
        // Mint initial supply: 1 billion tokens
        _mint(msg.sender, 1_000_000_000 * 10 ** decimals());
    }

    /**
     * @dev Updates the Omega Score for a specific asset
     * @param asset Address of the asset
     * @param params Score parameters (Ψ, Θ, CVaR, PoLE)
     */
    function updateOmegaScore(
        address asset,
        OmegaScore.ScoreParams memory params
    ) public onlyOwner {
        require(asset != address(0), "Invalid asset address");

        uint256 score = params.calculateOmegaScore();
        omegaScores[asset] = score;
        assetParams[asset] = params;

        emit OmegaScoreUpdated(asset, score);
    }

    /**
     * @dev Batch update Omega Scores for multiple assets
     * @param assets Array of asset addresses
     * @param params Array of score parameters
     */
    function batchUpdateOmegaScores(
        address[] calldata assets,
        OmegaScore.ScoreParams[] calldata params
    ) external onlyOwner {
        require(assets.length == params.length, "Arrays length mismatch");

        for (uint256 i = 0; i < assets.length; i++) {
            updateOmegaScore(assets[i], params[i]);
        }
    }

    /**
     * @dev Whitelist or delist an asset
     * @param asset Address of the asset
     * @param status Whitelist status
     */
    function setAssetWhitelist(address asset, bool status) external onlyOwner {
        require(asset != address(0), "Invalid asset address");
        whitelistedAssets[asset] = status;
        emit AssetWhitelisted(asset, status);
    }

    /**
     * @dev Get Omega Score for an asset
     * @param asset Address of the asset
     * @return The Omega Score
     */
    function getOmegaScore(address asset) external view returns (uint256) {
        return omegaScores[asset];
    }

    /**
     * @dev Check if an asset meets minimum Omega Score requirement
     * @param asset Address of the asset
     * @param minScore Minimum required score
     * @return True if asset meets requirement
     */
    function meetsScoreRequirement(address asset, uint256 minScore) external view returns (bool) {
        return omegaScores[asset] >= minScore;
    }

    /**
     * @dev Stake OMEGA tokens
     * @param amount Amount to stake
     */
    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake 0");
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");

        _transfer(msg.sender, address(this), amount);
        // Additional staking logic would be implemented here
    }

    /**
     * @dev Burn tokens to reduce supply
     * @param amount Amount to burn
     */
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}
