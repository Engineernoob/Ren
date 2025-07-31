import requests

API_BASE = "http://localhost:5001"

def ask_text():
    print("🟢 Ren CLI – Type your message (type 'exit' to quit):")
    while True:
        msg = input("> ").strip()
        if msg.lower() in ["exit", "quit"]:
            print("👋 Goodbye.")
            break
        if not msg:
            continue

        try:
            response = requests.post(
                f"{API_BASE}/ask",
                json={"message": msg}
            )
            if response.ok:
                data = response.json()
                print(f"🧠 Ren: {data['response']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    ask_text()