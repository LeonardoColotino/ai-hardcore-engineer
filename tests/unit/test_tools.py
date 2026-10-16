from app.tools.customer_lookup import CustomerLookupTool
from app.tools.transaction_lookup import TransactionLookupTool
from app.tools.payment_status import PaymentStatusTool


def test_customer_lookup_valid(tmp_repo):
    r = CustomerLookupTool(tmp_repo).run("u1")
    assert r.success and r.data["customer"]["name"] == "A"


def test_customer_lookup_missing(tmp_repo):
    r = CustomerLookupTool(tmp_repo).run("missing")
    assert not r.success and "not found" in r.error.lower()


def test_transactions_are_user_scoped(tmp_repo):
    r = TransactionLookupTool(tmp_repo).run("u1")
    assert r.success and all(x["user_id"] == "u1" for x in r.data["transactions"])


def test_transactions_missing_user(tmp_repo):
    assert not TransactionLookupTool(tmp_repo).run("u2").success


def test_payment_status_valid(tmp_repo):
    r = PaymentStatusTool(tmp_repo).run("u1")
    assert r.success and r.data["payments"][0]["status"] == "scheduled"


def test_payment_status_missing(tmp_repo):
    assert not PaymentStatusTool(tmp_repo).run("u2").success
