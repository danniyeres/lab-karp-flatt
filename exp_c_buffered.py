"""Reduce Queue traffic by aggregating records in worker-local buffers."""

import time
from multiprocessing import Process, Queue


def buffered_worker(out_queue: Queue, items_per_worker: int, batch_size: int = 10_000) -> None:
    buffer = []
    for i in range(items_per_worker):
        buffer.append(i % 7)
        if len(buffer) >= batch_size:
            out_queue.put(sum(buffer))
            buffer.clear()
    if buffer:
        out_queue.put(sum(buffer))
    out_queue.put(None)


def run_buffered(workers: int, total_items: int = 10_000_000, batch_size: int = 10_000) -> tuple[float, int]:
    if total_items % workers:
        raise ValueError("total_items must be divisible by workers")
    out_queue = Queue()
    items_per_worker = total_items // workers
    processes = [
        Process(target=buffered_worker, args=(out_queue, items_per_worker, batch_size))
        for _ in range(workers)
    ]
    start = time.perf_counter()
    for process in processes:
        process.start()
    total_sum, active = 0, workers
    while active:
        value = out_queue.get()
        if value is None:
            active -= 1
        else:
            total_sum += value
    for process in processes:
        process.join()
    elapsed = time.perf_counter() - start
    out_queue.close()
    out_queue.join_thread()
    if any(process.exitcode != 0 for process in processes):
        raise RuntimeError("A worker process failed")
    expected_sum = workers * sum(i % 7 for i in range(items_per_worker))
    if total_sum != expected_sum:
        raise AssertionError(f"Expected checksum {expected_sum}, got {total_sum}")
    return elapsed, total_sum


def main() -> None:
    runtimes = {}
    for p in (1, 2, 4, 8):
        elapsed, checksum = run_buffered(p)
        runtimes[p] = elapsed
        print(f"P={p} | Runtime={elapsed:.3f}s | Checksum={checksum}")
    t1 = runtimes[1]
    print("\n--- Buffered Aggregation Karp-Flatt Analysis ---")
    for p in (1, 2, 4, 8):
        tp = runtimes[p]
        speedup = t1 / tp
        efficiency = speedup / p
        karp_flatt = None if p == 1 else ((p * tp / t1) - 1.0) / (p - 1.0)
        metric = "n/a" if karp_flatt is None else f"{karp_flatt:.3f}"
        print(f"P={p} | Speedup={speedup:.2f}x | Efficiency={efficiency:.1%} | Karp-Flatt e={metric}")


if __name__ == "__main__":
    main()
