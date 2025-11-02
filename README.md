# DOCU-GEN

AI-powered documentation generation system that creates comprehensive documentation from simple user ideas using multi-agent collaboration.

## 🚀 Quick Start

```bash
# Install dependencies
./scripts/setup.sh

# Set API key
echo "GEMINI_API_KEY=your_key" > .env

# Run tests
pytest tests/unit

# Generate documentation
python -m src.coordination.coordinator
```

## 📋 Features

- **Multi-Agent System**: Specialized agents for different documentation types
- **Multi-LLM Support**: Works with Gemini, OpenAI, and extensible to others
- **Quality Assurance**: Automated quality checks and scoring
- **Scalable Architecture**: Built for extension and growth

## 📚 Documentation

See [docs/README.md](docs/README.md) for complete documentation.

- **Architecture**: [docs/architecture/](docs/architecture/)
- **Development**: [docs/development/](docs/development/)
- **Configuration**: [docs/configuration/](docs/configuration/)

## 🏗️ Project Structure

```
docu-gen/
├── src/                    # Source code
│   ├── agents/            # Documentation agents
│   ├── context/           # Shared context management
│   ├── coordination/      # Workflow orchestration
│   ├── llm/               # LLM provider abstractions
│   ├── quality/           # Quality checking
│   ├── rate_limit/        # Rate limiting
│   └── utils/             # Utilities
├── tests/                 # Test suite (pytest)
├── docs/                   # Documentation
├── scripts/                # Setup and utility scripts
├── prompts/                # System prompts (editable)
└── pyproject.toml          # Project configuration
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Unit tests only (fast)
pytest tests/unit -m unit

# With coverage
pytest --cov=src --cov-report=html
```

## 📝 License

MIT License - see [LICENSE](LICENSE)
