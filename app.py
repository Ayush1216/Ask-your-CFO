"""
CFO Copilot - Streamlit Web App
"""
import streamlit as st
import plotly.graph_objects as go
from agent.cfo_agent import CFOAgent
from agent.pdf_exporter import PDFExporter
import os
import re
import base64
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="CFO Copilot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2E86AB;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #A23B72;
    }
    .assistant-message {
        background-color: #e8f4f8;
        border-left-color: #2E86AB;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1e5f7a;
    }
    /* Prevent accidental italics from markdown/em */
    em { font-style: normal !important; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    st.session_state.agent = None

# Initialize agent
@st.cache_resource
def get_agent():
    """Get or create the CFO agent"""
    try:
        return CFOAgent("data.xlsx")
    except Exception as e:
        st.error(f"Error initializing CFO Agent: {str(e)}")
        return None

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">📊 CFO Copilot</h1>', unsafe_allow_html=True)
    st.markdown("Ask questions about your financial data and get instant insights with charts.")
    
    # Sidebar
    with st.sidebar:
        st.header("💡 Sample Questions")
        st.markdown("""
        **Revenue Analysis:**
        - What was June 2025 revenue vs budget?
        - Show me revenue trends
        
        **Margin Analysis:**
        - Show gross margin trend for the last 3 months
        - What's our current gross margin?
        
        **Expense Analysis:**
        - Break down Opex by category for June
        - Show me Opex trends
        
        **Cash Analysis:**
        - What is our cash runway right now?
        - Show cash balance trends
        
        **Profitability:**
        - Show me EBITDA analysis
        - What's our profitability trend?
        """)
        
        st.header("📈 Key Metrics")
        if st.session_state.agent:
            try:
                summary = st.session_state.agent.data_loader.get_monthly_summary()
                runway_data = st.session_state.agent.data_loader.get_cash_runway()
                
                st.metric("Revenue", f"${summary['revenue_actual']:,.0f}")
                st.metric("Gross Margin", f"{summary['gross_margin_actual']:.1f}%")
                st.metric("EBITDA", f"${summary['ebitda_actual']:,.0f}")
                st.metric("Cash Runway", f"{runway_data['runway_months']:.1f} months")
            except:
                st.info("Load data to see metrics")
        
        st.header("📄 Export Reports")
        if st.session_state.agent:
            try:
                pdf_exporter = PDFExporter(st.session_state.agent.data_loader, st.session_state.agent.analyzer)
                # Generate bytes on each render so the download URL stays valid
                exec_bytes = pdf_exporter.export_executive_summary()
                cash_bytes = pdf_exporter.export_cash_trend_report()

                # Data URL link (works even when download managers intercept blob URLs)
                exec_b64 = base64.b64encode(exec_bytes).decode("utf-8")
                st.markdown("**Executive Summary**")
                st.markdown(
                    f"<a href='data:application/pdf;base64,{exec_b64}' download='cfo_executive_summary.pdf' target='_blank'>Open/Download</a>",
                    unsafe_allow_html=True,
                )

                cash_b64 = base64.b64encode(cash_bytes).decode("utf-8")
                st.markdown("**Cash Trend Report**")
                st.markdown(
                    f"<a href='data:application/pdf;base64,{cash_b64}' download='cfo_cash_trend_report.pdf' target='_blank'>Open/Download</a>",
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"PDF export error: {str(e)}")
    
    # Initialize agent
    if st.session_state.agent is None:
        st.session_state.agent = get_agent()
    
    if st.session_state.agent is None:
        st.error("Failed to initialize CFO Agent. Please check your data file.")
        return
    
    # Chat interface
    st.header("💬 Ask Your CFO Questions")
    
    # Display chat messages
    def render_message(content: str):
        # Convert a limited subset of our markdown to HTML to avoid Streamlit's markdown quirks
        lines = content.split("\n")
        # Basic styling for dark theme readability
        html_parts = [
            """
            <div class='msg' style="color:#e6eef2;font-size:16px;line-height:1.6;">
            <style>
            .msg ul{margin:0 0 8px 22px;padding:0}
            .msg li{margin:6px 0}
            .msg p{margin:0 0 8px 0}
            .msg strong{color:#e6eef2}
            </style>
            """
        ]
        in_ul = False
        bold = re.compile(r"\*\*(.*?)\*\*")
        for line in lines:
            if line.strip().startswith("• "):
                if not in_ul:
                    html_parts.append("<ul>")
                    in_ul = True
                text = line.strip()[2:]
                text = text.replace("&nbsp;", "&nbsp;")
                text = bold.sub(r"<strong>\1</strong>", text)
                html_parts.append(f"<li>{text}</li>")
            elif line.strip() == "":
                if in_ul:
                    html_parts.append("</ul>")
                    in_ul = False
                html_parts.append("<div style='height:6px'></div>")
            else:
                text = bold.sub(r"<strong>\1</strong>", line)
                html_parts.append(f"<p>{text}</p>")
        if in_ul:
            html_parts.append("</ul>")
        html_parts.append("</div>")
        html = "".join(html_parts)
        # Heuristic height so content is visible without cutting off
        est_height = min(900, max(220, 28 * (len([l for l in lines if l.strip()]) + 3)))
        components.html(html, height=est_height, scrolling=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            render_message(message["content"]) 
            if "chart" in message and message["chart"] is not None:
                st.plotly_chart(message["chart"], use_container_width=True)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your financial data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                try:
                    response, chart = st.session_state.agent.process_query(prompt)
                    
                    # Display response
                    render_message(response)
                    
                    # Display chart if available
                    if chart is not None:
                        st.plotly_chart(chart, use_container_width=True)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "chart": chart
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "chart": None
                    })
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        CFO Copilot - AI-powered financial analysis assistant
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
