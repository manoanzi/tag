"""Static configuration for the user domain, read from the JSON files next to this module."""

import json
from pathlib import Path

_HERE = Path(__file__).parent

BLOCKED_EMAIL_DOMAINS: frozenset[str] = frozenset(json.loads((_HERE / "blocked_email_domains.json").read_text()))

CREATE_USER_HTTP_STATUS: dict[str, int] = json.loads((_HERE / "create_user_http_status.json").read_text())

USER_ERROR_MESSAGES: dict[str, str] = json.loads((_HERE / "user_error_messages.json").read_text())
