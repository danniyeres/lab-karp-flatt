"""Compare multiprocessing dispatch costs for fine and coarse chunks."""

import time
from multiprocessing import Pool


def collatz_steps(n: int) -> int:
    steps = 0
    while n > 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def run_granularity(workers: int, total_items: int = 1_000_000, chunk_size: int = 1) -> tuple[float, int]:
    numbers = range(1, total_items + 1)
    start = time.perf_counter()
    with Pool(processes=workers) as pool:
        results = pool.map(collatz_steps, numbers, chunksize=chunk_size)
    return time.perf_counter() - start, sum(results)


def report(label: str, runtimes: dict[int, float]) -> None:
    t1 = runtimes[1]
    print(f"\n{label}")
    for p, tp in runtimes.items():
        speedup = t1 / tp
        efficiency = speedup / p
        karp_flatt = None if p == 1 else ((p * tp / t1) - 1.0) / (p - 1.0)
        metric = "n/a" if karp_flatt is None else f"{karp_flatt:.3f}"
        print(f"P={p} | Runtime={tp:.3f}s | Speedup={speedup:.2f}x | Efficiency={efficiency:.1%} | Karp-Flatt e={metric}")


def main() -> None:
    workers_to_test = (1, 2, 4, 8)
    for chunk_size, name in ((1, "Micro-tasks (chunksize=1)"), (10_000, "Coarse chunks (chunksize=10000)")):
        runtimes = {}
        checksums = set()
        for workers in workers_to_test:
            elapsed, checksum = run_granularity(workers, chunk_size=chunk_size)
            runtimes[workers] = elapsed
            checksums.add(checksum)
        if len(checksums) != 1:
            raise AssertionError("Checksums differ across worker counts")
        report(name, runtimes)
        print(f"Checksum={checksums.pop()}")


if __name__ == "__main__":
    main()
