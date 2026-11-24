from starlette.testclient import TestClient
from app.main import app

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["adapters"]["optimization"] in ("real", "mock")
    assert data["adapters"]["security"] in ("real", "mock")
    assert data["llm_connection"] in ("connected", "unreachable", "no_models", "not_configured")
    assert "ollama" in data
    assert "toolchains" in data
    assert "javascript" in data["supported_languages"]
    assert "pipeline" in data["supported_modes"]
    assert "optimize" in data["supported_modes"]
    assert "security" in data["supported_modes"]
