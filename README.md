# CFO Copilot 📊

An AI-powered financial analysis assistant that helps CFOs get instant insights from their financial data. Ask questions in natural language and get back concise, board-ready answers with interactive charts.

## Features

- **Natural Language Queries**: Ask questions like "What was June 2025 revenue vs budget?" or "Show me gross margin trends"
- **Interactive Charts**: Get visual insights with Plotly charts embedded in responses
- **Key Financial Metrics**: Revenue vs Budget, Gross Margin %, Opex breakdown, EBITDA, Cash runway
- **Real-time Analysis**: Instant responses with data-driven insights
- **Board-ready Format**: Concise summaries perfect for executive presentations

## Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cfo-copilot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## Data Format

The application expects an Excel file (`data.xlsx`) with the following sheets:

### actuals
| month | entity | account_category | amount | currency |
|-------|--------|------------------|--------|----------|
| 2023-01 | ParentCo | Revenue | 380000 | USD |
| 2023-01 | ParentCo | COGS | 57000 | USD |
| 2023-01 | ParentCo | Opex:Marketing | 76000 | USD |

### budget
| month | entity | account_category | amount | currency |
|-------|--------|------------------|--------|----------|
| 2023-01 | ParentCo | Revenue | 400000 | USD |
| 2023-01 | ParentCo | COGS | 56000 | USD |
| 2023-01 | ParentCo | Opex:Marketing | 72000 | USD |

### cash
| month | entity | cash_usd |
|-------|---------|----------|
| 2023-01 | Consolidated | 6000000 |
| 2023-02 | Consolidated | 5950000 |

### fx
| month | currency | rate_to_usd |
|-------|----------|-------------|
| 2023-01 | USD | 1.000 |
| 2023-01 | EUR | 1.085 |

## Sample Questions

### Revenue Analysis
- "What was June 2025 revenue vs budget in USD?"
- "Show me revenue trends for the last 6 months"
- "How did we perform against budget this quarter?"

### Margin Analysis
- "Show Gross Margin % trend for the last 3 months"
- "What's our current gross margin?"
- "How is our profitability trending?"

### Expense Analysis
- "Break down Opex by category for June"
- "Show me Opex trends"
- "What are our biggest expense categories?"

### Cash Analysis
- "What is our cash runway right now?"
- "Show cash balance trends"
- "How long can we operate with current cash?"

### Profitability
- "Show me EBITDA analysis"
- "What's our profitability trend?"
- "How are we performing on EBITDA vs budget?"

## Architecture

```
cfo-copilot/
├── app.py                 # Streamlit web application
├── requirements.txt       # Python dependencies
├── data.xlsx             # Financial data (Excel file)
├── agent/                # Core agent logic
│   ├── __init__.py
│   ├── cfo_agent.py      # Main agent orchestrator
│   ├── data_loader.py    # Data loading and processing
│   ├── intent_classifier.py # Query intent classification
│   └── financial_analyzer.py # Financial analysis and charting
├── tests/                # Test suite
│   ├── __init__.py
│   └── test_agent.py     # Unit tests
└── README.md             # This file
```

## Key Components

### 1. Intent Classification
The system uses pattern matching to classify user queries into specific intents:
- Revenue vs Budget analysis
- Gross Margin trends
- Opex breakdown
- Cash runway analysis
- EBITDA analysis

### 2. Data Processing
- Loads financial data from Excel sheets
- Calculates key metrics (margins, EBITDA, variances)
- Handles time-based analysis and trends

### 3. Chart Generation
- Interactive Plotly charts
- Revenue vs Budget comparisons
- Trend analysis over time
- Category breakdowns
- Cash runway visualizations

### 4. Response Generation
- Concise, board-ready summaries
- Key metrics and variances
- Actionable insights
- Visual charts for context

## Testing

Run the test suite:

```bash
pytest tests/
```

Or run specific tests:

```bash
pytest tests/test_agent.py::TestIntentClassifier::test_revenue_vs_budget_intent
```

## Development

### Adding New Analysis Types

1. **Add intent pattern** in `agent/intent_classifier.py`
2. **Create analysis function** in `agent/financial_analyzer.py`
3. **Update agent routing** in `agent/cfo_agent.py`
4. **Add tests** in `tests/test_agent.py`

### Customizing Charts

Charts are generated using Plotly in `agent/financial_analyzer.py`. You can customize:
- Colors and styling
- Chart types (bar, line, scatter, etc.)
- Layout and formatting
- Interactive features

## Troubleshooting

### Common Issues

1. **"Error initializing CFO Agent"**
   - Check that `data.xlsx` exists in the project root
   - Verify Excel file has required sheets (actuals, budget, cash, fx)

2. **"No data available"**
   - Ensure data sheets have the correct column names
   - Check that data is in the expected format

3. **Charts not displaying**
   - Verify Plotly is installed: `pip install plotly`
   - Check browser console for JavaScript errors

### Data Validation

The system expects:
- Month format: YYYY-MM (e.g., 2023-01)
- Currency: USD (other currencies supported via FX rates)
- Account categories: Revenue, COGS, Opex:*, etc.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the test cases for usage examples
3. Open an issue on GitHub

---

**CFO Copilot** - Making financial analysis as easy as asking a question! 🚀
