from datacleaner.DataLoader import DataLoader
from datacleaner.Cleaner import Cleaner
from datacleaner.Saver import Saver
import typer
import time
import warnings
import pandas as pd

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

app = typer.Typer()

@app.command()
def run_clean():

    raw_data = typer.prompt("📄 Path to your CSV file")
    object1 = DataLoader(raw_data)
    df = object1.load()

    time.sleep(1)
    inspect = typer.confirm("🔍 Would you like to inspect the dataset first?", default=False)
    time.sleep(1)

    if inspect:

        time.sleep(0.75)
        print("\n📊 Dataset Preview:\n")
        time.sleep(0.75)
        print("Head:\n")
        time.sleep(0.75)
        print(df.head(), '\n')
        time.sleep(0.75)
        print("-------------------------------------------------------------")
        time.sleep(0.75)
        print("Tail:\n")
        time.sleep(0.75)
        print(df.tail(), '\n')
        time.sleep(0.75)
        print("-------------------------------------------------------------\n")
        time.sleep(0.75)
        print("Structure:\n")
        time.sleep(0.75)
        print(df.info(), '\n') 
        time.sleep(0.75)
        print(df.dtypes, '\n')
        time.sleep(0.75)
        print("-------------------------------------------------------------\n")
        time.sleep(0.75)
        print("Stats:\n")
        time.sleep(0.75)
        print(df.describe(), '\n')
        time.sleep(0.75)
        print("-------------------------------------------------------------\n")
        time.sleep(0.75)
        print("Uniques:\n")
        time.sleep(0.75)
        print("Unique value % per column:\n")
        print(((df.nunique() / len(df)) * 100).round(2).astype(str) + '%')
        time.sleep(0.75)
        print("Missing:\n")
        time.sleep(0.75)
        print("Missing value % per column:\n")
        print((df.isnull().mean() * 100).round(2).astype(str) + '%')
        time.sleep(0.75)
        print("-------------------------------------------------------------\n")
        time.sleep(1)

    structure = typer.confirm("📐 Run structure inference? (recommended)", default=True)

    # ---------------- Missing Value Handling ----------------
    time.sleep(1)
    missing = typer.confirm("🧼 Would you like to handle missing values?", default=False)
    missing_strategy = ''
    imputation_method = ''

    if missing:
        missing_strategy = typer.prompt("➤ Strategy for missing values [impute / drop / interpolate]").lower()
        if missing_strategy not in ['impute', 'drop', 'interpolate']:
            raise typer.BadParameter("Invalid missing strategy. Choose from: impute, drop, interpolate.")

        if missing_strategy == 'impute':
            imputation_method = typer.prompt("➤ Imputation method [mean / median / mode]").lower()
            if imputation_method not in ['mean', 'median', 'mode']:
                raise typer.BadParameter("Invalid imputation method. Choose from: mean, median, mode.")
    time.sleep(1)
    # ---------------- Duplicate Handling ----------------
    time.sleep(1)
    duplicates = typer.confirm("🔁 Would you like to handle duplicates?", default=False)
    duplicates_strategy = ''

    if duplicates:
        duplicates_strategy = typer.prompt("➤ Duplicate strategy [remove_all / keep_first / keep_last]").lower()
        if duplicates_strategy not in ['remove_all', 'keep_first', 'keep_last']:
            raise typer.BadParameter("Invalid duplicates strategy. Choose from: remove_all, keep_first, keep_last.")
    time.sleep(1)
    # ---------------- Outlier Handling ----------------
    time.sleep(1)
    outliers = typer.confirm("📊 Would you like to detect and handle outliers?", default=False)
    outliers_strategy = ''
    outliers_threshold = None 
    outliers_action = ''
    outliers_cap_method = 0 
    outliers_cap_method2 = 100

    outliers_imputation_method = None 

    if outliers:
        outliers_strategy = typer.prompt("➤ Outlier detection method [z-score / IQR]").lower()
        if outliers_strategy not in ['z-score', 'iqr']:
            raise typer.BadParameter("Invalid outlier strategy. Choose from: z-score, IQR.")

        custom_threshold = typer.confirm("➤ Would you like to specify a custom threshold (e.g., 2.5 for z-score, 1.5 for IQR)?", default=False)
        if custom_threshold:
            try:
                outliers_threshold = float(typer.prompt("➤ Enter custom threshold/multiplier (e.g., 2.5 for z-score, 1.5 for IQR)"))
            except ValueError:
                raise typer.BadParameter("Threshold must be a numeric value.")
        else:
            if outliers_strategy == 'z-score':
                outliers_threshold = 3.0
            elif outliers_strategy == 'iqr':
                outliers_threshold = 1.5

        outliers_action = typer.prompt("➤ How should outliers be handled? [trim / cap / impute]").lower()
        if outliers_action not in ['trim', 'cap', 'impute']:
            raise typer.BadParameter("Invalid outlier handling strategy. Choose from: trim, cap, impute.")
        
        if outliers_action == 'cap':
            outliers_cap_method = int(typer.prompt("➤ Enter cap lower percentile (0 - 100)").lower())
            outliers_cap_method2 = int(typer.prompt("➤ Enter cap upper percentile (0 - 100)").lower())
            if outliers_cap_method not in range(0, 101) or outliers_cap_method2 not in range(0, 101):
                raise typer.BadParameter("Percentile values must be a numeric values between 0 - 100")
            if outliers_cap_method >= outliers_cap_method2:
                raise typer.BadParameter("Lowe percentile cannot be equal to or greater than upper percentile")

        if outliers_action == 'impute':
            outliers_imputation_method = typer.prompt("➤ Imputation method [mean / median / mode]").lower()
            if outliers_imputation_method not in ['mean', 'median', 'mode']:
                raise typer.BadParameter("Invalid imputation method. Choose from: mean, median, mode.")
            
            
    time.sleep(1)

    object2 = Cleaner(
        df,
        outliers,
        outliers_strategy,
        outliers_threshold,
        outliers_action,
        outliers_cap_method,
        outliers_cap_method2,
        outliers_imputation_method,
        duplicates,
        duplicates_strategy,
        structure,
        missing,
        missing_strategy,
        imputation_method,
    )

    cleaned_df = object2.clean()

    print("\n🧾 Cleaned DataFrame Preview:\n")
    print(cleaned_df.head())

    file_path = typer.prompt('➤ Enter the full file path to save your cleaned CSV file (e.g., ./outputs/cleaned.csv). If you drag your folder, ensure you manually enter your filename of choice at the end .csv')
    if not file_path.endswith('.csv'):
        raise typer.BadParameter('filename must end with .csv (case sensitive)')
    
    object3 = Saver(cleaned_df, file_path)
    object3.save_to_file_path()

if __name__ == '__main__':
    app()
    run_clean() 