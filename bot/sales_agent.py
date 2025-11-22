"""
Sales Agent - AI-powered investment advisor for Telegram bot
"""

import random


class SalesAgent:
    """
    Simple rule-based sales agent
    In production, integrate with OpenAI or other LLM
    """

    def __init__(self):
        self.keywords = {
            'invest': self._recommend_investment,
            'fund': self._explain_funds,
            'risk': self._explain_risk,
            'omega': self._explain_omega_score,
            'safe': self._recommend_safe,
            'growth': self._recommend_growth,
            'help': self._provide_help,
            'return': self._explain_returns,
            'score': self._explain_omega_score
        }

    def get_response(self, message: str) -> str:
        """
        Get response based on user message
        """
        message_lower = message.lower()

        # Check for keywords
        for keyword, handler in self.keywords.items():
            if keyword in message_lower:
                return handler()

        # Default response
        return self._default_response()

    def _recommend_investment(self) -> str:
        return """
🎯 *Investment Recommendation*

Based on current market conditions, I recommend:

*For Growth Seekers:*
• Omega Growth Fund (Ω: 8500)
• Expected yearly return: ~45%
• Higher risk, higher reward

*For Stability Seekers:*
• Omega Stable Fund (Ω: 9200)
• Expected yearly return: ~12%
• Lower risk, steady growth

Use /invest to start investing!
        """

    def _explain_funds(self) -> str:
        return """
🏦 *About Omega Funds*

Omega Funds are tokenized investment vehicles similar to ETFs, but fully on-chain.

*Benefits:*
• 24/7 trading
• Instant liquidity
• Transparent holdings
• Low fees
• Ω-Score validated

*Available Funds:*
• Growth Fund (high risk/reward)
• Stable Fund (low risk/steady)

Use /funds to see details!
        """

    def _explain_risk(self) -> str:
        return """
⚠️ *Risk Management*

We use the Ω-Score to assess risk:

*Risk Factors:*
• CVaR (Conditional Value at Risk)
• Volatility metrics
• Liquidity depth
• Historical performance

*Risk Levels:*
• Ω 9000+: Very Low Risk
• Ω 8000-8999: Low Risk
• Ω 7000-7999: Moderate Risk
• Ω <7000: Higher Risk

Higher Ω-Score = Better risk-adjusted returns!
        """

    def _explain_omega_score(self) -> str:
        return """
🎯 *Ω-Score Explained*

The Omega Score is our proprietary metric:

```
Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
```

• Ψ: Asset quality
• Θ: Risk-adjusted returns
• CVaR: Value at Risk
• PoLE: Liquidity efficiency

Use /omega for detailed explanation!
        """

    def _recommend_safe(self) -> str:
        return """
🛡️ *Safe Investment Recommendation*

For conservative investors:

*Omega Stable Fund*
• Ω-Score: 9200 (Excellent)
• Yearly return: ~12%
• Low volatility
• High liquidity
• Diversified holdings

Perfect for risk-averse investors seeking steady growth.

Invest with /invest
        """

    def _recommend_growth(self) -> str:
        return """
📈 *Growth Investment Recommendation*

For aggressive investors:

*Omega Growth Fund*
• Ω-Score: 8500 (Very Good)
• Yearly return: ~45%
• Higher volatility
• High growth potential
• Tech-focused DeFi assets

Perfect for investors seeking maximum returns.

Invest with /invest
        """

    def _provide_help(self) -> str:
        return """
💬 *How Can I Help?*

Ask me about:
• Investment recommendations
• Fund details
• Risk assessment
• Ω-Score explanation
• Returns and performance

Or use these commands:
/invest - Start investing
/funds - View all funds
/omega - Learn about Ω-Score
/metrics - Platform stats

What would you like to know?
        """

    def _explain_returns(self) -> str:
        return """
💰 *Investment Returns*

Our funds have delivered:

*Omega Growth Fund:*
• Monthly: +8.7%
• Yearly: +45.2%

*Omega Stable Fund:*
• Monthly: +2.5%
• Yearly: +12.3%

*Important:*
Past performance doesn't guarantee future results.
All investments carry risk.

Ready to invest? Use /invest
        """

    def _default_response(self) -> str:
        responses = [
            "I'm here to help with your investments! Ask me about our funds or use /help for commands.",
            "Looking to invest? Check out our funds with /funds or start investing with /invest!",
            "Want to learn about Ω-Score? Use /omega to understand our rating system!",
            "Need investment advice? Ask me about growth or safe investments!"
        ]
        return random.choice(responses)
