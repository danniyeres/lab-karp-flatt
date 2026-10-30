# Variant B: Scalability Diagnostics

## Environment and method

- Platform: macOS 27.0.1, arm64
- `os.cpu_count()`: 8; `multiprocessing.cpu_count()`: 8
- Process counts: 1, 2, 4, and 8
- One sequential measurement per configuration; timings are reported as observed, without averaging.

Speedup is `T1 / Tp`; efficiency is `speedup / p`; Karp–Flatt is `((p * Tp / T1) - 1) / (p - 1)`. The metric is undefined for `p=1`.

## Experiment A: Task granularity

The checksum matched at every process count (`131434424`).

| Task mode | T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(4) | e(8) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Micro (`chunksize=1`) | 16.693 | 18.974 | 21.156 | 22.434 | 0.74x | 1.273 | 1.356 | 1.393 | Dispatch/IPC overhead dominates; adding workers makes the run slower. |
| Coarse (`chunksize=10000`) | 7.306 | 3.963 | 2.557 | 1.955 | 3.74x | 0.085 | 0.133 | 0.163 | Chunking restores speedup, with overhead still rising at larger process counts. |

## Experiment B: Queue choke point

| T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(4) | e(8) | Verdict |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2.146 | 5.064 | 6.594 | 7.639 | 0.28x | 3.721 | 3.764 | 3.926 | Negative scaling and increasing e are consistent with a shared Queue/pipe bottleneck. |

## Experiment C: Buffered aggregation

The benchmark processes 10,000,000 records and sends one aggregate per 10,000 records, plus one completion sentinel per worker. The computed checksum is validated against each worker's partition.

| T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(4) | e(8) | Verdict |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1.463 | 0.646 | 0.412 | 0.366 | 4.00x | -0.116 | 0.043 | 0.143 | Buffering restores speedup, but this run does not meet the handout's S8 > 5 and e(8) ≤ 0.05 targets. |

## Notes

These are single-run measurements and may vary with system load and scheduling. The handout's expected values are diagnostic targets, not guaranteed results. The eight-process configuration reaches 50% parallel efficiency in Experiment C on this host.
