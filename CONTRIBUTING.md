# Contributing to Windows AI Assistant

Thank you for your interest in contributing to Windows AI Assistant! This document provides guidelines and instructions for contributors.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Python version
   - Windows version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs

### Suggesting Features

1. Check existing feature requests
2. Provide a clear description of the feature
3. Explain the use case and benefit
4. Consider if it fits the project's privacy-first philosophy

### Submitting Code

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests/ -v`)
5. Commit your changes (`git commit -m "feat: add amazing feature"`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a pull request

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Add tests for new functionality

### Commit Messages

Use conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add USB webcam support`

### Testing

- Write unit tests for new functionality
- Ensure tests pass before submitting PR
- Aim for >80% code coverage
- Use pytest for testing

## Project Philosophy

Windows AI Assistant is built on these principles:
- **Privacy First**: All processing happens locally
- **No Cloud Dependencies**: No telemetry, no external APIs
- **User Control**: Emergency brake, configurable behavior
- **Accessibility**: Works on standard Windows hardware
- **Open Source**: Free to use, modify, and distribute

When contributing, ensure your changes align with these principles.

## Areas for Contribution

We welcome help in:
- Additional awareness modules (network, webcam, etc.)
- Performance optimizations
- Documentation improvements
- Bug fixes
- Windows compatibility improvements
- Testing on different hardware configurations

## Getting Help

- Open an issue for bugs or questions
- Check existing documentation
- Join discussions in issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Windows AI Assistant! 🎉
