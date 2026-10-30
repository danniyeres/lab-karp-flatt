
import time
from multiprocessing import Lock, Process, Value


def contended_worker(shared_counter: Value, lock: Lock, iterations: int) -> None:
    for _ in range(iterations):
        with lock:
            shared_counter.value += 1


def run_contended(workers: int, total_increments: int = 2_000_000) -> float:
    if total_increments % workers:
        raise ValueError("total_increments must be divisible by workers")
    increments_per_worker = total_increments // workers
    counter = Value("q", 0)
    lock = Lock()
    processes = [
        Process(target=contended_worker, args=(counter, lock, increments_per_worker))
        for _ in range(workers)
    ]
    start = time.perf_counter()
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    elapsed = time.perf_counter() - start
    if any(process.exitcode != 0 for process in processes):
        raise RuntimeError("A worker process failed")
    if counter.value != total_increments:
        raise AssertionError(f"Expected {total_increments}, got {counter.value}")
    return elapsed


def main() -> None:
    runtimes = {p: run_contended(p) for p in (1, 2, 4)}
    t1 = runtimes[1]
    for p in (1, 2, 4):
        tp = runtimes[p]
        speedup = t1 / tp
        karp_flatt = None if p == 1 else ((p * tp / t1) - 1.0) / (p - 1.0)
        metric = "n/a" if karp_flatt is None else f"{karp_flatt:.3f}"
        print(f"P={p} | Runtime={tp:.3f}s | Speedup={speedup:.2f}x | Karp-Flatt e={metric}")


if __name__ == "__main__":
    main()
