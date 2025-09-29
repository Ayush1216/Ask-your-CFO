"""
PDF export functionality for CFO Copilot
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Any, List
import io
import base64
from .data_loader import FinancialDataLoader
from .financial_analyzer import FinancialAnalyzer

class PDFExporter:
    """Export financial reports to PDF"""
    
    def __init__(self, data_loader: FinancialDataLoader, analyzer: FinancialAnalyzer):
        self.data_loader = data_loader
        self.analyzer = analyzer
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72')
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
    
    def export_executive_summary(self) -> bytes:
        """Export executive summary to PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Build the PDF content
        story = []
        
        # Title
        story.append(Paragraph("CFO Executive Summary", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Get financial data
        summary = self.data_loader.get_monthly_summary()
        runway_data = self.data_loader.get_cash_runway()
        opex_breakdown = self.data_loader.get_opex_breakdown()
        
        # Key Metrics Section
        story.append(Paragraph("Key Financial Metrics", self.styles['SectionHeader']))
        
        # Create metrics table
        metrics_data = [
            ['Metric', 'Actual', 'Budget', 'Variance', 'Variance %'],
            ['Revenue', f"${summary['revenue_actual']:,.0f}", f"${summary['revenue_budget']:,.0f}", 
             f"${summary['revenue_actual'] - summary['revenue_budget']:,.0f}", 
             f"{(summary['revenue_actual'] - summary['revenue_budget']) / summary['revenue_budget'] * 100:+.1f}%"],
            ['COGS', f"${summary['cogs_actual']:,.0f}", f"${summary['cogs_budget']:,.0f}", 
             f"${summary['cogs_actual'] - summary['cogs_budget']:,.0f}", 
             f"{(summary['cogs_actual'] - summary['cogs_budget']) / summary['cogs_budget'] * 100:+.1f}%"],
            ['Opex', f"${summary['opex_actual']:,.0f}", f"${summary['opex_budget']:,.0f}", 
             f"${summary['opex_actual'] - summary['opex_budget']:,.0f}", 
             f"{(summary['opex_actual'] - summary['opex_budget']) / summary['opex_budget'] * 100:+.1f}%"],
            ['EBITDA', f"${summary['ebitda_actual']:,.0f}", f"${summary['ebitda_budget']:,.0f}", 
             f"${summary['ebitda_actual'] - summary['ebitda_budget']:,.0f}", 
             f"{(summary['ebitda_actual'] - summary['ebitda_budget']) / summary['ebitda_budget'] * 100:+.1f}%"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Gross Margin Section
        story.append(Paragraph("Gross Margin Analysis", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Actual Gross Margin:</b> {summary['gross_margin_actual']:.1f}%", self.styles['MetricValue']))
        story.append(Paragraph(f"<b>Budget Gross Margin:</b> {summary['gross_margin_budget']:.1f}%", self.styles['MetricValue']))
        story.append(Paragraph(f"<b>Variance:</b> {summary['gross_margin_actual'] - summary['gross_margin_budget']:+.1f} percentage points", self.styles['MetricValue']))
        story.append(Spacer(1, 20))
        
        # Opex Breakdown Section
        if not opex_breakdown.empty:
            story.append(Paragraph("Opex Breakdown by Category", self.styles['SectionHeader']))
            
            opex_data = [['Category', 'Actual', 'Budget', 'Variance %']]
            for _, row in opex_breakdown.iterrows():
                category = row['account_category'].replace('Opex:', '')
                opex_data.append([
                    category,
                    f"${row['actual']:,.0f}",
                    f"${row['budget']:,.0f}",
                    f"{row['variance_pct']:+.1f}%"
                ])
            
            opex_table = Table(opex_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
            opex_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(opex_table)
            story.append(Spacer(1, 20))
        
        # Cash Runway Section
        story.append(Paragraph("Cash Runway Analysis", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Current Cash:</b> ${runway_data['current_cash']:,.0f}", self.styles['MetricValue']))
        story.append(Paragraph(f"<b>Average Monthly Burn:</b> ${runway_data['avg_monthly_burn']:,.0f}", self.styles['MetricValue']))
        story.append(Paragraph(f"<b>Cash Runway:</b> {runway_data['runway_months']:.1f} months", self.styles['MetricValue']))
        
        # Status indicator
        if runway_data['runway_months'] > 12:
            status = "🟢 Healthy"
        elif runway_data['runway_months'] > 6:
            status = "🟡 Monitor"
        else:
            status = "🔴 Critical"
        
        story.append(Paragraph(f"<b>Status:</b> {status}", self.styles['MetricValue']))
        story.append(Spacer(1, 20))
        
        # Summary and Recommendations
        story.append(Paragraph("Summary & Recommendations", self.styles['SectionHeader']))
        
        # Generate summary based on performance
        revenue_variance_pct = (summary['revenue_actual'] - summary['revenue_budget']) / summary['revenue_budget'] * 100
        ebitda_variance_pct = (summary['ebitda_actual'] - summary['ebitda_budget']) / summary['ebitda_budget'] * 100
        
        summary_text = f"""
        <b>Revenue Performance:</b> {'Above budget' if revenue_variance_pct > 0 else 'Below budget'} by {abs(revenue_variance_pct):.1f}%
        <br/><b>EBITDA Performance:</b> {'Above budget' if ebitda_variance_pct > 0 else 'Below budget'} by {abs(ebitda_variance_pct):.1f}%
        <br/><b>Cash Position:</b> {runway_data['runway_months']:.1f} months runway
        <br/><br/>
        <b>Key Recommendations:</b>
        <br/>• {'Continue current growth trajectory' if revenue_variance_pct > 5 else 'Focus on revenue growth initiatives' if revenue_variance_pct < -5 else 'Maintain current revenue levels'}
        <br/>• {'Optimize cost structure' if ebitda_variance_pct < -10 else 'Maintain current cost efficiency'}
        <br/>• {'Monitor cash burn closely' if runway_data['runway_months'] < 12 else 'Cash position is healthy'}
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_cash_trend_report(self) -> bytes:
        """Export cash trend analysis to PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        story.append(Paragraph("Cash Trend Analysis", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Get cash data
        cash_data = self.data_loader.get_cash()
        runway_data = self.data_loader.get_cash_runway()
        
        if not cash_data.empty:
            # Cash trend table
            story.append(Paragraph("Cash Balance Trend", self.styles['SectionHeader']))
            
            # Show last 12 months or all available data
            recent_cash = cash_data.tail(12) if len(cash_data) > 12 else cash_data
            
            cash_table_data = [['Month', 'Cash Balance (USD)', 'Monthly Change']]
            for _, row in recent_cash.iterrows():
                change = row['cash_usd'] - recent_cash[recent_cash['month'] == row['month']].iloc[0]['cash_usd'] if len(recent_cash) > 1 else 0
                if len(recent_cash) > 1:
                    prev_month = recent_cash[recent_cash['month'] < row['month']]
                    if not prev_month.empty:
                        change = row['cash_usd'] - prev_month.iloc[-1]['cash_usd']
                
                cash_table_data.append([
                    str(row['month']),
                    f"${row['cash_usd']:,.0f}",
                    f"${change:,.0f}" if change != 0 else "$0"
                ])
            
            cash_table = Table(cash_table_data, colWidths=[1.5*inch, 2*inch, 1.5*inch])
            cash_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cash_table)
            story.append(Spacer(1, 20))
        
        # Runway analysis
        story.append(Paragraph("Cash Runway Analysis", self.styles['SectionHeader']))
        story.append(Paragraph(f"<b>Current Cash:</b> ${runway_data['current_cash']:,.0f}", self.styles['MetricValue']))
        story.append(Paragraph(f"<b>Average Monthly Burn:</b> ${runway_data['avg_monthly_burn']:,.0f}", self.styles['MetricValue']))
        story.append(Paragraph(f"<b>Cash Runway:</b> {runway_data['runway_months']:.1f} months", self.styles['MetricValue']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
