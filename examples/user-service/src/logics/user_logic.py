from typing import Literal

from src.domains.user import CreateUserOutcome, UserError, UserRecord, UserRuleCheck
from src.resources.user_rules import BLOCKED_EMAIL_DOMAINS

# A decision table, not configuration: it never changes between environments.
HTTP_STATUS_BY_OUTCOME: dict[UserError | None, int] = {
    None: 201,
    UserError.INVALID_PAYLOAD: 422,
    UserError.EMAIL_DOMAIN_NOT_ALLOWED: 422,
    UserError.USER_ALREADY_EXISTS: 409,
    UserError.STORAGE_FAILURE: 500,
}


def check_email_domain(email: str) -> UserRuleCheck:
    domain = email.split("@")[-1].lower()
    if domain in BLOCKED_EMAIL_DOMAINS:
        return UserRuleCheck(error=UserError.EMAIL_DOMAIN_NOT_ALLOWED)
    return UserRuleCheck()


def check_user_is_new(existing: list[UserRecord]) -> UserRuleCheck:
    if existing:
        return UserRuleCheck(error=UserError.USER_ALREADY_EXISTS)
    return UserRuleCheck()


def resolve_create_user_status(outcome: CreateUserOutcome) -> int:
    return HTTP_STATUS_BY_OUTCOME[outcome.error]


def resolve_create_user_log_level(outcome: CreateUserOutcome) -> Literal["info", "error"]:
    if outcome.error is None:
        return "info"
    return "error"
