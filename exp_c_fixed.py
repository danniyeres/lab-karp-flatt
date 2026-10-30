
import time
from multiprocessing import Pool


def private_worker(iterations: int) -> int:
    local_sum = 0
    for _ in range(iterations):
        local_sum += 1
    return local_sum


def run_privatized(workers: int, total_increments: int = 20_000_000) -> float:
    if total_increments % workers:
        raise ValueError("total_increments must be divisible by workers")
    increments_per_worker = total_increments // workers
    tasks = [increments_per_worker] * workers
    start = time.perf_counter()
    with Pool(processes=workers) as pool:
        results = pool.map(private_worker, tasks)
    total = sum(results)
    elapsed = time.perf_counter() - start
    if total != total_increments:
        raise AssertionError(f"Expected {total_increments}, got {total}")
    return elapsed


def main() -> None:
    runtimes = {p: run_privatized(p) for p in (1, 2, 4)}
    t1 = runtimes[1]
    for p in (1, 2, 4):
        tp = runtimes[p]
        speedup = t1 / tp
        efficiency = speedup / p
        karp_flatt = None if p == 1 else ((p * tp / t1) - 1.0) / (p - 1.0)
        metric = "n/a" if karp_flatt is None else f"{karp_flatt:.3f}"
        print(f"P={p} | Runtime={tp:.3f}s | Speedup={speedup:.2f}x | Efficiency={efficiency:.1%} | Karp-Flatt e={metric}")


if __name__ == "__main__":
    main()
