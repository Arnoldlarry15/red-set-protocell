"""
Red Set ProtoCell - Telemetry Export Demo

Demonstrates telemetry export capabilities.
"""

import logging
from datetime import datetime

from app.telemetry import (
    TelemetryExporter,
    ExportFormat,
    SessionMetricsExtractor,
    create_metrics_snapshot,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def demo_csv_export():
    """Demonstrate CSV export functionality."""
    logger.info("=== CSV Export Demo ===")
    
    exporter = TelemetryExporter(output_dir="demo_exports")
    
    # Sample metrics data
    data = [
        {
            'round': 1,
            'score': 0.23,
            'blocked': False,
            'domain': 'injection',
        },
        {
            'round': 2,
            'score': 0.45,
            'blocked': False,
            'domain': 'jailbreak',
        },
        {
            'round': 3,
            'score': 0.89,
            'blocked': True,
            'domain': 'csam',
        },
    ]
    
    # Export to CSV
    filepath = exporter.export(
        data=data,
        format=ExportFormat.CSV,
        filename="demo_metrics.csv"
    )
    
    logger.info(f"Exported to: {filepath}")


def demo_json_export():
    """Demonstrate JSON export functionality."""
    logger.info("\n=== JSON Export Demo ===")
    
    exporter = TelemetryExporter(output_dir="demo_exports")
    
    # Sample session summary
    data = {
        'session_id': 'rsp_demo_20260109',
        'total_rounds': 50,
        'average_score': 0.34,
        'critical_findings': 2,
        'high_findings': 5,
        'model_version': 'gpt-3.5-turbo',
    }
    
    # Export to JSON
    filepath = exporter.export(
        data=data,
        format=ExportFormat.JSON,
        filename="demo_session.json"
    )
    
    logger.info(f"Exported to: {filepath}")


def demo_metrics_extraction():
    """Demonstrate metrics extraction from database."""
    logger.info("\n=== Metrics Extraction Demo ===")
    
    extractor = SessionMetricsExtractor()
    
    logger.info("Metrics extraction capabilities:")
    logger.info("- Extract session-level metrics from database")
    logger.info("- Extract round-level metrics")
    logger.info("- Generate time series data")
    logger.info("- List all sessions with filters")
    logger.info("- Export in multiple formats (CSV, JSON, JSON Lines)")


def demo_metrics_snapshot():
    """Demonstrate metrics snapshot creation."""
    logger.info("\n=== Metrics Snapshot Demo ===")
    
    snapshot = create_metrics_snapshot(
        session_id="rsp_demo_20260109",
        metrics={
            'total_rounds': 50,
            'average_score': 0.34,
            'blocked_count': 3,
        },
        metadata={
            'model': 'gpt-3.5-turbo',
            'backend': 'openai',
        }
    )
    
    logger.info(f"Snapshot created at: {snapshot.timestamp}")
    logger.info(f"Session ID: {snapshot.session_id}")
    logger.info(f"Metrics: {snapshot.metrics}")


def main():
    """Main demo function."""
    print("\n" + "="*60)
    print("Red Set ProtoCell - Telemetry Export Demo")
    print("="*60 + "\n")
    
    print("This demo shows the new telemetry export capabilities:")
    print("1. Export metrics to CSV for spreadsheet analysis")
    print("2. Export metrics to JSON for programmatic processing")
    print("3. Extract metrics from session database")
    print("4. Create metrics snapshots")
    print("\n")
    
    demo_csv_export()
    demo_json_export()
    demo_metrics_extraction()
    demo_metrics_snapshot()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("See 'demo_exports/' directory for exported files")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
