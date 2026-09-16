package com.finai.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AccountBalanceWallet
import androidx.compose.material.icons.rounded.Add
import androidx.compose.material.icons.rounded.Article
import androidx.compose.material.icons.rounded.AutoAwesome
import androidx.compose.material.icons.rounded.Bookmark
import androidx.compose.material.icons.rounded.BookmarkBorder
import androidx.compose.material.icons.rounded.Bolt
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.CloudDone
import androidx.compose.material.icons.rounded.Home
import androidx.compose.material.icons.rounded.Info
import androidx.compose.material.icons.rounded.MenuBook
import androidx.compose.material.icons.rounded.MoreHoriz
import androidx.compose.material.icons.rounded.NotificationsNone
import androidx.compose.material.icons.rounded.Person
import androidx.compose.material.icons.rounded.School
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.Send
import androidx.compose.material.icons.rounded.Settings
import androidx.compose.material.icons.rounded.Shield
import androidx.compose.material.icons.rounded.ShowChart
import androidx.compose.material.icons.rounded.Timeline
import androidx.compose.material.icons.rounded.Visibility
import androidx.compose.material3.AssistChip
import androidx.compose.material3.AssistChipDefaults
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat

private enum class AppSection(val label: String, val icon: ImageVector) {
    Home("Home", Icons.Rounded.Home),
    Notes("Notes", Icons.Rounded.Article),
    Market("Market", Icons.Rounded.ShowChart),
    Learn("Learn", Icons.Rounded.MenuBook),
    Profile("Profile", Icons.Rounded.Person),
}

private data class NewsItem(
    val id: Int,
    val source: String,
    val age: String,
    val title: String,
    val summary: String,
    val impact: String,
    val positive: Boolean,
)

private data class Lesson(val title: String, val topic: String, val minutes: Int, val progress: Float)

private val newsFeed = listOf(
    NewsItem(1, "National Bank", "18 min", "Rate guidance keeps tenge risk in focus", "The signal matters more for your USD exposure than for today's index move.", "FX exposure", false),
    NewsItem(2, "KASE", "42 min", "Telecom turnover rises above its 20-day median", "Liquidity improved, but the spread can still erase a small position's expected edge.", "KZTK watch", true),
    NewsItem(3, "MOEX", "1 h", "Energy names lead the morning session", "The move is broad, although oil sensitivity makes the basket less diversified than it looks.", "Sector crowding", true),
    NewsItem(4, "Global markets", "2 h", "US futures trade flat before inflation data", "A quiet tape before macro data is not a low-risk signal. Volatility can arrive after release.", "Event risk", false),
)

private val learningPath = listOf(
    Lesson("Why safe-to-try is not spare cash", "Personal risk", 6, 0.72f),
    Lesson("FX can rewrite your stock return", "Currencies", 8, 0.34f),
    Lesson("Liquidity before valuation", "Execution", 5, 0.0f),
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.statusBarColor = android.graphics.Color.rgb(11, 14, 12)
        window.navigationBarColor = android.graphics.Color.rgb(14, 18, 15)
        WindowCompat.getInsetsController(window, window.decorView).apply {
            isAppearanceLightStatusBars = false
            isAppearanceLightNavigationBars = false
        }
        setContent { FinaiApp() }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun FinaiApp() {
    var state by remember { mutableStateOf(demoState) }
    var selected by rememberSaveable { mutableStateOf(AppSection.Home) }
    var proMode by rememberSaveable { mutableStateOf(false) }
    var agentOpen by remember { mutableStateOf(false) }
    var agentContext by remember { mutableStateOf("today's portfolio") }
    var apiBase by rememberSaveable { mutableStateOf("http://10.0.2.2:8000") }
    var symbol by rememberSaveable { mutableStateOf("KSPI") }
    var provider by rememberSaveable { mutableStateOf("demo_cis") }
    var amount by rememberSaveable { mutableStateOf("25000") }
    var horizon by rememberSaveable { mutableStateOf("30") }
    var thesis by rememberSaveable { mutableStateOf("Check this idea as a controlled paper experiment within my safe-to-try limit.") }
    var loading by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("Demo data · connect API when ready") }
    val context = LocalContext.current

    fun askMolly(contextText: String) {
        agentContext = contextText
        agentOpen = true
    }

    fun loadSession() {
        loading = true
        status = "MOLOX is testing the thesis..."
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
                    status = "Live analysis · ${result.actionPrimary}"
                    selected = AppSection.Market
                    loading = false
                }
            } catch (error: Exception) {
                (context as ComponentActivity).runOnUiThread {
                    status = "Offline demo · ${error.message ?: "API unavailable"}"
                    loading = false
                }
            }
        }.start()
    }

    FinaiTheme {
        Scaffold(
            containerColor = Canvas,
            bottomBar = { FinaiBottomBar(selected) { selected = it } },
            floatingActionButton = { MollyButton { askMolly(selected.label) } },
        ) { innerPadding ->
            Box(Modifier.fillMaxSize().padding(innerPadding)) {
                when (selected) {
                    AppSection.Home -> HomeScreen(state, status, proMode, { proMode = it }, { selected = AppSection.Market }, { selected = AppSection.Notes }, ::askMolly)
                    AppSection.Notes -> NotesScreen(::askMolly)
                    AppSection.Market -> MarketScreen(
                        state, proMode, symbol, provider, amount, horizon, thesis, loading,
                        { symbol = it }, { provider = it }, { amount = it }, { horizon = it }, { thesis = it },
                        ::loadSession, ::askMolly,
                    )
                    AppSection.Learn -> LearnScreen(state, ::askMolly)
                    AppSection.Profile -> ProfileScreen(state, apiBase, { apiBase = it }, proMode, { proMode = it })
                }
            }
        }
        if (agentOpen) {
            MollySheet(agentContext, state, proMode, { agentOpen = false }) {
                agentOpen = false
                selected = AppSection.Learn
            }
        }
    }
}

@Composable
private fun FinaiBottomBar(selected: AppSection, onSelect: (AppSection) -> Unit) {
    NavigationBar(
        modifier = Modifier.navigationBarsPadding(),
        containerColor = Color(0xFF0E120F),
        tonalElevation = 0.dp,
    ) {
        AppSection.entries.forEach { section ->
            NavigationBarItem(
                selected = selected == section,
                onClick = { onSelect(section) },
                icon = { Icon(section.icon, contentDescription = section.label) },
                label = { Text(section.label, fontSize = 11.sp) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Acid,
                    selectedTextColor = Acid,
                    indicatorColor = SurfaceHigh,
                    unselectedIconColor = Muted,
                    unselectedTextColor = Muted,
                ),
            )
        }
    }
}

@Composable
private fun MollyButton(onClick: () -> Unit) {
    var dragOffset by remember { mutableStateOf(Offset.Zero) }
    FloatingActionButton(
        onClick = onClick,
        modifier = Modifier
            .graphicsLayer { translationX = dragOffset.x; translationY = dragOffset.y }
            .pointerInput(Unit) {
                detectDragGestures { _, dragAmount -> dragOffset += dragAmount }
            },
        shape = CircleShape,
        containerColor = Acid.copy(alpha = 0.90f),
        contentColor = Color(0xFF102000),
    ) { Icon(Icons.Rounded.AutoAwesome, contentDescription = "Ask Molly") }
}

@Composable
private fun ScreenHeader(eyebrow: String, title: String, action: ImageVector? = null, onAction: (() -> Unit)? = null) {
    Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.CenterVertically) {
        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(eyebrow.uppercase(), color = Acid, fontSize = 11.sp, fontWeight = FontWeight.Bold)
            Text(title, color = Ink, fontSize = 30.sp, fontWeight = FontWeight.SemiBold)
        }
        if (action != null && onAction != null) {
            IconButton(onClick = onAction) { Icon(action, contentDescription = null, tint = Ink) }
        }
    }
}

@Composable
private fun HomeScreen(
    state: FinaiDemoState,
    status: String,
    proMode: Boolean,
    onModeChange: (Boolean) -> Unit,
    onAnalyze: () -> Unit,
    onOpenNews: () -> Unit,
    onAsk: (String) -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize().statusBarsPadding(),
        contentPadding = PaddingValues(18.dp, 16.dp, 18.dp, 104.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            ScreenHeader(
                if (proMode) "MOLOX intelligence" else "Good evening",
                if (proMode) "Command center" else "Your money, in context",
                Icons.Rounded.NotificationsNone,
                onOpenNews,
            )
        }
        item { ModeSwitch(proMode, onModeChange) }
        item { CapitalHero(state, proMode, status, onAnalyze) }
        item {
            SectionTitle("Today", "3 priorities")
            PriorityRow(Icons.Rounded.Shield, SignalGold, "Keep the experiment small", "${state.safeToTry} is the current safe-to-try ceiling.") { onAsk("safe-to-try limit") }
            PriorityRow(Icons.Rounded.ShowChart, SignalBlue, "${state.symbol} · ${state.dayChange}", state.actionTitle, onAnalyze)
            PriorityRow(Icons.Rounded.School, Acid, "Learn from this position", state.teacherNote) { onAsk("today's learning point") }
        }
        if (proMode) item { ProRadar(state) } else item { DailyLessonCard(state, onAsk) }
        item { MarketPulse(newsFeed.take(2), onOpenNews, onAsk) }
    }
}

@Composable
private fun ModeSwitch(proMode: Boolean, onModeChange: (Boolean) -> Unit) {
    Row(
        Modifier.fillMaxWidth().background(SurfaceLow, RoundedCornerShape(8.dp)).border(1.dp, Hairline, RoundedCornerShape(8.dp)).padding(4.dp),
    ) {
        ModeOption("Personal", !proMode, Modifier.weight(1f)) { onModeChange(false) }
        ModeOption("MOLOX Pro", proMode, Modifier.weight(1f)) { onModeChange(true) }
    }
}

@Composable
private fun ModeOption(label: String, selected: Boolean, modifier: Modifier, onClick: () -> Unit) {
    Box(
        modifier.clip(RoundedCornerShape(6.dp)).background(if (selected) SurfaceHigh else Color.Transparent).clickable(onClick = onClick).padding(vertical = 10.dp),
        contentAlignment = Alignment.Center,
    ) { Text(label, color = if (selected) Ink else Muted, fontSize = 13.sp, fontWeight = FontWeight.Bold) }
}

@Composable
private fun CapitalHero(state: FinaiDemoState, proMode: Boolean, status: String, onAnalyze: () -> Unit) {
    FinCard(Color(0xFF171D18), Color(0xFF384331)) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.Top) {
            Column {
                Text(if (proMode) "CAPITAL IN SCOPE" else "AVAILABLE TO INVEST", color = Muted, fontSize = 11.sp)
                Text(state.freeCash, color = Ink, fontSize = 30.sp, fontWeight = FontWeight.Bold)
            }
            StatusDot(if (status.startsWith("Live")) "LIVE" else "DEMO")
        }
        HorizontalDivider(color = Hairline)
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            MiniMetric("SAFE-TO-TRY", state.safeToTry, SignalGold)
            MiniMetric("FX", state.fxRate.substringAfter(" "), SignalBlue)
            MiniMetric("RISK", state.riskBadge.uppercase(), SignalRed)
        }
        Button(
            onClick = onAnalyze,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Acid, contentColor = Color(0xFF102000)),
            shape = RoundedCornerShape(7.dp),
        ) {
            Icon(Icons.Rounded.Bolt, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text("Test an investment idea", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun MiniMetric(label: String, value: String, color: Color) {
    Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
        Text(label, color = Muted, fontSize = 10.sp)
        Text(value, color = color, fontSize = 13.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun StatusDot(label: String) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        Box(Modifier.size(7.dp).background(Acid, CircleShape))
        Text(label, color = Acid, fontSize = 10.sp, fontWeight = FontWeight.Bold)
    }
}

@Composable
private fun SectionTitle(title: String, meta: String? = null) {
    Row(
        Modifier.fillMaxWidth().padding(top = 4.dp, bottom = 2.dp),
        Arrangement.SpaceBetween,
        Alignment.CenterVertically,
    ) {
        Text(title, color = Ink, fontSize = 19.sp, fontWeight = FontWeight.SemiBold)
        if (meta != null) Text(meta, color = Muted, fontSize = 12.sp)
    }
}

@Composable
private fun PriorityRow(icon: ImageVector, color: Color, title: String, body: String, onClick: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().clickable(onClick = onClick).padding(vertical = 11.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Box(Modifier.size(42.dp).background(color.copy(alpha = 0.14f), RoundedCornerShape(7.dp)), contentAlignment = Alignment.Center) {
            Icon(icon, contentDescription = null, tint = color)
        }
        Column(Modifier.weight(1f)) {
            Text(title, color = Ink, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            Text(body, color = Muted, fontSize = 13.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
        }
        Icon(Icons.Rounded.ChevronRight, contentDescription = null, tint = Muted)
    }
}

@Composable
private fun DailyLessonCard(state: FinaiDemoState, onAsk: (String) -> Unit) {
    FinCard(Color(0xFF151A20), Color(0xFF27384E)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(Icons.Rounded.School, contentDescription = null, tint = SignalBlue)
            Text("MOLLY'S 5-MINUTE LESSON", color = SignalBlue, fontSize = 11.sp, fontWeight = FontWeight.Bold)
        }
        Text("Currency risk can cancel a good stock call", color = Ink, fontSize = 20.sp, fontWeight = FontWeight.SemiBold)
        Text(state.teacherNote, color = Muted, fontSize = 14.sp, lineHeight = 20.sp)
        TextButton(onClick = { onAsk("currency risk lesson") }, contentPadding = PaddingValues(0.dp)) {
            Text("Open with Molly", color = SignalBlue)
            Icon(Icons.Rounded.ChevronRight, contentDescription = null, tint = SignalBlue)
        }
    }
}

@Composable
private fun ProRadar(state: FinaiDemoState) {
    FinCard(Color(0xFF1B1811), Color(0xFF4B3B22)) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Column {
                Text("MOLOX SIGNAL MAP", color = SignalGold, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text("Opportunity radar", color = Ink, fontSize = 20.sp, fontWeight = FontWeight.SemiBold)
            }
            Icon(Icons.Rounded.Timeline, contentDescription = null, tint = SignalGold)
        }
        state.radar.take(3).forEachIndexed { index, item ->
            Row(Modifier.fillMaxWidth().padding(vertical = 7.dp), verticalAlignment = Alignment.CenterVertically) {
                Text("0${index + 1}", color = Muted, fontSize = 12.sp, modifier = Modifier.width(28.dp))
                Column(Modifier.weight(1f)) {
                    Text(item.symbol, color = Ink, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                    Text(item.watchItem, color = Muted, fontSize = 12.sp)
                }
                Text(item.score, color = SignalGold, fontSize = 14.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun MarketPulse(items: List<NewsItem>, onOpenNews: () -> Unit, onAsk: (String) -> Unit) {
    SectionTitle("Market pulse", "Live context")
    items.forEach { item -> CompactNews(item) { onAsk(item.title) } }
    TextButton(onClick = onOpenNews, contentPadding = PaddingValues(0.dp)) {
        Text("All market notes", color = Acid)
        Icon(Icons.Rounded.ChevronRight, contentDescription = null, tint = Acid)
    }
}

@Composable
private fun CompactNews(item: NewsItem, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(onClick = onClick).padding(vertical = 10.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Box(Modifier.padding(top = 7.dp).size(8.dp).background(if (item.positive) Acid else SignalGold, CircleShape))
        Column(Modifier.weight(1f)) {
            Text(item.title, color = Ink, fontSize = 15.sp, fontWeight = FontWeight.Medium)
            Text("${item.source} · ${item.age}", color = Muted, fontSize = 12.sp)
        }
    }
}

@Composable
private fun NotesScreen(onAsk: (String) -> Unit) {
    var filter by rememberSaveable { mutableStateOf("For you") }
    val saved = remember { mutableStateListOf<Int>() }
    var expanded by remember { mutableStateOf<Int?>(1) }
    val filters = listOf("For you", "Central banks", "Companies", "Macro")

    LazyColumn(
        Modifier.fillMaxSize().statusBarsPadding(),
        contentPadding = PaddingValues(18.dp, 16.dp, 18.dp, 104.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item { ScreenHeader("Molly's briefing", "Notes", Icons.Rounded.Search) {} }
        item { Text("Noise compressed into decisions that can affect your money.", color = Muted, fontSize = 14.sp, lineHeight = 20.sp) }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                filters.forEach { item -> FilterChip(filter == item, { filter = item }, { Text(item) }) }
            }
        }
        item {
            FinCard(Color(0xFF1C1810), Color(0xFF4D3E24)) {
                Text("PRIORITY NOTE", color = SignalGold, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text("The next rate signal changes your FX risk before it changes your watchlist.", color = Ink, fontSize = 20.sp, fontWeight = FontWeight.SemiBold)
                Text("Molly connected this to your USD-denominated KSPI idea.", color = Muted, fontSize = 13.sp)
                TextButton(onClick = { onAsk("priority central bank note") }, contentPadding = PaddingValues(0.dp)) {
                    Icon(Icons.Rounded.AutoAwesome, contentDescription = null, tint = SignalGold)
                    Spacer(Modifier.width(7.dp))
                    Text("Explain the connection", color = SignalGold)
                }
            }
        }
        items(newsFeed, key = { it.id }) { item ->
            NewsCard(
                item,
                expanded == item.id,
                item.id in saved,
                { expanded = if (expanded == item.id) null else item.id },
                { if (item.id in saved) saved.remove(item.id) else saved.add(item.id) },
                { onAsk(item.title) },
            )
        }
    }
}

@Composable
private fun NewsCard(item: NewsItem, expanded: Boolean, saved: Boolean, onExpand: () -> Unit, onSave: () -> Unit, onAsk: () -> Unit) {
    FinCard(onClick = onExpand) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Text("${item.source} · ${item.age}", color = Muted, fontSize = 12.sp)
            IconButton(onClick = onSave, modifier = Modifier.size(28.dp)) {
                Icon(if (saved) Icons.Rounded.Bookmark else Icons.Rounded.BookmarkBorder, if (saved) "Remove bookmark" else "Bookmark", tint = if (saved) Acid else Muted)
            }
        }
        Text(item.title, color = Ink, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            Box(Modifier.size(7.dp).background(if (item.positive) Acid else SignalGold, CircleShape))
            Text(item.impact, color = if (item.positive) Acid else SignalGold, fontSize = 12.sp, fontWeight = FontWeight.Bold)
        }
        if (expanded) {
            HorizontalDivider(color = Hairline)
            Text(item.summary, color = Muted, fontSize = 14.sp, lineHeight = 20.sp)
            TextButton(onClick = onAsk, contentPadding = PaddingValues(0.dp)) {
                Icon(Icons.Rounded.AutoAwesome, contentDescription = null)
                Spacer(Modifier.width(6.dp))
                Text("Ask Molly why this matters")
            }
        }
    }
}

@Composable
private fun MarketScreen(
    state: FinaiDemoState,
    proMode: Boolean,
    symbol: String,
    provider: String,
    amount: String,
    horizon: String,
    thesis: String,
    loading: Boolean,
    onSymbolChange: (String) -> Unit,
    onProviderChange: (String) -> Unit,
    onAmountChange: (String) -> Unit,
    onHorizonChange: (String) -> Unit,
    onThesisChange: (String) -> Unit,
    onAnalyze: () -> Unit,
    onAsk: (String) -> Unit,
) {
    val watchlist = listOf("KSPI", "KZTK", "SBER", "AAPL")
    LazyColumn(
        Modifier.fillMaxSize().statusBarsPadding(),
        contentPadding = PaddingValues(18.dp, 16.dp, 18.dp, 104.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item { ScreenHeader(if (proMode) "MOLOX terminal" else "Paper market", "Market", Icons.Rounded.Search) {} }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                watchlist.forEach { ticker -> FilterChip(symbol == ticker, { onSymbolChange(ticker) }, { Text(ticker) }) }
                AssistChip({ onSymbolChange("") }, { Text("Add") }, leadingIcon = { Icon(Icons.Rounded.Add, null, Modifier.size(17.dp)) })
            }
        }
        item { QuoteCard(state, onAsk) }
        item { ScenarioCard(state.scenarios) }
        item {
            AnalysisComposer(symbol, provider, amount, horizon, thesis, loading, onSymbolChange, onProviderChange, onAmountChange, onHorizonChange, onThesisChange, onAnalyze)
        }
        item { AgentConsensus(state, proMode, onAsk) }
        if (proMode) item { ProRadar(state) }
    }
}

@Composable
private fun QuoteCard(state: FinaiDemoState, onAsk: (String) -> Unit) {
    FinCard {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Column {
                Text(state.exchange, color = Muted, fontSize = 11.sp, maxLines = 1)
                Text(state.symbol, color = Ink, fontSize = 34.sp, fontWeight = FontWeight.Bold)
            }
            Column(horizontalAlignment = Alignment.End) {
                Text(state.price, color = Ink, fontSize = 23.sp, fontWeight = FontWeight.Bold)
                Text(state.dayChange, color = if (state.dayChange.startsWith("-")) SignalRed else Acid, fontSize = 14.sp)
            }
        }
        Box(Modifier.fillMaxWidth().height(84.dp).background(Color(0xFF101712), RoundedCornerShape(6.dp))) {
            Row(Modifier.fillMaxSize().padding(horizontal = 12.dp), Arrangement.SpaceEvenly, Alignment.CenterVertically) {
                listOf(14, 28, 19, 43, 35, 58, 49, 70, 63, 81).forEachIndexed { index, value ->
                    Box(Modifier.width(4.dp).height(value.dp).background(if (index > 6) Acid else SignalBlue.copy(alpha = 0.65f), CircleShape))
                }
            }
        }
        TextButton(onClick = { onAsk("${state.symbol} price move") }, contentPadding = PaddingValues(0.dp)) {
            Icon(Icons.Rounded.AutoAwesome, contentDescription = null)
            Spacer(Modifier.width(6.dp))
            Text("Explain this move")
        }
    }
}

@Composable
private fun ScenarioCard(scenarios: List<ScenarioState>) {
    FinCard {
        SectionTitle("Scenario range", "30 days")
        scenarios.forEach { scenario ->
            val color = when (scenario.kind) { ScenarioKind.Loss -> SignalRed; ScenarioKind.Neutral -> SignalBlue; ScenarioKind.Gain -> Acid }
            val progress = when (scenario.kind) { ScenarioKind.Loss -> 0.30f; ScenarioKind.Neutral -> 0.58f; ScenarioKind.Gain -> 0.82f }
            Row(Modifier.fillMaxWidth().padding(vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                Text(scenario.label, color = Muted, fontSize = 13.sp, modifier = Modifier.width(62.dp))
                LinearProgressIndicator({ progress }, Modifier.weight(1f).height(6.dp).clip(CircleShape), color, Hairline)
                Text(scenario.percent, color = color, fontSize = 12.sp, modifier = Modifier.width(62.dp), fontWeight = FontWeight.Bold)
            }
        }
    }
}

@Composable
private fun AnalysisComposer(
    symbol: String,
    provider: String,
    amount: String,
    horizon: String,
    thesis: String,
    loading: Boolean,
    onSymbolChange: (String) -> Unit,
    onProviderChange: (String) -> Unit,
    onAmountChange: (String) -> Unit,
    onHorizonChange: (String) -> Unit,
    onThesisChange: (String) -> Unit,
    onAnalyze: () -> Unit,
) {
    var expanded by rememberSaveable { mutableStateOf(false) }
    FinCard(Color(0xFF161B17), Color(0xFF354037)) {
        Row(Modifier.fillMaxWidth().clickable { expanded = !expanded }, Arrangement.SpaceBetween, Alignment.CenterVertically) {
            Column {
                Text("TEST AN IDEA", color = Acid, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text("$symbol · $amount KZT · $horizon days", color = Ink, fontSize = 17.sp, fontWeight = FontWeight.SemiBold)
            }
            Icon(if (expanded) Icons.Rounded.Close else Icons.Rounded.Settings, contentDescription = null, tint = Muted)
        }
        if (expanded) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                DarkField(symbol, onSymbolChange, "Ticker", Modifier.weight(1f))
                DarkField(provider, onProviderChange, "Provider", Modifier.weight(1f))
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                DarkField(amount, onAmountChange, "Amount", Modifier.weight(1f), true)
                DarkField(horizon, onHorizonChange, "Days", Modifier.weight(1f), true)
            }
            DarkField(thesis, onThesisChange, "Your thesis", Modifier.fillMaxWidth(), minLines = 3)
        } else {
            Text(thesis, color = Muted, fontSize = 13.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
        }
        Button(
            onClick = onAnalyze,
            enabled = !loading && symbol.isNotBlank(),
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Acid, contentColor = Color(0xFF102000)),
            shape = RoundedCornerShape(7.dp),
        ) {
            Icon(if (loading) Icons.Rounded.MoreHoriz else Icons.Rounded.Bolt, contentDescription = null)
            Spacer(Modifier.width(7.dp))
            Text(if (loading) "Agents are debating..." else "Run MOLOX analysis", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun DarkField(value: String, onValueChange: (String) -> Unit, label: String, modifier: Modifier, numeric: Boolean = false, minLines: Int = 1) {
    OutlinedTextField(
        value,
        onValueChange,
        modifier,
        label = { Text(label) },
        minLines = minLines,
        singleLine = minLines == 1,
        keyboardOptions = if (numeric) KeyboardOptions(keyboardType = KeyboardType.Number) else KeyboardOptions.Default,
    )
}

@Composable
private fun AgentConsensus(state: FinaiDemoState, proMode: Boolean, onAsk: (String) -> Unit) {
    FinCard {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Column {
                Text(if (proMode) "MULTI-AGENT VERDICT" else "MOLLY'S VERDICT", color = SignalBlue, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text(state.actionTitle, color = Ink, fontSize = 19.sp, fontWeight = FontWeight.SemiBold)
            }
            Icon(Icons.Rounded.CheckCircle, contentDescription = null, tint = SignalBlue)
        }
        Text(state.action, color = Muted, fontSize = 14.sp, lineHeight = 20.sp)
        if (proMode) {
            state.agents.take(4).forEach { agent ->
                Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
                    Text(agent.role, color = Ink, fontSize = 13.sp)
                    Text(agent.stance.uppercase(), color = SignalGold, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
        TextButton(onClick = { onAsk("agent verdict for ${state.symbol}") }, contentPadding = PaddingValues(0.dp)) {
            Text("Challenge this verdict", color = SignalBlue)
            Icon(Icons.Rounded.ChevronRight, contentDescription = null, tint = SignalBlue)
        }
    }
}

@Composable
private fun LearnScreen(state: FinaiDemoState, onAsk: (String) -> Unit) {
    var answer by rememberSaveable { mutableStateOf<Int?>(null) }
    LazyColumn(
        Modifier.fillMaxSize().statusBarsPadding(),
        contentPadding = PaddingValues(18.dp, 16.dp, 18.dp, 104.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item { ScreenHeader("Built from your activity", "Learn") }
        item {
            FinCard(Color(0xFF151A20), Color(0xFF293A50)) {
                Text("YOUR CURRENT THREAD", color = SignalBlue, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text("From ${state.symbol} to currency risk", color = Ink, fontSize = 23.sp, fontWeight = FontWeight.SemiBold)
                Text("Molly turned your last analysis into a short path with examples from your own budget.", color = Muted, fontSize = 14.sp, lineHeight = 20.sp)
                LinearProgressIndicator({ 0.54f }, Modifier.fillMaxWidth().height(7.dp).clip(CircleShape), SignalBlue, Hairline)
                Text("54% complete", color = SignalBlue, fontSize = 12.sp)
            }
        }
        item { SectionTitle("Next lessons", "Personalized") }
        items(learningPath) { lesson -> LessonRow(lesson) { onAsk("lesson: ${lesson.title}") } }
        item {
            FinCard(Color(0xFF1B1811), Color(0xFF4B3B22)) {
                Text("QUICK CHECK", color = SignalGold, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                Text("A stock gained 8%, but USD/KZT fell 10%. What should you inspect first?", color = Ink, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                listOf("The stock logo", "Currency-adjusted return", "Yesterday's volume only").forEachIndexed { index, option ->
                    FilterChip(answer == index, { answer = index }, { Text(option) }, modifier = Modifier.fillMaxWidth())
                }
                if (answer != null) Text(if (answer == 1) "Correct. Your return lives in your home currency." else "Look at the asset and currency move together.", color = if (answer == 1) Acid else SignalGold, fontSize = 13.sp)
            }
        }
    }
}

@Composable
private fun LessonRow(lesson: Lesson, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(onClick = onClick).padding(vertical = 9.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Box(Modifier.size(44.dp).background(SurfaceHigh, RoundedCornerShape(7.dp)), contentAlignment = Alignment.Center) {
            Icon(Icons.Rounded.MenuBook, contentDescription = null, tint = SignalBlue)
        }
        Column(Modifier.weight(1f)) {
            Text(lesson.topic.uppercase(), color = SignalBlue, fontSize = 10.sp, fontWeight = FontWeight.Bold)
            Text(lesson.title, color = Ink, fontSize = 15.sp, fontWeight = FontWeight.Medium)
            Text("${lesson.minutes} min", color = Muted, fontSize = 12.sp)
        }
        if (lesson.progress > 0f) Text("${(lesson.progress * 100).toInt()}%", color = Acid, fontSize = 12.sp)
        else Icon(Icons.Rounded.ChevronRight, contentDescription = null, tint = Muted)
    }
}

@Composable
private fun ProfileScreen(state: FinaiDemoState, apiBase: String, onApiBaseChange: (String) -> Unit, proMode: Boolean, onModeChange: (Boolean) -> Unit) {
    var alerts by rememberSaveable { mutableStateOf(true) }
    LazyColumn(
        Modifier.fillMaxSize().statusBarsPadding(),
        contentPadding = PaddingValues(18.dp, 16.dp, 18.dp, 104.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item { ScreenHeader("Local demo profile", "Profile") }
        item {
            FinCard {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(13.dp)) {
                    Box(Modifier.size(48.dp).background(Acid, CircleShape), contentAlignment = Alignment.Center) { Text("YM", color = Color(0xFF102000), fontWeight = FontWeight.Bold) }
                    Column(Modifier.weight(1f)) {
                        Text("Yedige", color = Ink, fontSize = 18.sp, fontWeight = FontWeight.SemiBold)
                        Text("Paper investor · KZT base", color = Muted, fontSize = 13.sp)
                    }
                    IconButton(onClick = {}) { Icon(Icons.Rounded.MoreHoriz, contentDescription = "More") }
                }
            }
        }
        item {
            SectionTitle("Money profile")
            SettingsRow(Icons.Rounded.AccountBalanceWallet, "Free cash", state.freeCash)
            SettingsRow(Icons.Rounded.Shield, "Safe-to-try", state.safeToTry)
            SettingsRow(Icons.Rounded.Visibility, "Paper positions", state.portfolio.count.toString())
        }
        item {
            FinCard {
                SectionTitle("Experience")
                ToggleRow("MOLOX Pro", "Dense signals, agent debate and radar", proMode, onModeChange)
                HorizontalDivider(color = Hairline)
                ToggleRow("Priority alerts", "Only events tied to your money", alerts) { alerts = it }
            }
        }
        item {
            FinCard {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Icon(Icons.Rounded.CloudDone, contentDescription = null, tint = Acid)
                    Column {
                        Text("Backend connection", color = Ink, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
                        Text("Use 10.0.2.2 for Android Emulator", color = Muted, fontSize = 12.sp)
                    }
                }
                DarkField(apiBase, onApiBaseChange, "API URL", Modifier.fillMaxWidth())
            }
        }
        item {
            Row(verticalAlignment = Alignment.Top, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Icon(Icons.Rounded.Info, contentDescription = null, tint = Muted, modifier = Modifier.size(17.dp))
                Text("FinAI currently runs paper analysis only and never places broker orders.", color = Muted, fontSize = 12.sp)
            }
        }
    }
}

@Composable
private fun ToggleRow(title: String, body: String, checked: Boolean, onChecked: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.CenterVertically) {
        Column(Modifier.weight(1f)) {
            Text(title, color = Ink, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
            Text(body, color = Muted, fontSize = 12.sp)
        }
        Switch(checked, onChecked)
    }
}

@Composable
private fun SettingsRow(icon: ImageVector, title: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 10.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        Icon(icon, contentDescription = null, tint = Muted)
        Text(title, color = Ink, fontSize = 14.sp, modifier = Modifier.weight(1f))
        Text(value, color = Ink, fontSize = 14.sp, fontWeight = FontWeight.Bold)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MollySheet(context: String, state: FinaiDemoState, proMode: Boolean, onDismiss: () -> Unit, onOpenLearn: () -> Unit) {
    var input by remember { mutableStateOf("") }
    var answer by remember { mutableStateOf("I connected $context to your budget, market exposure and current thesis. What should we unpack first?") }
    ModalBottomSheet(onDismissRequest = onDismiss, containerColor = SurfaceLow, contentColor = Ink) {
        Column(Modifier.fillMaxWidth().padding(start = 18.dp, end = 18.dp, bottom = 28.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(11.dp)) {
                Box(Modifier.size(42.dp).background(Acid, CircleShape), contentAlignment = Alignment.Center) { Icon(Icons.Rounded.AutoAwesome, null, tint = Color(0xFF102000)) }
                Column(Modifier.weight(1f)) {
                    Text("Molly", color = Ink, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                    Text(if (proMode) "Powered by MOLOX multi-agent review" else "Your financial context agent", color = Muted, fontSize = 12.sp)
                }
                StatusDot("READY")
            }
            FinCard(SurfaceHigh, Hairline) { Text(answer, color = Ink, fontSize = 15.sp, lineHeight = 21.sp) }
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("Why it matters", "Show the risk", "Teach me").forEach { prompt ->
                    AssistChip(
                        onClick = {
                            answer = when (prompt) {
                                "Why it matters" -> "It matters because ${state.symbol} competes for the same ${state.safeToTry} risk budget as every other idea."
                                "Show the risk" -> "The current signal is ${state.riskBadge}. Start with the stress scenario and liquidity before expected return."
                                else -> "I made a short lesson from this exact example. Open Learn when you're ready."
                            }
                        },
                        label = { Text(prompt) },
                        colors = AssistChipDefaults.assistChipColors(containerColor = SurfaceHigh),
                    )
                }
            }
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(input, { input = it }, Modifier.weight(1f), placeholder = { Text("Ask about this screen") }, singleLine = true)
                FilledIconButton(
                    onClick = {
                        if (input.isNotBlank()) {
                            answer = "For '$input', I would compare the claim against your safe-to-try limit, FX exposure and the latest market evidence."
                            input = ""
                        }
                    },
                    colors = IconButtonDefaults.filledIconButtonColors(containerColor = Acid, contentColor = Color(0xFF102000)),
                ) { Icon(Icons.Rounded.Send, contentDescription = "Send") }
            }
            TextButton(onClick = onOpenLearn, modifier = Modifier.align(Alignment.End)) {
                Icon(Icons.Rounded.MenuBook, contentDescription = null)
                Spacer(Modifier.width(6.dp))
                Text("Turn this into a lesson")
            }
        }
    }
}

@Composable
private fun FinCard(background: Color = SurfaceLow, border: Color = Hairline, onClick: (() -> Unit)? = null, content: @Composable ColumnScope.() -> Unit) {
    val modifier = Modifier
        .fillMaxWidth()
        .background(background, RoundedCornerShape(8.dp))
        .border(1.dp, border, RoundedCornerShape(8.dp))
        .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier)
        .padding(15.dp)
    Column(modifier, verticalArrangement = Arrangement.spacedBy(9.dp), content = content)
}
