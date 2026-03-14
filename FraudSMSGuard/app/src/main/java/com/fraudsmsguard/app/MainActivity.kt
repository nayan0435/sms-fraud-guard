package com.fraudsmsguard.app

import android.Manifest
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    companion object {
        private const val PERMISSION_REQUEST_CODE = 100
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.RECEIVE_SMS,
            Manifest.permission.READ_SMS,
            Manifest.permission.READ_PHONE_STATE
        )
    }

    private lateinit var prefs: SharedPreferences
    private lateinit var statusText: TextView
    private lateinit var totalScannedText: TextView
    private lateinit var fraudDetectedText: TextView
    private lateinit var blockedCountText: TextView
    private lateinit var autoBlockSwitch: Switch
    private lateinit var monitorSwitch: Switch
    private lateinit var recentList: RecyclerView
    private lateinit var testInput: EditText
    private lateinit var testButton: Button
    private lateinit var testResult: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences("fraud_sms_guard", MODE_PRIVATE)

        initViews()
        checkPermissions()
        loadStats()
    }

    private fun initViews() {
        // Status
        statusText = findViewById(R.id.statusText)

        // Stats cards
        totalScannedText = findViewById(R.id.totalScanned)
        fraudDetectedText = findViewById(R.id.fraudDetected)
        blockedCountText = findViewById(R.id.blockedCount)

        // Toggles
        autoBlockSwitch = findViewById(R.id.autoBlockSwitch)
        autoBlockSwitch.isChecked = prefs.getBoolean("auto_block", true)
        autoBlockSwitch.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("auto_block", isChecked).apply()
            updateStatus()
        }

        monitorSwitch = findViewById(R.id.monitorSwitch)
        monitorSwitch.isChecked = prefs.getBoolean("monitoring", false)
        monitorSwitch.setOnCheckedChangeListener { _, isChecked ->
            prefs.edit().putBoolean("monitoring", isChecked).apply()
            if (isChecked) startMonitorService() else stopMonitorService()
            updateStatus()
        }

        // Test scanner
        testInput = findViewById(R.id.testInput)
        testButton = findViewById(R.id.testButton)
        testResult = findViewById(R.id.testResult)
        testButton.setOnClickListener { testMessage() }

        // Navigation buttons
        findViewById<Button>(R.id.blockedButton).setOnClickListener {
            startActivity(Intent(this, BlockedMessagesActivity::class.java))
        }

        findViewById<Button>(R.id.settingsButton).setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }

        updateStatus()
    }

    private fun checkPermissions() {
        val permissionsToRequest = REQUIRED_PERMISSIONS.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }.toMutableList()

        // Add notification permission for Android 13+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissionsToRequest.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                permissionsToRequest.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        } else {
            onPermissionsGranted()
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            if (allGranted) {
                onPermissionsGranted()
            } else {
                statusText.text = "⚠️ SMS permissions required for monitoring"
                Toast.makeText(this, "Please grant SMS permissions to enable fraud detection", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun onPermissionsGranted() {
        statusText.text = "✅ Permissions granted — Ready to protect"
        if (prefs.getBoolean("monitoring", false)) {
            startMonitorService()
        }
    }

    private fun updateStatus() {
        val monitoring = prefs.getBoolean("monitoring", false)
        val autoBlock = prefs.getBoolean("auto_block", true)
        statusText.text = when {
            monitoring && autoBlock -> "🛡️ Active — Monitoring & Auto-Blocking"
            monitoring -> "📡 Active — Monitoring Only"
            else -> "⏸️ Inactive — Enable monitoring to start"
        }
    }

    private fun startMonitorService() {
        val intent = Intent(this, SmsMonitorService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        Toast.makeText(this, "SMS monitoring started", Toast.LENGTH_SHORT).show()
    }

    private fun stopMonitorService() {
        stopService(Intent(this, SmsMonitorService::class.java))
        Toast.makeText(this, "SMS monitoring stopped", Toast.LENGTH_SHORT).show()
    }

    private fun testMessage() {
        val message = testInput.text.toString().trim()
        if (message.isEmpty()) {
            Toast.makeText(this, "Enter a message to test", Toast.LENGTH_SHORT).show()
            return
        }

        testButton.isEnabled = false
        testResult.text = "⏳ Analyzing..."

        val serverUrl = prefs.getString("server_url", "http://10.0.2.2:5000") ?: "http://10.0.2.2:5000"

        thread {
            try {
                val url = URL("$serverUrl/api/predict")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true
                conn.connectTimeout = 5000
                conn.readTimeout = 5000

                val json = JSONObject().apply {
                    put("message", message)
                    put("sender", "Test")
                }

                conn.outputStream.bufferedWriter().use { it.write(json.toString()) }

                val response = conn.inputStream.bufferedReader().use { it.readText() }
                val result = JSONObject(response)

                val isFraud = result.getBoolean("is_fraud")
                val confidence = result.getDouble("confidence")
                val riskLevel = result.getString("risk_level")

                runOnUiThread {
                    testResult.text = if (isFraud) {
                        "🚨 FRAUD DETECTED\nConfidence: ${String.format("%.1f", confidence)}%\nRisk: ${riskLevel.uppercase()}"
                    } else {
                        "✅ MESSAGE IS SAFE\nConfidence: ${String.format("%.1f", confidence)}%"
                    }
                    testButton.isEnabled = true
                    loadStats()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    testResult.text = "❌ Error: ${e.message}\n\nMake sure the server is running at:\n${prefs.getString("server_url", "http://10.0.2.2:5000")}"
                    testButton.isEnabled = true
                }
            }
        }
    }

    private fun loadStats() {
        val serverUrl = prefs.getString("server_url", "http://10.0.2.2:5000") ?: "http://10.0.2.2:5000"

        thread {
            try {
                val url = URL("$serverUrl/api/stats")
                val conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = 3000
                val response = conn.inputStream.bufferedReader().use { it.readText() }
                val stats = JSONObject(response)

                runOnUiThread {
                    totalScannedText.text = stats.getInt("total_scanned").toString()
                    fraudDetectedText.text = stats.getInt("fraud_detected").toString()
                    blockedCountText.text = stats.getInt("blocked_count").toString()
                }
            } catch (e: Exception) {
                // Stats load fails silently on first run
            }
        }
    }

    override fun onResume() {
        super.onResume()
        loadStats()
        updateStatus()
    }
}
