# VulnHGNN

VulnHGNN is a C/C++ vulnerability-analysis project that combines a Gemini-compatible security-review agent, local Clang diagnostics, graph neural-network inference, and an optional bounded repair workflow.

## What it does
- Reviews full web analyses with the configured Gemini model and combines its findings with local Clang checks.
- Keeps the legacy PyTorch Geometric/GNN CLI and pipeline available for model-based detection and localization.
- Keeps legacy self-healing workflows and compiler-checked, user-reviewed source repair proposals.
- Exports the latest web analysis as a downloadable JSON security report.
- Checks C syntax and constant division-by-zero warnings while you type in the web editor.
- Runs debounced, local-only editor checks: Clang validates syntax and confirms constant division-by-zero warnings. Live checks do not call Gemini.
- Provides an interactive Flask web UI to review agent and Clang findings.
- Includes a full CLI pipeline to process source files and generate reports from your terminal.
- Tracks carbon emissions using CodeCarbon to measure the environmental impact of your ML workloads.

## What you need
Make sure you have Python 3.8 or newer installed. You'll also need Windows since we use `.bat` scripts for the launchers.

## How to set it up
1. Clone or download this repository to your machine.
2. Open your terminal or command prompt in the project folder.
3. Run `setup.bat` to create the virtual environment and install dependencies.
4. Activate the environment manually only if you need a terminal session:
   `venv\Scripts\activate`.

## Verification

Run the complete test suite in the project virtual environment:

```powershell
venv\Scripts\python.exe -m pytest tests -q
```

## Getting started

### Running the Web UI
The easiest way to use VulnHGNN is through the web app. Just double-click the `run.bat` file in the project folder, or run `run.bat` from your command prompt. It will automatically activate your environment and start the Flask server. Once it's running, open your browser and go to http://127.0.0.1:5000.

If you prefer doing it manually, activate the environment and run:

```powershell
python src\app.py
```

### Gemini agent review for web analysis
Every full web analysis sends source code (up to 64 KB) to the configured provider and requires a successful Gemini response. Live checks while typing remain local. To use a Gemini API key from Google AI Studio, configure the OpenAI-compatible endpoint before starting Flask:

```powershell
Copy-Item .env.example .env
# Open .env and paste your Google AI Studio key into VULNHGNN_LLM_API_KEY.
python src/app.py
```

The example selects `gemini-3.1-flash-lite` and Google's OpenAI-compatible endpoint. The app loads `.env` from the repository root. Keep that file private; `.env` is ignored by Git. Never paste the key into source code, commit it, or send it in chat. Pressing **Analyze** sends source to the configured provider; source over 64 KB is not sent. If the provider is unconfigured or unavailable, the full analysis returns an explicit error rather than falling back to GNN predictions. Gemini findings are advisory and do not execute code or apply repairs. Free-tier eligibility and request limits depend on Google's current model and account quotas. Review Google's data-handling terms before sending proprietary code.

### Live editor checks
After a short pause in typing, the web editor compiles the selected C or C++ source with Clang and reports syntax errors and any constant division-by-zero warnings Clang confirms. These live checks do not send code to Gemini or modify source, and they do not detect all vulnerability types. Press **Analyze** for a full Gemini-assisted review combined with Clang checks. A clean result does not prove that code is secure. Install Clang for syntax and local security checks.

### Running the CLI
If you want to process files directly from the command line, you can use the `run_pipeline.bat` script. The CLI and self-healing pipeline continue to use the existing GNN model. By default, the launcher runs a test file against the pre-trained model.

To run it on your own files, you can manually run the pipeline like this:
1. Activate your virtual environment.
2. Set your python path: `set PYTHONPATH=%PYTHONPATH%;%CD%\src`
3. Run the script: `python src\pipeline.py path\to\your_file.c --no-carbon --model results\pyg_gnn_v9\best_pyg_model.pt`

## Folder structure
```text
src/                    Flask app, agent review, GNN, parser, localization, and repair
tests/                  Unit, integration, live-check, and end-to-end tests
test_files/             C/C++ source fixtures
dataset/                Training/support data
data/                   Supporting project data
docs/                   Architecture diagrams and report images
results/                Checkpoints and generated evaluation results
scripts/                Report-generation and utility scripts
report/                 Final academic report Word/PDF deliverables
mid_evaluation_report/  Mid-evaluation report deliverables
```

## Architecture
See [docs/architecture.md](docs/architecture.md) for a plain-language comparison of what changed, why it helps, the runtime flow, and the bounded repair loop.
Open the [updated architecture diagram PNG](docs/vulnhgnn_updated_architecture.png) for presentations. It keeps the original phase-based, pastel-box style and adds real-time editor checks and compiler-checked, user-reviewed repair proposals.

### Diagnostic fixture evaluation
Run the local model over the repository's ten labeled C fixtures and save a reproducible diagnostic report:

```powershell
python src/evaluate_fixtures.py --model results/pyg_gnn_v9/best_pyg_model.pt --output results/fixture_diagnostic.json
```

These fixtures may overlap training or tuning data, so this report is **not** an independent held-out benchmark. Model training now splits graphs by source file to prevent functions from the same file appearing in multiple splits; retrain with a complete labeled corpus before using its metrics as generalization evidence.
