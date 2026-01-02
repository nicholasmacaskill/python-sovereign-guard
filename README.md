# 🛡️ Sovereign Guard Suite (2026 Edition)

> **"Your hardware is secure, but is your session?"**

Sovereign Guard is a high-fidelity, zero-trust security perimeter designed to protect modern workstations against the 2026 threat landscape. While 2024-era protections like **Device Bound Session Credentials (DBSC)** secured cookies to hardware, they left a massive blind spot: **Local Environment Exploitation.**

Sovereign Guard fills that gap by monitoring the integrity of your browser's execution and the sanctity of your clipboard.

---

## ⚡️ The 2026 Threat Landscape

In 2026, account hijacking has evolved beyond simple cookie theft. Attackers now leverage:

### 1. DBSC "Inside-Out" Bypasses
DBSC binds your session to your TPM/Secure Enclave. However, malware running on your machine can launch a **legitimate, hardware-signed browser** with `--remote-debugging-port`. The session is "securely bound" to your machine, but the attacker controls it remotely via the DevTools Protocol.

### 2. Advanced Clipboard "Clippers"
Sophisticated malware now monitors your clipboard in real-time. When it detects a high-value address (BTC/ETH) or a sensitive command (`curl | bash`), it swaps the content in the milliseconds between **Copy** and **Paste**.

### 3. "Ghost" Browser Spoofing
Malware replaces your standard browser binaries with "Ghost" versions or launches browsers from hidden directories (`/tmp/.chrome`) that look identical to the user but navigate through malicious proxies.

---

## 🛡️ Mitigation Strategies

Sovereign Guard neutralizes these threats through multi-layered, low-latency monitoring.

### 🏗️ Execution Integrity (Anti-Hijack)
*   **Flag Neutralization**: Kills any browser process launched with dangerous flags (`--remote-debugging-port`, `--load-extension`) that allow external control or unvetted code execution.
*   **Path Enforcement**: Rejects any browser binary running from untrusted locations. Chrome must run from `/Applications/` or it is considered a compromise.
*   **Origin Tracing**: Every event logs the **Parent Process**, unmasking the hidden scripts or agents that attempted the launch.

### 📋 Clipboard Sentry (Anti-Virus)
*   **Strict Neutralization**: Detects and overwrites "Instructional Threats" (command injections like `curl | bash`) and "Script Droppers" (`eval(atob)`) the moment they enter the clipboard.
*   **Swap-Mode Protection**: Actively monitors financial addresses. If a background process attempts to swap your copied BTC address for an attacker's, the system detects the delta and resets it to a safety warning.
*   **Exposure Prevention**: Alerts you if sensitive keys (RSA, AWS Secrets) are copied while suspicious background activity is detected.

### ⚡️ Active Counter-Response (Honeypotting)
*   **Attacker Identification**: If a remote hijack is detected via a debug port, the system automatically traces the **Remote IP address** of the attacker.
*   **Forensic Scare Messages**: Instead of a generic warning, the system overwrites the clipboard with a targeted message: `[SOVEREIGN_SEC_LOG]: ATTACKER IP [IP] LOGGED. WE HAVE YOUR FINGERPRINT.`
*   **Aggressive Alerts**: Vocalizes a severe warning: *"Active hijack confirmed. Attacker location traced. Forensic counter-measures initiated."*
When a threat is neutralized, the system automatically initiates a deep-dive audit:
*   **Persistence Audit**: Scans `~/Library/LaunchAgents` for malicious persistence.
*   **Network Sentry**: Scans for listening debugger ports that bypassed process checks.
*   **Malware Pulse**: Triggers an automated `clamscan` of high-risk directories (`~/Downloads`, `/tmp`).

---

## 🚀 Installation & Setup

### 1. Configure Your Secret
Sovereign Guard uses a secret key to authorize "Safe Mode" and prevent malware from disabling the monitor.
```bash
cp .env.example .env.sovereign
# Edit .env.sovereign and set a strong SOVEREIGN_SECRET
nano .env.sovereign
```

### 2. Run the Initializer
The setup script creates a Python virtual environment, installs dependencies, and configures the macOS LaunchAgent.
```bash
./setup.sh
```

### 3. Verify OS Hardening
Run the audit tool to ensure your macOS settings are optimized.
```bash
./sovereign scan
```

---

## ⚡️ Quick Controls

Use the `sovereign` CLI to manage your perimeter.

| Command | Action |
| :--- | :--- |
| `./sovereign start` | Launch the background monitor |
| `./sovereign status` | View perimeter health and active mode |
| `./sovereign dev` | Enable **Safe Mode** (Suspends auto-kill for debugging) |
| `./sovereign secure`| Re-arm the **Active Defense** |
| `./sovereign scan` | Perform a one-time security audit |
| `./sovereign stop` | Disable the monitor |

---

## 📜 Technical Details & Logs

*   **Logs**: Audit-trail is stored in `guard_monitor.log` and `guard_monitor.out`.
*   **Remediation**: Uses terminal `pkill` and macOS `say` for instant feedback.
*   **Voice**: Provides vocal alerts via the macOS "Samantha" voice for hands-free threat awareness.

**Stay Sovereign. Stay Secure.**
