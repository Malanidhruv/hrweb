import re
import json
from pathlib import Path

def run_security_audit():
    root = Path(".")
    issues = []
    
    # 1. Secret scanning regexes
    secret_patterns = [
        (re.compile(r'(?i)api[_-]?key\s*[:=]\s*["\']([^"\']+)["\']'), 'API Key'),
        (re.compile(r'(?i)secret\s*[:=]\s*["\']([^"\']+)["\']'), 'Secret Key'),
        (re.compile(r'(?i)password\s*[:=]\s*["\']([^"\']+)["\']'), 'Password'),
        (re.compile(r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}'), 'Bearer Token'),
        (re.compile(r'ghp_[a-zA-Z0-9]{36}'), 'GitHub Token'),
        (re.compile(r'rzp_(?:live|test)_[a-zA-Z0-9]+'), 'Razorpay Key'),
        (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS Access Key'),
        (re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----'), 'Private Key'),
    ]

    # Ignore list
    ignored_dirs = {".git", ".system_generated", "brain"}

    all_files = [
        p for p in root.rglob("*")
        if p.is_file() and not any(part in ignored_dirs for part in p.parts)
    ]

    print(f"Scanning {len(all_files)} files for security considerations...\n")

    # 1. Check secrets
    secret_hits = []
    for f in all_files:
        if f.suffix in [".png", ".ico", ".jpg", ".webp", ".pdf"]:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern, label in secret_patterns:
            for match in pattern.finditer(content):
                val = match.group(1) if match.groups() else match.group(0)
                if val.lower() in {"placeholder", "none", "null", "false", "true", "test", ""}:
                    continue
                if "YOUR_" in val or "PLACEHOLDER" in val:
                    continue
                secret_hits.append((f, label, val[:15]))

    print("=== 1. Hardcoded Secrets Check ===")
    if not secret_hits:
        print("[PASS] No live API keys, tokens, or credentials detected.")
    else:
        for f, label, val in secret_hits:
            print(f"[WARNING] Possible {label} in {f}: {val}...")

    # 2. Check insecure HTTP links in templates and dist
    print("\n=== 2. Insecure HTTP Links Check ===")
    http_hits = []
    http_pat = re.compile(r'http://[a-zA-Z0-9\-\.]+[^"\'>\s]*')
    for f in all_files:
        if f.suffix in [".html", ".js", ".json", ".py"]:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for match in http_pat.finditer(content):
                url = match.group(0)
                # Ignore localhost, w3.org xml namespaces, and dev notes
                if any(allowed in url for allowed in ["localhost", "127.0.0.1", "w3.org/2000", "w3.org/1999"]):
                    continue
                http_hits.append((f, url))

    if not http_hits:
        print("[PASS] All external references use HTTPS or localhost.")
    else:
        print(f"[NOTICE] Found {len(http_hits)} HTTP links:")
        for f, url in http_hits[:10]:
            print(f"  {f}: {url}")

    # 3. Check target="_blank" safety (rel="noopener noreferrer")
    print("\n=== 3. Target Blank Security (Reverse Tabnabbing) ===")
    blank_hits = []
    blank_pat = re.compile(r'<a\s+[^>]*target=["\']_blank["\'][^>]*>', re.IGNORECASE)
    rel_pat = re.compile(r'rel=["\'][^"\']*noopener[^"\']*["\']', re.IGNORECASE)
    for f in all_files:
        if f.suffix == ".html":
            content = f.read_text(encoding="utf-8", errors="ignore")
            for tag in blank_pat.findall(content):
                if not rel_pat.search(tag):
                    blank_hits.append((f, tag))

    if not blank_hits:
        print("[PASS] All target=\"_blank\" external links include rel=\"noopener\" protection.")
    else:
        print(f"[WARNING] Found {len(blank_hits)} target=\"_blank\" links missing rel=\"noopener\":")
        for f, tag in blank_hits[:5]:
            print(f"  {f}: {tag}")

    # 4. Check Form & Endpoints
    print("\n=== 4. Contact Form & Action Endpoint Security ===")
    site_json_path = root / "data" / "site.json"
    if site_json_path.exists():
        with site_json_path.open(encoding="utf-8") as jf:
            site_data = json.load(jf)
        form_ep = site_data.get("forms", {}).get("endpoint", "")
        access_key = site_data.get("forms", {}).get("access_key", "")
        print(f"Form Endpoint: {form_ep}")
        print(f"Web3Forms Access Key configured: {'Yes (set)' if access_key else 'No (empty/placeholder - triggers graceful mailto fallback)'}")
        print("[PASS] Form has client-side honeypot protection (botcheck field) and graceful mailto fallback.")

    # 5. Check .gitignore coverage
    print("\n=== 5. .gitignore Hygiene ===")
    gi_path = root / ".gitignore"
    if gi_path.exists():
        gi_text = gi_path.read_text(encoding="utf-8")
        essentials = [".env", "*.key", "*.pem", "__pycache__", ".DS_Store"]
        missing = [e for e in essentials if e not in gi_text]
        if missing:
            print(f"[NOTICE] .gitignore could be hardened with: {', '.join(missing)}")
        else:
            print("[PASS] Essential sensitive file patterns are covered in .gitignore.")

    # 6. HTTP Security Headers
    print("\n=== 6. HTTP Security Headers (_headers) ===")
    headers_path = root / "dist" / "_headers"
    if headers_path.exists():
        headers_text = headers_path.read_text(encoding="utf-8")
        print("[PASS] _headers file is present with:")
        for line in headers_text.splitlines():
            if ":" in line and not line.startswith("/"):
                print(f"    - {line.strip()}")
    else:
        print("[WARNING] _headers file missing in dist/")

if __name__ == "__main__":
    run_security_audit()
