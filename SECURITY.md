# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes     |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do not** create a public issue
2. Send an email to: security@windows-ai-assistant.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if known)

### What to Expect

- We will acknowledge receipt within 48 hours
- We will provide a detailed response within 7 days
- We will work on a fix and coordinate disclosure

## Security Principles

Windows AI Assistant is designed with security in mind:

### Privacy by Design
- All processing happens locally on your machine
- No data leaves your computer
- No telemetry or analytics
- No cloud dependencies

### User Control
- Emergency brake (Ctrl+Alt+Shift+E) freezes all automation
- Configurable behavior via config.yaml
- Open source code for audit

### Minimal Privileges
- Runs with standard user permissions
- No admin rights required
- No system modifications

## Known Security Considerations

### Screen Capture
- Desktop awareness captures screen content locally
- Screenshots are never transmitted externally
- Users can disable awareness features

### Audio Capture
- Audio awareness captures microphone input locally
- Audio is never transmitted externally
- Users can disable audio features

### MCP Integration
- WinScript MCP provides UI automation tools
- Tools execute locally on Windows
- No external API calls

### LLM Integration
- Ollama runs locally on your machine
- Prompts are processed locally
- No external LLM APIs used

## Best Practices for Users

1. **Review Configuration**: Check config.yaml before running
2. **Use Emergency Brake**: Keep Ctrl+Alt+Shift+E handy
3. **Monitor Logs**: Check logs/assistant.log for unusual activity
4. **Keep Updated**: Update dependencies regularly
5. **Run as Standard User**: Don't run with admin privileges unless necessary

## Dependency Security

We regularly update dependencies to address known vulnerabilities. To update:

```bash
pip install --upgrade -r requirements.txt
```

## Security Audits

We welcome security audits of the codebase. If you find issues, please report them following the vulnerability reporting process.

## License

This project is licensed under the MIT License. See LICENSE for details.

## Contact

For security-related questions: security@windows-ai-assistant.com
