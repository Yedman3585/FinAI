package com.finai.mobile

import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.text.DecimalFormat
import kotlin.math.roundToInt

class FinaiApiClient(
    private val baseUrl: String,
) {
    fun loadMobileSession(
        symbol: String,
        provider: String,
        amount: Double,
        horizonDays: Int,
        thesis: String,
    ): FinaiDemoState {
        val connection = URL("${baseUrl.trimEnd('/')}/api/mobile/session").openConnection() as HttpURLConnection
        connection.requestMethod = "POST"
        connection.connectTimeout = 8000
        connection.readTimeout = 12000
        connection.setRequestProperty("Content-Type", "application/json")
        connection.doOutput = true

        OutputStreamWriter(connection.outputStream).use { writer ->
            writer.write(buildRequest(symbol, provider, amount, horizonDays, thesis).toString())
        }

        val status = connection.responseCode
        val stream = if (status in 200..299) connection.inputStream else connection.errorStream
        val body = BufferedReader(InputStreamReader(stream)).use { it.readText() }
        connection.disconnect()

        if (status !in 200..299) {
            throw IllegalStateException(body.ifBlank { "API error $status" })
        }

        return parseSession(JSONObject(body))
    }

    private fun buildRequest(
        symbol: String,
        provider: String,
        amount: Double,
        horizonDays: Int,
        thesis: String,
    ): JSONObject {
        return JSONObject()
            .put("symbol", symbol)
            .put("provider", provider)
            .put("amount", amount)
            .put("horizon_days", horizonDays)
            .put("thesis", thesis)
            .put("watchlist", JSONArray(listOf(symbol, "KSPI", "KZTK", "AAPL")))
            .put("include_review", true)
            .put(
                "profile",
                JSONObject()
                    .put("monthly_income", 500000)
                    .put("currency", "KZT")
                    .put("emergency_fund", 350000)
                    .put("desired_investment_amount", amount)
                    .put(
                        "expenses",
                        JSONArray(
                            listOf(
                                expense("Rent", 180000, "housing"),
                                expense("Food", 120000, "food"),
                                expense("Transport", 35000, "transport"),
                            ),
                        ),
                    ),
            )
    }

    private fun expense(name: String, amount: Int, category: String): JSONObject {
        return JSONObject()
            .put("name", name)
            .put("amount", amount)
            .put("category", category)
            .put("recurring", true)
    }

    private fun parseSession(root: JSONObject): FinaiDemoState {
        val profile = root.getJSONObject("profile_summary")
        val market = root.getJSONObject("market")
        val actionState = root.getJSONObject("action_state")
        val analysis = root.getJSONObject("analysis")
        val memo = analysis.getJSONObject("memo")
        val review = root.optJSONObject("review")
        val fx = root.optJSONObject("fx_rate")
        val scenarios = parseScenarios(root.getJSONArray("scenarios"), market.optString("currency", "KZT"))
        val agents = parseAgents(analysis.getJSONArray("agents"))
        val radar = parseRadar(root.getJSONObject("radar").getJSONArray("candidates"))
        val monitor = parseMonitor(root.getJSONObject("market_brief").getJSONArray("items"))
        val portfolio = root.getJSONObject("portfolio")

        val fxValue = fx?.optDouble("rate")?.let { amount(it) } ?: "1.00"
        val currency = market.optString("currency", "KZT")
        val price = "${market.optDouble("last_price").formatPrice()} $currency"

        return FinaiDemoState(
            freeCash = moneyKzt(profile.optDouble("free_cash")),
            safeToTry = moneyKzt(profile.optDouble("safe_to_try_amount")),
            fxRate = "${currency}/KZT $fxValue",
            symbol = market.optString("symbol"),
            exchange = market.optString("exchange"),
            price = price,
            dayChange = percent(market.optDouble("day_change_percent")),
            actionTitle = actionState.optString("title"),
            actionPrimary = actionState.optString("primary_label"),
            actionSecondary = actionState.optString("secondary_label"),
            riskBadge = actionState.optString("risk_badge"),
            action = actionState.optString("message", memo.optString("position_size_hint")),
            teacherNote = analysis.optString("teacher_note"),
            reviewStatus = review?.optString("thesis_status")?.replace("_", " ") ?: "not reviewed",
            reviewReturn = percent(review?.optDouble("return_percent") ?: 0.0),
            reviewNote = review?.optString("verdict") ?: "Review появится после live ответа.",
            metrics = listOf(
                MetricState("Свободно", moneyKzt(profile.optDouble("free_cash"))),
                MetricState("Safe-to-try", moneyKzt(profile.optDouble("safe_to_try_amount")), accent = true),
                MetricState("FX", fxValue),
            ),
            scenarios = scenarios,
            agents = agents,
            radar = radar,
            monitor = monitor,
            portfolio = PortfolioState(
                count = portfolio.getJSONArray("positions").length(),
                unrealized = percent(portfolio.optDouble("weighted_unrealized_percent")),
                note = portfolio.optString("note"),
            ),
        )
    }

    private fun parseScenarios(items: JSONArray, currency: String): List<ScenarioState> {
        val result = mutableListOf<ScenarioState>()
        for (index in 0 until items.length()) {
            val item = items.getJSONObject(index)
            val outcome = item.optDouble("outcome_percent")
            if (item.optString("label") in setOf("Stress", "Base gain", "Strong")) {
                result.add(
                    ScenarioState(
                        label = item.optString("label").replace("Base gain", "Base"),
                        value = "${item.optDouble("projected_value").formatPrice()} $currency",
                        percent = percent(outcome),
                        kind = when {
                            outcome < -1 -> ScenarioKind.Loss
                            outcome > 8 -> ScenarioKind.Gain
                            else -> ScenarioKind.Neutral
                        },
                    ),
                )
            }
        }
        return result.ifEmpty { demoState.scenarios }
    }

    private fun parseAgents(items: JSONArray): List<AgentState> {
        val result = mutableListOf<AgentState>()
        for (index in 0 until items.length()) {
            val item = items.getJSONObject(index)
            val role = item.optString("role")
            if (role in setOf("Risk Manager", "Teacher Agent", "Portfolio Manager", "Pro Opportunity Scout")) {
                result.add(
                    AgentState(
                        role = role,
                        stance = item.optString("stance"),
                        summary = item.optString("summary"),
                    ),
                )
            }
        }
        return result.ifEmpty { demoState.agents }
    }

    private fun parseRadar(items: JSONArray): List<RadarState> {
        val result = mutableListOf<RadarState>()
        for (index in 0 until items.length()) {
            val item = items.getJSONObject(index)
            result.add(
                RadarState(
                    symbol = item.optString("symbol"),
                    action = item.optString("action").replace("_", " "),
                    score = amount(item.optDouble("rank_score")),
                    watchItem = item.optString("top_watch_item"),
                ),
            )
        }
        return result.ifEmpty { demoState.radar }
    }

    private fun parseMonitor(items: JSONArray): List<MarketBriefState> {
        val result = mutableListOf<MarketBriefState>()
        for (index in 0 until items.length()) {
            val item = items.getJSONObject(index)
            result.add(
                MarketBriefState(
                    title = item.optString("title"),
                    body = item.optString("body"),
                ),
            )
        }
        return result.ifEmpty { demoState.monitor }
    }

    private fun moneyKzt(value: Double): String = "${value.roundToInt()} KZT"

    private fun percent(value: Double): String {
        val sign = if (value > 0) "+" else ""
        return "$sign${amount(value)}%"
    }

    private fun Double.formatPrice(): String = amount(this)

    private fun amount(value: Double): String = DecimalFormat("#,##0.##").format(value)
}
