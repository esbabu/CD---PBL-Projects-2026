import time
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_create_and_poll_run():
    payload = {
        "mode": "optimize",
        "language": "cpp",
        "source_code": "int sumArray(int* arr, int n) { int sum; for(int i=0; i<=n; i++) sum += arr[i]; return sum; }",
        "inference_mode": "heuristics",
        "options": {"force_mock": True}
    }
    res = client.post("/api/runs", json=payload)
    assert res.status_code == 202
    data = res.json()
    assert "run_id" in data
    run_id = data["run_id"]
    assert data["mode"] == "optimize"

    # Poll status until completed
    status_data = None
    for _ in range(30):
        time.sleep(0.1)
        res_status = client.get(f"/api/runs/{run_id}")
        assert res_status.status_code == 200
        status_data = res_status.json()
        if status_data["status"] == "completed":
            break

    assert status_data["status"] == "completed"

    # Check results
    res_results = client.get(f"/api/runs/{run_id}/results")
    assert res_results.status_code == 200
    res_data = res_results.json()
    assert res_data["run_id"] == run_id
    assert res_data["optimization_result"] is not None
    assert res_data["security_result"] is None

def test_api_cancel_run():
    payload = {
        "mode": "pipeline",
        "language": "cpp",
        "source_code": "int main() { return 0; }",
        "inference_mode": "heuristics",
        "options": {}
    }
    res = client.post("/api/runs", json=payload)
    assert res.status_code == 202
    run_id = res.json()["run_id"]

    cancel_res = client.post(f"/api/runs/{run_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"
