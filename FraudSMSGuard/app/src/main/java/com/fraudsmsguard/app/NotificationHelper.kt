package com.fraudsmsguard.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat

/**
 * Helper class for creating and displaying notifications.
 * Shows alerts when fraud SMS is detected.
 */
object NotificationHelper {

    private const val CHANNEL_FRAUD = "fraud_alerts"
    private const val CHANNEL_SERVICE = "monitoring_service"
    private const val FRAUD_NOTIFICATION_BASE_ID = 1000
    private var notificationCounter = 0

    /**
     * Create notification channels (required for Android 8+)
     */
    fun createChannels(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = context.getSystemService(NotificationManager::class.java)

            // Fraud alerts channel - high importance
            val fraudChannel = NotificationChannel(
                CHANNEL_FRAUD,
                "Fraud Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Alerts when fraudulent SMS is detected"
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 500, 200, 500)
                setShowBadge(true)
            }

            // Service channel - low importance
            val serviceChannel = NotificationChannel(
                CHANNEL_SERVICE,
                "Monitoring Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Background SMS monitoring service"
                setShowBadge(false)
            }

            manager.createNotificationChannels(listOf(fraudChannel, serviceChannel))
        }
    }

    /**
     * Show a notification when fraud SMS is detected
     */
    fun showFraudAlert(
        context: Context,
        sender: String,
        message: String,
        confidence: Double,
        riskLevel: String
    ) {
        createChannels(context)

        val intent = Intent(context, BlockedMessagesActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val riskEmoji = when (riskLevel) {
            "high" -> "🔴"
            "medium" -> "🟡"
            else -> "🟠"
        }

        val notification = NotificationCompat.Builder(context, CHANNEL_FRAUD)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle("$riskEmoji Fraud SMS Blocked!")
            .setContentText("From: $sender | Risk: ${riskLevel.uppercase()}")
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText("From: $sender\n\n\"${message.take(150)}${if (message.length > 150) "..." else ""}\"\n\nConfidence: ${String.format("%.1f", confidence)}% | Risk: ${riskLevel.uppercase()}\n\nThis message has been blocked and reported to the security team.")
            )
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setVibrate(longArrayOf(0, 500, 200, 500))
            .addAction(
                android.R.drawable.ic_menu_view,
                "View Blocked",
                pendingIntent
            )
            .build()

        try {
            NotificationManagerCompat.from(context)
                .notify(FRAUD_NOTIFICATION_BASE_ID + notificationCounter++, notification)
        } catch (e: SecurityException) {
            // Notification permission not granted
        }
    }

    /**
     * Create the persistent notification for the foreground service
     */
    fun createServiceNotification(context: Context): Notification {
        createChannels(context)

        val intent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(context, CHANNEL_SERVICE)
            .setSmallIcon(android.R.drawable.ic_lock_idle_lock)
            .setContentTitle("🛡️ SMS Fraud Guard Active")
            .setContentText("Monitoring incoming messages for fraud")
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }
}
