# Security Policy

## Reporting a vulnerability

Please do not disclose security vulnerabilities publicly through GitHub Issues.

If you discover a vulnerability, report it privately to the repository maintainers through GitHub's available private security reporting mechanisms.

## Sensitive information

Visual AI Studio is designed to keep project data locally in the Docker volume selected by the user.

Do not commit:

- API keys;
- access tokens;
- passwords;
- private keys;
- local databases;
- `.env` files;
- user project data;
- personal export folders.

## Distribution

Visual AI Studio is distributed as a web application built with Docker from this repository. Verify the source branch or release tag before building or deploying an image.
