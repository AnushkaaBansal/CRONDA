# Contributing to CRONDA

Thank you for your interest in contributing to CRONDA! This document provides guidelines and steps for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

### 1. Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/yourusername/cronda/issues) section
- If not, create a new issue with:
  - A clear, descriptive title
  - Steps to reproduce the bug
  - Expected vs actual behavior
  - Environment details (OS, Python version, etc.)
  - Screenshots if applicable

### 2. Suggesting Enhancements

- Check if the enhancement has already been suggested
- Create a new issue with:
  - A clear, descriptive title
  - Detailed description of the enhancement
  - Why it would be useful
  - Any potential implementation ideas

### 3. Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Ensure all tests pass:
   ```bash
   python -m pytest tests/
   ```
5. Commit your changes with a clear message:
   ```bash
   git commit -m "Description of changes"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request

### 4. Code Style

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Include docstrings for functions and classes
- Add comments for complex logic
- Write tests for new features

### 5. Development Setup

1. Set up the development environment:
   ```bash
   # Backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Frontend
   cd frontend
   npm install
   ```

2. Run tests:
   ```bash
   # Backend tests
   python -m pytest tests/

   # Frontend tests
   cd frontend
   npm test
   ```

### 6. Documentation

- Update README.md for significant changes
- Add/update docstrings for new functions
- Update API documentation if needed

## Getting Help

If you need help or have questions:
- Open an issue
- Join our community chat (if available)
- Contact the maintainers

Thank you for contributing to CRONDA! 