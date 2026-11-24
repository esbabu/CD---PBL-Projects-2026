import os

from backend.app import app

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    print("\n" + "=" * 60)
    print("  🚀 AST Studio Server is Running!")
    print(f"  👉 Open in your browser: {url}")
    print("  (Keep this terminal open while using the app)")
    print("  To stop the server, press Ctrl+C")
    print("=" * 60 + "\n")
    app.run(host=HOST, port=PORT, debug=app.config["DEBUG"])
