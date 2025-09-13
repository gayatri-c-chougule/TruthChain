# Import graph from LangGraph
from LangGraph import get_remedy_graph
import csv
import json
import os
from dotenv import load_dotenv

load_dotenv()

# === Input/Output Paths from .env ===
EVAL_INPUT = os.getenv("EVAL_INPUT", os.path.join("Evaluation", "test_cases.csv"))
EVAL_OUTPUT = os.getenv("EVAL_OUTPUT", os.path.join("Evaluation", "evaluation_results.csv"))

# Load the LangGraph instance
graph = get_remedy_graph()

# Initialize evaluation storage
results_array = []  # Will hold each row of evaluation results
total_accuracy = 0  # Counter for correct verdicts


# === Evaluation Script ===
# Reads a list of test claims and expected verdicts from CSV,
# runs them through the LangGraph, collects outputs from selected tools,
# compares verdict to ground truth, calculates accuracy,
# and writes final results to a new CSV file.

# Read test cases from CSV
with open(EVAL_INPUT, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        claim = row['Claim'].strip()
        ground_truth = row['Ground Truth'].strip()

        # Handle empty claims gracefully
        if not claim:
            print(f"⚠️ Skipping empty claim at row {len(results_array)+1}")
            result = {
                "claim": "",
                "ground_truth": ground_truth,
                "selected_tools": "Skipped",
                "tools_output": "⚠️ Empty claim input. Skipped.",
                "verdict": "Skipped",
                "reasoning": "",
                "accuracy": 0
            }
            results_array.append(result)
            continue
        
        print(
            f"Current Accuracy: {total_accuracy}/{len(results_array)} "
            f"(Processing case {len(results_array)+1}: {claim[:50]}...)"
        )

        try:
            # Run the claim through the LangGraph pipeline
            final_state = graph.invoke({"user_input": claim})

            # Truncate tool outputs to 350 characters for compactness
            tool_outputs_raw = final_state.get("tool_outputs", {})
            truncated_outputs = {
                tool: output[:350] + "…" if len(output) > 350 else output
                for tool, output in tool_outputs_raw.items()
            }

            result = {
                "claim": claim,
                "ground_truth": ground_truth,
                "selected_tools": ", ".join(final_state.get("selected_tools", [])),
                "tools_output": json.dumps(truncated_outputs, ensure_ascii=False),
            }

            # Extract and normalize the verdict to "True", "False", or "Unverifiable"
            full_verdict = final_state.get("final_verdict", "")
            verdict_text = full_verdict.lower()

            if "true" in verdict_text:
                result["verdict"] = "True"
            elif "false" in verdict_text:
                result["verdict"] = "False"
            elif "unverifiable" in verdict_text:
                result["verdict"] = "Unverifiable"
            else:
                result["verdict"] = "Unknown"

            # Extract reasoning from the verdict, if present
            # Prompt is such that the reasoning will start with "Reason:"
            reason_part = ""
            if "Reason:" in full_verdict:
                reason_part = full_verdict.split("Reason:", 1)[1].strip()

            result["reasoning"] = reason_part

            # Compare with ground truth and update accuracy
            result["accuracy"] = 1 if ground_truth.lower() == result["verdict"].lower() else 0
            total_accuracy += result["accuracy"]

        except Exception as e:
            # Handle errors (e.g., LLM failure) and mark the case as incorrect
            result = {
                "claim": claim,
                "ground_truth": ground_truth,
                "selected_tools": "Error",
                "tools_output": f"❌ Error: {str(e)}",
                "verdict": "Error",
                "reasoning": "",
                "accuracy": 0
            }

        # Append result for this test case
        results_array.append(result)

# === Final summary ===
accuracy_percentage = total_accuracy / len(results_array) * 100
print(f"✅ Evaluation complete: {len(results_array)} cases | Accuracy: {accuracy_percentage:.2f}%")

# === Save results to CSV ===
output_file = EVAL_OUTPUT
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=results_array[0].keys())
    writer.writeheader()
    writer.writerows(results_array)
