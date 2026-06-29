from pathlib import Path
import re
import pandas as pd


def read_nodes(path: Path) -> dict[str, list[int | float]]:
    """
    Reads the nodes from a txt file output from ANSYS APDL.  Returns a dict
    containing the NODE number and the X, Y, and Z coordinates.

    typical usage:
    >>> nodes = pd.DataFrame(read_nodes(...))
    """
    nodes: dict[str, list[int | float]] = {}

    with open(path, "r") as f:
        content = f.readlines()

    node: list[int] = []
    x: list[float] = []
    y: list[float] = []
    z: list[float] = []

    for line in content:
        if len(line.split()) == 0:
            continue
        if (line.split()[0]).isnumeric():
            node.append(int(line.split()[0]))
            x.append(float(line.split()[1]))
            y.append(float(line.split()[2]))
            z.append(float(line.split()[3]))

    nodes["NODE"] = node
    nodes["X"] = x
    nodes["Y"] = y
    nodes["Z"] = z

    return nodes


def read_pretab(path: Path) -> dict[str, list[int | float]]:
    """
    Reads output from APDL pretab txt file.  Returns a dict containing
    the pretab data for each element in the file.
    """
    elements: dict[str, list[int | float]] = {}

    with open(path, "r") as f:
        content = f.readlines()

    for line in content:
        if len(line.split()) == 0:
            continue
        # Get keys for the dict
        if line.split()[0] == "ELEM" and len(elements) == 0:
            keys: list[str] = line.split()
            for key in keys:
                elements[key] = []
        if (line.split()[0]).isnumeric():
            for i, key in enumerate(keys):
                if key == "ELEM":
                    elements[key].append(int(line.split()[i]))
                else:
                    elements[key].append(float(line.split()[i]))

    return elements


def read_prnsol(path: Path) -> dict[str, list[int | float]]:
    """
    Reads output from APDL prnsol txt file.  Returns a dict containing
    the prnsol data for each element in the file.
    """

    nodes: dict[str, list[int | float]] = {}

    with open(path, "r") as f:
        content = f.readlines()

    node: list[int] = []
    ux: list[float] = []
    key: str | None = None

    for line in content:
        if len(line.split()) == 0:
            continue
        if line.split()[0] == "NODE" and key is None:
            key = line.split()[1]
        if (line.split()[0]).isnumeric():
            node.append(int(line.split()[0]))
            ux.append(float(line.split()[1]))

    nodes["NODE"] = node
    if key:
        nodes[key] = ux

    return nodes


def read_prnsol_files_to_dataframe(file_paths: list[Path | str]) -> pd.DataFrame:
    """
    Reads multiple PRNSOL-style test files and returns one combined DataFrame.

    Rules:
    - First relevant line starts with "NODE" and defines headers.
    - Any line that starts with an integer is data.
    - Any line that does not start with an integer is ignored.
    """
    numeric_line = re.compile(r"^\s*\d+\b")  # TODO: type hint
    frames = []  # TODO: type hint

    for file_path in file_paths:
        path: Path = Path(file_path)
        header: list[str] | None = None
        rows: list[int | float] = []

        with path.open("r") as f:
            for line in f:
                parts: list[str] = line.split()
                if not parts:
                    continue

                if header is None and parts[0] == "NODE":
                    header = parts
                    continue

                if header is None:
                    continue

                if numeric_line.match(line):
                    rows.append(parts[: len(header)])

        if header is None:
            raise ValueError(f'No header line starting with "NODE" found in {path}')

        if rows:
            frame: pd.DataFrame = pd.DataFrame(rows, columns=header)
            frame["source_file"] = path.name
            frames.append(frame)

    if not frames:
        return pd.DataFrame()

    combined: pd.DataFrame = pd.concat(frames, ignore_index=True)

    for col in combined.columns:
        if col != "source_file":
            combined[col] = pd.to_numeric(combined[col], errors="coerce")

    return combined


def read_linearized_stress():
    # TODO: read linearized stress
    raise NotImplementedError


def read_elements():
    # TODO: read elements
    raise NotImplementedError


def merge_results_to_nodes_dataframe(nodes_df: pd.DataFrame,
                                     results_df: pd.DataFrame,
                                     ansys_result_label: str,
                                     result_label: str) -> pd.DataFrame:
    """
    Merge the results from 'read_prnsol_files_to_dataframe()' to the nodes DataFrame.
    reads the column with header 'ansys_result_label' and renames it to 'result_label'.
    """
    return nodes_df.merge(
        results_df[["NODE", ansys_result_label]],
        on="NODE", how="left").rename(
        columns={ansys_result_label: result_label})
