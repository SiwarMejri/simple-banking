import pytest
from src.app.core import core
from src.app.models.account import Account


def test_get_account_balance_existing():
    core.reset_state()
    acc = core.create_or_update_account("x1", 100)
    assert core.get_account_balance("x1") == acc


def test_get_account_balance_missing():
    core.reset_state()
    assert core.get_account_balance("ghost") is None


def test_process_transaction_missing_parameters(mocker):
    db = mocker.Mock()
    data = {"from_account": "1"}  # champs manquants
    result = core.process_transaction(db, data)
    assert result["status"] == "failed"
    assert "manquants" in result["reason"]


def test_process_transaction_exception(mocker):
    db = mocker.Mock()
    # on provoque une erreur générique
    db.query.side_effect = Exception("Erreur DB")
    data = {"from_account": "1", "to_account": "2", "amount": 50}
    result = core.process_transaction(db, data)
    assert result["status"] == "failed"
    assert "Erreur DB" in result["reason"]
