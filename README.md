#  Data Cleaning CLI

**An interactive command-line tool to clean messy datasets, fast.**

---

## Overview

This project is a **purpose-built CLI tool** designed to help you rapidly clean CSV files using a streamlined, modular backend. While fully automated cleaning is unrealistic for most real-world data, this tool gives you **control through guided prompts** — automating repetitive cleaning tasks *with your input*.

Ideal for:
- Exploring raw datasets quickly
- Running consistent cleaning steps across projects
- Getting your data model-ready without opening Jupyter

---

##  Key Features

-  **Interactive Inspection**: Instantly preview head, tail, types, stats, and missing/unique value summaries.
-  **Structured Cleaning Flow**: Runs in a logical order: structure → missing → duplicates → outliers.
-  **Custom Outlier Handling**: Choose between trimming, capping, or imputing. Supports IQR and z-score.
-  **Smart Type Inference**: Automatically converts booleans, numbers, and datetimes (when safe).
-  **Duplicate Control**: Choose to drop all duplicates, keep the first, or keep the last.
-  **Safe Saving**: Saves cleaned file to your specified path with folder auto-creation and error handling.
-  **Fully Modular Backend**: Simple OOP-designed for possible reworking.

---

##  Installation

You can install the tool as a CLI command via [pipx](https://github.com/pypa/pipx) or editable mode.

### Option 1: pipx (Recommended)

```bash
pipx install path/to/your/project
```

### Option 2: Editable Mode (for development/testing)

```bash
cd path/to/your/project
pip install -e .
```

###  Usage

Once installed, run the tool from any terminal:

```bash
datacleaner
```

You’ll be guided step-by-step to load your CSV, inspect it, and apply cleaning operations. There’s no need to remember complex commands — just follow the prompts.

---

##  Quickstart Tips (Read This First!)

This section highlights key user behaviors to avoid confusion when running the CLI tool.

-  **CSV Location**:
  - You can use a **relative path** (e.g., `./sample.csv`) or an **absolute path** (e.g., `C:/Users/You/Desktop/data.csv`)
  - Your CSV does **not** need to be inside the project folder — it can be located anywhere.

-  **Input Responses**:
  - Always enter choices like `mean`, `drop`, `cap`, `interpolate` **exactly** as shown in the prompts — no quotes, no typos.

---

##  Common Pitfalls

-  Do **not** wrap paths in quotes — if dragging a folder into terminal, remove surrounding `' '` or `" "`.
-  Filenames **must end with `.csv`** (case-sensitive) or saving will fail.
-  If duplicate removal doesn’t seem to work, make sure your `id` column isn’t hiding them — ID columns are excluded from duplicate comparison but preserved in output.
-  When prompted for strategies (e.g. impute, cap), entering invalid choices will crash the run — answer exactly as suggested.
-  Structure inference may convert booleans, numerics, or datetimes — preview your data before and after to understand changes.
-  If saving fails, the most common issues are:
  - Quotation marks around path
  - Path not ending with `.csv`
  - Typos in folders or filenames

---

##  License

MIT License — free for personal and commercial use, with credit.

