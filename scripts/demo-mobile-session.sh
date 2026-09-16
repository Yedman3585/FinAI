#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000}"

curl -s -X POST "$API_BASE/api/mobile/session" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "KZTK",
    "provider": "demo_cis",
    "amount": 25000,
    "horizon_days": 30,
    "thesis": "Проверить локальную телеком идею как учебный paper-эксперимент.",
    "watchlist": ["KZTK", "KSPI", "AAPL"],
    "include_review": true,
    "profile": {
      "monthly_income": 500000,
      "currency": "KZT",
      "emergency_fund": 350000,
      "desired_investment_amount": 25000,
      "expenses": [
        {"name": "Rent", "amount": 180000, "category": "housing", "recurring": true},
        {"name": "Food", "amount": 120000, "category": "food", "recurring": true},
        {"name": "Transport", "amount": 35000, "category": "transport", "recurring": true}
      ]
    }
  }'
printf "\n"
