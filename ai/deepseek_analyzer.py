"""
DeepSeek LLM Integration
AI-powered market analysis using DeepSeek's language model
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import logger
from config import settings


class DeepSeekAnalyzer:
    """AI-powered market analysis using DeepSeek LLM"""

    def __init__(self):
        """Initialize DeepSeek analyzer"""
        self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        self.api_url = getattr(settings, 'DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        self.model = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-chat')

        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
        else:
            logger.info("DeepSeek analyzer initialized")

    def analyze_stock(
        self,
        symbol: str,
        current_data: Dict,
        technical_indicators: Dict,
        news: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Generate AI-powered analysis for a stock

        Args:
            symbol: Stock symbol
            current_data: Current market data (price, change, volume, etc.)
            technical_indicators: Technical indicators dict
            news: Optional list of recent news items

        Returns:
            Dictionary with analysis, summary, and recommendations
        """
        if not self.api_key:
            return {
                'summary': 'DeepSeek API key not configured',
                'analysis': 'Please add DEEPSEEK_API_KEY to your .env file',
                'recommendation': 'N/A'
            }

        try:
            # Build context prompt
            prompt = self._build_analysis_prompt(symbol, current_data, technical_indicators, news)

            # Call DeepSeek API
            response = self._call_deepseek(prompt)

            if response:
                return self._parse_analysis_response(response)
            else:
                return {
                    'summary': 'Analysis unavailable',
                    'analysis': 'Failed to get response from DeepSeek',
                    'recommendation': 'N/A'
                }

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            return {
                'summary': 'Error during analysis',
                'analysis': str(e),
                'recommendation': 'N/A'
            }

    def _build_analysis_prompt(
        self,
        symbol: str,
        current_data: Dict,
        technical_indicators: Dict,
        news: Optional[List[Dict]]
    ) -> str:
        """Build detailed prompt for stock analysis"""

        prompt = f"""Analyze the following stock and provide a concise market analysis:

**Stock:** {symbol}

**Current Market Data:**
- Price: ${current_data.get('price', 'N/A')}
- Change: {current_data.get('change_percent', 'N/A')}%
- Volume: {current_data.get('volume', 'N/A'):,}
- Market Cap: ${current_data.get('market_cap', 'N/A')}
- 52-Week High: ${current_data.get('high_52week', 'N/A')}
- 52-Week Low: ${current_data.get('low_52week', 'N/A')}
- P/E Ratio: {current_data.get('pe_ratio', 'N/A')}

**Technical Indicators:**
"""

        # Add technical indicators
        if technical_indicators.get('latest'):
            indicators = technical_indicators['latest']
            rsi = indicators.get('rsi')
            macd = indicators.get('macd')
            macd_signal = indicators.get('macd_signal')
            bb_upper = indicators.get('bb_upper')
            bb_lower = indicators.get('bb_lower')
            sma_20 = indicators.get('sma_20')
            sma_50 = indicators.get('sma_50')
            sma_200 = indicators.get('sma_200')

            prompt += f"""
- RSI (14): {f'{rsi:.2f}' if rsi else 'N/A'}
- MACD: {f'{macd:.2f}' if macd else 'N/A'}
- MACD Signal: {f'{macd_signal:.2f}' if macd_signal else 'N/A'}
- Bollinger Upper: ${f'{bb_upper:.2f}' if bb_upper else 'N/A'}
- Bollinger Lower: ${f'{bb_lower:.2f}' if bb_lower else 'N/A'}
- SMA 20: ${f'{sma_20:.2f}' if sma_20 else 'N/A'}
- SMA 50: ${f'{sma_50:.2f}' if sma_50 else 'N/A'}
- SMA 200: ${f'{sma_200:.2f}' if sma_200 else 'N/A'}
"""

        # Add trading signals
        if technical_indicators.get('signals'):
            signals = technical_indicators['signals']
            prompt += f"\n**Trading Signals:**\n"
            for key, value in signals.items():
                prompt += f"- {key.replace('_', ' ').title()}: {value}\n"

        # Add news if available
        if news and len(news) > 0:
            prompt += f"\n**Recent News Headlines:**\n"
            for i, item in enumerate(news[:3], 1):
                prompt += f"{i}. {item.get('title', 'N/A')}\n"

        prompt += """

Based on this data, provide:
1. A brief summary (2-3 sentences) of the current market position
2. Technical analysis interpretation
3. A clear recommendation (Bullish/Bearish/Neutral) with reasoning

Keep the analysis concise, factual, and actionable. Focus on the most important signals and trends."""

        return prompt

    def _call_deepseek(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Call DeepSeek API

        Args:
            prompt: Analysis prompt
            max_tokens: Maximum response tokens

        Returns:
            Response text or None
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': self.model,
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a professional financial analyst providing concise, data-driven stock market analysis.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': 0.7
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"Unexpected API response format: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling DeepSeek: {e}", exc_info=True)
            return None

    def _parse_analysis_response(self, response: str) -> Dict[str, str]:
        """
        Parse DeepSeek response into structured format

        Args:
            response: Raw response text

        Returns:
            Dictionary with summary, analysis, and recommendation
        """
        try:
            # Split response into sections
            lines = response.strip().split('\n')

            summary = ""
            analysis = ""
            recommendation = ""

            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Detect sections
                if 'summary' in line.lower() or 'overview' in line.lower():
                    current_section = 'summary'
                    continue
                elif 'analysis' in line.lower() or 'technical' in line.lower():
                    current_section = 'analysis'
                    continue
                elif 'recommend' in line.lower() or 'outlook' in line.lower():
                    current_section = 'recommendation'
                    continue

                # Add to appropriate section
                if current_section == 'summary':
                    summary += line + " "
                elif current_section == 'analysis':
                    analysis += line + " "
                elif current_section == 'recommendation':
                    recommendation += line + " "
                else:
                    # Default to analysis if no section detected
                    analysis += line + " "

            # If sections weren't detected, use the whole response as analysis
            if not summary and not analysis and not recommendation:
                analysis = response

            return {
                'summary': summary.strip() or analysis[:200] + "...",
                'analysis': analysis.strip() or response,
                'recommendation': recommendation.strip() or "See analysis for details"
            }

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                'summary': response[:200] if len(response) > 200 else response,
                'analysis': response,
                'recommendation': 'N/A'
            }

    def analyze_portfolio(
        self,
        stocks_data: List[Dict]
    ) -> Dict[str, str]:
        """
        Generate AI analysis for entire portfolio

        Args:
            stocks_data: List of stock data dictionaries

        Returns:
            Dictionary with portfolio analysis
        """
        if not self.api_key:
            return {
                'summary': 'DeepSeek API key not configured',
                'analysis': 'Please add DEEPSEEK_API_KEY to your .env file'
            }

        try:
            # Build portfolio summary
            prompt = f"""Analyze the following stock portfolio and provide a market overview:

**Portfolio Summary:**
"""

            for stock in stocks_data[:10]:  # Limit to 10 stocks
                symbol = stock.get('symbol', 'N/A')
                price = stock.get('price', 0)
                change = stock.get('change_percent', 0)
                prompt += f"- {symbol}: ${price:.2f} ({change:+.2f}%)\n"

            prompt += """

Provide a brief portfolio analysis covering:
1. Overall market sentiment
2. Key trends or patterns
3. Notable movers
4. Risk assessment

Keep it concise (3-4 sentences)."""

            response = self._call_deepseek(prompt, max_tokens=300)

            if response:
                return {
                    'summary': response[:200] + "..." if len(response) > 200 else response,
                    'analysis': response
                }
            else:
                return {
                    'summary': 'Analysis unavailable',
                    'analysis': 'Failed to get response from DeepSeek'
                }

        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}", exc_info=True)
            return {
                'summary': 'Error during analysis',
                'analysis': str(e)
            }


# Global analyzer instance
_analyzer = None


def get_analyzer() -> DeepSeekAnalyzer:
    """Get global DeepSeek analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = DeepSeekAnalyzer()
    return _analyzer


if __name__ == '__main__':
    # Test DeepSeek analyzer
    print("\n" + "="*60)
    print("DEEPSEEK ANALYZER TEST")
    print("="*60)

    analyzer = DeepSeekAnalyzer()

    if not analyzer.api_key:
        print("\n⚠️  DeepSeek API key not configured")
        print("   Add DEEPSEEK_API_KEY to .env to test")
    else:
        print("\n✓ DeepSeek analyzer initialized")

        # Test with sample data
        test_data = {
            'symbol': 'AAPL',
            'price': 175.50,
            'change_percent': 2.3,
            'volume': 50000000,
            'market_cap': 2800000000000,
            'high_52week': 199.62,
            'low_52week': 124.17,
            'pe_ratio': 29.5
        }

        test_indicators = {
            'latest': {
                'rsi': 65.5,
                'macd': 2.3,
                'macd_signal': 1.8,
                'bb_upper': 180.50,
                'bb_lower': 170.50,
                'sma_20': 175.00,
                'sma_50': 172.00,
                'sma_200': 168.00
            },
            'signals': {
                'rsi': 'neutral',
                'macd': 'bullish',
                'bollinger': 'neutral',
                'trend_short': 'bullish',
                'trend_long': 'bullish'
            }
        }

        print(f"\nAnalyzing {test_data['symbol']}...")
        analysis = analyzer.analyze_stock('AAPL', test_data, test_indicators)

        print(f"\n📊 Summary:")
        print(f"  {analysis['summary']}")
        print(f"\n📈 Analysis:")
        print(f"  {analysis['analysis']}")
        print(f"\n🎯 Recommendation:")
        print(f"  {analysis['recommendation']}")

    print("\n" + "="*60 + "\n")
