# Fix for the Generate button closing the application

This update hardens the Qt worker lifecycle used by generation and Agentic Security.

## What was corrected

1. `GeneratorWorker` no longer declares a custom signal named `finished`. That name belongs to `QThread` and indicates that the native thread has fully stopped. The worker now emits `result_ready` for its result and uses Qt's inherited `finished()` for cleanup.
2. The Generator keeps a reference to its worker until the native thread ends and prevents a second generation from replacing a still-running worker.
3. Agentic Security analysis runs in its own managed `QThread` instead of running synchronously in the GUI thread. Exceptions are returned to the UI as an error report rather than escaping the click/signal handler.
4. The post-generation dashboard and Agentic hand-off are guarded so an optional panel error does not terminate the application.
5. Unexpected main-thread exceptions are written to `logs/app_crash.log`.
6. The ML training worker also uses `result_ready`, leaving Qt's inherited `finished()` signal intact.
7. Closing the application while a generation, Agentic analysis, or training thread is still running is blocked with a message. Wait for the current task to finish before closing.

## Start the application

Open this folder in VS Code (the folder containing `run_gui.py`) and run:

```powershell
py run_gui.py
```

Keep the terminal open while testing. If the application still exits, send the terminal traceback and `logs/app_crash.log` (if present).

## Verification performed in the build environment

- `python -m compileall -q src run_gui.py`: passed.
- Existing non-GUI tests: 111 passed, 1 skipped.
- Python showcase generation pipeline: completed in a direct non-GUI test.
- Local Agentic Security analysis on the showcase Python source: completed in a direct non-GUI test.

The build environment did not have PyQt6 installed, and package download was unavailable, so the Windows GUI could not be launched here. Please perform the live GUI check on the Windows machine that has the project's PyQt6 environment installed.
