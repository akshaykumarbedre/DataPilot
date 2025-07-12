# DataPilot 🚀

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.46+-red.svg)
![AutoGen](https://img.shields.io/badge/autogen-0.6.4-green.svg)
![OpenAI](https://img.shields.io/badge/openai-gpt--4-orange.svg)
![Docker](https://img.shields.io/badge/docker-required-blue.svg)
![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)

**DataPilot** is an intelligent, AI-powered data analysis platform that revolutionizes how you interact with your data. Using advanced multi-agent architecture with OpenAI's GPT-4, DataPilot automatically analyzes CSV datasets, generates insights, creates visualizations, and answers complex data questions through natural language queries.

## 🌟 Features

- **🤖 Multi-Agent AI System**: Powered by AutoGen framework with specialized agents for data analysis and code execution
- **📊 Automated Data Analysis**: Upload CSV files and get instant insights through natural language queries
- **🎨 Dynamic Visualizations**: Automatically generates charts, plots, and graphs using matplotlib
- **🔒 Safe Code Execution**: Sandboxed Docker environment ensures secure Python code execution
- **💬 Interactive Chat Interface**: Streamlit-based web UI for seamless user experience
- **🧠 Intelligent Code Generation**: AI agents write and execute Python code to solve data problems
- **📈 Real-time Results**: Stream responses and view generated visualizations instantly
- **🔄 Stateful Conversations**: Maintains context across multiple queries in a session

## 🛠️ Technologies Used

- **Python 3.8+**: Core programming language
- **Streamlit**: Web interface framework
- **AutoGen**: Multi-agent conversation framework
- **OpenAI GPT-4**: Large language model for intelligent analysis
- **Docker**: Containerized code execution environment
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Data visualization library
- **NumPy**: Numerical computing
- **Asyncio**: Asynchronous programming support

## 📋 Prerequisites

Before installing DataPilot, ensure you have:

- Python 3.8 or higher
- Docker installed and running
- OpenAI API key
- Git (for cloning the repository)

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/akshaykumarbedre/DataPilot.git
cd DataPilot
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the root directory and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Ensure Docker is running:**
```bash
docker --version
```

## ⚡ Quick Start

1. **Clone and install:**
```bash
git clone https://github.com/akshaykumarbedre/DataPilot.git
cd DataPilot
pip install -r requirements.txt
```

2. **Set up your OpenAI API key:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Run the application:**
```bash
streamlit run streamlit_app.py
```

4. **Try it out:**
   - Upload the included `sample_data.csv` file
   - Ask: "Show me the average salary by department"
   - Watch DataPilot analyze your data automatically!

## 🎯 Usage

### Web Interface (Recommended)

1. **Start the Streamlit application:**
```bash
streamlit run streamlit_app.py
```

2. **Open your browser** and navigate to `http://localhost:8501`

3. **Upload a CSV file** using the file uploader

4. **Ask questions** about your data in natural language:
   - "What are the top 5 categories by sales?"
   - "Create a scatter plot showing the correlation between age and income"
   - "What's the average revenue by month?"
   - "Show me the distribution of customer ratings"

5. **View results** including generated code, analysis, and visualizations

### Command Line Interface

For advanced users, run the CLI version:
```bash
python main.py
```

## 📊 Example Queries

DataPilot can handle various types of data analysis questions:

- **Statistical Analysis**: "What's the correlation between these columns?"
- **Data Visualization**: "Create a bar chart showing sales by region"
- **Data Filtering**: "Show me records where revenue > 1000"
- **Trend Analysis**: "Plot the trend of monthly sales over time"
- **Aggregation**: "Calculate the average, median, and mode of prices"

## 🏗️ Architecture

DataPilot uses a sophisticated multi-agent architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  Data Analyzer   │    │ Code Executor   │
│                 │◄──►│     Agent        │◄──►│     Agent       │
│   (Interface)   │    │  (GPT-4 Based)   │    │  (Docker Env)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

- **Streamlit UI**: Provides the web interface for file uploads and chat
- **Data Analyzer Agent**: Analyzes data and generates Python code
- **Code Executor Agent**: Safely executes code in a Docker container
- **Selector Group Chat**: Coordinates agent interactions intelligently

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MODEL`: AI model to use (default: gpt-4o)
- `DOCKER_WORK_DIR`: Working directory for Docker (default: temp)
- `DOCKER_TIMEOUT`: Docker execution timeout (default: 120 seconds)
- `MAX_TURNS`: Maximum conversation turns (default: 15)

### Docker Configuration

DataPilot uses Docker for safe code execution. The application automatically:
- Starts a Docker container for code execution
- Mounts the working directory
- Installs required Python packages
- Executes generated code safely
- Cleans up resources after use

## 📁 Project Structure

```
DataPilot/
├── agents/
│   ├── code_executor_agent.py    # Docker-based code execution
│   ├── data_analyzer_agent.py    # AI data analysis agent
│   └── prompts/
│       └── data_analyzer_prompt.py
├── config/
│   ├── constants.py              # Configuration constants
│   ├── docker_utils.py           # Docker utilities
│   └── model_client.py           # OpenAI client setup
├── team/
│   └── analyzer_gpt_team.py      # Multi-agent coordination
├── temp/                         # Working directory for files
├── main.py                       # CLI interface
├── streamlit_app.py              # Web interface
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🤝 Contributing

We welcome contributions to DataPilot! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Make your changes** with clear, descriptive commit messages
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a detailed description

### Development Setup

1. Clone your fork and create a development branch
2. Install development dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest` (if tests exist)
4. Follow PEP 8 coding standards

### Code Style

- Use descriptive variable names
- Add docstrings to functions and classes
- Follow PEP 8 formatting guidelines
- Add type hints where appropriate

## 🐛 Known Issues

- Docker container startup may take a few seconds on first run
- Large CSV files (>100MB) may require additional memory configuration
- Some complex visualizations may need manual matplotlib configuration

## 🗺️ Roadmap

- [ ] Support for additional file formats (Excel, JSON, Parquet)
- [ ] Enhanced visualization templates
- [ ] Database connectivity (PostgreSQL, MySQL)
- [ ] Advanced statistical analysis features
- [ ] Export functionality for reports and visualizations
- [ ] User authentication and session management
- [ ] API endpoints for programmatic access

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Akshay Kumar Bedre** ([@akshaykumarbedre](https://github.com/akshaykumarbedre))

- GitHub: [akshaykumarbedre](https://github.com/akshaykumarbedre)
- LinkedIn: [Connect with me](https://www.linkedin.com/in/akshaykumarbedre)

## 🙏 Acknowledgments

- [AutoGen](https://github.com/microsoft/autogen) for the multi-agent framework
- [OpenAI](https://openai.com/) for GPT-4 API
- [Streamlit](https://streamlit.io/) for the web interface framework
- The open-source community for various Python libraries

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/akshaykumarbedre/DataPilot/issues) section
2. Create a new issue with detailed description
3. Join our community discussions

---

⭐ **If you find DataPilot useful, please consider giving it a star!** ⭐