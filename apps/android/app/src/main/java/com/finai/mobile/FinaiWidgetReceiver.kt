package com.finai.mobile

import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.Context
import android.widget.RemoteViews

class FinaiWidgetReceiver : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        for (appWidgetId in appWidgetIds) {
            val views = RemoteViews(context.packageName, R.layout.finai_widget)
            views.setTextViewText(R.id.widget_title, "FInAI")
            views.setTextViewText(R.id.widget_amount, "Safe-to-try: 30 000 KZT")
            views.setTextViewText(R.id.widget_note, "KSPI: риск умеренный, следи за USD/KZT")
            appWidgetManager.updateAppWidget(appWidgetId, views)
        }
    }
}

