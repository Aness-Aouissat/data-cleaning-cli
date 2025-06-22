# saves filed into user defined path
from pathlib import Path
class Saver:

    def __init__(self, cleaned_df, file_path):
        self.cleaned_df = cleaned_df
        self.file_path = file_path

    def save_to_file_path(self):

        try:
            filepath = Path(self.file_path)
            filepath.parent.mkdir(parents = True, exist_ok = True)
            self.cleaned_df.to_csv(filepath, index = False)
            print(f"✅ Cleaned file successfully saved to: {filepath}")
        except Exception as e:
            print(f"\n❌ Failed to save file: {e}")
            print(
                "⚠️  Possible issues:\n"
                "  • Extra quotation marks (especially from dragging folders)\n"
                "  • File path does not exist or has typos\n"
                "  • Filename missing or not ending in '.csv'\n"
                "  • You used a folder path without appending 'your_file.csv'\n\n"
                "💡 Tip: Try again and make sure your full path looks like this:\n"
                "      C:\\Users\\YourName\\Desktop\\cleaned.csv\n"
            )
