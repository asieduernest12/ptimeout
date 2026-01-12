import unittest
import subprocess
import os
import sys
import time

class TestPtimeout(unittest.TestCase):

    def run_command_helper(self, timeout_arg, command_parts, input_data=None, extra_args=[]):
        """Helper to run ptimeout as a subprocess and capture its output."""
        # Ensure that the python executable is used for ptimeout.py
        # Use the absolute path inside the Docker container
        
        # Construct the command parts for ptimeout
        ptimeout_cmd_parts = [sys.executable, os.path.join('/app', 'src', 'ptimeout', 'ptimeout.py')]

        # Add timeout argument
        if timeout_arg:
            ptimeout_cmd_parts.append(timeout_arg)
        
        # Add any extra arguments like -r, -d, -v
        ptimeout_cmd_parts.extend(extra_args)

        # Add the --command and the actual command parts
        if command_parts:
            ptimeout_cmd_parts.extend(['--command'] + command_parts)
        
        process = subprocess.Popen(
            ptimeout_cmd_parts,
            stdin=subprocess.PIPE if input_data else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True # Universal newlines and text decoding
        )
        stdout, stderr = process.communicate(input=input_data)
        return stdout, stderr, process.returncode

    def test_command_success(self):
        stdout, stderr, return_code = self.run_command_helper(
            '1s',
            ['python', '-c', 'import time; print("hello"); time.sleep(0.1); print("world")']
        )
        self.assertEqual(return_code, 0)
        self.assertIn("hello", stdout)
        self.assertIn("world", stdout)
        self.assertIn("Command finished successfully.", stderr)

    def test_command_timeout(self):
        stdout, stderr, return_code = self.run_command_helper(
            '1s',
            ['python', '-c', 'import time; time.sleep(5)']
        )
        self.assertNotEqual(return_code, 0)
        self.assertIn("Timeout of 1s reached. Command terminated.", stderr)
        self.assertEqual(stdout.strip(), "") # Should produce no stdout if terminated

    def test_command_failure(self):
        stdout, stderr, return_code = self.run_command_helper(
            '1s',
            ['python', '-c', 'import sys; sys.exit(1)']
        )
        self.assertEqual(return_code, 1)
        self.assertIn("Command failed with exit code 1.", stderr)

    def test_retries_success_after_failure(self):
        # Command fails once, then succeeds
        temp_file = "temp_fail_counter.txt"
        with open(temp_file, "w") as f:
            f.write("0")

        try:
            stdout, stderr, return_code = self.run_command_helper(
                '2s',
                ['python', '-c',
                 f'with open("{temp_file}", "r+") as f: count = int(f.read()); f.seek(0); f.write(str(count + 1)); exit(1 if count == 0 else 0)'],
                extra_args=['-r', '1']
            )
            self.assertEqual(return_code, 0)
            self.assertIn("Retrying (1/1)...", stderr)
            self.assertIn("Command finished successfully.", stderr)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_retries_timeout_after_failure(self):
        stdout, stderr, return_code = self.run_command_helper(
            '1s',
            ['python', '-c', 'import time; time.sleep(5); exit(1)'],
            extra_args=['-r', '1']
        )
        self.assertNotEqual(return_code, 0)
        self.assertIn("Retrying (1/1)...", stderr)
        self.assertIn("Timeout of 1s reached. Command terminated.", stderr)
        # Should be terminated twice

    def test_parse_timeout_seconds(self):
        stdout, stderr, return_code = self.run_command_helper('10s', ['true'])
        self.assertEqual(return_code, 0)

    def test_parse_timeout_minutes(self):
        stdout, stderr, return_code = self.run_command_helper('1m', ['true'])
        self.assertEqual(return_code, 0)

    def test_parse_timeout_hours(self):
        stdout, stderr, return_code = self.run_command_helper('1h', ['true'])
        self.assertEqual(return_code, 0)
    
    def test_parse_timeout_plain_integer(self):
        stdout, stderr, return_code = self.run_command_helper('10', ['true'])
        self.assertEqual(return_code, 0)

    def test_parse_timeout_invalid_unit(self):
        stdout, stderr, return_code = self.run_command_helper('1x', ['true'])
        self.assertNotEqual(return_code, 0)
        self.assertIn("error: Invalid time unit: 'x'. Use 's', 'm', or 'h'.", stderr)

    def test_parse_timeout_invalid_value(self):
        stdout, stderr, return_code = self.run_command_helper('abc', ['true'])
        self.assertNotEqual(return_code, 0)
        self.assertIn("error: Invalid timeout value: 'abc'", stderr)

    def test_missing_timeout_argument(self):
        stdout, stderr, return_code = self.run_command_helper(None, ['true'])
        self.assertNotEqual(return_code, 0)
        self.assertIn("error: The 'TIMEOUT' argument is required.", stderr)
    def test_version_flag(self):
        # Construct the command parts for ptimeout
        ptimeout_cmd_parts = [sys.executable, os.path.join('/app', 'src', 'ptimeout', 'ptimeout.py'), '--version']
        
        process = subprocess.Popen(
            ptimeout_cmd_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True # Universal newlines and text decoding
        )
        stdout, stderr = process.communicate()
        
        # Read version from version.txt
        with open(os.path.join(os.path.dirname(__file__), '..', 'version.txt'), 'r') as f:
            version = f.read().strip()
            
        self.assertEqual(process.returncode, 0)
        self.assertIn(version, stdout)



if __name__ == '__main__':
    unittest.main()
