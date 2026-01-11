import unittest
import subprocess
import os
import sys
import time

class TestPipeInput(unittest.TestCase):

    def run_ptimeout_with_pipe(self, input_data, timeout_arg, command_args=None):
        """Helper to run ptimeout with piped input."""
        cmd = [sys.executable, os.path.join('src', 'ptimeout', 'ptimeout.py'), timeout_arg]
        if command_args:
            cmd.extend(['--'] + command_args)

        # Set up subprocess.Popen to handle piping
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True # Decode stdin/stdout/stderr as text
        )

        try:
            # Let ptimeout itself handle the timeout; do not set a communicate timeout here
            stdout, stderr = process.communicate(input=input_data)
        except Exception as e:
            # This should ideally not happen if ptimeout handles timeouts correctly
            process.kill()
            stdout, stderr = process.communicate()
            return stdout, stderr, "COMMUNICATE_ERROR: " + str(e)
        
        return stdout, stderr, process.returncode

    def test_pipe_default_cat(self):
        """Test ptimeout with piped input and default 'cat' command."""
        input_data = "Hello from pipe!\nAnother line."
        stdout, stderr, return_code = self.run_ptimeout_with_pipe(input_data, "3s")

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), input_data.strip())
        self.assertIn("Command finished successfully.", stderr)


    def test_pipe_with_explicit_command(self):
        """Test ptimeout with piped input and an explicit command (grep)."""
        input_data = "apple\nbanana\norange\ngrape"
        stdout, stderr, return_code = self.run_ptimeout_with_pipe(input_data, "3s", ["grep", "anana"])

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), "banana")
        self.assertIn("Command finished successfully.", stderr)


    def test_pipe_with_timeout_expired(self):
        """Test ptimeout with piped input and a command that times out."""
        # Use a command that will wait longer than the timeout
        input_data = "start\n"
        stdout, stderr, return_code = self.run_ptimeout_with_pipe(input_data, "1s", ["sleep", "10"])

        self.assertNotEqual(return_code, 0) # Should not be successful
        self.assertIn("Timeout of 1s reached. Command terminated.", stderr)


    def test_pipe_with_command_failure(self):
        """Test ptimeout with piped input and a command that fails."""
        input_data = "some data"
        stdout, stderr, return_code = self.run_ptimeout_with_pipe(input_data, "3s", ["sh", "-c", "exit 1"])

        self.assertEqual(return_code, 1) # Expect the exit code of the failed command
        self.assertIn("Command failed with exit code 1.", stderr)


if __name__ == '__main__':
    unittest.main()