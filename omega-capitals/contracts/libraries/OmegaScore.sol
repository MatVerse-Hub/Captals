// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OmegaScore
 * @dev Library for calculating Ω-Score from portfolio risk metrics
 *
 * Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
 *
 * Where:
 * - CVaR: Conditional Value at Risk (95% confidence)
 * - β: Beta coefficient (market correlation)
 * - ERR₅m: Maximum 5-minute error ratio
 * - Idem: Idempotency score (strategy consistency)
 */
library OmegaScore {
    uint256 constant PRECISION = 1e18;

    /**
     * @dev Compute Ω-Score from normalized risk metrics
     * @param cvar Conditional Value at Risk (0-1e18 scale)
     * @param beta Beta coefficient (0-1e18 scale)
     * @param err5m Maximum 5-minute error (0-1e18 scale)
     * @param idem Idempotency score (0-1e18 scale)
     * @return omega Final Ω-Score (0-1000 scale)
     */
    function compute(
        uint256 cvar,
        uint256 beta,
        uint256 err5m,
        uint256 idem
    ) internal pure returns (uint256 omega) {
        require(cvar <= PRECISION, "CVaR exceeds max");
        require(beta <= PRECISION, "Beta exceeds max");
        require(err5m <= PRECISION, "ERR5m exceeds max");
        require(idem <= PRECISION, "Idem exceeds max");

        // Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
        uint256 term1 = 400 * (PRECISION - cvar) / PRECISION;  // 40% weight
        uint256 term2 = 300 * (PRECISION - beta) / PRECISION;   // 30% weight
        uint256 term3 = 200 * (PRECISION - err5m) / PRECISION;  // 20% weight
        uint256 term4 = 100 * idem / PRECISION;                 // 10% weight

        omega = term1 + term2 + term3 + term4;
    }

    /**
     * @dev Compute Ω-Score with custom weights
     * @param metrics Array of [cvar, beta, err5m, idem]
     * @param weights Array of weights (must sum to 1000)
     * @return omega Weighted Ω-Score
     */
    function computeWeighted(
        uint256[4] memory metrics,
        uint256[4] memory weights
    ) internal pure returns (uint256 omega) {
        require(
            weights[0] + weights[1] + weights[2] + weights[3] == 1000,
            "Weights must sum to 1000"
        );

        for (uint256 i = 0; i < 4; i++) {
            require(metrics[i] <= PRECISION, "Metric exceeds max");
        }

        omega =
            weights[0] * (PRECISION - metrics[0]) / PRECISION +
            weights[1] * (PRECISION - metrics[1]) / PRECISION +
            weights[2] * (PRECISION - metrics[2]) / PRECISION +
            weights[3] * metrics[3] / PRECISION;
    }

    /**
     * @dev Classify Ω-Score into risk tiers
     * @param omega Ω-Score value
     * @return tier Risk tier (0=Low, 1=Medium, 2=High, 3=Critical)
     */
    function getTier(uint256 omega) internal pure returns (uint8 tier) {
        if (omega >= 800) return 0;      // Low risk
        if (omega >= 600) return 1;      // Medium risk
        if (omega >= 400) return 2;      // High risk
        return 3;                        // Critical risk
    }

    /**
     * @dev Check if strategy meets minimum quality threshold
     * @param omega Ω-Score value
     * @param minThreshold Minimum acceptable score
     * @return bool Whether strategy qualifies
     */
    function meetsThreshold(uint256 omega, uint256 minThreshold) internal pure returns (bool) {
        return omega >= minThreshold;
    }
}
