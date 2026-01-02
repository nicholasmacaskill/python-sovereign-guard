
from flask import Flask, jsonify, render_template_string
import os
import re
from datetime import datetime

app = Flask(__name__)

# Constants
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guard_monitor.log')

# HTML Template (Cyberpunk/Terminal Style)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sovereign Guard Mission Control</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

        :root {
            --bg-gradient: radial-gradient(circle at 50% -20%, #1a2a40, #050505 80%);
            --glass-bg: rgba(20, 30, 50, 0.4);
            --glass-border: rgba(255, 255, 255, 0.1);
            --glass-highlight: rgba(255, 255, 255, 0.15);
            --text-primary: #e0f2ff;
            --text-secondary: #7a8ba0;
            --accent-green: #00ff9d;
            --accent-red: #ff3333;
            --accent-yellow: #ffcc00;
            --font-tech: 'Share Tech Mono', monospace;
        }
        body {
            background: var(--bg-gradient);
            color: var(--text-primary);
            font-family: var(--font-tech);
            margin: 0;
            padding: 20px; /* Reduced padding */
            height: 100vh;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            overflow: hidden; /* Prevent body scroll */
            letter-spacing: 0.5px;
        }
        /* Noise texture covers everything */
        /* Add subtle noise texture */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: -1;
        }

        .stat-card, .log-container {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-top: 1px solid var(--glass-highlight);
            border-left: 1px solid var(--glass-highlight);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--glass-border);
            padding-bottom: 20px;
            margin-bottom: 40px;
            backdrop-filter: blur(10px);
        }
        .title {
            font-size: 24px;
            font-weight: 200;
            display: flex;
            align-items: center;
            gap: 15px;
            letter-spacing: 1px;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 15px var(--accent-green);
            animation: pulse 3s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.8; box-shadow: 0 0 5px var(--accent-green); }
            50% { opacity: 0.4; box-shadow: 0 0 20px var(--accent-green); }
            100% { opacity: 0.8; box-shadow: 0 0 5px var(--accent-green); }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 25px;
            border-radius: 16px;
            border: 1px solid var(--glass-border);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.05);
        }
        .stat-value {
            font-size: 42px;
            font-weight: 300;
            color: var(--text-primary);
            margin-bottom: 5px;
        }
        .stat-label {
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
        }
        .log-container {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-top: 1px solid var(--glass-highlight);
            border-left: 1px solid var(--glass-highlight);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            /* Layout Fixes */
            flex-grow: 1; /* Fill remaining vertical space */
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-height: 0; /* Crucial for nested flex scroll */
        }
        .log-header {
            background: rgba(0, 0, 0, 0.2);
            padding: 15px 25px;
            font-weight: 500;
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            justify-content: space-between;
            color: var(--text-secondary);
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            flex-shrink: 0; /* Header stays fixed */
        }
        .log-list {
            list-style: none;
            padding: 0;
            margin: 0;
            overflow-y: auto; /* Scroll ONLY the list */
            flex-grow: 1;
        }
        .log-item {
            padding: 18px 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            display: grid;
            grid-template-columns: 160px 1fr 140px;
            gap: 20px;
            align-items: center;
            font-family: var(--font-mono);
            font-size: 13px;
            transition: background 0.2s;
        }
        .log-item:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }
        .timestamp {
            color: #666;
            font-variant-numeric: tabular-nums;
        }
        .message {
            color: var(--text-primary);
            line-height: 1.4;
        }
        .risk-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            text-align: center;
            font-size: 10px;
            letter-spacing: 0.5px;
            backdrop-filter: blur(4px);
        }
        .risk-critical {
            background: rgba(255, 77, 77, 0.1);
            color: var(--accent-red);
            border: 1px solid rgba(255, 77, 77, 0.2);
            box-shadow: 0 0 10px rgba(255, 77, 77, 0.05);
        }
        .risk-warning {
            background: rgba(255, 204, 0, 0.1);
            color: var(--accent-yellow);
            border: 1px solid rgba(255, 204, 0, 0.2);
        }
        .risk-info {
            background: rgba(0, 255, 157, 0.05);
            color: var(--accent-green);
            border: 1px solid rgba(0, 255, 157, 0.1);
        }
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .whitelist-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--glass-border);
            color: var(--text-secondary);
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 10px;
            font-family: -apple-system, sans-serif;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-right: 15px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .whitelist-btn:hover {
            border-color: var(--accent-green);
            color: #000;
            background: var(--accent-green);
            box-shadow: 0 0 15px rgba(0, 255, 157, 0.3);
            transform: translateY(-1px);
        }
        .sync-btn {
            background: rgba(0, 255, 157, 0.1);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
            font-family: var(--font-tech);
            font-weight: 600;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        .sync-btn:hover {
            background: var(--accent-green);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 157, 0.4);
        }
        .sync-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .spinning {
            display: inline-block;
            animation: spin 1s linear infinite;
        }
        .mode-badge {
            background: rgba(0, 255, 157, 0.15);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1px;
            margin-left: 15px;
        }
        .mode-badge.warn {
            background: rgba(255, 204, 0, 0.15);
            border-color: var(--accent-yellow);
            color: var(--accent-yellow);
        }
        .mode-badge.protect {
            background: rgba(255, 77, 77, 0.15);
            border-color: var(--accent-red);
            color: var(--accent-red);
        }
        .learning-banner {
            background: rgba(0, 255, 157, 0.05);
            border: 1px solid rgba(0, 255, 157, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">
            <div class="status-dot"></div>
            Sovereign Guard // MISSION CONTROL
            <span id="mode-badge" class="mode-badge">LEARN</span>
        </div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <div style="color: var(--text-secondary);">System Status: <span style="color: var(--accent-green);">SECURE</span></div>
            <button onclick="syncNow()" class="sync-btn" id="sync-btn">
                <span id="sync-icon">⟳</span> SYNC NOW
            </button>
        </div>
    </div>

    <div id="learning-banner" class="learning-banner" style="display: none;">
        <div style="flex-grow: 1;">
            <div style="font-weight: 600; margin-bottom: 5px;">🎓 Learning Your System</div>
            <div style="font-size: 12px; opacity: 0.8;" id="learning-progress">Day 1/7 - Observing processes...</div>
        </div>
        <div style="font-size: 24px; font-weight: 300;" id="learning-count">0</div>
        <div style="font-size: 11px; opacity: 0.6;">PROCESSES</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="count-threats">0</div>
            <div class="stat-label">Threats Neutralized</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="count-scans">0</div>
            <div class="stat-label">Scans Performed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="last-active">--:--</div>
            <div class="stat-label">Last Activity</div>
        </div>
    </div>

    <div class="log-container">
        <div class="log-header">
            <span>Event Log</span>
            <span style="font-size: 12px; color: var(--text-secondary);">Auto-refreshing...</span>
        </div>
        <ul class="log-list" id="log-list">
            <!-- Items injected by JS -->
        </ul>
    </div>

    <script>
        async function fetchLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                const list = document.getElementById('log-list');
                list.innerHTML = ''; // Clear current

                let threats = 0;
                let scans = 0;

                data.logs.forEach(log => {
                    const li = document.createElement('li');
                    li.className = 'log-item';
                    
                    // Parse Severity
                    let badgeClass = 'risk-info';
                    let badgeText = 'INFO';
                    let actionHtml = '';
                    
                    if (log.message.includes('SECURITY ALERT') || log.message.includes('THREAT')) {
                        badgeClass = 'risk-critical';
                        badgeText = 'THREAT';
                        threats++;
                        
                        // Extract Process Name for Whitelisting
                        // Message format: "SECURITY ALERT: Process 'searchpartyuseragent' (PID: 123)..."
                        const match = log.message.match(/Process '([^']+)'/);
                        if (match && match[1]) {
                            const procName = match[1];
                            actionHtml = `<button onclick="whitelist('${procName}')" class="whitelist-btn">WHITELIST '${procName}'</button>`;
                        }
                    } else if (log.message.includes('WARNING')) {
                        badgeClass = 'risk-warning';
                        badgeText = 'WARNING';
                    } else if (log.message.includes('scans') || log.message.includes('Scanned')) {
                        scans++;
                    }

                    // Clean Message
                    let cleanMsg = log.message.replace('WARNING - ', '').replace('INFO - ', '');
                    
                    li.innerHTML = `
                        <span class="timestamp">${log.timestamp}</span>
                        <div style="display:flex; justify-content:space-between; align-items:center; width:100%">
                            <span class="message">${cleanMsg}</span>
                            ${actionHtml}
                        </div>
                        <span class="risk-badge ${badgeClass}">${badgeText}</span>
                    `;
                    list.appendChild(li);
                });

                // Update Stats
                document.getElementById('count-threats').innerText = threats;
                document.getElementById('count-scans').innerText = "Active"; 
                if (data.logs.length > 0) {
                     document.getElementById('last-active').innerText = data.logs[0].timestamp.split(' ')[1];
                }

            } catch (e) {
                console.error("Failed to fetch logs", e);
            }
        }

        async function whitelist(procName) {
            if (!confirm(`Are you sure you want to whitelist '${procName}'? This will allow it to run securely.`)) return;
            
            try {
                const res = await fetch('/api/whitelist', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({process: procName})
                });
                const result = await res.json();
                if (result.success) {
                    alert("✅ " + result.message);
                } else {
                    alert("❌ Error: " + result.error);
                }
            } catch (e) {
                alert("❌ Network Error");
            }
        }

        async function syncNow() {
            const btn = document.getElementById('sync-btn');
            const icon = document.getElementById('sync-icon');
            
            btn.disabled = true;
            icon.classList.add('spinning');
            
            try {
                const res = await fetch('/api/sync', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({force: true})
                });
                const result = await res.json();
                
                if (result.success) {
                    if (result.new_count > 0) {
                        alert(`✅ ${result.message}\n\nNew processes:\n${result.new_processes.join(', ')}`);
                    } else {
                        alert("✅ " + result.message);
                    }
                } else {
                    alert("⚠️ " + result.message);
                }
            } catch (e) {
                alert("❌ Sync failed: Network error");
            } finally {
                btn.disabled = false;
                icon.classList.remove('spinning');
            }
        }

        // Initial Load + Interval
        fetchLogs();
        fetchLearningStats();
        setInterval(fetchLogs, 3000);
        setInterval(fetchLearningStats, 5000);
        
        async function fetchLearningStats() {
            try {
                const response = await fetch('/api/learning');
                const data = await response.json();
                
                // Update mode badge
                const modeBadge = document.getElementById('mode-badge');
                modeBadge.textContent = data.mode.toUpperCase();
                modeBadge.className = 'mode-badge ' + data.mode;
                
                // Show/hide learning banner
                const banner = document.getElementById('learning-banner');
                if (data.mode === 'learn' && data.stats.status === 'learning') {
                    banner.style.display = 'flex';
                    document.getElementById('learning-count').textContent = data.stats.unique_processes || 0;
                    document.getElementById('learning-progress').textContent = 
                        `Day ${data.stats.days_elapsed}/7 - ${data.stats.total_observations} observations`;
                } else {
                    banner.style.display = 'none';
                }
            } catch (e) {
                console.error("Failed to fetch learning stats", e);
            }
        }
    </script>
</body>
</html>
"""

def parse_logs():
    logs = []
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            # Read last 100 lines
            lines = f.readlines()[-100:]
            
            for line in reversed(lines):
                # Basic Parse: 2026-01-02 11:46:48,895 - WARNING - Message...
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    timestamp = parts[0].split(',')[0] # Remove milliseconds
                    level = parts[1]
                    message = parts[2].strip()
                    
                    logs.append({
                        "timestamp": timestamp,
                        "level": level,
                        "message": message
                    })
    except Exception as e:
        print(f"Error parsing logs: {e}")
        
    return logs




@app.route('/api/learning')
def get_learning_stats():
    """Get learning mode statistics"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import learning_engine
        stats = learning_engine.analyze_learnings()
        mode = learning_engine.get_protection_mode()
        
        return jsonify({
            "mode": mode,
            "stats": stats
        })
    except Exception as e:
        return jsonify({
            "mode": os.getenv('PROTECTION_MODE', 'protect'),
            "stats": {"status": "error", "error": str(e)}
        })

@app.route('/api/sync', methods=['POST'])
def sync_intelligence():
    """Trigger whitelist sync from cloud"""
    from flask import request
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        import sovereign_core as core
        
        # Get license key from env or request
        license_key = os.getenv('LICENSE_KEY', 'free-tier')
        force = request.json.get('force', False) if request.json else False
        
        result = core.sync_whitelist(license_key=license_key, force=force)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Sync error: {str(e)}",
            "new_count": 0
        }), 500

@app.route('/api/whitelist', methods=['POST'])
def whitelist_process():
    from flask import request
    data = request.json
    process_name = data.get('process')
    
    if not process_name:
        return jsonify({"success": False, "error": "No process name provided"}), 400
        
    core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sovereign_core.py')
    
    try:
        # Read the file
        with open(core_path, 'r') as f:
            lines = f.readlines()
            
        # Find the SAFE_LIST_PROCESSES list end
        insert_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('SAFE_LIST_PROCESSES = ['):
                # Search forward for the closing bracket
                for j in range(i, len(lines)):
                    if ']' in lines[j]:
                        insert_idx = j
                        break
                break
        
        if insert_idx != -1:
            # Check if already present
            content = "".join(lines)
            if f"'{process_name}'" in content or f'"{process_name}"' in content:
                 return jsonify({"success": True, "message": f"'{process_name}' is already whitelisted."})

            # Insert before the closing bracket
            new_line = f"    '{process_name}', # Added via Dashboard\n"
            lines.insert(insert_idx, new_line)
            
            with open(core_path, 'w') as f:
                f.writelines(lines)
                
            return jsonify({"success": True, "message": f"Successfully whitelisted '{process_name}'"})
        else:
            return jsonify({"success": False, "error": "Could not find SAFE_LIST in core file"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/logs')
def get_logs():
    return jsonify({"logs": parse_logs()})

if __name__ == '__main__':
    print(f"🚀 Dashboard running at http://127.0.0.1:5000")
    app.run(port=5000)
