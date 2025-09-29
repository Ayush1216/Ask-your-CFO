"""
Intent classification for CFO Copilot
"""
import re
from typing import Dict, List, Tuple
from enum import Enum

class IntentType(Enum):
    REVENUE_VS_BUDGET = "revenue_vs_budget"
    GROSS_MARGIN_TREND = "gross_margin_trend"
    OPEX_BREAKDOWN = "opex_breakdown"
    CASH_RUNWAY = "cash_runway"
    EBITDA_ANALYSIS = "ebitda_analysis"
    GENERAL_QUERY = "general_query"

class IntentClassifier:
    """Classifies user queries into specific intents"""
    
    def __init__(self):
        self.patterns = {
            IntentType.REVENUE_VS_BUDGET: [
                r"revenue.*vs.*budget",
                r"revenue.*budget",
                r"sales.*vs.*budget",
                r"sales.*budget",
                r"what.*revenue.*budget",
                r"revenue.*actual.*budget"
            ],
            IntentType.GROSS_MARGIN_TREND: [
                r"gross.*margin.*trend",
                r"margin.*trend",
                r"gross.*margin.*last",
                r"margin.*last.*months",
                r"show.*gross.*margin",
                r"gross.*margin.*chart"
            ],
            IntentType.OPEX_BREAKDOWN: [
                r"opex.*breakdown",
                r"opex.*category",
                r"operating.*expense.*breakdown",
                r"expense.*breakdown",
                r"opex.*by.*category",
                r"break.*down.*opex"
            ],
            IntentType.CASH_RUNWAY: [
                r"cash.*runway",
                r"runway",
                r"cash.*burn",
                r"how.*long.*cash",
                r"months.*cash",
                r"cash.*left"
            ],
            IntentType.EBITDA_ANALYSIS: [
                r"ebitda",
                r"profitability",
                r"earnings",
                r"operating.*profit"
            ]
        }
    
    def classify(self, query: str) -> Tuple[IntentType, Dict[str, str]]:
        """Classify user query and extract parameters"""
        query_lower = query.lower()
        
        # Extract month if mentioned
        month = self._extract_month(query_lower)
        
        # Extract time period for trends
        time_period = self._extract_time_period(query_lower)
        
        # Check each intent pattern
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent_type, {
                        'month': month,
                        'time_period': time_period,
                        'original_query': query
                    }
        
        # Default to general query
        return IntentType.GENERAL_QUERY, {
            'month': month,
            'time_period': time_period,
            'original_query': query
        }
    
    def _extract_month(self, query: str) -> str:
        """Extract month from query"""
        month_patterns = {
            r'january|jan': '2023-01',
            r'february|feb': '2023-02',
            r'march|mar': '2023-03',
            r'april|apr': '2023-04',
            r'may': '2023-05',
            r'june|jun': '2023-06',
            r'july|jul': '2023-07',
            r'august|aug': '2023-08',
            r'september|sep': '2023-09',
            r'october|oct': '2023-10',
            r'november|nov': '2023-11',
            r'december|dec': '2023-12'
        }
        
        for pattern, month in month_patterns.items():
            if re.search(pattern, query):
                return month
        
        # Check for YYYY-MM format
        date_match = re.search(r'(\d{4}-\d{2})', query)
        if date_match:
            return date_match.group(1)
        
        return None
    
    def _extract_time_period(self, query: str) -> str:
        """Extract time period for trends"""
        if re.search(r'last\s+(\d+)\s+months?', query):
            match = re.search(r'last\s+(\d+)\s+months?', query)
            return f"last_{match.group(1)}_months"
        elif re.search(r'last\s+3\s+months?', query):
            return "last_3_months"
        elif re.search(r'last\s+6\s+months?', query):
            return "last_6_months"
        elif re.search(r'last\s+12\s+months?', query):
            return "last_12_months"
        elif re.search(r'year\s+to\s+date|ytd', query):
            return "ytd"
        
        return None
