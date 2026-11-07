from pathlib import Path


def load_sql_queries(sql_file: Path) -> dict[str, str]:
    queries = {}
    current_query_name = None
    current_query_lines = []

    with sql_file.open("r", encoding="utf-8") as file:
        for line in file:
            stripped_line = line.strip()

            # Identify a query marker, e.g. -- SELECT_BY_ID:
            if stripped_line.startswith("--") and stripped_line.endswith(":"):
                if current_query_name is not None:
                    queries[current_query_name] = "\n".join(current_query_lines).strip()

                current_query_name = stripped_line[3:-1].strip()
                current_query_lines = []

            elif current_query_name is not None:
                current_query_lines.append(line.rstrip())

    # Store the final query
    if current_query_name is not None and current_query_name is not None:
        queries[current_query_name] = "\n".join(current_query_lines).strip()

    return queries
