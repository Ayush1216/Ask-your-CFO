"""
Data loading utilities for CFO Copilot
"""
import pandas as pd
import os
from typing import Dict, Any

class FinancialDataLoader:
    """Loads and processes financial data from Excel files"""
    
    def __init__(self, data_file: str = "data.xlsx"):
        self.data_file = data_file
        self._data_cache = {}
        
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all sheets from the Excel file"""
        if not self._data_cache:
            try:
                xl_file = pd.ExcelFile(self.data_file)
                for sheet_name in xl_file.sheet_names:
                    self._data_cache[sheet_name] = pd.read_excel(self.data_file, sheet_name=sheet_name)
            except Exception as e:
                raise Exception(f"Error loading data file {self.data_file}: {str(e)}")
        
        return self._data_cache
    
    def get_actuals(self) -> pd.DataFrame:
        """Get actuals data"""
        data = self.load_all_data()
        return data.get('actuals', pd.DataFrame())
    
    def get_budget(self) -> pd.DataFrame:
        """Get budget data"""
        data = self.load_all_data()
        return data.get('budget', pd.DataFrame())
    
    def get_cash(self) -> pd.DataFrame:
        """Get cash data"""
        data = self.load_all_data()
        return data.get('cash', pd.DataFrame())
    
    def get_fx_rates(self) -> pd.DataFrame:
        """Get FX rates data"""
        data = self.load_all_data()
        return data.get('fx', pd.DataFrame())
    
    def get_monthly_summary(self, month: str = None) -> Dict[str, Any]:
        """Get monthly financial summary"""
        actuals = self.get_actuals()
        budget = self.get_budget()
        cash = self.get_cash()
        
        if month:
            actuals = actuals[actuals['month'] == month]
            budget = budget[budget['month'] == month]
            cash = cash[cash['month'] == month]
        
        # Calculate metrics
        summary = {
            'revenue_actual': actuals[actuals['account_category'] == 'Revenue']['amount'].sum(),
            'revenue_budget': budget[budget['account_category'] == 'Revenue']['amount'].sum(),
            'cogs_actual': actuals[actuals['account_category'] == 'COGS']['amount'].sum(),
            'cogs_budget': budget[budget['account_category'] == 'COGS']['amount'].sum(),
            'opex_actual': actuals[actuals['account_category'].str.startswith('Opex:')]['amount'].sum(),
            'opex_budget': budget[budget['account_category'].str.startswith('Opex:')]['amount'].sum(),
            'cash': cash['cash_usd'].iloc[-1] if not cash.empty else 0
        }
        
        # Calculate derived metrics
        summary['gross_margin_actual'] = (summary['revenue_actual'] - summary['cogs_actual']) / summary['revenue_actual'] * 100 if summary['revenue_actual'] > 0 else 0
        summary['gross_margin_budget'] = (summary['revenue_budget'] - summary['cogs_budget']) / summary['revenue_budget'] * 100 if summary['revenue_budget'] > 0 else 0
        summary['ebitda_actual'] = summary['revenue_actual'] - summary['cogs_actual'] - summary['opex_actual']
        summary['ebitda_budget'] = summary['revenue_budget'] - summary['cogs_budget'] - summary['opex_budget']
        
        return summary
    
    def get_opex_breakdown(self, month: str = None) -> pd.DataFrame:
        """Get Opex breakdown by category"""
        actuals = self.get_actuals()
        budget = self.get_budget()
        
        if month:
            actuals = actuals[actuals['month'] == month]
            budget = budget[budget['month'] == month]
        
        # Filter for Opex categories
        opex_actuals = actuals[actuals['account_category'].str.startswith('Opex:')]
        opex_budget = budget[budget['account_category'].str.startswith('Opex:')]
        
        # Aggregate by category (sum amounts for each category)
        opex_actuals_agg = opex_actuals.groupby('account_category')['amount'].sum().reset_index()
        opex_budget_agg = opex_budget.groupby('account_category')['amount'].sum().reset_index()
        
        # Merge actuals and budget
        opex_breakdown = pd.merge(
            opex_actuals_agg.rename(columns={'amount': 'actual'}),
            opex_budget_agg.rename(columns={'amount': 'budget'}),
            on='account_category',
            how='outer'
        ).fillna(0)
        
        opex_breakdown['variance'] = opex_breakdown['actual'] - opex_breakdown['budget']
        opex_breakdown['variance_pct'] = (opex_breakdown['variance'] / opex_breakdown['budget'] * 100).fillna(0)
        
        return opex_breakdown
    
    def get_cash_runway(self) -> Dict[str, Any]:
        """Calculate cash runway based on average monthly burn"""
        cash_data = self.get_cash()
        
        if len(cash_data) < 3:
            return {'runway_months': 0, 'avg_monthly_burn': 0, 'current_cash': 0}
        
        # Calculate monthly burn (negative change in cash)
        cash_data = cash_data.sort_values('month')
        cash_data['monthly_burn'] = cash_data['cash_usd'].diff() * -1
        
        # Average burn over last 3 months
        last_3_months = cash_data.tail(3)
        avg_monthly_burn = last_3_months['monthly_burn'].mean()
        current_cash = cash_data['cash_usd'].iloc[-1]
        
        runway_months = current_cash / avg_monthly_burn if avg_monthly_burn > 0 else 0
        
        return {
            'runway_months': runway_months,
            'avg_monthly_burn': avg_monthly_burn,
            'current_cash': current_cash
        }
