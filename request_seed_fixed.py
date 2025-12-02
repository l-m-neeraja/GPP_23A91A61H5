#!/usr/bin/env python3
import sys, os, json, requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def read_and_normalize_pem(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    raw = open(path, "rb").read()
    # decode robustly and normalize CRLF -> LF
    text = raw.decode("utf-8", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    return text.strip() + "\n"  # ensure final newline

def main():
    if len(sys.argv) != 3:
        print("Usage: python request_seed_fixed.py <STUDENT_ID> <GITHUB_REPO_URL>")
        sys.exit(1)

    student_id = sys.argv[1]
    github_repo_url = sys.argv[2]

    pem_path = "keys/student_public.pem"
    try:
        pub = read_and_normalize_pem(pem_path)
    except Exception as e:
        print("Error reading public key:", e, file=sys.stderr)
        sys.exit(2)

    # basic validation
    if not (pub.startswith("-----BEGIN PUBLIC KEY-----") and "-----END PUBLIC KEY-----" in pub):
        print("Public key doesn't look like a PEM public key. Check keys/student_public.pem", file=sys.stderr)
        print("First 200 chars of file:")
        print(pub[:200])
        sys.exit(2)

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": pub   # <-- raw PEM with real newlines
    }

    print("Sending request to instructor API...")
    try:
        resp = requests.post(API_URL, json=payload, timeout=20)
    except Exception as e:
        print("Request failed:", e, file=sys.stderr)
        sys.exit(1)

    print("Status code:", resp.status_code)
    try:
        data = resp.json()
    except Exception:
        print("Response was not JSON:")
        print(resp.text)
        sys.exit(1)

    print("Response JSON:", json.dumps(data, indent=2))

    if data.get("status") != "success" or "encrypted_seed" not in data:
        print("Did not receive encrypted_seed. Check the response above.", file=sys.stderr)
        sys.exit(1)

    enc = data["encrypted_seed"]
    with open("encrypted_seed.txt", "w") as f:
        f.write(enc)
    os.chmod("encrypted_seed.txt", 0o600)
    print("✅ Saved encrypted seed to encrypted_seed.txt (DO NOT git add this file).")

if __name__ == "__main__":
    main()
