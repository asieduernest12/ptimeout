# Configuration File Format Research

## Task 1.1: Research common configuration file formats and their associated Python libraries

### INI Format (.ini)
**Python Library**: `configparser` (built-in)
**Pros**:
- Simple, human-readable format
- Built-in Python library, no external dependencies
- Widely understood by users
- Supports sections and key-value pairs
- Good for hierarchical configurations

**Cons**:
- Limited support for complex data structures
- No native support for lists/dictionaries
- Can be verbose for simple configurations

**Example**:
```ini
[defaults]
timeout = 30s
retries = 3
countdown_direction = down
verbose = false

[nested]
enable_support = true
```

### YAML Format (.yaml/.yml)
**Python Library**: `PyYAML` or `ruamel.yaml`
**Pros**:
- Very human-readable and clean
- Supports complex data structures (lists, dicts)
- Excellent for nested configurations
- Widely used in modern applications
- Supports comments

**Cons**:
- Requires external dependency (PyYAML)
- Sensitive to indentation errors
- Can be slower to parse than INI

**Example**:
```yaml
defaults:
  timeout: 30s
  retries: 3
  countdown_direction: down
  verbose: false

nested:
  enable_support: true
```

### JSON Format (.json)
**Python Library**: `json` (built-in)
**Pros**:
- Built-in Python library
- Strict syntax, less error-prone
- Excellent for complex data structures
- Widely supported across languages
- Fast parsing

**Cons**:
- No comments support
- More verbose than YAML
- Less human-readable for simple configs
- Strict syntax can be unforgiving

**Example**:
```json
{
  "defaults": {
    "timeout": "30s",
    "retries": 3,
    "countdown_direction": "down",
    "verbose": false
  },
  "nested": {
    "enable_support": true
  }
}
```

### TOML Format (.toml)
**Python Library**: `toml` or `tomllib` (Python 3.11+)
**Pros**:
- Clean, readable syntax
- Built-in support in Python 3.11+
- Good balance between simplicity and features
- Supports comments
- Growing popularity in Python ecosystem

**Cons**:
- Requires external dependency for Python < 3.11
- Less familiar to some users
- Newer format, less widespread adoption

**Example**:
```toml
[defaults]
timeout = "30s"
retries = 3
countdown_direction = "down"
verbose = false

[nested]
enable_support = true
```

## Recommendation

For `ptimeout`, I recommend **INI format** for the following reasons:

1. **No external dependencies** - Uses built-in `configparser`
2. **Sufficient for current needs** - Simple key-value pairs work well for timeout defaults
3. **User familiarity** - INI files are widely understood
4. **Simplicity** - Perfect for the configuration requirements described in the ticket
5. **Consistency with Unix tools** - Many CLI tools use INI-style configs

The configuration options mentioned (timeout, retries, countdown direction) are simple key-value pairs that don't require complex nested structures, making INI the ideal choice.