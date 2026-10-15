from src.statement_export import AccountStatement, WorkOrder, statement_markdown


def test_statement_total_and_follow_up_are_visible():
    statement = AccountStatement(
        "ACCT-9",
        "2026-08",
        [WorkOrder("WO-1", "2026-08-01", "Visit", 12500, 2, technician_follow_up="Call clinic")],
    )

    rendered = statement_markdown(statement)

    assert statement.total_cents == 12500
    assert "Call clinic" in rendered
    assert "**Total: $125.00**" in rendered
