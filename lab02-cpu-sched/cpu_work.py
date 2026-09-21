#!/usr/bin/env python3
"""
cpu_work.py
固定工作量 CPU 任务，用于观察调度和 CPU 竞争。
"""

import argparse
import os
import time

CHUNK_INNER = 20000


def one_chunk(seed: int) -> int:
    acc = seed & 0xFFFFFFFF
    for i in range(1, CHUNK_INNER + 1):
        acc = (acc * 1664525 + i * 1013904223) & 0xFFFFFFFF
        acc ^= (acc >> 13)
    return acc


def run_work(chunks: int) -> int:
    acc = 123456789
    for c in range(chunks):
        acc = one_chunk(acc + c)
    return acc


def calibrate(target_seconds: float) -> int:
    chunks = 20
    start = time.perf_counter()
    run_work(chunks)
    elapsed = time.perf_counter() - start
    if elapsed < 0.01:
        chunks = 100
        start = time.perf_counter()
        run_work(chunks)
        elapsed = time.perf_counter() - start
    return max(20, int(chunks * target_seconds / elapsed))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fixed-work CPU-bound workload for OS scheduling experiments."
    )
    parser.add_argument("--work", type=int, default=1000,
                        help="计算块数量：数值越大，运行越久")
    parser.add_argument("--calibrate", action="store_true",
                        help="根据 --target 粗略推荐一个 --work 值")
    parser.add_argument("--target", type=float, default=15.0,
                        help="校准目标秒数，只在 --calibrate 模式使用")
    args = parser.parse_args()

    if args.calibrate:
        suggested = calibrate(args.target)
        print(f"RECOMMENDED_WORK={suggested}")
        print(f"Use this for all conditions: export WORK={suggested}")
        return

    print(f"PID={os.getpid()} WORK={args.work} START={time.strftime('%H:%M:%S')}",
          flush=True)
    start = time.perf_counter()
    result = run_work(args.work)
    elapsed = time.perf_counter() - start

    print(f"PID={os.getpid()} RESULT={result} ELAPSED_SELF={elapsed:.3f}s "
          f"END={time.strftime('%H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
