class DataLoader:
    """Handles loading data from files."""
    @staticmethod
    def load_text_file(filepath: str) -> str | None:
        """Loads content from a text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {filepath}")
            return None
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None

    @staticmethod
    def load_professor_list(csv_path: str) -> list[dict] | None:
        """Loads professor data from a CSV file."""
        try:
            df = pd.read_csv(csv_path)
            required_cols = ['name', 'university', 'email', 'research_interests']
            if not all(col in df.columns for col in required_cols):
                print(f"Error: CSV file missing one or more required columns: {required_cols}")
                return None
            professor_list = df.to_dict('records')
            print(f"Loaded {len(professor_list)} professors from {csv_path}")
            return professor_list
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_path}")
            return None
        except Exception as e:
            print(f"Error reading CSV file {csv_path}: {e}")
            return None