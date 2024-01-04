import streamlit as st
import subprocess
import yaml


YEAR = 2024

EXCLUDE_VARS = {
    "employment_income_before_lsr",
    "employment_income_behavioral_response",
    "spm_unit_size",
}

year_str = f"<{YEAR},"  # String to match the year in the output


def create_yaml_file(variable_name):
    data = [
        {
            "name": "Scenario",
            "period": YEAR,
            "input": {},
            "output": {variable_name: 0},
        }
    ]

    with open("test.yaml", "w") as file:
        yaml.dump(data, file)


def run_policy_engine():
    command = "policyengine-core test test.yaml -c policyengine_us -v"
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True
    )
    return result.stdout


def extract_unique_leaf_nodes(output):
    lines = output.split("\n")
    leaf_nodes = set()
    non_leaf_nodes = set()

    for i in range(len(lines) - 1):
        line = lines[i]
        if "=" not in line or f"<{YEAR}," not in line:
            continue

        variable = line.split("=")[0].strip()
        # Remove the year and default tag
        variable = (
            variable.replace(year_str, "").replace("(default)>", "").strip()
        )

        if variable in EXCLUDE_VARS:
            continue
        current_indent = len(line) - len(line.lstrip())

        # Determine if the next line is more indented
        next_line = lines[i + 1]
        next_indent = len(next_line) - len(next_line.lstrip())
        if current_indent < next_indent:
            non_leaf_nodes.add(variable)
        elif variable not in non_leaf_nodes:
            leaf_nodes.add(variable)

    return sorted(leaf_nodes)


st.title("PolicyEngine Output")

variable_name = st.text_input("Enter a variable name (e.g., ssi):")

# Button to create YAML file and run policy engine
if st.button("Run PolicyEngine"):
    create_yaml_file(variable_name)
    output = run_policy_engine()
    # Make the raw output hideable
    with st.expander("Show Raw Output"):
        st.text_area("Raw Output", output, height=300)

    # Extract and display unique leaf nodes
    leaf_nodes = extract_unique_leaf_nodes(output)
    st.subheader("Unique Leaf Nodes")
    for node in leaf_nodes:
        st.write(node)
