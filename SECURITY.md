# Security Policy

## Supported Versions

We actively support the following versions of BioContextAI with security updates:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

We recommend always using the latest version to ensure you have the most recent security patches.

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### For Sensitive Security Issues

For security vulnerabilities that could potentially expose user data or compromise system integrity, please use GitHub's private vulnerability reporting feature:

1. Go to the [Security tab](https://github.com/biocontext-ai/knowledgebase-mcp/security) of our repository
2. Click "Report a vulnerability"
3. Fill out the private vulnerability report form

### For General Security Concerns

For less sensitive security issues or general security improvements, you can:

1. Create a [security issue](https://github.com/biocontext-ai/knowledgebase-mcp/issues/new?template=security.md) using our security template
2. Email us directly at contact@biocontext.ai

### What to Include

When reporting a security vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What an attacker could achieve by exploiting this vulnerability
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Components**: Which parts of the application are affected
- **Suggested Fix**: If you have ideas for how to fix the issue
- **Disclosure Timeline**: Your preferred timeline for public disclosure

## Security Measures

### Remote Hosting Security

- **Cloudflare Protection**: DDoS protection and enhanced security configuration
- **HTTPS Enforcement**: All connections use encrypted HTTPS transport
- **Minimal Data Collection**: Only user IP addresses and API requests are processed

## Security Best Practices

- **Prefer Self-Hosting**: Use local deployment for sensitive research data
- **Network Security**: Deploy behind reverse proxy (nginx/Caddy) for production
- **Regular Updates**: Keep MCP server updated to latest version
- **Compliance**: Ensure usage aligns with institutional data policies

## Incident Response

In the event of a security incident:

1. **Immediate Response**: We will acknowledge your report within 48 hours
2. **Investigation**: Our team will investigate and validate the reported vulnerability
3. **Fix Development**: We will develop and test a fix for confirmed vulnerabilities
4. **Disclosure**: We will coordinate responsible disclosure with the reporter
5. **Deployment**: Security fixes will be deployed as soon as possible
6. **Communication**: We will communicate with affected users as appropriate

## Security Updates

- Security updates are released as soon as fixes are available
- Critical security issues may result in emergency releases
- Users will be notified of security updates through:
  - GitHub security advisories
  - Release notes

## Scope

This security policy covers:

- The Python package
- Our remote hosted instance of the MCP server

## Recognition

We appreciate the security research community and will acknowledge researchers who responsibly disclose vulnerabilities:

- Recognition in our security advisories (with permission)
- Attribution in release notes
- Our sincere gratitude for helping keep BioContextAI secure

## Contact

For security-related questions or concerns:

- **Private Reports**: Use GitHub's private vulnerability reporting
- **General Questions**: Create a security issue on GitHub
- **Direct Contact**: contact@biocontext.ai

## Legal

This security policy is subject to our [Terms of Service](https://biocontext.ai/legal/terms) and [Privacy Policy](https://biocontext.ai/legal/privacy).
