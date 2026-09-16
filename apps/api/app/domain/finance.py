from app.domain.models import FinancialProfileRequest, FinancialProfileSummary


def summarize_profile(profile: FinancialProfileRequest) -> FinancialProfileSummary:
    total_expenses = sum(item.amount for item in profile.expenses)
    free_cash = max(profile.monthly_income - total_expenses, 0)

    # Keep the first MVP conservative: no more than 20% of free cash and never from base expenses.
    safe_to_try_amount = min(profile.desired_investment_amount, free_cash * 0.2)

    notes: list[str] = []
    if profile.emergency_fund < total_expenses:
        notes.append("Финансовая подушка меньше одного месяца расходов.")
    if free_cash <= 0:
        status = "risk_blocked"
        notes.append("Сейчас нет свободных денег для инвестиционного эксперимента.")
    elif safe_to_try_amount < profile.desired_investment_amount:
        status = "cautious"
        notes.append("Желаемая сумма выше безопасного лимита для эксперимента.")
    else:
        status = "ready"
        notes.append("Сумма выглядит допустимой для учебной paper position.")

    return FinancialProfileSummary(
        monthly_income=profile.monthly_income,
        currency=profile.currency,
        total_expenses=total_expenses,
        free_cash=free_cash,
        safe_to_try_amount=round(safe_to_try_amount, 2),
        status=status,
        notes=notes,
    )

