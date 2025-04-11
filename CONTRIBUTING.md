# Contributing to Python NFC Library

Thank you for considering contributing to Python NFC Library! This document outlines the process for contributing to this project.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the existing issues to see if the problem has already been reported. If it has and the issue is still open, add a comment to the existing issue instead of opening a new one.

When creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title** for the issue
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** after following the steps 
- **Explain what behavior you expected to see instead**
- **Include details about your environment**:
  - OS version
  - Python version
  - NFC reader model
  - Version of this library
  - Any other relevant software versions
- **Include screenshots or log files** if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! When suggesting an enhancement, please:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful to most users**
- **Include mockups or examples** if applicable

### Pull Requests

When submitting a pull request:

1. Fork the repository
2. Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name` or `git checkout -b fix/issue-number`)
3. Make your changes
4. Add or update tests as necessary
5. Ensure the test suite passes
6. Update documentation as needed
7. Commit your changes with clear commit messages
8. Push to your branch
9. Open a pull request against the main branch

## Development Environment Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/python-nfc-library.git
   cd python-nfc-library
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -e .
   pip install -r dev-requirements.txt  # For development dependencies
   ```

## Coding Standards

This project follows PEP 8 style guidelines. Some key points:

- Use 4 spaces for indentation
- Maximum line length of 88 characters
- Use meaningful variable and function names
- Document all public methods, classes, and modules
- Add type hints where possible

We use `black` for code formatting, `flake8` for linting, and `mypy` for type checking. 

Run these tools before submitting:
```
black .
flake8
mypy .
```

## Testing

All new features and bug fixes should include tests. We use `pytest` for testing.

To run tests:
```
pytest
```

## Documentation

Documentation is as important as code. Please update the documentation when making changes:

- Update docstrings for any modified functions, classes, or modules
- Keep the README.md up to date
- Update or add examples as needed

## Release Process

The maintainers will handle releases according to semantic versioning:

- Patch (x.y.Z): Bug fixes and minor changes that don't affect the API
- Minor (x.Y.z): New features or enhancements that don't break backward compatibility
- Major (X.y.z): Changes that break backward compatibility

## Questions?

If you have any questions about contributing, please open an issue with your question.

Thank you for your contribution!