"""Central route registration for API server."""


def register_routes(app, deps):
    """Register all HTTP and WebSocket routes from implementation functions."""
    app.add_api_route("/", deps["root"], methods=["GET"])
    app.add_api_route("/ping", deps["ping"], methods=["GET"])
    app.add_api_route("/health", deps["health_check_endpoint"], methods=["GET"])
    app.add_api_route("/health/detailed", deps["detailed_health_check"], methods=["GET"])
    app.add_api_route("/metrics", deps["get_metrics"], methods=["GET"])
    app.add_api_route("/info", deps["get_api_info"], methods=["GET"])

    app.add_api_route("/session/start", deps["start_session"], methods=["POST"])
    app.add_api_route("/session/{session_id}/execute", deps["execute_session"], methods=["POST"])
    app.add_api_route("/session/{session_id}/stop", deps["stop_session"], methods=["POST"])
    app.add_api_route("/prompt/execute", deps["execute_custom_prompt"], methods=["POST"])
    app.add_api_route("/session/{session_id}/stats", deps["get_session_stats"], methods=["GET"])

    app.add_api_route("/dashboard/live-sessions", deps["get_live_sessions"], methods=["GET"])
    app.add_api_route("/dashboard/historical-sessions", deps["get_historical_sessions"], methods=["GET"])
    app.add_api_route("/dashboard/compare-models", deps["compare_model_versions"], methods=["GET"])
    app.add_api_route("/dashboard/export/{session_id}", deps["export_session_results"], methods=["GET"])

    app.add_api_route("/auth/login", deps["login"], methods=["POST"])
    app.add_api_route("/auth/register", deps["register"], methods=["POST"])
    app.add_api_route("/auth/users", deps["list_users"], methods=["GET"])
    app.add_api_route("/auth/validate-llm-key", deps["validate_llm_key"], methods=["POST"])

    app.add_api_route("/remote/start-run", deps["start_remote_run"], methods=["POST"])
    app.add_api_route("/remote/config/save", deps["save_experiment_config"], methods=["POST"])
    app.add_api_route("/remote/config/list", deps["list_experiment_configs"], methods=["GET"])
    app.add_api_route("/remote/config/{config_id}", deps["get_experiment_config"], methods=["GET"])
    app.add_api_route("/remote/config/{config_id}", deps["delete_experiment_config"], methods=["DELETE"])

    app.add_api_websocket_route("/ws", deps["websocket_endpoint"])
