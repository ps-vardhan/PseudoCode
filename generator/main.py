import argparse
import sys
import os
import json

# Force UTF-8 encoding for Windows console (Python 3.7+)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    # Older Python versions may not support reconfigure; ignore.
    pass

# Import from the sibling file 'model.py'
try:
    import model
except ImportError:
    # If run as a package/module with different layout, adjust here if needed
    from generator import model  # type: ignore


def run_interactive(mock: bool = False, model_name: str | None = None) -> None:
    """
    Interactive CLI loop.
    - Asks for DESCRIPTION (non_code_text) and EXISTING CODE (code_text).
    - Builds a structured prompt.
    - Either:
        - Uses mock JSON generator (if mock=True), or
        - Calls the model to generate JSON output.
    - Parses JSON and saves it into global JSON file.
    """

    tokenizer = None
    loaded_model = None
    device = "cpu"

    if not mock:
        tokenizer, loaded_model, device = model.load_model(model_name=model_name)
    else:
        print("[main] Running in MOCK mode (no model will be loaded).")

    print("=== Interactive JSON Code-Unit Generator ===")
    print("Type 'exit' or 'quit' at any prompt to stop.")
    print()

    while True:
        try:
            non_code = input("Description (non-code text): ").strip()
            if non_code.lower() in ("exit", "quit"):
                break

            code_text = input("Existing Code (leave empty if none): ").strip()
            if code_text.lower() in ("exit", "quit"):
                break

            data = {
                "non_code_text": non_code,
                "code_text": code_text,
            }

            # Build prompt (even in mock mode, just to inspect)
            prompt = model.build_prompt_from_seper_output(data)
            print("\n--- Generated Prompt (for inspection) ---")
            print(prompt)
            print("----------------------------------------\n")

            # Generate JSON unit
            if mock:
                json_unit = model.mock_generate_json_unit(data)
            else:
                raw_output = model.generate_with_prompt(
                    tokenizer=tokenizer,
                    model=loaded_model,
                    device=device,
                    formatted_prompt=prompt,
                )
                print("--- Raw Model Output ---")
                print(raw_output)
                print("------------------------\n")

                json_unit = model.parse_model_json_output(raw_output)

            # Pretty-print the JSON unit to console
            print("=== Parsed JSON Unit ===")
            print(json.dumps(json_unit, indent=2, ensure_ascii=False))
            print("========================\n")

            # Save into global JSON
            model.save_generated_output(json_unit, output_dir="output")

        except KeyboardInterrupt:
            print("\n[main] Interrupted by user. Exiting.")
            break
        except ValueError as e:
            print(f"[main] JSON parse error: {e}")
            print("Raw model output above did not contain valid JSON.")
            print("Try again or adjust the prompt/description.\n")
        except Exception as e:
            print(f"[main] Error: {e}")
            print("Attempting to continue...\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="JSON-based Generator Interface")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run in mock mode without loading the model (generates fake JSON units)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override Hugging Face model name (default: deepseek-coder 1.3B instruct)",
    )
    args = parser.parse_args()

    run_interactive(mock=args.mock, model_name=args.model)


if __name__ == "__main__":
    main()
