# DataPilot 🚀

An AI-powered data analysis tool that uses intelligent agents to analyze CSV data through natural language conversations. Built with Microsoft AutoGen framework and powered by OpenAI's GPT models.

## ✨ Features

- **Multi-Agent System**: Orchestrates specialized AI agents for data analysis and code execution
- **Natural Language Queries**: Ask questions about your data in plain English
- **Automated Code Generation**: Generates Python code automatically to answer your questions
- **Secure Code Execution**: Runs analysis code in isolated Docker containers
- **Interactive Web Interface**: User-friendly Streamlit interface with file upload
- **Data Visualization**: Automatically generates charts and plots using matplotlib
- **CSV File Support**: Upload and analyze CSV files with ease
- **Real-time Processing**: Stream results as analysis progresses

## 🏗️ Architecture

DataPilot uses a multi-agent architecture with two main components:

- **DataAnalyzerAgent**: Analyzes data requirements and generates Python code
- **CodeExecutorAgent**: Executes the generated code in a secure Docker environment

The agents communicate through Microsoft AutoGen's SelectorGroupChat pattern, enabling intelligent conversation flow and task delegation.

## 🔧 Prerequisites

- **Python 3.8+**
- **Docker** (for secure code execution)
- **OpenAI API Key** (for GPT models)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akshaykumarbedre/DataPilot.git
   cd DataPilot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Copy the template and add your API key:
   ```bash
   cp .env.template .env
   # Edit .env file and add your OpenAI API key
   ```
   
   Or create a `.env` file manually:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Ensure Docker is running**
   ```bash
   docker --version
   ```

5. **Pull the required Docker image**
   ```bash
   docker pull amancevice/pandas
   ```

## 🚀 Quick Start

Want to get started immediately? Here's a 2-minute setup:

1. **Clone and setup**
   ```bash
   git clone https://github.com/akshaykumarbedre/DataPilot.git
   cd DataPilot
   pip install -r requirements.txt
   ```

2. **Add your OpenAI API key**
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

3. **Start the app**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open http://localhost:8501** and start analyzing data!

## 🚀 Usage

### Web Interface (Recommended)

1. **Start the Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Upload your CSV file** using the file uploader

4. **Ask questions** about your data in the chat interface:
   - "Show me a summary of the data"
   - "Create a bar chart of sales by region"
   - "What's the correlation between age and income?"
   - "Find outliers in the dataset"

### Command Line Interface

Run the CLI version with a predefined task:

```bash
python main.py
```

*Note: Edit the `task` variable in `main.py` to customize the analysis.*

## 📊 Example Queries

Here are some example questions you can ask DataPilot:

### Data Exploration
- "What are the column names and data types?"
- "Show me the first 10 rows"
- "What's the shape of this dataset?"
- "Are there any missing values?"

### Statistical Analysis
- "Calculate descriptive statistics for all numeric columns"
- "Find the correlation matrix"
- "Identify outliers in the price column"
- "Show me the distribution of categories"

### Data Visualization
- "Create a histogram of ages"
- "Make a scatter plot of height vs weight"
- "Show sales trends over time"
- "Generate a heatmap of correlations"

### Advanced Analysis
- "Perform clustering analysis"
- "Calculate the moving average"
- "Show seasonal patterns in the data"
- "Identify the top 10 customers by revenue"

## 🗂️ Project Structure

```
DataPilot/
├── agents/                     # AI agent definitions
│   ├── data_analyzer_agent.py  # Main analysis agent
│   ├── code_executor_agent.py  # Code execution agent
│   └── prompts/               # Agent system prompts
├── config/                    # Configuration files
│   ├── constants.py           # App constants
│   ├── docker_utils.py        # Docker utilities
│   └── model_client.py        # OpenAI client setup
├── team/                      # Agent orchestration
│   └── analyzer_gpt_team.py   # Team coordination logic
├── temp/                      # Temporary files
├── main.py                    # CLI interface
├── streamlit_app.py           # Web interface
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ⚙️ Configuration

### Model Settings
Edit `config/constants.py` to customize:
- **MODEL**: OpenAI model to use (default: `gpt-4o`)
- **MAX_TURNS**: Maximum conversation turns
- **DOCKER_TIMEOUT**: Code execution timeout

### Docker Configuration
The application uses Docker for secure code execution. Generated code runs in an isolated container using the `amancevice/pandas` image with access to:
- Python 3.x
- pandas, matplotlib, numpy, seaborn
- Jupyter notebook capabilities
- Common data analysis libraries

## 🔧 Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError" when running the app
**Solution**: Install dependencies with `pip install -r requirements.txt`

**Issue**: "OpenAI API key not found"
**Solution**: Set your API key in the `.env` file or environment variables

**Issue**: "Docker not found"
**Solution**: Install Docker and ensure it's running

**Issue**: "Permission denied" errors
**Solution**: Check Docker permissions and ensure user is in docker group

### Debug Mode

To enable verbose logging, set the environment variable:
```bash
export AUTOGEN_DEBUG=1
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests** (if available)
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Create a Pull Request**

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Areas for Contribution

- **New Agent Types**: Create specialized agents for different analysis tasks
- **Data Sources**: Add support for Excel, JSON, database connections
- **Visualizations**: Implement new chart types and interactive plots
- **Performance**: Optimize code execution and memory usage
- **Documentation**: Improve guides and tutorials

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft AutoGen** - Multi-agent framework
- **OpenAI** - GPT models for natural language processing
- **Streamlit** - Web interface framework
- **Docker** - Containerization technology

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [Issues](https://github.com/akshaykumarbedre/DataPilot/issues)
3. Create a new issue with detailed information

## 🔮 Roadmap

- [ ] Support for additional file formats (Excel, JSON, Parquet)
- [ ] Integration with cloud storage (AWS S3, Google Drive)
- [ ] Advanced machine learning capabilities
- [ ] Multi-language support
- [ ] Real-time data streaming
- [ ] Custom agent creation interface

---

**Made with ❤️ by the DataPilot Team**