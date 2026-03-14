package com.fraudsmsguard.app

import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

/**
 * Activity showing the list of blocked fraud messages.
 */
class BlockedMessagesActivity : AppCompatActivity() {

    private lateinit var blockedListView: RecyclerView
    private lateinit var emptyText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_blocked)

        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        supportActionBar?.title = "🚫 Blocked Messages"

        blockedListView = findViewById(R.id.blockedRecyclerView)
        emptyText = findViewById(R.id.emptyText)

        blockedListView.layoutManager = LinearLayoutManager(this)

        loadBlockedMessages()
    }

    private fun loadBlockedMessages() {
        val prefs = getSharedPreferences("fraud_sms_guard", MODE_PRIVATE)
        val serverUrl = prefs.getString("server_url", "http://10.0.2.2:5000")
            ?: "http://10.0.2.2:5000"

        thread {
            try {
                val url = URL("$serverUrl/api/blocked")
                val conn = url.openConnection() as HttpURLConnection
                conn.connectTimeout = 5000
                val response = conn.inputStream.bufferedReader().use { it.readText() }
                val messages = JSONArray(response)

                runOnUiThread {
                    if (messages.length() == 0) {
                        emptyText.text = "✅ No blocked messages\nYour inbox is clean!"
                        emptyText.visibility = android.view.View.VISIBLE
                        blockedListView.visibility = android.view.View.GONE
                    } else {
                        emptyText.visibility = android.view.View.GONE
                        blockedListView.visibility = android.view.View.VISIBLE
                        // Display messages using a simple adapter
                        val adapter = BlockedAdapter(messages)
                        blockedListView.adapter = adapter
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    emptyText.text = "❌ Could not load blocked messages\n${e.message}"
                    emptyText.visibility = android.view.View.VISIBLE
                }
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}

/**
 * Simple RecyclerView adapter for blocked messages
 */
class BlockedAdapter(private val messages: JSONArray) :
    RecyclerView.Adapter<BlockedAdapter.ViewHolder>() {

    class ViewHolder(view: android.view.View) : RecyclerView.ViewHolder(view) {
        val sender: TextView = view.findViewById(R.id.itemSender)
        val message: TextView = view.findViewById(R.id.itemMessage)
        val confidence: TextView = view.findViewById(R.id.itemConfidence)
        val time: TextView = view.findViewById(R.id.itemTime)
    }

    override fun onCreateViewHolder(parent: android.view.ViewGroup, viewType: Int): ViewHolder {
        val view = android.view.LayoutInflater.from(parent.context)
            .inflate(R.layout.item_message, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val msg = messages.getJSONObject(position)
        holder.sender.text = "📱 ${msg.optString("sender", "Unknown")}"
        holder.message.text = msg.getString("message")
        holder.confidence.text = "${String.format("%.1f", msg.getDouble("confidence"))}% fraud"
        holder.time.text = msg.optString("blocked_at", "")
    }

    override fun getItemCount() = messages.length()
}
