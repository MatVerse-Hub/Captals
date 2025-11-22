// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title OmegaFunds
 * @dev Tokenized investment funds (ETF-like) with LUA-PAY integration
 */
contract OmegaFunds is ERC20, Ownable, ReentrancyGuard {
    // LUA-PAY oracle address for payment verification
    address public luaPayOracle;

    // Minimum investment amount
    uint256 public minInvestment = 10 * 10**18; // 10 tokens

    // Total assets under management
    uint256 public totalAUM;

    // Fund performance metrics
    uint256 public navPerShare; // Net Asset Value per share (scaled by 1e18)

    struct Investment {
        uint256 amount;
        uint256 timestamp;
        string invoiceId;
        bool isActive;
    }

    // Investor to their investments
    mapping(address => Investment[]) public investments;

    // Invoice ID to payment status
    mapping(string => bool) public processedInvoices;

    // Events
    event InvestmentReceived(address indexed investor, uint256 amount, string invoiceId);
    event InvestmentRedeemed(address indexed investor, uint256 shares, uint256 amount);
    event NAVUpdated(uint256 newNAV, uint256 timestamp);
    event LuaPayOracleUpdated(address indexed newOracle);

    constructor(address _luaPayOracle) ERC20("Omega Fund Token", "OFUND") {
        require(_luaPayOracle != address(0), "Invalid oracle address");
        luaPayOracle = _luaPayOracle;
        navPerShare = 1e18; // Initial NAV = 1.0
    }

    /**
     * @dev Process LUA-PAY payment and mint fund shares
     * @param investor Investor address
     * @param amount Investment amount
     * @param invoiceId LUA-PAY invoice ID
     */
    function processLuaPayment(
        address investor,
        uint256 amount,
        string memory invoiceId
    ) external nonReentrant {
        require(msg.sender == luaPayOracle, "Only LUA-PAY oracle can call");
        require(investor != address(0), "Invalid investor address");
        require(amount >= minInvestment, "Amount below minimum");
        require(!processedInvoices[invoiceId], "Invoice already processed");

        // Mark invoice as processed
        processedInvoices[invoiceId] = true;

        // Calculate shares based on current NAV
        uint256 shares = (amount * 1e18) / navPerShare;

        // Mint shares to investor
        _mint(investor, shares);

        // Update AUM
        totalAUM += amount;

        // Record investment
        investments[investor].push(Investment({
            amount: amount,
            timestamp: block.timestamp,
            invoiceId: invoiceId,
            isActive: true
        }));

        emit InvestmentReceived(investor, amount, invoiceId);
    }

    /**
     * @dev Redeem fund shares for underlying assets
     * @param shares Amount of shares to redeem
     */
    function redeemShares(uint256 shares) external nonReentrant {
        require(shares > 0, "Invalid share amount");
        require(balanceOf(msg.sender) >= shares, "Insufficient shares");

        // Calculate redemption amount based on current NAV
        uint256 redemptionAmount = (shares * navPerShare) / 1e18;

        // Burn shares
        _burn(msg.sender, shares);

        // Update AUM
        totalAUM -= redemptionAmount;

        // Transfer funds (in production, this would transfer actual assets)
        // For now, we'll emit an event
        emit InvestmentRedeemed(msg.sender, shares, redemptionAmount);
    }

    /**
     * @dev Update NAV per share (called by oracle or governance)
     * @param newNAV New NAV value (scaled by 1e18)
     */
    function updateNAV(uint256 newNAV) external onlyOwner {
        require(newNAV > 0, "NAV must be positive");
        navPerShare = newNAV;
        emit NAVUpdated(newNAV, block.timestamp);
    }

    /**
     * @dev Update LUA-PAY oracle address
     * @param newOracle New oracle address
     */
    function updateLuaPayOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Invalid oracle address");
        luaPayOracle = newOracle;
        emit LuaPayOracleUpdated(newOracle);
    }

    /**
     * @dev Set minimum investment amount
     * @param newMin New minimum investment
     */
    function setMinInvestment(uint256 newMin) external onlyOwner {
        require(newMin > 0, "Minimum must be positive");
        minInvestment = newMin;
    }

    /**
     * @dev Get investor's total investments
     * @param investor Investor address
     * @return Total amount invested
     */
    function getTotalInvested(address investor) external view returns (uint256) {
        uint256 total = 0;
        Investment[] memory userInvestments = investments[investor];

        for (uint256 i = 0; i < userInvestments.length; i++) {
            if (userInvestments[i].isActive) {
                total += userInvestments[i].amount;
            }
        }

        return total;
    }

    /**
     * @dev Get investor's current value
     * @param investor Investor address
     * @return Current value based on NAV
     */
    function getCurrentValue(address investor) external view returns (uint256) {
        uint256 shares = balanceOf(investor);
        return (shares * navPerShare) / 1e18;
    }

    /**
     * @dev Get fund metrics
     * @return _totalAUM Total assets under management
     * @return _navPerShare Current NAV per share
     * @return _totalShares Total shares outstanding
     */
    function getFundMetrics() external view returns (
        uint256 _totalAUM,
        uint256 _navPerShare,
        uint256 _totalShares
    ) {
        return (totalAUM, navPerShare, totalSupply());
    }
}
