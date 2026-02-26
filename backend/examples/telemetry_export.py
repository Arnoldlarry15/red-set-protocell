"""
Red Set ProtoCell - Telemetry Export Examples

Shows telemetry export capabilities.
"""

import logging
from datetime import datetime

from app.telemetry import (
    ExportFormat,
    SessionMetricsExtractor,
    TelemetryExporter,
    create_metrics_snapshot,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_csv_export():
    """Show CSV export functionality."""
    logger.info("=== CSV Export Example ===")

    exporter = TelemetryExporter(output_dir="example_exports")

    # Sample metrics data
    data = [
        {
            "round": 1,
            "score": 0.23,
            "blocked": False,
            "domain": "injection",
        },
        {
            "round": 2,
            "score": 0.45,
            "blocked": False,
            "domain": "jailbreak",
        },
        {
            "round": 3,
            "score": 0.89,
            "blocked": True,
            "domain": "csam",
        },
    ]

    # Export to CSV
    filepath = exporter.export(
        data=data, format=ExportFormat.CSV, filename="example_metrics.csv"
    )

    logger.info(f"Exported to: {filepath}")


def run_json_export():
    """Show JSON export functionality."""
    logger.info("\n=== JSON Export Example ===")

    exporter = TelemetryExporter(output_dir="example_exports")

    # Sample session summary
    data = {
        "session_id": "rsp_example_20260109",
        "total_rounds": 50,
        "average_score": 0.34,
        "critical_findings": 2,
        "high_findings": 5,
        "model_version": "gpt-3.5-turbo",
    }

    # Export to JSON
    filepath = exporter.export(
        data=data, format=ExportFormat.JSON, filename="example_session.json"
    )

    logger.info(f"Exported to: {filepath}")


def run_metrics_extraction():
    """Show metrics extraction from database."""
    logger.info("\n=== Metrics Extraction Example ===")

    extractor = SessionMetricsExtractor()

    logger.info("Metrics extraction capabilities:")
    logger.info("- Extract session-level metrics from database")
    logger.info("- Extract round-level metrics")
    logger.info("- Generate time series data")
    logger.info("- List all sessions with filters")
    logger.info("- Export in multiple formats (CSV, JSON, JSON Lines)")


def run_metrics_snapshot():
    """Show metrics snapshot creation."""
    logger.info("\n=== Metrics Snapshot Example ===")

    snapshot = create_metrics_snapshot(
        session_id="rsp_example_20260109",
        metrics={
            "total_rounds": 50,
            "average_score": 0.34,
            "blocked_count": 3,
        },
        metadata={
            "model": "gpt-3.5-turbo",
            "backend": "openai",
        },
    )

    logger.info(f"Snapshot created at: {snapshot.timestamp}")
    logger.info(f"Session ID: {snapshot.session_id}")
    logger.info(f"Metrics: {snapshot.metrics}")


def main():
    """Main function."""
    print("\n" + "=" * 60)
    print("Red Set ProtoCell - Telemetry Export Examples")
    print("=" * 60 + "\n")

    print("This shows the new telemetry export capabilities:")
    print("1. Export metrics to CSV for spreadsheet analysis")
    print("2. Export metrics to JSON for programmatic processing")
    print("3. Extract metrics from session database")
    print("4. Create metrics snapshots")
    print("\n")

    run_csv_export()
    run_json_export()
    run_metrics_extraction()
    run_metrics_snapshot()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("See 'example_exports'/' directory for exported files")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
