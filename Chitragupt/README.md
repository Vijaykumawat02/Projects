Here’s a **GitHub-ready README.md template** for your recon framework **Chitragupt**. It’s structured, professional, and easy for others to understand and use right away.

---

# 🕵️‍♂️ Chitragupt – Web Recon Framework

## 📌 Overview
**Chitragupt** is a Python-based web reconnaissance framework designed for bug bounty hunters and penetration testers.  
It automates the execution of multiple recon tools, organizes outputs per target, and generates structured summary reports with keyword extraction for quick insights.

---

## ✨ Features
- 🔧 **Config-driven workflow** – Define tools in `tools.json`.
- ✅ **Dependency checks** – Ensures tools are installed before execution.
- 🔒 **Privilege awareness** – Warns if a tool requires root privileges.
- 📂 **Per-target folder organization** – Results stored in `results/<target>/`.
- ⚡ **Parallel execution** – Runs multiple tools simultaneously.
- 🕑 **Timestamped outputs** – Prevents overwriting results.
- 📊 **Summary report generation** – Consolidates findings into one file.
- 🔍 **Keyword extraction** – Highlights open ports, directories, technologies, and errors.
- 📝 **Logging** – Persistent logs stored in `chitragupt.log`.

---

## 📦 Installation

### Requirements
- Python 3.7+
- Recon tools installed and accessible in `$PATH` (e.g., `nmap`, `dirb`, `whatweb`).

### Setup
```bash
git clone https://github.com/<your-username>/chitragupt.git
cd chitragupt
chmod +x chitragupt.py
```

---

## 🚀 Usage

### Basic Command
```bash
python3 chitragupt.py -u example.com
```

### Options
- `-u, --url` → Target domain (required).
- `-o, --outdir` → Output directory (default: `results/`).

### Example
```bash
python3 chitragupt.py -u testsite.com -o outputs
```

This will create:
```
outputs/
└── testsite.com/
    ├── nmap_20260223.txt
    ├── dirb_20260223.txt
    ├── whatweb_20260223.json
    └── summary_report.txt
```

---

## ⚙️ Configuration (`tools.json`)

Define tools in a JSON file:

```json
[
  {
    "command": "nmap -Pn -T4",
    "normalize_url": false,
    "requires_root": true,
    "output_format": "txt"
  },
  {
    "command": "dirb",
    "normalize_url": true,
    "requires_root": false,
    "output_format": "txt"
  },
  {
    "command": "whatweb",
    "normalize_url": true,
    "requires_root": false,
    "output_format": "json"
  }
]
```

### Fields
- **command** → Tool command with arguments.
- **normalize_url** → Add `http://` if missing.
- **requires_root** → Warn if root privileges are needed.
- **output_format** → File format (`txt`, `json`, `xml`).

---

## 📂 Output Structure
Each target has its own folder:
```
results/
├── index.txt
├── index.html
└── example.com/
    ├── nmap_20260223.txt
    ├── dirb_20260223.txt
    ├── whatweb_20260223.json
    └── summary_report.txt
```

---

## 📊 Summary Report
The tool generates a **summary_report.txt** per target.

### Example:
```
=== Chitragupt Recon Summary Report ===
Target: example.com
Generated on: 2026-02-23 17:25:00

--- nmap_20260223.txt ---
PORT     STATE SERVICE
80/tcp   open  http
443/tcp  open  https
... [truncated]

--- dirb_20260223.txt ---
==> DIRECTORY: http://example.com/admin/
==> DIRECTORY: http://example.com/uploads/
... [truncated]

--- whatweb_20260223.json ---
Technology: Apache/2.4.41
CMS: WordPress 6.0
... [truncated]

=== Extracted Findings ===
Open Ports:
80/tcp   open  http
443/tcp  open  https

Directories:
==> DIRECTORY: http://example.com/admin/
==> DIRECTORY: http://example.com/uploads/

Technologies:
Technology: Apache/2.4.41
CMS: WordPress 6.0

Errors:
None
```

---

## 📝 Logging
Execution logs are stored in `chitragupt.log`:
- Successful tool runs
- Errors encountered
- Summary generation events

---

## 🔧 Extending the Tool
- Add new tools in `tools.json`.
- Adjust keyword extraction rules in `generate_summary()` for custom parsing.
- Integrate advanced parsers (e.g., XML/JSON parsing for structured tools).
- Add an **index file** at the root to track multiple targets.

---

## ⚠️ Best Practices
- Run with `sudo` if using tools that require root (e.g., `nmap` with certain flags).
- Keep `tools.json` minimal to avoid noisy outputs.
- Use the summary report for **quick triage**, then dive into detailed files for deeper analysis.
- Archive old results for long-term engagements.

---

## 📜 License
MIT License – Free to use, modify, and distribute.