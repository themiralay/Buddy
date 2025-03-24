# ICEx Buddy - Your Personal AI Assistant

&#x20;&#x20;

ICEx Buddy is an advanced, modular personal AI assistant designed to help with daily tasks, provide intelligent conversation, and remember important details about you and your preferences over time.

## 🌟 Features

- **Conversational Memory**: Remembers past interactions and learns your preferences
- **Semantic Search**: Recalls relevant information from previous conversations
- **Multi-LLM Support**: Built-in integration with OpenAI models with support for more
- **Voice Capabilities**: Text-to-speech and speech recognition support
- **Task Management**: Extracts and manages tasks and reminders from conversations
- **Profile Learning**: Builds a user profile over time to provide personalized assistance
- **Multi-Platform**: CLI, web interface, and messaging platform integrations
- **Self-Hosted**: Run on your own hardware for complete privacy and control

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/themiralay/icex-buddy.git
cd icex-buddy

# Configure your API keys
cp .env.example .env
# Edit the .env file with your API keys

# Start the container
docker-compose up -d
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/themiralay/icex-buddy.git
cd icex-buddy

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your API keys
cp .env.example .env
# Edit the .env file with your API keys

# Run the application
python main.py
```

## 📖 Documentation

- [Setup Guide](docs/setup.md)
- [Architecture Overview](docs/architecture.md)
- [Configuration Options](docs/configuration.md)
- [API Reference](docs/api.md)
- [Voice Integration](docs/voice.md)
- [Custom LLM Integration](docs/custom-llm.md)
- [Extending ICEx Buddy](docs/extending.md)

## 🔧 Configuration

ICEx Buddy uses a YAML configuration file and environment variables for credentials and settings. See [Configuration Options](docs/configuration.md) for a complete reference.

## 🤝 Contributing

Contributions are welcome! Please check our [Contributing Guidelines](CONTRIBUTING.md) before getting started.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- OpenAI for the powerful LLM models
- ElevenLabs for voice technology
- All contributors and supporters of the project

## 🔗 Links

- [Project Homepage](https://github.com/themiralay/icex-buddy)
- [Issue Tracker](https://github.com/themiralay/icex-buddy/issues)
- [Discord Community](https://discord.gg/icex-buddy)

Built with ❤️ by Miralay

