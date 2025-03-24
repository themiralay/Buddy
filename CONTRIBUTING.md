
## 2. CONTRIBUTING.md

```markdown
# Contributing to ICEx Buddy

Thank you for your interest in contributing to ICEx Buddy! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/icex-buddy.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment (see below)

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- pip
- API keys for OpenAI and other services used

### Setup Steps

1. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
2. Copy the example environment file: `cp .env.example .env`
3. Add your API keys to the `.env` file
4. Run tests to verify your setup: `pytest`

## Coding Standards

We follow PEP 8 style guidelines for Python code.

- Use 4 spaces for indentation
- Maximum line length of 100 characters
- Use docstrings for all modules, classes, and functions
- Write clear commit messages

## Testing

- Write unit tests for all new functionality
- All tests must pass before submitting a pull request
- Run tests with: `pytest`
- Run linting with: `flake8`

## Pull Request Process

1. Ensure your code follows the coding standards
2. Update the documentation if necessary
3. Add or update tests as appropriate
4. Verify all tests pass
5. Submit a pull request with a clear description of the changes

## Feature Requests and Bug Reports

- Use the GitHub Issues tracker to report bugs or request features
- Provide as much detail as possible
- For bugs, include steps to reproduce, expected behavior, and actual behavior

## Documentation

- Update documentation for any changes to functionality
- Follow the existing documentation style
- Documentation is written in Markdown

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

## Questions?

Feel free to reach out to the maintainers if you have any questions!