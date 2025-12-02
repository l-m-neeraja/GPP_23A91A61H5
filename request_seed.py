import sys
import json
import requests

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def main():
    if len(sys.argv) != 3:
        print("Usage: python request_seed.py <STUDENT_ID> <GITHUB_REPO_URL>")
        sys.exit(1)

    student_id = sys.argv[1]
    github_repo_url = sys.argv[2]

    with open("keys/student_public.pem", "r") as f:
        pub = f.read().strip()

    pub_escaped = pub.replace("\n", "\\n")

    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": pub_escaped,
    }

    print("Sending request to instructor API...")
    try:
        resp = requests.post(API_URL, json=payload, timeout=15)
    except Exception as e:
        print("Request failed:", e)
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
        print("Did not receive encrypted_seed. Check the error above.")
        sys.exit(1)

    encrypted_seed = data["encrypted_seed"]

    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("✅ Saved encrypted seed to encrypted_seed.txt (DO NOT git add this file).")

if __name__ == "__main__":
    main()
