# frontend/ren_cli.py
import requests

API_URL = "http://127.0.0.1:5001"

def ask_ren():
    print("🧠 Talk to Ren. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Ren: Until next time.")
            break

        try:
            res = requests.post(f"{API_URL}/ask", json={"message": user_input})
            res.raise_for_status()
            reply = res.json().get("response", "[No response]")
            print(f"Ren: {reply}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    ask_ren()