#!/usr/bin/env python3
"""
ptimeout systemd utility - Generate systemd user service files for ptimeout commands.
"""

import argparse
import os
import sys
from pathlib import Path


def generate_systemd_service(args):
    """Generate a systemd service file content based on provided arguments."""

    # Build the ptimeout command
    ptimeout_cmd = ["/usr/local/bin/ptimeout"]

    if args.retries:
        ptimeout_cmd.extend(["-r", str(args.retries)])

    if args.verbose:
        ptimeout_cmd.append("-v")

    if args.count_direction:
        ptimeout_cmd.extend(["-d", args.count_direction])

    if args.config:
        ptimeout_cmd.extend(["--config", args.config])

    # Add timeout and command
    ptimeout_cmd.extend([args.timeout, "--"] + args.command)

    # Build the systemd service file content
    service_content = f"""[Unit]
Description={args.description}
Documentation=man:ptimeout(1)
"""

    if args.after:
        service_content += f"After={args.after}\n"

    service_content += """
[Service]
Type=simple
ExecStart=
"""

    # Add ExecStart line with environment variables if provided
    if args.environment:
        for env_var in args.environment:
            service_content += f"Environment={env_var}\n"

    service_content += f"ExecStart={' '.join(ptimeout_cmd)}\n"

    if args.working_directory:
        service_content += f"WorkingDirectory={args.working_directory}\n"

    if args.user:
        service_content += f"User={args.user}\n"
    else:
        service_content += "User=%i\n"

    if args.group:
        service_content += f"Group={args.group}\n"
    else:
        service_content += "Group=%i\n"

    if args.restart:
        service_content += f"Restart={args.restart}\n"

    if args.restart_sec:
        service_content += f"RestartSec={args.restart_sec}\n"

    if args.memory_limit:
        service_content += f"MemoryMax={args.memory_limit}\n"

    if args.cpu_quota:
        service_content += f"CPUQuota={args.cpu_quota}\n"

    if args.stdout_log:
        service_content += f"StandardOutput=append:{args.stdout_log}\n"

    if args.stderr_log:
        service_content += f"StandardError=append:{args.stderr_log}\n"

    service_content += """
[Install]
WantedBy=default.target
"""

    return service_content


def main():
    """Main function for ptimeout systemd utility."""
    parser = argparse.ArgumentParser(
        description="Generate systemd user service files for ptimeout commands",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--version", action="version", version="ptimeout systemd 1.0.0")

    # Required arguments
    parser.add_argument(
        "--name",
        required=True,
        help="Name of the systemd service (without .service extension)",
    )

    parser.add_argument(
        "--timeout",
        required=True,
        help="Timeout for the ptimeout command (e.g., '10s', '5m', '1h')",
    )

    parser.add_argument(
        "--command",
        nargs="+",
        required=True,
        help="Command to run with timeout (as a list of arguments)",
    )

    # Optional service metadata
    parser.add_argument(
        "--description",
        default="ptimeout managed service",
        help="Description for the systemd service",
    )

    parser.add_argument(
        "--after", help="Units this service should start after (e.g., 'network.target')"
    )

    # Execution options
    parser.add_argument(
        "--retries", type=int, help="Number of retries for ptimeout command"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output for ptimeout command",
    )

    parser.add_argument(
        "--count-direction",
        choices=["up", "down"],
        help="Count direction for ptimeout timer",
    )

    parser.add_argument("--config", help="Path to ptimeout configuration file")

    # Service execution options
    parser.add_argument("--working-directory", help="Working directory for the service")

    parser.add_argument(
        "--user", help="User to run the service as (default: %%i for template)"
    )

    parser.add_argument(
        "--group", help="Group to run the service as (default: %%i for template)"
    )

    parser.add_argument(
        "--restart",
        choices=["no", "on-success", "on-failure", "on-abnormal", "on-abort", "always"],
        default="on-failure",
        help="Restart policy (default: on-failure)",
    )

    parser.add_argument(
        "--restart-sec",
        type=int,
        default=30,
        help="Seconds to wait before restart (default: 30)",
    )

    # Resource limits
    parser.add_argument("--memory-limit", help="Memory limit (e.g., '512M', '2G')")

    parser.add_argument("--cpu-quota", help="CPU quota (e.g., '50%%', '80%%')")

    # Logging options
    parser.add_argument("--stdout-log", help="Path to stdout log file")

    parser.add_argument("--stderr-log", help="Path to stderr log file")

    parser.add_argument(
        "--environment",
        action="append",
        help="Environment variables (can be used multiple times)",
    )

    # Output options
    parser.add_argument(
        "--output-file", help="Path to write the service file (default: stdout)"
    )

    parser.add_argument(
        "--install-path", help="Copy service file to systemd user service directory"
    )

    args = parser.parse_args()

    # Generate the service content
    service_content = generate_systemd_service(args)

    # Output the service file
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(service_content)
        print(f"Service file written to: {output_path}")
    else:
        print(service_content)

    # Install to systemd directory if requested
    if args.install_path:
        if not args.output_file:
            # If no output file specified, use the service name
            filename = f"{args.name}.service"
            service_path = Path(args.install_path) / filename
            service_path.write_text(service_content)
        else:
            service_path = Path(args.install_path) / Path(args.output_file).name
            service_path.write_text(service_content)

        print(f"Service file installed to: {service_path}")
        print("\nTo enable and start the service:")
        print(f"systemctl --user daemon-reload")
        print(f"systemctl --user enable {args.name}.service")
        print(f"systemctl --user start {args.name}.service")


if __name__ == "__main__":
    main()
