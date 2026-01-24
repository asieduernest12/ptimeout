#!/usr/bin/env python3

import argparse


def test_args():
    parser = argparse.ArgumentParser(
        description="Run a command with a time-based progress bar, or process piped input with a timeout.",
        formatter_class=argparse.RawTextHelpFormatter,
        usage="%(prog)s TIMEOUT [-h] [-v] [-r RETRIES] [-d {up,down}] -- COMMAND [ARGS...]",
    )

    parser.add_argument(
        "timeout_arg",
        type=str,
        help="The maximum execution time. Use optional suffixes: s (seconds), m (minutes), h (hours). E.g., '10s', '5m', '1h'.",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )
    parser.add_argument(
        "-r",
        "--retries",
        type=int,
        default=0,
        help="Max number of times to retry the command upon failure. Defaults to 0.",
    )
    parser.add_argument(
        "-d",
        "--count-direction",
        type=str,
        choices=["up", "down"],
        default="up",
        help="Specify count direction: 'up' to count elapsed time (default), 'down' to count remaining time.",
    )

    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help='The command and its arguments to run. Precede with "--" to separate from ptimeout options.',
    )

    args = parser.parse_args()
    print(f"Parsed args: {args}")
    print(f"retries: {args.retries}")


if __name__ == "__main__":
    test_args()
