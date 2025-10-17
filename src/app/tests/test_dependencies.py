import pytest
from src.app.dependencies import get_current_user

def test_get_current_user():
    user = get_current_user()
    assert isinstance(user, dict)
    assert user["sub"] == "anonymous"
    assert user["preferred_username"] == "public_user"
    assert "admin" in user["realm_access"]["roles"]
