package com.fraudsmsguard.app

import android.app.Service
import android.content.Intent
import android.os.IBinder

/**
 * Foreground Service that keeps SMS monitoring active even when app is in background.
 * Shows a persistent notification indicating the app is protecting the device.
 */
class SmsMonitorService : Service() {

    companion object {
        private const val NOTIFICATION_ID = 1
    }

    override fun onCreate() {
        super.onCreate()
        NotificationHelper.createChannels(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationHelper.createServiceNotification(this)
        startForeground(NOTIFICATION_ID, notification)
        return START_STICKY // Restart service if killed
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        stopForeground(STOP_FOREGROUND_REMOVE)
    }
}
