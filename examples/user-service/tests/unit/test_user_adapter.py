from uuid import UUID

from pydantic import ValidationError

from src.adapters.user_adapter import to_create_user_input, to_create_user_output, to_user_domain
from src.domains.user import CreateUserInput, User


def test_tolerant_reader_ignores_unknown_fields():
    data = to_create_user_input({"email": "ana@gmail.com", "name": "Ana", "nickname": "ignored"}).unwrap()
    assert data == CreateUserInput(email="ana@gmail.com", name="Ana")


def test_invalid_email_is_rejected():
    result = to_create_user_input({"email": "not-an-email", "name": "Ana"})
    assert isinstance(result.failure(), ValidationError)


def test_to_user_domain_generates_id():
    user = to_user_domain(CreateUserInput(email="ana@gmail.com", name="Ana"))
    assert isinstance(user.id, UUID)


def test_to_create_user_output():
    user = User(id=UUID("12345678-1234-5678-1234-567812345678"), email="ana@gmail.com", name="Ana")
    assert to_create_user_output(user).id == "12345678-1234-5678-1234-567812345678"
