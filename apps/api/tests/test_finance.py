from app.domain.finance import summarize_profile
from app.domain.models import Currency, ExpenseItem, FinancialProfileRequest


def test_safe_to_try_amount_is_conservative() -> None:
    profile = FinancialProfileRequest(
        monthly_income=500_000,
        currency=Currency.KZT,
        emergency_fund=300_000,
        desired_investment_amount=100_000,
        expenses=[
            ExpenseItem(name="Rent", amount=180_000, category="housing"),
            ExpenseItem(name="Food", amount=120_000, category="food"),
        ],
    )

    summary = summarize_profile(profile)

    assert summary.free_cash == 200_000
    assert summary.safe_to_try_amount == 40_000
    assert summary.status == "cautious"

