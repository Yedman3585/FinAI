#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000}"
PYTHON_BIN="${PYTHON_BIN:-apps/api/.venv/bin/python}"

PROFILE='{
  "monthly_income": 500000,
  "currency": "KZT",
  "emergency_fund": 350000,
  "desired_investment_amount": 25000,
  "expenses": [
    {"name": "Rent", "amount": 180000, "category": "housing", "recurring": true},
    {"name": "Food", "amount": 120000, "category": "food", "recurring": true},
    {"name": "Transport", "amount": 35000, "category": "transport", "recurring": true}
  ]
}'

curl -s "$API_BASE/api/agents/engines"
printf "\n\n"

curl -s "$API_BASE/api/agents/mandates"
printf "\n\n"

ANALYSIS_JSON=$(curl -s -X POST "$API_BASE/api/agents/deep-analysis" \
  -H "Content-Type: application/json" \
  -d "{
    \"symbol\": \"KZTK\",
    \"provider\": \"demo_cis\",
    \"amount\": 25000,
    \"horizon_days\": 30,
    \"pro_mode\": true,
    \"thesis\": \"Хочу проверить локальную телеком идею как учебный эксперимент.\",
    \"profile\": $PROFILE
  }")
printf "%s" "$ANALYSIS_JSON"
RUN_ID=$(printf "%s" "$ANALYSIS_JSON" | "$PYTHON_BIN" -c 'import json, sys; print(json.load(sys.stdin)["id"])')
printf "\n\n"

curl -s "$API_BASE/api/agents/runs/$RUN_ID/review"
printf "\n\n"

curl -s -X POST "$API_BASE/api/agents/opportunity-radar" \
  -H "Content-Type: application/json" \
  -d "{
    \"provider\": \"demo_cis\",
    \"symbols\": [\"KSPI\", \"KZTK\", \"AAPL\"],
    \"amount\": 25000,
    \"horizon_days\": 30,
    \"max_results\": 3,
    \"profile\": $PROFILE
  }"
printf "\n"
