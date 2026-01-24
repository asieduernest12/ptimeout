# systemd Service Examples for ptimeout

This directory contains example systemd user service files for running ptimeout commands as persistent services.

## Usage

1. **Copy the appropriate example** to your systemd user service directory:
   ```bash
   cp backup-timeout.service ~/.config/systemd/user/
   ```

2. **Customize the service file** to match your needs:
   - Update paths to match your actual script locations
   - Modify timeout values as needed
   - Adjust user and group settings
   - Add or modify environment variables

3. **Enable and start the service**:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable backup-timeout.service
   systemctl --user start backup-timeout.service
   ```

4. **Check service status**:
   ```bash
   systemctl --user status backup-timeout.service
   journalctl --user -u backup-timeout.service -f
   ```

## Available Examples

### backup-timeout.service
- **Purpose**: Run backup scripts with a 1-hour timeout
- **Features**: Resource limits, restart on failure, environment variables
- **Use case**: Regular backup operations with timeout protection

### data-processor.service
- **Purpose**: Process data files with a 30-minute timeout
- **Features**: Output logging to files, higher resource limits
- **Use case**: Data processing tasks that need timeout protection and logging

### monitoring.service
- **Purpose**: System monitoring with 10-minute timeout and custom config
- **Features**: Custom configuration file, always restart
- **Use case**: Continuous monitoring with timeout protection and auto-restart

## Template Variables

The example service files use `%i` as a template variable for the username. When using these files, replace `%i` with your actual username, or use systemd template instantiation:

```bash
# Copy as a template
cp backup-timeout.service ~/.config/systemd/user/backup-timeout@.service

# Start for your user
systemctl --user enable backup-timeout@$(whoami).service
systemctl --user start backup-timeout@$(whoami).service
```

## Security Notes

- These are **user services** that run with your user privileges
- Ensure script files have appropriate permissions (executable)
- Use absolute paths to avoid PATH manipulation issues
- Review resource limits based on your system capabilities

## Troubleshooting

If a service fails to start:
1. Check the service status: `systemctl --user status service-name.service`
2. View logs: `journalctl --user -u service-name.service -n 50`
3. Validate syntax: `systemctl --user daemon-reload`
4. Check file permissions and paths in the service file