// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "../libraries/OmegaScore.sol";

/**
 * @title OmegaPool
 * @dev Automated Market Maker (AMM) pool with Omega Score integration
 */
contract OmegaPool is ReentrancyGuard, Ownable {
    using OmegaScore for OmegaScore.ScoreParams;

    IERC20 public immutable tokenA;
    IERC20 public immutable tokenB;

    uint256 public reserveA;
    uint256 public reserveB;
    uint256 public totalLiquidity;

    mapping(address => uint256) public liquidityBalance;

    // Fee: 0.3% (30 basis points)
    uint256 public constant FEE_NUMERATOR = 3;
    uint256 public constant FEE_DENOMINATOR = 1000;

    // Minimum liquidity locked forever
    uint256 public constant MINIMUM_LIQUIDITY = 1000;

    event LiquidityAdded(address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event LiquidityRemoved(address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event Swap(address indexed trader, address tokenIn, uint256 amountIn, uint256 amountOut);

    constructor(address _tokenA, address _tokenB) {
        require(_tokenA != address(0) && _tokenB != address(0), "Invalid token addresses");
        require(_tokenA != _tokenB, "Identical tokens");

        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
    }

    /**
     * @dev Add liquidity to the pool
     * @param amountA Amount of token A
     * @param amountB Amount of token B
     * @return liquidity Liquidity tokens minted
     */
    function addLiquidity(
        uint256 amountA,
        uint256 amountB
    ) external nonReentrant returns (uint256 liquidity) {
        require(amountA > 0 && amountB > 0, "Invalid amounts");

        // Transfer tokens from sender
        require(tokenA.transferFrom(msg.sender, address(this), amountA), "Transfer A failed");
        require(tokenB.transferFrom(msg.sender, address(this), amountB), "Transfer B failed");

        if (totalLiquidity == 0) {
            // First liquidity provider
            liquidity = sqrt(amountA * amountB);
            require(liquidity > MINIMUM_LIQUIDITY, "Insufficient liquidity");

            // Lock minimum liquidity
            totalLiquidity = liquidity - MINIMUM_LIQUIDITY;
            liquidityBalance[address(0)] = MINIMUM_LIQUIDITY;
            liquidityBalance[msg.sender] = liquidity - MINIMUM_LIQUIDITY;
        } else {
            // Subsequent providers
            uint256 liquidityA = (amountA * totalLiquidity) / reserveA;
            uint256 liquidityB = (amountB * totalLiquidity) / reserveB;
            liquidity = liquidityA < liquidityB ? liquidityA : liquidityB;

            liquidityBalance[msg.sender] += liquidity;
            totalLiquidity += liquidity;
        }

        reserveA += amountA;
        reserveB += amountB;

        emit LiquidityAdded(msg.sender, amountA, amountB, liquidity);
    }

    /**
     * @dev Remove liquidity from the pool
     * @param liquidity Amount of liquidity to remove
     * @return amountA Amount of token A returned
     * @return amountB Amount of token B returned
     */
    function removeLiquidity(
        uint256 liquidity
    ) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        require(liquidity > 0, "Invalid liquidity amount");
        require(liquidityBalance[msg.sender] >= liquidity, "Insufficient liquidity");

        amountA = (liquidity * reserveA) / totalLiquidity;
        amountB = (liquidity * reserveB) / totalLiquidity;

        require(amountA > 0 && amountB > 0, "Insufficient liquidity burned");

        liquidityBalance[msg.sender] -= liquidity;
        totalLiquidity -= liquidity;
        reserveA -= amountA;
        reserveB -= amountB;

        require(tokenA.transfer(msg.sender, amountA), "Transfer A failed");
        require(tokenB.transfer(msg.sender, amountB), "Transfer B failed");

        emit LiquidityRemoved(msg.sender, amountA, amountB, liquidity);
    }

    /**
     * @dev Swap tokens
     * @param tokenIn Address of input token
     * @param amountIn Amount of input token
     * @return amountOut Amount of output token
     */
    function swap(
        address tokenIn,
        uint256 amountIn
    ) external nonReentrant returns (uint256 amountOut) {
        require(amountIn > 0, "Invalid input amount");
        require(tokenIn == address(tokenA) || tokenIn == address(tokenB), "Invalid token");

        bool isTokenA = tokenIn == address(tokenA);
        (IERC20 inputToken, IERC20 outputToken, uint256 inputReserve, uint256 outputReserve) = isTokenA
            ? (tokenA, tokenB, reserveA, reserveB)
            : (tokenB, tokenA, reserveB, reserveA);

        // Transfer input tokens
        require(inputToken.transferFrom(msg.sender, address(this), amountIn), "Transfer failed");

        // Calculate output amount with fee
        uint256 amountInWithFee = amountIn * (FEE_DENOMINATOR - FEE_NUMERATOR);
        amountOut = (amountInWithFee * outputReserve) / (inputReserve * FEE_DENOMINATOR + amountInWithFee);

        require(amountOut > 0, "Insufficient output amount");
        require(amountOut < outputReserve, "Insufficient liquidity");

        // Update reserves
        if (isTokenA) {
            reserveA += amountIn;
            reserveB -= amountOut;
        } else {
            reserveB += amountIn;
            reserveA -= amountOut;
        }

        // Transfer output tokens
        require(outputToken.transfer(msg.sender, amountOut), "Transfer failed");

        emit Swap(msg.sender, tokenIn, amountIn, amountOut);
    }

    /**
     * @dev Calculate Omega Score for the pool
     * @return Omega Score based on pool metrics
     */
    function getOmegaScoreForPool() external view returns (uint256) {
        if (totalLiquidity == 0) return 0;

        // Calculate utilization rate (simplified)
        uint256 utilizationRate = (totalLiquidity * 10000) / (reserveA + reserveB);

        OmegaScore.ScoreParams memory params = OmegaScore.ScoreParams({
            psi: reserveA / 1e18,          // Asset quality based on reserve A
            theta: reserveB / 1e18,        // Risk adjustment based on reserve B
            cvar: 500,                     // Conservative CVaR estimate
            pole: OmegaScore.calculatePoLE(totalLiquidity, utilizationRate)
        });

        return params.calculateOmegaScore();
    }

    /**
     * @dev Get current pool reserves
     * @return _reserveA Reserve of token A
     * @return _reserveB Reserve of token B
     */
    function getReserves() external view returns (uint256 _reserveA, uint256 _reserveB) {
        return (reserveA, reserveB);
    }

    /**
     * @dev Square root function for liquidity calculation
     */
    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }
}
