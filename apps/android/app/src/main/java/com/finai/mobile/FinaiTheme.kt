package com.finai.mobile

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Ink = Color(0xFFF1F4F0)
val Muted = Color(0xFF9BA49E)
val Canvas = Color(0xFF0B0E0C)
val SurfaceLow = Color(0xFF121613)
val SurfaceHigh = Color(0xFF1A201C)
val Hairline = Color(0xFF2B332E)
val Acid = Color(0xFFB7F36B)
val SignalBlue = Color(0xFF78A9FF)
val SignalGold = Color(0xFFE2B75F)
val SignalRed = Color(0xFFFF7B6B)

private val FinaiColors = darkColorScheme(
    primary = Acid,
    onPrimary = Color(0xFF102000),
    secondary = SignalBlue,
    tertiary = SignalGold,
    background = Canvas,
    onBackground = Ink,
    surface = SurfaceLow,
    onSurface = Ink,
    surfaceVariant = SurfaceHigh,
    onSurfaceVariant = Muted,
    outline = Hairline,
    error = SignalRed,
)

@Composable
fun FinaiTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = FinaiColors, content = content)
}
