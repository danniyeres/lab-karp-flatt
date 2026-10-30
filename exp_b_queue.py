"""Measure shared multiprocessing.Queue throughput under producer load."""

import time
from multiprocessing import Process, Queue


def queue_worker(out_queue: Queue, items_per_worker: int) -> None:
    for i in range(items_per_worker):
        out_queue.put(i % 7)


def run_queue_benchmark(workers: int, total_items: int = 400_000) -> tuple[float, int]:
    if total_items % workers:
        raise ValueError("total_items must be divisible by workers")
    out_queue = Queue()
    items_per_worker = total_items // workers
    processes = [Process(target=queue_worker, args=(out_queue, items_per_worker)) for _ in range(workers)]
    start = time.perf_counter()
    for process in processes:
        process.start()
    total_sum = 0
    for _ in range(total_items):
        total_sum += out_queue.get()
    for process in processes:
        process.join()
    elapsed = time.perf_counter() - start
    out_queue.close()
    out_queue.join_thread()
    if any(process.exitcode != 0 for process in processes):
        raise RuntimeError("A producer process failed")
    # Every producer emits residues 0..6; compute the expected aggregate directly.
    expected_sum = workers * sum(i % 7 for i in range(items_per_worker))
    if total_sum != expected_sum:
        raise AssertionError(f"Expected checksum {expected_sum}, got {total_sum}")
    return elapsed, total_sum


def main() -> None:
    runtimes = {}
    for p in (1, 2, 4, 8):
        runtimes[p], _ = run_queue_benchmark(p)
    t1 = runtimes[1]
    print("\n--- Queue Contention Karp-Flatt Analysis ---")
    for p in (1, 2, 4, 8):
        tp = runtimes[p]
        speedup = t1 / tp
        karp_flatt = None if p == 1 else ((p * tp / t1) - 1.0) / (p - 1.0)
        metric = "n/a" if karp_flatt is None else f"{karp_flatt:.3f}"
        print(f"P={p:2d} | Time={tp:6.3f}s | Speedup={speedup:5.2f}x | Karp-Flatt e={metric}")


if __name__ == "__main__":
    main()
