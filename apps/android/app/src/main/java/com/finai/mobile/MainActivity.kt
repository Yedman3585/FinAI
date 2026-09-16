package com.finai.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private enum class AppTab {
    Idea,
    Agents,
    Monitor,
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            FinaiApp()
        }
    }
}

@Composable
private fun FinaiApp() {
    var state by remember { mutableStateOf(demoState) }
    var apiBase by remember { mutableStateOf("http://10.0.2.2:8000") }
    var symbol by remember { mutableStateOf("KZTK") }
    var provider by remember { mutableStateOf("demo_cis") }
    var amount by remember { mutableStateOf("25000") }
    var horizon by remember { mutableStateOf("30") }
    var thesis by remember { mutableStateOf("Проверить локальную телеком идею как учебный paper-эксперимент.") }
    var selectedTab by remember { mutableStateOf(AppTab.Idea) }
    var loading by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("Demo mode: можно открыть приложение без backend.") }
    val context = LocalContext.current

    fun loadSession() {
        loading = true
        status = "Запрашиваю mobile-session backend..."
        Thread {
            try {
                val result = FinaiApiClient(apiBase).loadMobileSession(
                    symbol = symbol,
                    provider = provider,
                    amount = amount.toDoubleOrNull() ?: 25_000.0,
                    horizonDays = horizon.toIntOrNull() ?: 30,
                    thesis = thesis,
                )
                (context as ComponentActivity).runOnUiThread {
                    state = result
                    status = "Live API: ${result.symbol}, ${result.actionPrimary}."
                    selectedTab = AppTab.Agents
                    loading = false
                }
            } catch (error: Exception) {
                (context as ComponentActivity).runOnUiThread {
                    status = "Fallback: ${error.message ?: "backend недоступен"}"
                    loading = false
                }
            }
        }.start()
    }

    MaterialTheme {
        Surface(color = Color(0xFFDFE7DF)) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Header(state, status)
                Metrics(state.metrics)
                ControlPanel(
                    apiBase = apiBase,
                    amount = amount,
                    horizon = horizon,
                    loading = loading,
                    onAmountChange = { amount = it },
                    onApiBaseChange = { apiBase = it },
                    onHorizonChange = { horizon = it },
                    onProviderChange = { provider = it },
                    onRefresh = { loadSession() },
                    onSymbolChange = { symbol = it },
                    onThesisChange = { thesis = it },
                    provider = provider,
                    symbol = symbol,
                    thesis = thesis,
                )
                TabBar(selectedTab) { selectedTab = it }
                when (selectedTab) {
                    AppTab.Idea -> IdeaTab(state)
                    AppTab.Agents -> AgentsTab(state, onReview = { loadSession() }, loading = loading)
                    AppTab.Monitor -> MonitorTab(state)
                }
            }
        }
    }
}

@Composable
private fun Header(state: FinaiDemoState, status: String) {
    Column(verticalArrangement = Arrangement.spacedBy(7.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "FInAI",
                color = Color(0xFF115C44),
                fontSize = 15.sp,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = state.riskBadge.ifBlank { "demo" },
                color = Color(0xFF115C44),
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
            )
        }
        Text(
            text = "${state.safeToTry} можно безопасно тестировать",
            color = Color(0xFF111714),
            fontSize = 28.sp,
            lineHeight = 31.sp,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = status,
            color = Color(0xFF4D5752),
            fontSize = 14.sp,
            lineHeight = 20.sp,
        )
    }
}

@Composable
private fun Metrics(metrics: List<MetricState>) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            MetricBox(metrics[0], Modifier.weight(1f))
            MetricBox(metrics[1], Modifier.weight(1f))
        }
        MetricBox(metrics[2], Modifier.fillMaxWidth())
    }
}

@Composable
private fun MetricBox(metric: MetricState, modifier: Modifier) {
    val borderColor = if (metric.accent) Color(0xFFF2BD63) else Color(0xFFD7DFD6)
    val textColor = if (metric.accent) Color(0xFFB55B21) else Color(0xFF111714)
    Column(
        modifier = modifier
            .background(if (metric.accent) Color(0xFFFFF3E1) else Color.White)
            .border(1.dp, borderColor, RoundedCornerShape(7.dp))
            .padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Text(metric.label, color = Color(0xFF626C66), fontSize = 13.sp)
        Text(metric.value, color = textColor, fontSize = 19.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun ControlPanel(
    apiBase: String,
    amount: String,
    horizon: String,
    loading: Boolean,
    onAmountChange: (String) -> Unit,
    onApiBaseChange: (String) -> Unit,
    onHorizonChange: (String) -> Unit,
    onProviderChange: (String) -> Unit,
    onRefresh: () -> Unit,
    onSymbolChange: (String) -> Unit,
    onThesisChange: (String) -> Unit,
    provider: String,
    symbol: String,
    thesis: String,
) {
    Panel(background = Color(0xFF11241D), border = Color(0xFF11241D)) {
        Text("Backend", color = Color(0xFFB8C9BF), fontSize = 13.sp, fontWeight = FontWeight.Bold)
        OutlinedTextField(
            value = apiBase,
            onValueChange = onApiBaseChange,
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            label = { Text("API URL") },
        )
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            OutlinedTextField(
                value = symbol,
                onValueChange = onSymbolChange,
                modifier = Modifier.weight(1f),
                singleLine = true,
                label = { Text("Ticker") },
            )
            OutlinedTextField(
                value = provider,
                onValueChange = onProviderChange,
                modifier = Modifier.weight(1f),
                singleLine = true,
                label = { Text("Provider") },
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            OutlinedTextField(
                value = amount,
                onValueChange = onAmountChange,
                modifier = Modifier.weight(1f),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                label = { Text("Amount") },
            )
            OutlinedTextField(
                value = horizon,
                onValueChange = onHorizonChange,
                modifier = Modifier.weight(1f),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                label = { Text("Days") },
            )
        }
        OutlinedTextField(
            value = thesis,
            onValueChange = onThesisChange,
            modifier = Modifier.fillMaxWidth(),
            minLines = 2,
            label = { Text("Thesis") },
        )
        Button(
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFF05A38)),
            enabled = !loading,
            modifier = Modifier.fillMaxWidth(),
            onClick = onRefresh,
        ) {
            Text(if (loading) "Считаю..." else "Анализ")
        }
    }
}

@Composable
private fun TabBar(selected: AppTab, onSelect: (AppTab) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFFECF0EA), RoundedCornerShape(7.dp))
            .border(1.dp, Color(0xFFD5DED4), RoundedCornerShape(7.dp))
            .padding(4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        TabButton("Идея", AppTab.Idea, selected, onSelect, Modifier.weight(1f))
        TabButton("Агенты", AppTab.Agents, selected, onSelect, Modifier.weight(1f))
        TabButton("Монитор", AppTab.Monitor, selected, onSelect, Modifier.weight(1f))
    }
}

@Composable
private fun TabButton(
    label: String,
    tab: AppTab,
    selected: AppTab,
    onSelect: (AppTab) -> Unit,
    modifier: Modifier,
) {
    TextButton(
        modifier = modifier.background(
            if (tab == selected) Color.White else Color.Transparent,
            RoundedCornerShape(6.dp),
        ),
        onClick = { onSelect(tab) },
    ) {
        Text(label, color = Color(0xFF111714), fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun IdeaTab(state: FinaiDemoState) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        MarketPanel(state)
        ScenarioPanel(state.scenarios)
        ActionPanel(state)
    }
}

@Composable
private fun MarketPanel(state: FinaiDemoState) {
    Panel {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(modifier = Modifier.weight(1f)) {
                Text(state.exchange, color = Color(0xFF626C66), fontSize = 13.sp)
                Text(state.symbol, color = Color(0xFF111714), fontSize = 38.sp, fontWeight = FontWeight.Bold)
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(state.price, color = Color(0xFF111714), fontSize = 25.sp, fontWeight = FontWeight.Bold)
                Text(
                    state.dayChange,
                    color = if (state.dayChange.startsWith("-")) Color(0xFFC9362A) else Color(0xFF0C7C59),
                    fontSize = 16.sp,
                )
            }
        }
    }
}

@Composable
private fun ScenarioPanel(scenarios: List<ScenarioState>) {
    Panel {
        Text("Сценарии", color = Color(0xFF111714), fontSize = 20.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(2.dp))
        scenarios.forEach { scenario ->
            ScenarioRow(scenario)
        }
    }
}

@Composable
private fun ScenarioRow(scenario: ScenarioState) {
    val color = when (scenario.kind) {
        ScenarioKind.Loss -> Color(0xFFC9362A)
        ScenarioKind.Neutral -> Color(0xFF2F68A6)
        ScenarioKind.Gain -> Color(0xFF0C7C59)
    }
    val width = when (scenario.kind) {
        ScenarioKind.Loss -> 82.dp
        ScenarioKind.Neutral -> 118.dp
        ScenarioKind.Gain -> 148.dp
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.width(82.dp)) {
            Text(scenario.label, color = Color(0xFF626C66), fontSize = 14.sp)
            Text(scenario.percent, color = color, fontSize = 14.sp, fontWeight = FontWeight.Bold)
        }
        Bar(width, color)
        Text(
            scenario.value,
            modifier = Modifier.weight(1f),
            color = color,
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}

@Composable
private fun Bar(width: Dp, color: Color) {
    Box(
        modifier = Modifier
            .width(160.dp)
            .height(8.dp)
            .background(Color(0xFFE7ECE5), RoundedCornerShape(6.dp)),
    ) {
        Box(
            modifier = Modifier
                .width(width)
                .height(8.dp)
                .background(color, RoundedCornerShape(6.dp)),
        )
    }
    Spacer(modifier = Modifier.width(10.dp))
}

@Composable
private fun ActionPanel(state: FinaiDemoState) {
    Panel(background = Color(0xFFFFF3E1), border = Color(0xFFF2BD63)) {
        Text(state.actionTitle, color = Color(0xFFB55B21), fontSize = 18.sp, fontWeight = FontWeight.Bold)
        Text(state.action, color = Color(0xFF111714), fontSize = 16.sp, lineHeight = 22.sp)
        Text(state.teacherNote, color = Color(0xFF4D5752), fontSize = 15.sp, lineHeight = 21.sp)
    }
}

@Composable
private fun AgentsTab(state: FinaiDemoState, onReview: () -> Unit, loading: Boolean) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Panel(background = Color(0xFFF2F8F6), border = Color(0xFFBDD7CA)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Column {
                    Text("Review", color = Color(0xFF626C66), fontSize = 13.sp)
                    Text(state.reviewStatus, color = Color(0xFF115C44), fontSize = 22.sp, fontWeight = FontWeight.Bold)
                }
                Column(horizontalAlignment = Alignment.End) {
                    Text("Return", color = Color(0xFF626C66), fontSize = 13.sp)
                    Text(state.reviewReturn, color = Color(0xFF0C7C59), fontSize = 22.sp, fontWeight = FontWeight.Bold)
                }
            }
            Text(state.reviewNote, color = Color(0xFF4D5752), fontSize = 15.sp, lineHeight = 21.sp)
            Button(
                enabled = !loading,
                modifier = Modifier.fillMaxWidth(),
                onClick = onReview,
            ) {
                Text(if (loading) "Проверяю..." else state.actionSecondary)
            }
        }

        state.agents.forEach { agent ->
            Panel {
                Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                    Text(agent.role, color = Color(0xFF111714), fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    Text(agent.stance, color = Color(0xFF115C44), fontSize = 13.sp, fontWeight = FontWeight.Bold)
                }
                Text(agent.summary, color = Color(0xFF4D5752), fontSize = 15.sp, lineHeight = 21.sp)
            }
        }

        Panel {
            Text("Opportunity radar", color = Color(0xFF111714), fontSize = 20.sp, fontWeight = FontWeight.Bold)
            state.radar.forEachIndexed { index, item ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text("${index + 1}", color = Color(0xFF115C44), fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.width(12.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(item.symbol, color = Color(0xFF111714), fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        Text("${item.action} · ${item.watchItem}", color = Color(0xFF626C66), fontSize = 13.sp)
                    }
                    Text(item.score, color = Color(0xFF115C44), fontSize = 16.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun MonitorTab(state: FinaiDemoState) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Panel {
            Text("Paper portfolio", color = Color(0xFF111714), fontSize = 20.sp, fontWeight = FontWeight.Bold)
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text("${state.portfolio.count} positions", color = Color(0xFF626C66), fontSize = 15.sp)
                Text(state.portfolio.unrealized, color = Color(0xFF0C7C59), fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
            Text(state.portfolio.note, color = Color(0xFF4D5752), fontSize = 14.sp, lineHeight = 20.sp)
        }
        MarketMonitor(state.monitor)
    }
}

@Composable
private fun MarketMonitor(items: List<MarketBriefState>) {
    Panel {
        Text("Market monitor", color = Color(0xFF111714), fontSize = 20.sp, fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(2.dp))
        items.forEach { item ->
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, Color(0xFFD7DFD6), RoundedCornerShape(7.dp))
                    .padding(12.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Text(item.title, color = Color(0xFF111714), fontSize = 15.sp, fontWeight = FontWeight.Bold)
                Text(item.body, color = Color(0xFF626C66), fontSize = 14.sp, lineHeight = 19.sp)
            }
            Spacer(modifier = Modifier.height(8.dp))
        }
    }
}

@Composable
private fun Panel(
    background: Color = Color.White,
    border: Color = Color(0xFFD7DFD6),
    content: @Composable Column.() -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(background, RoundedCornerShape(7.dp))
            .border(1.dp, border, RoundedCornerShape(7.dp))
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        content = content,
    )
}
