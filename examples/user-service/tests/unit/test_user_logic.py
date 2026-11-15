from src.logics.user_logic import ensure_user_not_exists, validate_email_domain


def test_accepts_allowed_domain():
    assert validate_email_domain("ana@gmail.com").unwrap() == "ana@gmail.com"


def test_rejects_blocked_domain():
    assert "tempmail.com" in validate_email_domain("ana@tempmail.com").failure()


def test_user_does_not_exist_when_no_rows():
    assert ensure_user_not_exists([]).unwrap() is None


def test_user_exists_when_rows_found():
    assert ensure_user_not_exists([{"id": "1"}]).failure()
