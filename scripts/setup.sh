#!/bin/bash
# Setup script for DOCU-GEN
# Usage: ./scripts/setup.sh

set -e

echo "🚀 Setting up DOCU-GEN..."

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📦 Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
uv venv

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
uv pip install --python .venv/bin/python \
    google-generativeai>=0.3.0 \
    ratelimit>=2.2.1 \
    diskcache>=5.6.3 \
    textstat>=0.7.3 \
    python-dotenv>=1.0.0

# Install dev dependencies
echo ""
echo "📦 Installing development dependencies..."
uv pip install --python .venv/bin/python \
    pytest>=7.0.0 \
    pytest-cov>=4.1.0 \
    pytest-mock>=3.12.0

# Verify installation
echo ""
echo "✅ Verifying installation..."
.venv/bin/python -c "
import sys
packages = ['google.generativeai', 'ratelimit', 'diskcache', 'textstat', 'pytest']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg}')
    except ImportError:
        print(f'  ❌ {pkg}')
        sys.exit(1)
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "💡 Next steps:"
echo "   1. Create .env file: echo 'GEMINI_API_KEY=your_key' > .env"
echo "   2. Run tests: pytest tests/unit"
echo "   3. See docs/README.md for more information"
echo ""
