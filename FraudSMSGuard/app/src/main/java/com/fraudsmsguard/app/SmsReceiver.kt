package com.fraudsmsguard.app

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.provider.Telephony
import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

/**
 * BroadcastReceiver that intercepts incoming SMS messages.
 * Sends each message to the ML API for fraud classification.
 * If fraud is detected and auto-block is enabled, blocks the message
 * and sends notifications to the user and security team.
 */
class SmsReceiver : BroadcastReceiver() {

    companion object {
        private const val TAG = "SmsReceiver"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val prefs = context.getSharedPreferences("fraud_sms_guard", Context.MODE_PRIVATE)
        if (!prefs.getBoolean("monitoring", false)) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        if (messages.isNullOrEmpty()) return

        // Combine multi-part SMS
        val sender = messages[0].displayOriginatingAddress ?: "Unknown"
        val fullMessage = messages.joinToString("") { it.messageBody ?: "" }

        Log.d(TAG, "SMS received from: $sender")

        // Send to API for classification
        thread {
            classifyAndHandle(context, prefs, sender, fullMessage)
        }
    }

    private fun classifyAndHandle(
        context: Context,
        prefs: SharedPreferences,
        sender: String,
        message: String
    ) {
        val serverUrl = prefs.getString("server_url", "http://10.0.2.2:5000")
            ?: "http://10.0.2.2:5000"

        try {
            val url = URL("$serverUrl/api/predict")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type", "application/json")
            conn.doOutput = true
            conn.connectTimeout = 10000
            conn.readTimeout = 10000

            val json = JSONObject().apply {
                put("message", message)
                put("sender", sender)
            }

            conn.outputStream.bufferedWriter().use { it.write(json.toString()) }

            val responseCode = conn.responseCode
            if (responseCode == 200) {
                val response = conn.inputStream.bufferedReader().use { it.readText() }
                val result = JSONObject(response)

                val isFraud = result.getBoolean("is_fraud")
                val confidence = result.getDouble("confidence")
                val riskLevel = result.getString("risk_level")
                val autoBlocked = result.getBoolean("auto_blocked")

                Log.d(TAG, "Classification: fraud=$isFraud, confidence=$confidence, risk=$riskLevel")

                if (isFraud) {
                    // Update local stats
                    incrementStat(prefs, "local_fraud_count")

                    // Send notification to user
                    NotificationHelper.showFraudAlert(
                        context, sender, message, confidence, riskLevel
                    )

                    if (autoBlocked) {
                        incrementStat(prefs, "local_blocked_count")
                        Log.d(TAG, "Message auto-blocked and reported to security team")
                    }
                }

                incrementStat(prefs, "local_scan_count")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to classify SMS: ${e.message}")
            // If server is unreachable, keep the message (fail-safe)
        }
    }

    private fun incrementStat(prefs: SharedPreferences, key: String) {
        val current = prefs.getInt(key, 0)
        prefs.edit().putInt(key, current + 1).apply()
    }
}
