# Empirical Scalability Diagnostics: Karp–Flatt Metric

## Hardware and method

- Platform: macOS 27.0.1, arm64
- Logical CPUs reported by `os.cpu_count()`: 8
- Python multiprocessing process counts measured: 1, 2, and 4
- Timings are one sequential run per process count using the handout's default workloads. They are local observations, not statistically averaged benchmarks.

Speedup is `T1 / Tp`; Karp–Flatt is `((p * Tp / T1) - 1) / (p - 1)`. The `p=1` baseline has no Karp–Flatt value.

| Experiment | T1 (s) | T2 (s) | T4 (s) | e(2) | e(4) | Architectural diagnosis |
|---|---:|---:|---:|---:|---:|---|
| A: Serial tail | 3.540 | 2.111 | 1.393 | 0.193 | 0.192 | Nearly constant e indicates a fixed serial/overhead component. The observed value is above the handout's 0.10–0.15 target. |
| B: Lock contention | 5.488 | 9.996 | 13.554 | 2.643 | 2.959 | Runtime worsens as process count rises and e grows above 1, consistent with severe shared-lock contention. |
| C: Privatized state | 0.536 | 0.280 | 0.197 | 0.047 | 0.158 | Privatization restores speedup (T4 < T1), but scaling is not near-linear at four processes; e(4)=0.158 and parallel efficiency is 67.8%. |

## Interpretation and limits

The measurements show the intended qualitative contrast: A has a flat Karp–Flatt score, B has negative speedup and a rising score, and C removes per-increment synchronization. The numerical targets are workload- and machine-dependent. In particular, this host reports eight logical CPUs, but process count is not a guarantee of dedicated physical cores; the handout's expected timings should not be treated as reproducible constants.

Each point was measured once, so scheduling and thermal variation can affect the results. Repeat each experiment several times and compare medians for a more stable report.
