import urllib.request
import json
import time

def test(energy):
    t0 = time.time()
    payload = {
        "code": open("tests/secure.c").read(),
        "filename": "secure.c",
        "energy": energy
    }
    req = urllib.request.Request(
        "http://127.0.0.1:5050/api/compile",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed = time.time() - t0
    print(f"Energy={energy}: took {elapsed:.3f}s | ok={data.get('ok')} | energy_available={data.get('energy', {}).get('available')}")

if __name__ == "__main__":
    print("Testing energy=False...")
    test(False)
    print("\nTesting energy=True...")
    test(True)
