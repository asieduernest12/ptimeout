#!/usr/bin/env python3

"""
Dev Watcher - Automatic file monitoring and rebuild system for ptimeout
Monitors source files and restarts/rebuilds as needed
"""

import os
import sys
import signal
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# Rich imports for nice output
try:
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

    class Console:
        def print(self, *args, **kwargs):
            print(*args, file=sys.stderr)

        def rule(self, text=""):
            print(f"--- {text} ---", file=sys.stderr)


# Watchdog imports
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DevWatcher(FileSystemEventHandler):
    def __init__(self, console):
        self.console = console
        self.process = None
        self.should_exit = False
        self.last_change_time = 0
        self.restart_delay = float(os.environ.get("WATCHER_RESTART_DELAY", "1.0"))

    def on_modified(self, event):
        if event.is_directory:
            return

        # Ignore cache and build files
        if any(
            pattern in event.src_path
            for pattern in ["__pycache__", ".pyc", ".pytest_cache"]
        ):
            return

        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_change_time < self.restart_delay:
            return
        self.last_change_time = current_time

        file_path = Path(event.src_path)

        if file_path.name == "requirements.txt":
            self.console.print(
                f"📦 requirements.txt changed → Rebuilding...", style="yellow"
            )
            self.rebuild_all()
        elif file_path.suffix == ".py":
            self.console.print(
                f"📝 {file_path.name} changed → Restarting...", style="blue"
            )
            self.restart_process()

    def rebuild_all(self):
        """Reinstall dependencies and rebuild binary"""
        try:
            # Reinstall dependencies
            self.console.print("   📦 Reinstalling dependencies...", style="dim")
            result = subprocess.run(
                ["pip", "install", "-r", "src/requirements.txt"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.console.print(
                    f"   ❌ Dependency install failed: {result.stderr}", style="red"
                )
                return

            # Rebuild binary
            self.console.print("   🔨 Rebuilding ptimeout binary...", style="dim")
            result = subprocess.run(
                ["bash", "scripts/build_binary.sh"],
                capture_output=True,
                text=True,
                cwd="/app",
            )
            if result.returncode != 0:
                self.console.print(f"   ❌ Build failed: {result.stderr}", style="red")
                return

            # Install new binary
            self.console.print("   📎 Installing new binary...", style="dim")
            result = subprocess.run(
                ["bash", "scripts/install.sh"],
                capture_output=True,
                text=True,
                cwd="/app",
            )
            if result.returncode != 0:
                self.console.print(
                    f"   ❌ Install failed: {result.stderr}", style="red"
                )
                return

            self.console.print("   ✅ Rebuild complete!", style="green")
            self.restart_process()

        except Exception as e:
            self.console.print(f"   ❌ Rebuild error: {e}", style="red")

    def restart_process(self):
        """Restart the ptimeout process"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Start new process
        self.start_process()

    def start_process(self):
        """Start the ptimeout process"""
        try:
            # For now, just start a simple process that keeps running
            # In real usage, this would run the actual ptimeout application
            self.process = subprocess.Popen(
                ["tail", "-f", "/dev/null"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            self.console.print(f"❌ Failed to start process: {e}", style="red")


class DevWatcherApp:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else Console()
        self.observer = None
        self.should_exit = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.console.print(
            f"\n🛑 Received signal {signum}, shutting down...", style="yellow"
        )
        self.should_exit = True
        if self.observer:
            self.observer.stop()

    def setup_initial_state(self):
        """Install dependencies and build on first start"""
        self.console.print("🚀 Starting Dev Watcher...", style="bold green")

        # Install dependencies
        self.console.print("📦 Installing dependencies...", style="blue")
        result = subprocess.run(
            ["pip", "install", "-r", "src/requirements.txt"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.console.print(
                f"❌ Dependency install failed: {result.stderr}", style="red"
            )
            return False

        # Build binary
        self.console.print("🔨 Building ptimeout binary...", style="blue")
        result = subprocess.run(
            ["bash", "scripts/build_binary.sh"],
            capture_output=True,
            text=True,
            cwd="/app",
        )
        if result.returncode != 0:
            self.console.print(f"❌ Build failed: {result.stderr}", style="red")
            return False

        # Install binary
        self.console.print("📎 Installing binary...", style="blue")
        result = subprocess.run(
            ["bash", "scripts/install.sh"], capture_output=True, text=True, cwd="/app"
        )
        if result.returncode != 0:
            self.console.print(f"❌ Install failed: {result.stderr}", style="red")
            return False

        self.console.print("✅ Setup complete!", style="green")
        return True

    def start_watching(self):
        """Start file system monitoring"""
        event_handler = DevWatcher(self.console)
        event_handler.start_process()

        # Setup observer
        self.observer = Observer()
        watch_paths = ["/app/src", "/app/scripts"]

        for path in watch_paths:
            if os.path.exists(path):
                self.observer.schedule(event_handler, path, recursive=True)
                self.console.print(f"🐍 Watching {path} for changes...", style="dim")

        self.observer.start()

        # Show ready message
        if RICH_AVAILABLE:
            ready_text = Text(
                "🎯 Dev Watcher Ready!\nWatching for file changes...",
                style="bold green",
            )
            panel = Panel(ready_text, border_style="green")
            self.console.print(panel)
        else:
            self.console.print("🎯 Dev Watcher Ready! Watching for file changes...")

        # Keep running until shutdown
        try:
            while not self.should_exit:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        if self.observer:
            self.observer.join()

        # Cleanup
        if event_handler.process:
            event_handler.process.terminate()

        self.console.print("👋 Dev Watcher stopped", style="yellow")


def main():
    app = DevWatcherApp()

    # Check initial setup
    if not app.setup_initial_state():
        sys.exit(1)

    # Start watching
    app.start_watching()


if __name__ == "__main__":
    main()
