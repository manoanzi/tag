from returns.result import Failure, Result, Success

BLOCKED_EMAIL_DOMAINS = frozenset({"tempmail.com", "disposable.com", "throwaway.email"})


def validate_email_domain(email: str) -> Result[str, str]:
    domain = email.split("@")[-1].lower()
    if domain in BLOCKED_EMAIL_DOMAINS:
        return Failure(f"Email domain not allowed: {domain}")
    return Success(email)


def ensure_user_not_exists(rows: list[dict]) -> Result[None, str]:
    if rows:
        return Failure("A user with this email already exists")
    return Success(None)
