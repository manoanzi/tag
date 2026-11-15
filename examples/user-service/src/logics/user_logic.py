from returns.result import Failure, Result, Success

from src.domains.user import CreateUserOutput, UserError, UserRecord

BLOCKED_EMAIL_DOMAINS = frozenset({"tempmail.com", "disposable.com", "throwaway.email"})

HTTP_STATUS_BY_ERROR: dict[UserError, int] = {
    UserError.INVALID_PAYLOAD: 422,
    UserError.EMAIL_DOMAIN_NOT_ALLOWED: 422,
    UserError.USER_ALREADY_EXISTS: 409,
    UserError.STORAGE_FAILURE: 500,
}


def validate_email_domain(email: str) -> Result[str, UserError]:
    domain = email.split("@")[-1].lower()
    if domain in BLOCKED_EMAIL_DOMAINS:
        return Failure(UserError.EMAIL_DOMAIN_NOT_ALLOWED)
    return Success(email)


def ensure_user_not_exists(existing: list[UserRecord]) -> Result[None, UserError]:
    if existing:
        return Failure(UserError.USER_ALREADY_EXISTS)
    return Success(None)


def resolve_create_user_status(result: Result[CreateUserOutput, UserError]) -> int:
    """Decides the HTTP status of the use case: 201 on success, mapped status on failure."""
    return result.map(lambda _: 201).lash(lambda error: Success(HTTP_STATUS_BY_ERROR[error])).unwrap()
