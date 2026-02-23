#!/usr/bin/env python3
import argparse
import subprocess
import shutil
import os
import json
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(filename="chitragupt.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def check_command_exists(command):
    """Check if a command exists in the system PATH."""
    return shutil.which(command.split()[0]) is not None

def normalize_url(url):
    """Normalize URL for all tools. Ensures it starts with http:// or https://"""
    if not url.startswith(("http://", "https://")):
        return "http://" + url
    return url

def run_command(command, target, output_format="txt", outdir="results"):
    """Run a command with the target and save output to a file inside target-specific folder."""
    cmd_list = command.split() + [target]
    base_cmd = command.split()[0]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create per-target folder
    target_folder = os.path.join(outdir, target.replace("http://", "").replace("https://", "").replace("/", "_"))
    os.makedirs(target_folder, exist_ok=True)

    filename = os.path.join(target_folder, f"{base_cmd}_{timestamp}.{output_format}")

    print(f"[+] Running: {' '.join(cmd_list)}")

    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        output = result.stdout + result.stderr

        with open(filename, "w") as f:
            f.write(output)

        print(f"[+] Output saved to {filename}")
        logging.info(f"Command '{command}' executed successfully, output saved to {filename}")
        return filename
    except Exception as e:
        print(f"[-] Error running {command}: {e}")
        logging.error(f"Error running {command}: {e}")
        return None

def load_tools(config_file="tools.json"):
    """Load tool configuration from JSON file."""
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[-] Error loading {config_file}: {e}")
        logging.error(f"Error loading {config_file}: {e}")
        return []

def generate_summary(target, outdir="results", summary_file="summary_report.txt"):
    """Generate a consolidated summary report from all tool outputs for a specific target."""
    target_folder = os.path.join(outdir, target.replace("http://", "").replace("https://", "").replace("/", "_"))
    summary_path = os.path.join(target_folder, summary_file)
    findings = {
        "open_ports": [],
        "directories": [],
        "technologies": [],
        "errors": []
    }

    with open(summary_path, "w") as summary:
        summary.write("=== Chitragupt Recon Summary Report ===\n")
        summary.write(f"Target: {target}\n")
        summary.write(f"Generated on: {datetime.datetime.now()}\n\n")

        for file in sorted(os.listdir(target_folder)):
            if file.endswith((".txt", ".json", ".xml")) and file != summary_file:
                summary.write(f"\n--- {file} ---\n")
                try:
                    with open(os.path.join(target_folder, file), "r") as f:
                        content = f.read()
                        lines = content.splitlines()

                        # Extract keywords
                        for line in lines:
                            if "open" in line and "/" in line:
                                findings["open_ports"].append(line.strip())
                            if "==>" in line or "FOUND" in line:
                                findings["directories"].append(line.strip())
                            if "Technology" in line or "CMS" in line or "Server:" in line:
                                findings["technologies"].append(line.strip())
                            if "error" in line.lower() or "failed" in line.lower():
                                findings["errors"].append(line.strip())

                        preview = "\n".join(lines[:20])
                        summary.write(preview + "\n")
                        if len(lines) > 20:
                            summary.write("... [truncated]\n")

                except Exception as e:
                    summary.write(f"Error reading {file}: {e}\n")

        # Structured findings
        summary.write("\n=== Extracted Findings ===\n")
        summary.write("\nOpen Ports:\n" + "\n".join(findings["open_ports"]) if findings["open_ports"] else "\nOpen Ports: None")
        summary.write("\n\nDirectories:\n" + "\n".join(findings["directories"]) if findings["directories"] else "\nDirectories: None")
        summary.write("\n\nTechnologies:\n" + "\n".join(findings["technologies"]) if findings["technologies"] else "\nTechnologies: None")
        summary.write("\n\nErrors:\n" + "\n".join(findings["errors"]) if findings["errors"] else "\nErrors: None")

    print(f"[+] Summary report generated: {summary_path}")
    logging.info(f"Summary report generated at {summary_path}")

def update_index(outdir="results", index_file="index.txt", html_file="index.html"):
    """Update or create index files (text + HTML) listing all scanned targets."""
    index_path = os.path.join(outdir, index_file)
    html_path = os.path.join(outdir, html_file)
    os.makedirs(outdir, exist_ok=True)

    # Collect all target folders
    targets = [d for d in os.listdir(outdir) if os.path.isdir(os.path.join(outdir, d))]

    # --- Text Index ---
    with open(index_path, "w") as index:
        index.write("=== Chitragupt Recon Index ===\n")
        index.write(f"Generated on: {datetime.datetime.now()}\n\n")
        index.write("Targets Scanned:\n----------------\n")

        for i, target in enumerate(sorted(targets), 1):
            summary_path = os.path.join(outdir, target, "summary_report.txt")
            index.write(f"{i}. {target}\n")
            index.write(f"   Summary: {summary_path}\n")
            index.write(f"   Outputs: {os.path.join(outdir, target)}\n\n")

    # --- HTML Index ---
    with open(html_path, "w") as html:
        html.write("<!DOCTYPE html>\n<html>\n<head>\n")
        html.write("<meta charset='UTF-8'>\n<title>Chitragupt Recon Index</title>\n")
        html.write("<style>body{font-family:Arial;} h1{color:#333;} ul{line-height:1.6;}</style>\n")
        html.write("</head>\n<body>\n")
        html.write("<h1>Chitragupt Recon Index</h1>\n")
        html.write(f"<p>Generated on: {datetime.datetime.now()}</p>\n")
        html.write("<ul>\n")

        for target in sorted(targets):
            summary_rel = os.path.join(target, "summary_report.txt")
            html.write(f"<li><strong>{target}</strong><br>")
            html.write(f"Summary: <a href='{summary_rel}'>{summary_rel}</a><br>")
            html.write(f"Outputs: {os.path.join(outdir, target)}</li><br>\n")

        html.write("</ul>\n</body>\n</html>")

    print(f"[+] Index updated: {index_path}, {html_path}")
    logging.info(f"Index updated at {index_path} and {html_path}")

def main():
    parser = argparse.ArgumentParser(description="Chitragupt - Web Recon Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL (example.com)")
    parser.add_argument("-o", "--outdir", default="results", help="Output directory")
    args = parser.parse_args()

    target = args.url.strip()
    tools = load_tools()

    tasks = []
    output_files = []
    with ThreadPoolExecutor() as executor:
        for tool in tools:
            command = tool["command"]
            base_cmd = command.split()[0]

            if not check_command_exists(base_cmd):
                print(f"[-] Error: '{base_cmd}' is not installed or not in PATH. Please install it before running.")
                continue

            run_target = normalize_url(target) if tool.get("normalize_url", False) else target

            if tool.get("requires_root", False) and os.geteuid() != 0:
                print(f"[!] Info: '{base_cmd}' may require root privileges for full functionality. Run with sudo if needed.")

            tasks.append(executor.submit(run_command, command, run_target,
                                         tool.get("output_format", "txt"), args.outdir))

        for task in tasks:
            result = task.result()
            if result:
                output_files.append(result)

    generate_summary(target, args.outdir)
    update_index(args.outdir)
    print(f"[+] Recon completed. Results stored in {args.outdir}/{target}/")

if __name__ == "__main__":
    main()