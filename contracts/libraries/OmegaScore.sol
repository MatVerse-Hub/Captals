// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OmegaScore Library
 * @dev Implements Ω-Score calculation for asset valuation and risk assessment
 * Formula: Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
 */
library OmegaScore {
    struct ScoreParams {
        uint256 psi;    // Ψ: Asset quality metrics (0-10000, scaled by 100)
        uint256 theta;  // Θ: Risk-adjusted returns (0-10000, scaled by 100)
        uint256 cvar;   // CVaR: Conditional Value at Risk (0-10000, scaled by 100)
        uint256 pole;   // PoLE: Proof of Liquidity Efficiency (0-10000, scaled by 100)
    }

    /**
     * @dev Calculates the Omega Score based on the provided parameters
     * @param params The score parameters (Ψ, Θ, CVaR, PoLE)
     * @return The calculated Omega Score
     */
    function calculateOmegaScore(ScoreParams memory params) internal pure returns (uint256) {
        require(params.psi > 0, "Psi must be positive");
        require(params.theta > 0, "Theta must be positive");

        // Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
        // Using safe math to prevent overflow
        uint256 numerator = params.psi * params.theta;
        uint256 denominator = params.cvar + 100; // Add 100 (scaled 1) to prevent division by zero
        uint256 mainScore = numerator / denominator;

        return mainScore + params.pole;
    }

    /**
     * @dev Evaluates asset risk based on liquidity and volatility
     * @param liquidity Total liquidity available
     * @param volatility Asset volatility measure
     * @return Risk score (higher is better)
     */
    function evaluateAssetRisk(uint256 liquidity, uint256 volatility) internal pure returns (uint256) {
        if (liquidity == 0) return 0;
        if (volatility == 0) return 10000; // Perfect score for zero volatility

        // Risk score inversely proportional to volatility/liquidity ratio
        return liquidity > volatility ? 10000 : (liquidity * 10000) / volatility;
    }

    /**
     * @dev Calculates Proof of Liquidity Efficiency (PoLE)
     * @param totalLiquidity Total liquidity in pool
     * @param utilizationRate Percentage of liquidity being utilized (0-10000)
     * @return PoLE score
     */
    function calculatePoLE(uint256 totalLiquidity, uint256 utilizationRate) internal pure returns (uint256) {
        require(utilizationRate <= 10000, "Utilization rate must be <= 100%");

        // Optimal utilization is 70-80%
        uint256 optimalUtilization = 7500; // 75%
        uint256 deviation = utilizationRate > optimalUtilization
            ? utilizationRate - optimalUtilization
            : optimalUtilization - utilizationRate;

        // Higher liquidity and closer to optimal utilization = higher PoLE
        uint256 efficiencyScore = 10000 - (deviation * 2);
        return (totalLiquidity * efficiencyScore) / 1e18; // Normalize
    }

    /**
     * @dev Calculates Conditional Value at Risk (CVaR)
     * @param returns Array of historical returns
     * @param confidenceLevel Confidence level (e.g., 9500 for 95%)
     * @return CVaR value
     */
    function calculateCVaR(int256[] memory returns, uint256 confidenceLevel) internal pure returns (uint256) {
        require(returns.length > 0, "Returns array cannot be empty");
        require(confidenceLevel <= 10000, "Confidence level must be <= 100%");

        // Simplified CVaR calculation
        // In production, this would use more sophisticated statistical methods
        int256 sum = 0;
        uint256 count = 0;

        for (uint256 i = 0; i < returns.length; i++) {
            if (returns[i] < 0) {
                sum += returns[i];
                count++;
            }
        }

        if (count == 0) return 0; // No losses

        int256 avgLoss = sum / int256(count);
        return uint256(-avgLoss); // Return absolute value
    }
}
