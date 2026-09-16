package com.finai.mobile

data class MetricState(
    val label: String,
    val value: String,
    val accent: Boolean = false,
)

data class ScenarioState(
    val label: String,
    val value: String,
    val percent: String,
    val kind: ScenarioKind,
)

enum class ScenarioKind {
    Loss,
    Neutral,
    Gain,
}

data class AgentState(
    val role: String,
    val stance: String,
    val summary: String,
)

data class RadarState(
    val symbol: String,
    val action: String,
    val score: String,
    val watchItem: String,
)

data class MarketBriefState(
    val title: String,
    val body: String,
)

data class PortfolioState(
    val count: Int,
    val unrealized: String,
    val note: String,
)

data class FinaiDemoState(
    val freeCash: String,
    val safeToTry: String,
    val fxRate: String,
    val symbol: String,
    val exchange: String,
    val price: String,
    val dayChange: String,
    val actionTitle: String,
    val actionPrimary: String,
    val actionSecondary: String,
    val riskBadge: String,
    val action: String,
    val teacherNote: String,
    val reviewStatus: String,
    val reviewReturn: String,
    val reviewNote: String,
    val metrics: List<MetricState>,
    val scenarios: List<ScenarioState>,
    val agents: List<AgentState>,
    val radar: List<RadarState>,
    val monitor: List<MarketBriefState>,
    val portfolio: PortfolioState,
)

val demoState = FinaiDemoState(
    freeCash = "150 000 KZT",
    safeToTry = "30 000 KZT",
    fxRate = "USD/KZT 540.00",
    symbol = "KSPI",
    exchange = "NASDAQ / Kazakhstan-linked ADR",
    price = "\$121.40",
    dayChange = "+1.20%",
    actionTitle = "Сначала paper-наблюдение",
    actionPrimary = "Paper-watch",
    actionSecondary = "Review thesis",
    riskBadge = "elevated",
    action = "Открывать только учебную paper-position и уменьшить сумму до safe-to-try лимита.",
    teacherNote = "Инвестиционная идея становится учебным примером: бюджет, валюта, ликвидность и сценарии видны рядом.",
    reviewStatus = "on track",
    reviewReturn = "+0.00%",
    reviewNote = "Тезис пока внутри нормального учебного коридора.",
    metrics = listOf(
        MetricState("Свободно", "150 000 KZT"),
        MetricState("Safe-to-try", "30 000 KZT", accent = true),
        MetricState("FX", "540.00"),
    ),
    scenarios = listOf(
        ScenarioState("Stress", "\$49.40", "-50.60%", ScenarioKind.Loss),
        ScenarioState("Base", "\$105.20", "+5.20%", ScenarioKind.Neutral),
        ScenarioState("Strong", "\$144.30", "+44.30%", ScenarioKind.Gain),
    ),
    agents = listOf(
        AgentState("Risk Manager", "defensive", "Paper-only режим лучше реального входа, пока риск повышен."),
        AgentState("Teacher Agent", "explain", "Главная тема урока: валютный риск и границы личного бюджета."),
    ),
    radar = listOf(
        RadarState("KZTK", "small paper", "45.6", "liquidity gap"),
        RadarState("KSPI", "paper watch", "38.9", "FX volatility"),
    ),
    monitor = listOf(
        MarketBriefState("KSPI +1.2%", "Валютный риск KZT/USD важнее заголовка про рост акции."),
        MarketBriefState("KASE liquidity", "Локальные инструменты требуют проверки стакана и оборота перед реальной сделкой."),
    ),
    portfolio = PortfolioState(
        count = 0,
        unrealized = "+0.00%",
        note = "Paper portfolio only: no broker orders.",
    ),
)
