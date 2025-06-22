# loades file into pandas df to be cleaned in cleaner.py
import pandas as pd

class DataLoader:
    
    def __init__(self, file_path):
        self.file_path = file_path
    
    def load(self):
        log = []

        try:
            df = pd.read_csv(self.file_path, delimiter = ',')
            log.append(f'CSV file \'{self.file_path}\' loaded into pandas dataframe')
            return df        
        except Exception as e:
            raise Exception(f'CSV file \'{self.file_path}\' was unable to load: {e}')

#maybe consider how to make an absolute path/something that allows you to simply put csv as an argument irrespective of its path/directory after it is setup using toml.