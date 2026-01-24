# Ticket-009: Add support for different progress bar styles/renderers

## 1. Problem Statement
The current progress bar might not be suitable for all terminal types or user preferences. Providing different styles or renderers would enhance user experience and accessibility.

## 2. Proposed Solution
Implement support for configurable progress bar styles. This could involve offering a few predefined styles (e.g., ASCII-only, Unicode, minimal) and potentially allowing users to define custom formats.

## 3. Acceptance Criteria
- [x] AC 1.1: Users can select from at least two different predefined progress bar styles via a command-line option.
- [x] AC 1.2: One style is guaranteed to be ASCII-only for maximum terminal compatibility.
- [x] AC 1.3: The selected style is applied to the interactive progress bar.
- [x] AC 1.4: Documentation explains how to choose and preview different styles.

## 4. Technical Considerations
- **Terminal Compatibility**: Ensure styles render correctly across various terminal emulators.
- **Library Choice**: Consider using a library like `tqdm` or `rich` for rich progress bar functionality, or implement custom renderers.
- **Configuration**: Integrate style selection into argument parsing or a configuration file.

## 5. Dependencies
- None.

## 6. Subtask Checklist

#### Main Task Structure
- [x] Task 1: Research and select suitable progress bar rendering approaches.
  - **Problem**: Need to identify how to implement different visual styles for progress bar effectively.
  - **Test**: Document research findings and design choices.
  - **Subtasks**:
    - [x] Subtask 1.1: Evaluate existing Python libraries for progress bar rendering (e.g., `tqdm`, `rich`, custom ASCII art).
      - **Objective**: Understand their capabilities, dependencies, and suitability for `ptimeout`.
      - **Test**: Summarize findings on selected libraries/approaches.
      - **Research findings**: 
        - Rich (already used): Excellent choice - supports Unicode and ASCII modes, customizable styles, automatic terminal detection
        - tqdm: Popular but less customization than rich, heavier dependency
        - Custom ASCII: More control but requires significant implementation effort
        - **Recommendation**: Continue using rich, extend its built-in styling capabilities
    - [x] Subtask 1.2: Define at least two distinct progress bar styles: one ASCII-only, one more visually rich.
      - **Objective**: Design visual representation for each style.
      - **Test**: Provide examples of how each style would look.
      - **Proposed styles**:
        - **ascii**: Pure ASCII characters for maximum compatibility `[====>    ] 50%`
        - **unicode**: Rich Unicode characters for modern terminals `[━━━━▶    ] 50%`
        - **minimal**: Simple dots for clean output `......50%`
        - **fancy**: Decorated Unicode with animation `[■■■■▪▪▪▪] 50%`
- [x] Task 2: Implement a mechanism to select and render different progress bar styles.
  - **Problem**: The existing progress bar logic needs to be extended to support multiple styles.
  - **Test**: Integration tests for rendering different styles and verifying their appearance.
  - **Subtasks**:
    - [x] Subtask 2.1: Add a command-line option (e.g., `--progress-style <style>`) to `ptimeout`.
      - **Objective**: Allow users to choose their preferred progress bar style.
      - **Test**: Verify `argparse` correctly captures the chosen style.
      - **Implementation**: Successfully added `--progress-style` argument with choices: unicode, ascii, minimal, fancy. Default is unicode. Argument parser correctly validates input.
    - [x] Subtask 2.2: Modify the progress bar rendering logic to dynamically apply the selected style.
      - **Objective**: Create functions or classes for each style that can render the progress bar based on the elapsed time and total timeout.
      - **Test**: Run `ptimeout` with different `--progress-style` options and visually confirm the correct rendering.
       - **Implementation**: 
         - Added `get_progress_columns()` function that returns appropriate Rich progress column configuration based on style
         - Modified `run_command()` function to accept `progress_style` parameter  
         - Updated all calls to `run_command()` to pass the progress style
         - Successfully tested all four styles: unicode, ascii, minimal, fancy
         - All styles render correctly and maintain functionality
