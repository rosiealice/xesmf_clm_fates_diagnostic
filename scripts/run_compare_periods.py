#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from typing import List, Tuple


def build_periods(start_year: int, end_year: int, period_years: int, step_years: int) -> List[Tuple[int, int]]:
    periods: List[Tuple[int, int]] = []
    year = start_year
    while year <= end_year:
        period_end = min(year + period_years - 1, end_year)
        periods.append((year, period_end))
        year += step_years
    return periods


def fmt_period(period: Tuple[int, int]) -> str:
    return f"{period[0]}-{period[1]}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run run_diagnostic_full_from_terminal.py for adjacent time-period comparisons."
    )
    parser.add_argument("--run-path", required=True, help="Path to lnd/hist folder")
    parser.add_argument("--outpath", required=True, help="Base output path")
    parser.add_argument("--pamfile", required=True, help="PAM json file path")
    parser.add_argument("--weight", required=True, help="Weight file path")
    parser.add_argument(
        "--compare-path",
        default=None,
        help="Comparison run path. Defaults to --run-path",
    )
    parser.add_argument("--start-year", type=int, default=1850)
    parser.add_argument("--end-year", type=int, default=2021)
    parser.add_argument("--period-years", type=int, default=20)
    parser.add_argument(
        "--step-years",
        type=int,
        default=20,
        help="Step between period starts. Default 20 gives non-overlapping periods.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=None,
        help="Optional cap for number of comparisons (for testing).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands only; do not execute.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip a run if its comparison log file already exists.",
    )
    parser.add_argument(
        "--log-child-output",
        action="store_true",
        help="Write child diagnostic output to per-comparison logs instead of streaming to terminal.",
    )

    args = parser.parse_args()

    run_path = args.run_path
    compare_path = args.compare_path or args.run_path
    script_path = os.path.join(os.path.dirname(__file__), "run_diagnostic_full_from_terminal.py")

    periods = build_periods(args.start_year, args.end_year, args.period_years, args.step_years)
    if len(periods) < 2:
        print("Need at least two periods; adjust year/period settings.")
        return 2

    comparisons: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
    for idx in range(1, len(periods)):
        newer = periods[idx]
        older = periods[idx - 1]
        comparisons.append((newer, older))

    if args.max_runs is not None:
        comparisons = comparisons[: args.max_runs]

    print("Periods:", ", ".join(fmt_period(p) for p in periods))
    print(f"Planned adjacent comparisons: {len(comparisons)}")

    outpath_run = args.outpath
    os.makedirs(outpath_run, exist_ok=True)

    for i, (newer, older) in enumerate(comparisons, start=1):
        range_arg = f"{fmt_period(newer)}_{fmt_period(older)}"
        run_tag = f"cmp_{fmt_period(newer)}_vs_{fmt_period(older)}"
        log_path = os.path.join(outpath_run, f"run_compare_periods_{run_tag}.log")

        if args.skip_existing and args.log_child_output and os.path.exists(log_path):
            print(f"[{i}/{len(comparisons)}] Skipping existing log {log_path}")
            continue

        cmd = [
            sys.executable,
            script_path,
            run_path,
            f"outpath={outpath_run}",
            f"pamfile={args.pamfile}",
            f"weight={args.weight}",
            "mute_trend=True",
            "mute_maps=True",
            f"compare={compare_path}",
            f"compare_custom_year_range={range_arg}",
        ]

        print(f"[{i}/{len(comparisons)}] Running {range_arg}")
        if args.log_child_output:
            print(f"[{i}/{len(comparisons)}] Child output -> {log_path}")

        if args.dry_run:
            print(f"[{i}/{len(comparisons)}] {' '.join(cmd)}")
            continue

        if args.log_child_output:
            with open(log_path, "w", encoding="utf-8") as logf:
                proc = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
        else:
            proc = subprocess.run(cmd)

        if proc.returncode != 0:
            print(f"Run failed with exit code {proc.returncode} for {range_arg}")
            if args.log_child_output:
                print(f"See log: {log_path}")
            return proc.returncode

    print("Finished all requested period comparisons.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
