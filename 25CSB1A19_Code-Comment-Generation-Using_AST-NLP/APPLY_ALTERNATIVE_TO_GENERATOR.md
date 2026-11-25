# Apply Alternative to Generator

The **Apply Alternative to Generator** button is displayed in the **Generator** workspace, directly below the input-code editor. It is disabled until Agentic Security produces a safer alternative.

## How to use

1. Open **Generator** and enter or select source code.
2. Click **Generate & Attach Comments**. The source is passed to Agentic Security for analysis.
3. Open **Agentic Security** to review the findings, **Best Recommended Secure Alternative**, and **Secure Rewrite Notes**.
4. Return to **Generator**. The **Apply Alternative to Generator** button below the input editor becomes enabled when an alternative is available.
5. Click the button and confirm the replacement. The alternative is loaded into the Generator input editor.
6. Review the replacement code. Click **Generate & Attach Comments** again only when ready to regenerate documentation and analysis.

## Safety and behaviour

- The original source file on disk is not overwritten by this action. The editor is treated as pasted/unsaved source after applying an alternative.
- The previous annotated output preview is cleared so it is not confused with output generated from the new code.
- The language selector is updated to match the alternative's language.
- The code is not automatically generated or executed after applying it; the user remains in control.
- For non-Python languages, automatic source rewrites may not be available. The button stays disabled when no alternative code was produced.
- Starting a new Agentic Security scan invalidates the previous alternative until the new result is ready.
- A safer alternative is a recommendation, not a guarantee. Review it, rescan it, and test it in a suitable safe environment before use.
