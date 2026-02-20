from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes import register_routes


def _json_response(payload):
    async def _handler():
        return payload

    return _handler


def _minimal_deps():
    return {
        "root": _json_response({"ok": True}),
        "ping": _json_response({"ok": True}),
        "health_check_endpoint": _json_response({"status": "healthy"}),
        "detailed_health_check": _json_response({"status": "healthy"}),
        "get_metrics": _json_response({}),
        "get_api_info": _json_response({}),
        "start_session": _json_response({}),
        "execute_session": _json_response({}),
        "stop_session": _json_response({}),
        "execute_custom_prompt": _json_response({}),
        "get_session_stats": _json_response({}),
        "get_live_sessions": _json_response({}),
        "get_historical_sessions": _json_response({}),
        "compare_model_versions": _json_response({}),
        "export_session_results": _json_response({}),
        "login": _json_response({}),
        "register": _json_response({}),
        "list_users": _json_response({}),
        "validate_llm_key": _json_response({}),
        "start_remote_run": _json_response({}),
        "save_experiment_config": _json_response({}),
        "list_experiment_configs": _json_response({}),
        "get_experiment_config": _json_response({}),
        "delete_experiment_config": _json_response({}),
        "websocket_endpoint": lambda websocket: None,
    }


def test_health_route_available_with_and_without_api_prefix():
    app = FastAPI()
    register_routes(app, _minimal_deps())
    client = TestClient(app)

    plain = client.get("/health")
    prefixed = client.get("/api/health")

    assert plain.status_code == 200
    assert prefixed.status_code == 200
    assert plain.json() == prefixed.json() == {"status": "healthy"}
