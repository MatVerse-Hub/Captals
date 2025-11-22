// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "../libraries/OmegaScore.sol";

/**
 * @title OmegaPool
 * @dev Liquidity pool for Omega Capitals strategies
 * Users deposit USDC/USDT, pool manager executes strategies, profits distributed based on Ω-Score
 */
contract OmegaPool is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    struct Strategy {
        uint256 id;
        address manager;
        uint256 omegaScore;
        uint256 allocatedCapital;
        uint256 currentValue;
        uint256 lastUpdateTime;
        bool active;
    }

    struct Deposit {
        uint256 amount;
        uint256 shares;
        uint256 timestamp;
    }

    // State variables
    IERC20 public immutable baseToken;  // USDC/USDT
    uint256 public totalDeposits;
    uint256 public totalShares;
    uint256 public minOmegaScore = 600;  // Minimum Ω-Score to qualify
    uint256 public performanceFee = 20;  // 20% performance fee

    mapping(uint256 => Strategy) public strategies;
    mapping(address => Deposit) public deposits;
    uint256 public strategyCounter;

    // Events
    event StrategyAdded(uint256 indexed strategyId, address indexed manager, uint256 omegaScore);
    event CapitalAllocated(uint256 indexed strategyId, uint256 amount);
    event Deposited(address indexed user, uint256 amount, uint256 shares);
    event Withdrawn(address indexed user, uint256 amount, uint256 shares);
    event PerformanceRecorded(uint256 indexed strategyId, uint256 newValue, int256 pnl);

    constructor(address _baseToken) Ownable(msg.sender) {
        baseToken = IERC20(_baseToken);
    }

    /**
     * @dev Add new strategy to pool (only owner/governance)
     * @param manager Strategy manager address
     * @param cvar CVaR metric
     * @param beta Beta metric
     * @param err5m ERR5m metric
     * @param idem Idempotency metric
     */
    function addStrategy(
        address manager,
        uint256 cvar,
        uint256 beta,
        uint256 err5m,
        uint256 idem
    ) external onlyOwner returns (uint256) {
        uint256 omegaScore = OmegaScore.compute(cvar, beta, err5m, idem);
        require(omegaScore >= minOmegaScore, "Omega score too low");

        uint256 strategyId = ++strategyCounter;

        strategies[strategyId] = Strategy({
            id: strategyId,
            manager: manager,
            omegaScore: omegaScore,
            allocatedCapital: 0,
            currentValue: 0,
            lastUpdateTime: block.timestamp,
            active: true
        });

        emit StrategyAdded(strategyId, manager, omegaScore);
        return strategyId;
    }

    /**
     * @dev Deposit USDC/USDT into pool
     * @param amount Amount to deposit
     */
    function deposit(uint256 amount) external nonReentrant {
        require(amount > 0, "Zero amount");

        uint256 shares;
        if (totalShares == 0) {
            shares = amount;
        } else {
            shares = (amount * totalShares) / totalDeposits;
        }

        baseToken.safeTransferFrom(msg.sender, address(this), amount);

        deposits[msg.sender].amount += amount;
        deposits[msg.sender].shares += shares;
        deposits[msg.sender].timestamp = block.timestamp;

        totalDeposits += amount;
        totalShares += shares;

        emit Deposited(msg.sender, amount, shares);
    }

    /**
     * @dev Withdraw funds from pool
     * @param shares Number of shares to redeem
     */
    function withdraw(uint256 shares) external nonReentrant {
        require(shares > 0 && shares <= deposits[msg.sender].shares, "Invalid shares");

        uint256 amount = (shares * totalDeposits) / totalShares;

        deposits[msg.sender].amount -= amount;
        deposits[msg.sender].shares -= shares;

        totalDeposits -= amount;
        totalShares -= shares;

        baseToken.safeTransfer(msg.sender, amount);

        emit Withdrawn(msg.sender, amount, shares);
    }

    /**
     * @dev Allocate capital to strategy
     * @param strategyId Strategy ID
     * @param amount Amount to allocate
     */
    function allocateCapital(uint256 strategyId, uint256 amount) external onlyOwner {
        Strategy storage strategy = strategies[strategyId];
        require(strategy.active, "Strategy not active");
        require(amount <= baseToken.balanceOf(address(this)), "Insufficient balance");

        strategy.allocatedCapital += amount;
        strategy.currentValue += amount;

        baseToken.safeTransfer(strategy.manager, amount);

        emit CapitalAllocated(strategyId, amount);
    }

    /**
     * @dev Record strategy performance update
     * @param strategyId Strategy ID
     * @param newValue New portfolio value
     */
    function recordPerformance(uint256 strategyId, uint256 newValue) external {
        Strategy storage strategy = strategies[strategyId];
        require(msg.sender == strategy.manager || msg.sender == owner(), "Not authorized");
        require(strategy.active, "Strategy not active");

        int256 pnl = int256(newValue) - int256(strategy.currentValue);
        strategy.currentValue = newValue;
        strategy.lastUpdateTime = block.timestamp;

        if (pnl > 0) {
            uint256 fee = (uint256(pnl) * performanceFee) / 100;
            totalDeposits += uint256(pnl) - fee;
        } else if (pnl < 0) {
            totalDeposits = totalDeposits > uint256(-pnl) ? totalDeposits - uint256(-pnl) : 0;
        }

        emit PerformanceRecorded(strategyId, newValue, pnl);
    }

    /**
     * @dev Get user's current balance
     * @param user User address
     * @return balance Current value of user's shares
     */
    function getBalance(address user) external view returns (uint256) {
        if (totalShares == 0) return 0;
        return (deposits[user].shares * totalDeposits) / totalShares;
    }

    /**
     * @dev Get pool's total value locked
     */
    function getTVL() external view returns (uint256) {
        return totalDeposits;
    }

    /**
     * @dev Update minimum Ω-Score threshold
     */
    function setMinOmegaScore(uint256 newMin) external onlyOwner {
        minOmegaScore = newMin;
    }

    /**
     * @dev Update performance fee
     */
    function setPerformanceFee(uint256 newFee) external onlyOwner {
        require(newFee <= 30, "Fee too high");
        performanceFee = newFee;
    }

    /**
     * @dev Deactivate strategy
     */
    function deactivateStrategy(uint256 strategyId) external onlyOwner {
        strategies[strategyId].active = false;
    }
}
