"""
Main CFO Copilot Agent
"""
from typing import Tuple, Any
from .intent_classifier import IntentClassifier, IntentType
from .financial_analyzer import FinancialAnalyzer, format_currency
from .data_loader import FinancialDataLoader

class CFOAgent:
    """Main CFO Copilot Agent that processes queries and returns responses"""
    
    def __init__(self, data_file: str = "data.xlsx"):
        self.data_loader = FinancialDataLoader(data_file)
        self.intent_classifier = IntentClassifier()
        self.analyzer = FinancialAnalyzer(self.data_loader)
    
    def process_query(self, query: str) -> Tuple[str, Any]:
        """Process a user query and return response with chart"""
        try:
            # Classify intent
            intent, params = self.intent_classifier.classify(query)
            
            # Route to appropriate analyzer
            if intent == IntentType.REVENUE_VS_BUDGET:
                return self.analyzer.analyze_revenue_vs_budget(params.get('month'))
            
            elif intent == IntentType.GROSS_MARGIN_TREND:
                return self.analyzer.analyze_gross_margin_trend(params.get('time_period', 'last_3_months'))
            
            elif intent == IntentType.OPEX_BREAKDOWN:
                return self.analyzer.analyze_opex_breakdown(params.get('month'))
            
            elif intent == IntentType.CASH_RUNWAY:
                return self.analyzer.analyze_cash_runway()
            
            elif intent == IntentType.EBITDA_ANALYSIS:
                return self.analyzer.analyze_ebitda(params.get('month'))
            
            else:
                # General query - provide overview
                return self._handle_general_query(query)
                
        except Exception as e:
            return f"Sorry, I encountered an error processing your query: {str(e)}", None
    
    def _handle_general_query(self, query: str) -> Tuple[str, Any]:
        """Handle general queries with a summary overview"""
        try:
            summary = self.data_loader.get_monthly_summary()
            runway_data = self.data_loader.get_cash_runway()
            
            # Calculate variances for overview
            revenue_variance = summary['revenue_actual'] - summary['revenue_budget']
            revenue_variance_pct = (revenue_variance / summary['revenue_budget'] * 100) if summary['revenue_budget'] > 0 else 0
            
            ebitda_variance = summary['ebitda_actual'] - summary['ebitda_budget']
            ebitda_variance_pct = (ebitda_variance / summary['ebitda_budget'] * 100) if summary['ebitda_budget'] > 0 else 0
            
            response = f"""**Financial Overview (Latest Month)**

• **Revenue:** {format_currency(summary['revenue_actual'])} actual&nbsp;vs&nbsp;{format_currency(summary['revenue_budget'])} budget  
  - Variance: {format_currency(revenue_variance)} ({revenue_variance_pct:+.1f}%)

• **Gross Margin:** {summary['gross_margin_actual']:.1f}% actual&nbsp;vs&nbsp;{summary['gross_margin_budget']:.1f}% budget

• **EBITDA:** {format_currency(summary['ebitda_actual'])} actual&nbsp;vs&nbsp;{format_currency(summary['ebitda_budget'])} budget  
  - Variance: {format_currency(ebitda_variance)} ({ebitda_variance_pct:+.1f}%)

• **Cash Runway:** {runway_data['runway_months']:.1f} months

**Available Analyses:**

• Revenue vs Budget comparisons

• Gross Margin trends

• Opex breakdown by category

• Cash runway analysis

• EBITDA performance

Try asking: "What was June 2025 revenue vs budget?" or "Show me gross margin trends"
"""
            
            return response.strip(), None
            
        except Exception as e:
            return f"Sorry, I couldn't generate a summary: {str(e)}", None
