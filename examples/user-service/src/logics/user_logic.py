from src.domains.user import CreateUserOutcome, UserError, UserRecord, UserRuleCheck
from src.resources.user_rules import BLOCKED_EMAIL_DOMAINS, CREATE_USER_HTTP_STATUS


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
    if outcome.error is None:
        return CREATE_USER_HTTP_STATUS["created"]
    return CREATE_USER_HTTP_STATUS[outcome.error]
