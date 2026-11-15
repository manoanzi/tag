"""User domain configuration: values that may change per environment or client without code changes."""

import json
from pathlib import Path

_HERE = Path(__file__).parent

BLOCKED_EMAIL_DOMAINS: frozenset[str] = frozenset(json.loads((_HERE / "blocked_email_domains.json").read_text()))

USER_ERROR_MESSAGES: dict[str, str] = json.loads((_HERE / "user_error_messages.json").read_text())
