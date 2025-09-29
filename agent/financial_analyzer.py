"""
Financial analysis functions for CFO Copilot
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, Tuple
from .data_loader import FinancialDataLoader

def format_currency(amount: float) -> str:
    """Return an HTML-safe USD string that avoids MathJax ($...$) parsing in Streamlit."""
    return f"&#36;{amount:,.0f}"

def direction_word(value: float, up_word: str = "above", down_word: str = "below") -> str:
    """Small wording helper for narratives."""
    if value > 0:
        return up_word
    if value < 0:
        return down_word
    return "in line with"

def trend_word(delta: float) -> str:
    if delta > 0.05:
        return "improving"
    if delta < -0.05:
        return "declining"
    return "flat"

class FinancialAnalyzer:
    """Performs financial analysis and generates charts"""
    
    def __init__(self, data_loader: FinancialDataLoader):
        self.data_loader = data_loader
    
    def analyze_revenue_vs_budget(self, month: str = None) -> Tuple[str, go.Figure]:
        """Analyze revenue vs budget for a specific month or overall"""
        summary = self.data_loader.get_monthly_summary(month)
        
        if month:
            title = f"Revenue vs Budget - {month}"
        else:
            title = "Revenue vs Budget - Latest Month"
        
        # Create comparison chart
        fig = go.Figure()
        
        categories = ['Revenue', 'COGS', 'Opex', 'EBITDA']
        actual_values = [
            summary['revenue_actual'],
            summary['cogs_actual'],
            summary['opex_actual'],
            summary['ebitda_actual']
        ]
        budget_values = [
            summary['revenue_budget'],
            summary['cogs_budget'],
            summary['opex_budget'],
            summary['ebitda_budget']
        ]
        
        fig.add_trace(go.Bar(
            name='Actual',
            x=categories,
            y=actual_values,
            marker_color='#2E86AB'
        ))
        
        fig.add_trace(go.Bar(
            name='Budget',
            x=categories,
            y=budget_values,
            marker_color='#A23B72'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Category',
            yaxis_title='Amount (USD)',
            barmode='group',
            height=400
        )
        
        # Generate text response
        revenue_variance = summary['revenue_actual'] - summary['revenue_budget']
        revenue_variance_pct = (revenue_variance / summary['revenue_budget'] * 100) if summary['revenue_budget'] > 0 else 0
        
        ebitda_variance = summary['ebitda_actual'] - summary['ebitda_budget']
        ebitda_variance_pct = (ebitda_variance / summary['ebitda_budget'] * 100) if summary['ebitda_budget'] > 0 else 0
        
        gm_delta_pp = summary['gross_margin_actual'] - summary['gross_margin_budget']

        response = f"""**Revenue vs Budget Analysis {'for ' + month if month else '(Latest Month)'}**

• **Revenue:** {format_currency(summary['revenue_actual'])} actual&nbsp;vs&nbsp;{format_currency(summary['revenue_budget'])} budget  
  - Variance: {format_currency(revenue_variance)} ({revenue_variance_pct:+.1f}%)

• **Gross Margin:** {summary['gross_margin_actual']:.1f}% actual&nbsp;vs&nbsp;{summary['gross_margin_budget']:.1f}% budget

• **EBITDA:** {format_currency(summary['ebitda_actual'])} actual&nbsp;vs&nbsp;{format_currency(summary['ebitda_budget'])} budget  
  - Variance: {format_currency(ebitda_variance)} ({ebitda_variance_pct:+.1f}%)

Summary: Revenue was {direction_word(revenue_variance)} budget by {format_currency(abs(revenue_variance))}; gross margin is {trend_word(gm_delta_pp/100)} vs plan ({gm_delta_pp:+.1f} pp); EBITDA finished {direction_word(ebitda_variance)} plan by {format_currency(abs(ebitda_variance))}."""
        
        return response.strip(), fig
    
    def analyze_gross_margin_trend(self, time_period: str = "last_3_months") -> Tuple[str, go.Figure]:
        """Analyze gross margin trend over time"""
        actuals = self.data_loader.get_actuals()
        budget = self.data_loader.get_budget()
        
        # Get recent months based on time period
        if time_period == "last_3_months":
            months = actuals['month'].unique()[-3:]
        elif time_period == "last_6_months":
            months = actuals['month'].unique()[-6:]
        elif time_period == "last_12_months":
            months = actuals['month'].unique()[-12:]
        else:
            months = actuals['month'].unique()[-3:]  # Default to last 3 months
        
        # Calculate gross margin for each month
        margin_data = []
        for month in months:
            month_actuals = actuals[actuals['month'] == month]
            month_budget = budget[budget['month'] == month]
            
            revenue_actual = month_actuals[month_actuals['account_category'] == 'Revenue']['amount'].sum()
            cogs_actual = month_actuals[month_actuals['account_category'] == 'COGS']['amount'].sum()
            revenue_budget = month_budget[month_budget['account_category'] == 'Revenue']['amount'].sum()
            cogs_budget = month_budget[month_budget['account_category'] == 'COGS']['amount'].sum()
            
            gross_margin_actual = (revenue_actual - cogs_actual) / revenue_actual * 100 if revenue_actual > 0 else 0
            gross_margin_budget = (revenue_budget - cogs_budget) / revenue_budget * 100 if revenue_budget > 0 else 0
            
            margin_data.append({
                'month': month,
                'actual': gross_margin_actual,
                'budget': gross_margin_budget
            })
        
        df = pd.DataFrame(margin_data)
        
        # Create trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['actual'],
            mode='lines+markers',
            name='Actual',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['budget'],
            mode='lines+markers',
            name='Budget',
            line=dict(color='#A23B72', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f'Gross Margin Trend - {time_period.replace("_", " ").title()}',
            xaxis_title='Month',
            yaxis_title='Gross Margin (%)',
            height=400
        )
        
        # Generate text response
        latest_actual = df['actual'].iloc[-1]
        latest_budget = df['budget'].iloc[-1]
        avg_actual = df['actual'].mean()
        avg_budget = df['budget'].mean()
        
        latest_variance = latest_actual - latest_budget
        avg_variance = avg_actual - avg_budget
        
        response = f"""**Gross Margin Trend Analysis - {time_period.replace('_', ' ').title()}**

• **Latest Month:** {latest_actual:.1f}% actual&nbsp;vs&nbsp;{latest_budget:.1f}% budget  
  - Variance: {latest_variance:+.1f} percentage points

• **Average:** {avg_actual:.1f}% actual&nbsp;vs&nbsp;{avg_budget:.1f}% budget  
  - Variance: {avg_variance:+.1f} percentage points

• **Trend:** {'Improving' if df['actual'].iloc[-1] > df['actual'].iloc[0] else 'Declining'} over the period

Summary: Latest margin is {direction_word(latest_variance, 'above', 'below')} budget by {latest_variance:+.1f} pp; the period average is {direction_word(avg_variance, 'above', 'below')} budget by {avg_variance:+.1f} pp."""
        
        return response.strip(), fig
    
    def analyze_opex_breakdown(self, month: str = None) -> Tuple[str, go.Figure]:
        """Analyze Opex breakdown by category"""
        opex_breakdown = self.data_loader.get_opex_breakdown(month)
        
        if opex_breakdown.empty:
            return "No Opex data available for the specified period.", go.Figure()
        
        # Create breakdown chart
        fig = go.Figure()
        
        # Clean category names for display
        opex_breakdown['category_display'] = opex_breakdown['account_category'].str.replace('Opex:', '')
        
        fig.add_trace(go.Bar(
            x=opex_breakdown['category_display'],
            y=opex_breakdown['actual'],
            name='Actual',
            marker_color='#2E86AB'
        ))
        
        fig.add_trace(go.Bar(
            x=opex_breakdown['category_display'],
            y=opex_breakdown['budget'],
            name='Budget',
            marker_color='#A23B72'
        ))
        
        fig.update_layout(
            title=f'Opex Breakdown by Category {"- " + month if month else "(Latest Month)"}',
            xaxis_title='Category',
            yaxis_title='Amount (USD)',
            barmode='group',
            height=400
        )
        
        # Generate text response
        total_actual = opex_breakdown['actual'].sum()
        total_budget = opex_breakdown['budget'].sum()
        total_variance = total_actual - total_budget
        total_variance_pct = (total_variance / total_budget * 100) if total_budget > 0 else 0
        
        response = f"""**Opex Breakdown Analysis {'for ' + month if month else '(Latest Month)'}**

• **Total Opex:** {format_currency(total_actual)} actual&nbsp;vs&nbsp;{format_currency(total_budget)} budget  
  - Variance: {format_currency(total_variance)} ({total_variance_pct:+.1f}%)

**By Category:**
"""
        
        for _, row in opex_breakdown.iterrows():
            response += (
                f"\n\n• **{row['category_display']}:** "
                f"{format_currency(row['actual'])} actual&nbsp;vs&nbsp;{format_currency(row['budget'])} "
                f"budget ({row['variance_pct']:+.1f}%)"
            )
        top_cat = opex_breakdown.sort_values('actual', ascending=False).iloc[0]
        response += (
            f"\n\nSummary: Total opex was {direction_word(total_variance, 'over', 'under')} budget by {format_currency(abs(total_variance))}. "
            f"Largest spend was {top_cat['account_category'].replace('Opex:','')} at {format_currency(top_cat['actual'])}."
        )

        return response.strip(), fig
    
    def analyze_cash_runway(self) -> Tuple[str, go.Figure]:
        """Analyze cash runway"""
        runway_data = self.data_loader.get_cash_runway()
        cash_data = self.data_loader.get_cash()
        
        if cash_data.empty:
            return "No cash data available.", go.Figure()
        
        # Create cash trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=cash_data['month'],
            y=cash_data['cash_usd'],
            mode='lines+markers',
            name='Cash Balance',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='Cash Balance Trend',
            xaxis_title='Month',
            yaxis_title='Cash (USD)',
            height=400
        )
        
        # Generate text response
        response = f"""**Cash Runway Analysis**

• **Current Cash:** \\${runway_data['current_cash']:,.0f}

• **Average Monthly Burn:** \\${runway_data['avg_monthly_burn']:,.0f}

• **Cash Runway:** {runway_data['runway_months']:.1f} months

**Status**: {'🟢 Healthy' if runway_data['runway_months'] > 12 else '🟡 Monitor' if runway_data['runway_months'] > 6 else '🔴 Critical'}

Summary: With {format_currency(runway_data['current_cash'])} on hand and an average monthly burn of {format_currency(runway_data['avg_monthly_burn'])}, runway is approximately {runway_data['runway_months']:.1f} months."""
        
        return response.strip(), fig
    
    def analyze_ebitda(self, month: str = None) -> Tuple[str, go.Figure]:
        """Analyze EBITDA performance"""
        summary = self.data_loader.get_monthly_summary(month)
        
        # Create EBITDA waterfall chart
        fig = go.Figure()
        
        categories = ['Revenue', 'COGS', 'Opex', 'EBITDA']
        values = [
            summary['revenue_actual'],
            -summary['cogs_actual'],
            -summary['opex_actual'],
            summary['ebitda_actual']
        ]
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'${v:,.0f}' for v in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f'EBITDA Analysis {"- " + month if month else "(Latest Month)"}',
            xaxis_title='Category',
            yaxis_title='Amount (USD)',
            height=400
        )
        
        # Generate text response
        ebitda_variance = summary['ebitda_actual'] - summary['ebitda_budget']
        ebitda_variance_pct = (ebitda_variance / summary['ebitda_budget'] * 100) if summary['ebitda_budget'] > 0 else 0
        
        response = f"""**EBITDA Analysis {'for ' + month if month else '(Latest Month)'}**

• **Revenue:** \\${summary['revenue_actual']:,.0f}

• **COGS:** \\${summary['cogs_actual']:,.0f}

• **Opex:** \\${summary['opex_actual']:,.0f}

• **EBITDA:** \\${summary['ebitda_actual']:,.0f} actual&nbsp;vs&nbsp;\\${summary['ebitda_budget']:,.0f} budget  
  - Variance: \\${ebitda_variance:,.0f} ({ebitda_variance_pct:+.1f}%)

• **Gross Margin:** {summary['gross_margin_actual']:.1f}%

Summary: EBITDA was {direction_word(ebitda_variance)} budget by {format_currency(abs(ebitda_variance))}."""
        
        return response.strip(), fig
