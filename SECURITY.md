# Security Policy

## Supported Versions

We actively support the current version and maintain the previous version with hotfixes for vulnerabilities that may be reported by our users.

| Version | Support stage | End of support |
| ------- | ------------- | -------------- |
| 3.x.x   | Active        | Not planned    |
| 2.x.x   | Maintenance   | Dec 2025       |
| 1.x.x   | Deprecated    | Dec 2024       |
| 0.x.x   | Deprecated    | Dec 2024       |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. Create a [new discussion](https://github.com/eclipse-score/bazel-tools-cc/issues)
2. Label it with either `security` or `vulnerability` tags
3. Include all necessary information following the discussion template

## Security Best Practices

### For Contributors

- **Never commit secrets, tokens, or credentials**
- **Use secure coding practices**
- **Keep dependencies up to date**
- **Follow the principle of least privilege**
- **Validate all inputs**

### For Users

- **Always use the latest supported version**
- **Keep your environment updated**
- **Report suspicious behavior**

## Security Features

This project includes:

- Automated vulnerability scanning (pip-audit)
- Static code analysis
- Code quality checks
- Hermetic builds and releases with integrity verification
- Secure build pipeline

## Known Vulnerabilities

Known vulnerabilities may vary according to the selected Python version.

You can check our latest constraints against vulnerable package versions in our [requirements.in file](third_party/pip/requirements.in).

The following table lists all known vulnerabilities that could not be fixed:

| Package | Vulnerability ID    | Vulnerable Version | Fixed Version | Python Version | Reason                               |
| ------- | ------------------- | ------------------ | ------------- | -------------- | ------------------------------------ |
| urllib3 | GHSA-48p4-8xcf-vxj5 | 2.2.3              | 2.5.0         | 3.8            | Fixed package requires Python >= 3.9 |
| urllib3 | GHSA-pq67-6m6q-mj2v | 2.2.3              | 2.5.0         | 3.8            | Fixed package requires Python >= 3.9 |
| pip     | GHSA-4xh5-x5gv-qwph | 25.0.1             | 25.3          | 3.8            | Fixed package requires Python >= 3.9 |

### Vulnerable Python Versions

The [official status of Python versions](https://devguide.python.org/versions/) shows which Python versions are no longer supported and therefore are vulnerable.

While we might support some vulnerable Python versions for backwards compatibility, we strongly advise our users to consider upgrading to a more recent version.
