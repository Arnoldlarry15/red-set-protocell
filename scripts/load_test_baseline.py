#!/usr/bin/env python3
"""Simple HTTP load baseline for health endpoints.

Usage:
  python scripts/load_test_baseline.py --base-url http://localhost:8000 --requests 200 --concurrency 20
"""

from __future__ import annotations

import argparse
import concurrent.futures
import statistics
import time
import urllib.request
from dataclasses import dataclass


@dataclass
class Result:
    ok: bool
    latency_ms: float
    status: int


def fetch(url: str, timeout: float) -> Result:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            latency = (time.perf_counter() - start) * 1000
            return Result(ok=200 <= resp.status < 400, latency_ms=latency, status=resp.status)
    except Exception:
        latency = (time.perf_counter() - start) * 1000
        return Result(ok=False, latency_ms=latency, status=0)


def run(url: str, requests: int, concurrency: int, timeout: float) -> list[Result]:
    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(fetch, url, timeout) for _ in range(requests)]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())
    return results


def summarize(name: str, results: list[Result]) -> tuple[float, float, float, float]:
    latencies = [r.latency_ms for r in results]
    success = sum(1 for r in results if r.ok)
    success_rate = (success / len(results)) * 100
    p50 = statistics.median(latencies)
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
    avg = statistics.mean(latencies)
    print(f"[{name}] success={success}/{len(results)} ({success_rate:.2f}%) avg={avg:.1f}ms p50={p50:.1f}ms p95={p95:.1f}ms")
    return success_rate, avg, p50, p95


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    if args.requests < 1:
        raise SystemExit("--requests must be >= 1")
    if args.concurrency < 1:
        raise SystemExit("--concurrency must be >= 1")

    overall_ok = True
    for path in ("/health", "/api/health"):
        url = f"{args.base_url}{path}"
        results = run(url, args.requests, args.concurrency, args.timeout)
        success_rate, _avg, _p50, p95 = summarize(path, results)
        if success_rate < 99.0 or p95 > 500:
            overall_ok = False

    if not overall_ok:
        raise SystemExit("Load baseline failed: requires >=99% success and p95 <= 500ms")


if __name__ == "__main__":
    main()
