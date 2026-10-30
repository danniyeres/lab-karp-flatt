
import math
import time
from multiprocessing import Pool


def heavy_math(n: int) -> float:
    return sum(math.sin(i) * math.cos(i) for i in range(1, n))


def run_experiment(workers: int, total_chunks: int = 16, chunk_size: int = 2_000_000) -> float:
    start = time.perf_counter()
    time.sleep(0.40)
    with Pool(processes=workers) as pool:
        pool.map(heavy_math, [chunk_size] * total_chunks)
    return time.perf_counter() - start


def main() -> None:
    runtimes = {p: run_experiment(p) for p in (1, 2, 4)}
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
