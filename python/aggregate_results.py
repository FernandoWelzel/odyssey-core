import os
import numpy as np
from tabulate import tabulate

def load_and_merge_results(results_dir):
    """
    Load all saved numpy arrays from the results folder and merge the counts.

    Args:
        results_dir (str): Path to the results directory.

    Returns:
        dict, dict: Merged instruction counts and merged true counts.
    """
    merged_counts = {}
    merged_true_counts = {}

    for filename in sorted(os.listdir(results_dir)):
        if filename.endswith("_true_count.npy"):
            true_count_data = np.load(os.path.join(results_dir, filename), allow_pickle=True).item()
            merge_dicts(merged_true_counts, true_count_data)
        elif filename.endswith("_count.npy"):
            count_data = np.load(os.path.join(results_dir, filename), allow_pickle=True).item()
            merge_dicts(merged_counts, count_data)

    return merged_counts, merged_true_counts

def merge_dicts(target, source):
    """
    Merge source dictionary into the target dictionary.

    Args:
        target (dict): Target dictionary to merge into.
        source (dict): Source dictionary to merge from.
    """
    for inst_type, counts in source.items():
        if inst_type not in target:
            target[inst_type] = {}
        for inst, value in counts.items():
            target[inst_type][inst] = target[inst_type].get(inst, 0) + value

def generate_table(merged_counts, merged_true_counts):
    """
    Generate a formatted table from merged counts.

    Args:
        merged_counts (dict): Merged instruction counts.
        merged_true_counts (dict): Merged true instruction counts.

    Returns:
        list: Formatted table rows.
    """
    total_instruction_true_count = 0
    total_instruction_count = 0
    table_data = []

    for inst_type in merged_counts:
        for name in merged_counts[inst_type]:
            total_count = merged_counts[inst_type][name]
            true_count = merged_true_counts[inst_type][name]
            ratio = (true_count / total_count * 100) if total_count != 0 else 0

            table_data.append([name, inst_type, true_count, total_count, f"{ratio:.2f}"])
            total_instruction_true_count += true_count
            total_instruction_count += total_count

    # Add total summary
    total_ratio = (total_instruction_true_count / total_instruction_count * 100) if total_instruction_count != 0 else 0
    table_data.append(["TOTAL", "-", total_instruction_true_count, total_instruction_count, f"{total_ratio:.2f}"])

    return table_data

def main():
    results_dir = "results"
    if not os.path.exists(results_dir):
        print(f"Results directory '{results_dir}' does not exist.")
        return

    # Load and merge results
    merged_counts, merged_true_counts = load_and_merge_results(results_dir)

    print(merged_true_counts)

    # Generate and display the table
    table = generate_table(merged_counts, merged_true_counts)
    print(tabulate(table, headers=["Inst", "FMT", "Correct", "Total", "Ratio (%)"], tablefmt="grid"))

if __name__ == "__main__":
    main()
