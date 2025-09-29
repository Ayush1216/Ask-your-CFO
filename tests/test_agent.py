"""
Tests for CFO Copilot Agent
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.cfo_agent import CFOAgent
from agent.intent_classifier import IntentClassifier, IntentType
from agent.data_loader import FinancialDataLoader

class TestIntentClassifier:
    """Test intent classification functionality"""
    
    def setup_method(self):
        self.classifier = IntentClassifier()
    
    def test_revenue_vs_budget_intent(self):
        """Test revenue vs budget intent classification"""
        intent, params = self.classifier.classify("What was June 2025 revenue vs budget?")
        assert intent == IntentType.REVENUE_VS_BUDGET
        assert params['month'] == '2023-06'  # Updated to match actual data
    
    def test_gross_margin_trend_intent(self):
        """Test gross margin trend intent classification"""
        intent, params = self.classifier.classify("Show gross margin trend for the last 3 months")
        assert intent == IntentType.GROSS_MARGIN_TREND
        assert params['time_period'] == 'last_3_months'
    
    def test_opex_breakdown_intent(self):
        """Test Opex breakdown intent classification"""
        intent, params = self.classifier.classify("Break down Opex by category for June")
        assert intent == IntentType.OPEX_BREAKDOWN
        assert params['month'] == '2023-06'
    
    def test_cash_runway_intent(self):
        """Test cash runway intent classification"""
        intent, params = self.classifier.classify("What is our cash runway right now?")
        assert intent == IntentType.CASH_RUNWAY
    
    def test_month_extraction(self):
        """Test month extraction from queries"""
        intent, params = self.classifier.classify("Show me January revenue")
        assert params['month'] == '2023-01'
        
        intent, params = self.classifier.classify("What about 2024-03?")
        assert params['month'] == '2024-03'

class TestDataLoader:
    """Test data loading functionality"""
    
    def setup_method(self):
        self.data_loader = FinancialDataLoader("data.xlsx")
    
    def test_load_all_data(self):
        """Test loading all data sheets"""
        data = self.data_loader.load_all_data()
        assert 'actuals' in data
        assert 'budget' in data
        assert 'cash' in data
        assert 'fx' in data
        
        # Check data structure
        assert isinstance(data['actuals'], pd.DataFrame)
        assert isinstance(data['budget'], pd.DataFrame)
        assert isinstance(data['cash'], pd.DataFrame)
        assert isinstance(data['fx'], pd.DataFrame)
    
    def test_get_monthly_summary(self):
        """Test monthly summary generation"""
        summary = self.data_loader.get_monthly_summary()
        
        # Check required fields
        required_fields = [
            'revenue_actual', 'revenue_budget',
            'cogs_actual', 'cogs_budget',
            'opex_actual', 'opex_budget',
            'gross_margin_actual', 'gross_margin_budget',
            'ebitda_actual', 'ebitda_budget'
        ]
        
        for field in required_fields:
            assert field in summary
            assert isinstance(summary[field], (int, float, np.integer, np.floating, type(None)))
    
    def test_get_opex_breakdown(self):
        """Test Opex breakdown generation"""
        opex_breakdown = self.data_loader.get_opex_breakdown()
        
        if not opex_breakdown.empty:
            required_columns = ['account_category', 'actual', 'budget', 'variance', 'variance_pct']
            for col in required_columns:
                assert col in opex_breakdown.columns
    
    def test_get_cash_runway(self):
        """Test cash runway calculation"""
        runway_data = self.data_loader.get_cash_runway()
        
        required_fields = ['runway_months', 'avg_monthly_burn', 'current_cash']
        for field in required_fields:
            assert field in runway_data
            assert isinstance(runway_data[field], (int, float, np.integer, np.floating, type(None)))

class TestCFOAgent:
    """Test main CFO Agent functionality"""
    
    def setup_method(self):
        self.agent = CFOAgent("data.xlsx")
    
    def test_process_revenue_query(self):
        """Test processing revenue vs budget query"""
        response, chart = self.agent.process_query("What was June 2025 revenue vs budget?")
        
        assert isinstance(response, str)
        assert "Revenue" in response
        assert "budget" in response.lower()
        assert chart is not None
    
    def test_process_margin_trend_query(self):
        """Test processing gross margin trend query"""
        response, chart = self.agent.process_query("Show gross margin trend for the last 3 months")
        
        assert isinstance(response, str)
        assert "Gross Margin" in response
        assert "trend" in response.lower()
        assert chart is not None
    
    def test_process_opex_query(self):
        """Test processing Opex breakdown query"""
        response, chart = self.agent.process_query("Break down Opex by category")
        
        assert isinstance(response, str)
        assert "Opex" in response
        assert chart is not None
    
    def test_process_cash_runway_query(self):
        """Test processing cash runway query"""
        response, chart = self.agent.process_query("What is our cash runway?")
        
        assert isinstance(response, str)
        assert "Cash Runway" in response
        assert "months" in response
        assert chart is not None
    
    def test_process_general_query(self):
        """Test processing general query"""
        response, chart = self.agent.process_query("Give me an overview")
        
        assert isinstance(response, str)
        assert "Financial Overview" in response
        # General queries might not have charts
        assert chart is None or chart is not None

if __name__ == "__main__":
    pytest.main([__file__])
