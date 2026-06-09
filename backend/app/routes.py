"""Central route registration for API server."""


def register_routes(app, deps):
    """Register all HTTP and WebSocket routes from implementation functions."""

    route_definitions = [
        ("/", deps["root"], ["GET"]),
        ("/ping", deps["ping"], ["GET"]),
        ("/health", deps["health_check_endpoint"], ["GET"]),
        ("/health/detailed", deps["detailed_health_check"], ["GET"]),
        ("/metrics", deps["get_metrics"], ["GET"]),
        ("/info", deps["get_api_info"], ["GET"]),
        ("/session/start", deps["start_session"], ["POST"]),
        ("/session/{session_id}/execute", deps["execute_session"], ["POST"]),
        ("/session/{session_id}/stop", deps["stop_session"], ["POST"]),
        ("/prompt/execute", deps["execute_custom_prompt"], ["POST"]),
        ("/session/{session_id}/stats", deps["get_session_stats"], ["GET"]),
        ("/dashboard/live-sessions", deps["get_live_sessions"], ["GET"]),
        ("/dashboard/historical-sessions", deps["get_historical_sessions"], ["GET"]),
        ("/dashboard/compare-models", deps["compare_model_versions"], ["GET"]),
        ("/dashboard/export/{session_id}", deps["export_session_results"], ["GET"]),
        ("/early-access", deps["submit_early_access"], ["POST"]),
        ("/admin/early-access-signups", deps["list_early_access_signups"], ["GET"]),
        ("/admin/early-access-signups/export", deps["export_early_access_signups"], ["GET"]),
        ("/admin/early-access-signups/{signup_id}", deps["delete_early_access_signup"], ["DELETE"]),
        ("/admin/early-access-signups/{signup_id}/verify", deps["verify_early_access_signup"], ["POST"]),
        ("/auth/login", deps["login"], ["POST"]),
        ("/auth/register", deps["register"], ["POST"]),
        ("/auth/users", deps["list_users"], ["GET"]),
        ("/auth/validate-llm-key", deps["validate_llm_key"], ["POST"]),
        ("/remote/start-run", deps["start_remote_run"], ["POST"]),
        ("/remote/config/save", deps["save_experiment_config"], ["POST"]),
        ("/remote/config/list", deps["list_experiment_configs"], ["GET"]),
        ("/remote/config/{config_id}", deps["get_experiment_config"], ["GET"]),
        ("/remote/config/{config_id}", deps["delete_experiment_config"], ["DELETE"]),
        ("/github/prs", deps["list_github_prs"], ["POST"]),
        ("/github/prs/{pr_number}/close", deps["close_github_pr"], ["POST"]),
        ("/github/prs/{pr_number}/merge", deps["merge_github_pr"], ["POST"]),
    ]

    # Backward-compatible API contract:
    # - Historically some clients used /api/* paths
    # - Current frontend/backend may use bare paths (e.g. /health)
    # Register both so clients remain stable while docs converge.
    for prefix in ("", "/api"):
        for path, endpoint, methods in route_definitions:
            if prefix == "/api" and path == "/":
                # Avoid creating /api/ root alias
                continue
            app.add_api_route(f"{prefix}{path}", endpoint, methods=methods)

    for prefix in ("", "/api"):
        app.add_api_websocket_route(f"{prefix}/ws", deps["websocket_endpoint"])
