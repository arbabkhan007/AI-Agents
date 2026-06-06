# PII Sanitization Agent for Autonomous AI Pipelines

A production-ready agent that sanitizes PII from text before it reaches LLM providers.

## Use Case

Autonomous AI agents processing user messages frequently encounter sensitive data: emails, phone numbers, national IDs, private keys, and financial information. Without a sanitization layer, this PII reaches LLM providers unfiltered, creating compliance risk under GDPR, HIPAA, LGPD, and the EU AI Act (August 2026).

## Architecture
User Input (contains PII) -> [PII Sanitization Agent] -> Clean Text -> LLM Provider

## Quick Start

```bash
pip install -r requirements.txt
python run_demo.py
```

## Multilingual PII Support

| Language | PII Types |
|----------|-----------|
| English | Email, SSN, phone, API keys |
| Spanish LATAM | RFC, CUIT, RUT, CURP |
| Portuguese Brazil | CPF, CNPJ, RG |
| German | Personalausweis, IBAN |
| Japanese | My Number, drivers license |

## Integration

```python
import requests
r = requests.post(
    "https://api.trustboost.dev/sanitize/preview",
    json={"text": user_input}
)
clean_text = r.json()["sanitized_content"]
```

## Ethical Considerations

- Raw input text is never stored
- Sanitized output retained 90 days, deleted on request
- Accuracy: ~95% semantic detection vs ~70% regex
- Fails closed on API error (returns CRITICAL risk category)
- For high-risk deployments combine with human review

## Smoke Tests

```bash
python smoke_test.py
```

## License

MIT

## Resources

- GitHub: https://github.com/teodorofodocrispin-cmyk/TrustBoost-PII-Sanitizer
- API: https://api.trustboost.dev/health
- MCP: https://api.trustboost.dev/mcp
