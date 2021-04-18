"""
parse_darab: Parses an exported WinDarab text file into a .csv file, and if available, a pandas DataFrame.
filepath (str): Input file path to parse, exported from WinDarab
outpath (str, optional): Output file path to write .csv formatted data into
with_units (boolean): Include units (e.g. [A]) on the end of columns, if available

Returns:
    - If `pandas` is available, a `DataFrame`
    - Otherwise, a data dictionary
"""


def parse_darab(filepath, outpath=None, with_units=True):
    from collections import defaultdict
    import csv

    with open(filepath) as f:
        # List of column names
        column_names = []
        # Data list: list of {key: value}
        data = []
        for line in f.readlines():
            assert len(line) >= 1

            # Comment
            if line[0] == "#":
                continue

            # Header
            if "[" in line:
                # Split column headers
                header = line.split("\t")
                # Normalize names, should be <name> [unit] or just <name>
                columns = []
                for c in header:
                    name, unit = c.split("[")  # split
                    name = name.strip()  # remove spaces
                    unit = unit.replace("]", "").strip()  # remove brackets and spaces
                    # append name
                    if with_units and unit != "none" and unit != "":
                        column_names.append("{} [{}]".format(name, unit))
                    else:
                        column_names.append(name)
            # Data line
            else:
                data_dict = {}
                for i, d in enumerate(line.split("\t")):
                    d = d.strip()
                    if d.isnumeric():
                        d = float(d)
                    data_dict[column_names[i]] = d
                data.append(data_dict)
        # Export to csv
        if outpath is not None:
            with open(outpath, "w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=column_names)
                writer.writeheader()
                for d in data:
                    writer.writerow(d)
    try:
        import pandas as pd

        # Convert to pandas, coerce to numeric if possible
        df = pd.DataFrame.from_dict(data)
        return df.apply(pd.to_numeric, errors="coerce").fillna(df)
    except:
        return data
