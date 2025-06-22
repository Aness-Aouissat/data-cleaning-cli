# cleans data depending on user CLI arguments
import pandas as pd
import time
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_datetime64_any_dtype
import warnings

class Cleaner:

    def __init__(self, df, outliers, outliers_strategy, outliers_threshold, outliers_action, outliers_cap_method, outliers_cap_method2, outliers_imputation_method, duplicates, duplicates_strategy, structure, missing, missing_strategy, imputation_method):
        self.df = df
        self.outliers = outliers
        self.outliers_strategy = outliers_strategy
        self.outliers_threshold = outliers_threshold
        self.outliers_action = outliers_action
        self.outliers_cap_method = outliers_cap_method
        self.outliers_cap_method2 = outliers_cap_method2
        self.outliers_imputation_method = outliers_imputation_method
        self.duplicates = duplicates
        self.duplicates_strategy = duplicates_strategy 
        self.structure = structure
        self.missing = missing
        self.missing_strategy = missing_strategy
        self.imputation_method = imputation_method

    #idea is to pass user arguments which have boolean true/false values into a cleaner object through constructor. if argument was true, then automatically we can execute the command through the below methods 
    #order: structure --> missing --> duplicates --> outliers

    def deal_with_outliers(self): 
        
        log = []

        for columnName, columnItems in self.df.items(): 

            if is_numeric_dtype(columnItems):

                count = 0   

                lower_percentile = columnItems.quantile(((self.outliers_cap_method)/100))
                upper_percentile = columnItems.quantile(((self.outliers_cap_method2)/100))

                average = self.df[columnName].mean()
                median = self.df[columnName].median()
                mode = self.df[columnName].mode().iloc[0]

                if self.outliers_strategy in ['z-score', 'iqr'] and 'id' in columnName.lower():
                        log.append(f'Skipped column \'{columnName}\' (likely identifier). Strategy \'{self.outliers_strategy}\' not applied to ID fields.')
                        continue
            
                if self.outliers_strategy == 'iqr':

                    copy_of_series = columnItems.copy()

                    Q1 = copy_of_series.quantile(0.25)
                    Q3 = copy_of_series.quantile(0.75)

                    if Q1 == Q3:
                        log.append(f"Column '{columnName}' has identical Q1 and Q3 → no variability. Skipping IQR outlier detection.")
                        continue

                    IQR = Q3 - Q1

                    lower_bound = Q1 - self.outliers_threshold*IQR
                    upper_bound = Q3 + self.outliers_threshold*IQR 

                    values = columnItems.copy()
                    
                    for i in range(len(columnItems)):

                        current_value = columnItems.iloc[i]
                        current_index = columnItems.index[i]

                        if current_value < lower_bound or current_value > upper_bound:

                            count += 1

                            if self.outliers_action == 'trim':
                                index_to_trim = columnItems.index[i]
                                self.df = self.df.drop(index = index_to_trim)
                                
                            elif self.outliers_action == 'cap':
                                if current_value < lower_bound:
                                    values.loc[current_index] = lower_percentile
                                else: 
                                    values.loc[current_index] = upper_percentile

                            elif self.outliers_action == 'impute':
                                if self.outliers_imputation_method == 'mean':
                                    values.loc[current_index] = average
                                elif self.outliers_imputation_method == 'median':
                                    values.loc[current_index] = median
                                elif self.outliers_imputation_method == 'mode':
                                    values.loc[current_index]  = mode

                    if self.outliers_action in ['cap', 'impute']:
                        self.df[columnName] = values
                    
                    if self.outliers_action == 'trim':
                        log.append(f'Detected and trimmed {count} outlier rows in \'{columnName}\' through IQR method')
                    elif self.outliers_action == 'cap':
                        log.append(f'Detected and capped {count} outlier values in \'{columnName}\' to user-defined percentiles: {self.outliers_cap_method}th and {self.outliers_cap_method2}th through IQR method')
                    elif self.outliers_action == 'impute':
                        log.append(f'Dedected and imputed {count} outlier values in \'{columnName}\' with {self.outliers_imputation_method} of series through IQR method')

                elif self.outliers_strategy == 'z-score':
                    
                    standard_deviation = self.df[columnName].std(numeric_only = True)
                    if standard_deviation == 0:
                        log.append(f'Standard deviation of \'{columnName}\' is 0 and therefore the column is skipped. Requires manual handling.')
                        continue
                    threshold = self.outliers_threshold 

                    values = columnItems.copy()

                    for i in range(len(columnItems)):

                        current_value = columnItems.iloc[i]
                        current_index = columnItems.index[i]

                        z_score = (current_value - average)/standard_deviation

                        if z_score < (-1*threshold) or z_score > threshold:

                            count += 1

                            if self.outliers_action == 'trim':
                                index_to_trim = columnItems.index[i]
                                self.df = self.df.drop(index = index_to_trim)

                            elif self.outliers_action == 'cap':
                                if z_score < (-1*threshold):
                                    values.loc[current_index] = lower_percentile
                                else:
                                    values.loc[current_index] = upper_percentile

                            elif self.outliers_action == 'impute':
                                if self.outliers_imputation_method == 'mean':
                                    values.loc[current_index] = average
                                elif self.outliers_imputation_method == 'median':
                                    values.loc[current_index] = median
                                elif self.outliers_imputation_method == 'mode':
                                    values.loc[current_index] = mode

                    if self.outliers_action in ['cap', 'impute']:
                        self.df[columnName] = values

                    if self.outliers_action == 'trim':
                        log.append(f'Dedected and trimmed {count} outlier rows in \'{columnName}\' through z-score method')
                    elif self.outliers_action == 'cap':
                        log.append(f'Dedected and capped {count} outlier values in \'{columnName}\' to user-defined percentiles: {self.outliers_cap_method}th and {self.outliers_cap_method2}th through z-score method')
                    elif self.outliers_action == 'impute':
                        log.append(f'Dedected and imputed {count} outlier values in \'{columnName}\' with {self.outliers_imputation_method} of series through z-score method')

            else:
                log.append(f'Skipped {columnName}: unable to find outlier due to incompatible data type (outlier handling is automated for numeric types only - manual handling is required for the rest)')

        print("\n==============================")
        print("📊 OUTLIER DETECTION & HANDLING")
        print("==============================")

        time.sleep(2)
        for entry_ in log:
            print(f'{entry_} \n')
            time.sleep(1)

    def deal_with_duplicates(self):
        
        log = []

        subset_cols = [col for col in self.df.columns if 'id' not in col.lower()]
        df_no_ids = self.df[subset_cols]

        if df_no_ids.duplicated().any():
            if self.duplicates_strategy == 'remove_all':
                self.df = self.df.drop_duplicates(subset=subset_cols)
                log.append('Removed all duplicate rows')
            elif self.duplicates_strategy == 'keep_first':
                self.df = self.df.drop_duplicates(subset=subset_cols, keep = 'first')
                log.append('Removed all duplicate rows except the first')
            elif self.duplicates_strategy == 'keep_last':
                self.df = self.df.drop_duplicates(subset=subset_cols, keep = 'last')
                log.append('Removed all duplicate rows except the last')
        else:
            log.append('No duplicates found')

        print("\n==============================")
        print("🧼 DUPLICATE VALUE HANDLING")
        print("==============================")

        time.sleep(2)
        print(log)

    def deal_with_structure(self):

        log = []

        for columnName, columnItems in self.df.items():

            smallest = 100
            values = columnItems
            best = values
            conversion_type = 'unchanged'
            threshold = 10

            if self.df[columnName].dtype == 'object':

                boolean_map = {'yes' : True, 'no' : False, 'true' : True, 'false' : False, '1' : True, '0' : False, 'on' : True, 'off' : False, 1 : True, 0 : False, 1.0 : True, 0.0 : False}
                before_boolean_conversion = values.copy()
                before_boolean_conversion = before_boolean_conversion.apply(lambda x: x.lower().strip() if not pd.isna(x) else x)              
                Fails3 = 0
                for val in before_boolean_conversion:
                    if pd.isna(val):
                        pass
                    elif val not in boolean_map:
                        Fails3 += 1
                Fails3 = (((Fails3/len(before_boolean_conversion))*100))
                if Fails3 < smallest and Fails3 <= threshold:
                    smallest = Fails3
                    best = before_boolean_conversion.map(boolean_map)
                    conversion_type = 'to boolean'
                
                numeric_converted = pd.to_numeric(values, errors = 'coerce')
                Fails1 = ((numeric_converted.isnull().mean()*100))
                if Fails1 < smallest and Fails1 <= threshold:
                    smallest = Fails1
                    best = numeric_converted
                    conversion_type = 'to numeric'

                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    datetime_converted = pd.to_datetime(values, errors = 'coerce')
                    Fails2 = ((datetime_converted.isnull().mean()*100))
                    if Fails2 < smallest and Fails2 <= threshold:
                        smallest = Fails2
                        best = datetime_converted
                        conversion_type = 'to datetime'

                if conversion_type != 'unchanged':
                    self.df[columnName] = best

            log.append({'column': columnName, 
                    'inferred type': self.df[columnName].dtype,
                    'action': conversion_type, 
                    'fail rate': smallest})

        print("\n==============================")
        print("🔍 STRUCTURE INFERENCE")
        print("==============================")

        time.sleep(2)
        for entry in log:
            print(f'{entry} \n')
            time.sleep(1)
                           
    def deal_with_missing(self):

        self.deal_with_missing_strategy_helper(self.missing_strategy)

    def deal_with_missing_strategy_helper(self, val):
        
        log = []
        log.append(f'Total missing values before: {self.df.isnull().sum().sum()}')
        time.sleep(1)

        for columnName, columnItems in self.df.items():

            percent_missing = (self.df[columnName].isnull().sum())/len(columnItems)

            if percent_missing >= 50:
                self.df = self.df.drop(columns = columnName) 
                log.append(f'More than 50% of column \'{columnName}\' is empty. Full column has been dropped.')
            
            elif is_numeric_dtype(columnItems):
                if self.df[columnName].isna().any():
                    if val in ['impute', 'interpolate'] and 'id' in columnName.lower():
                        log.append(f'Skipped column \'{columnName}\' (likely identifier). Strategy \'{val}\' not applied to ID fields.')
                        continue
                    elif val == 'impute':
                        if self.imputation_method == 'mean':
                            self.df[columnName] = self.df[columnName].fillna(self.df[columnName].mean()) 
                            log.append(f'Filled missing values in \'{columnName}\' using mean-based imputation. (dtype: numeric)')
                        elif self.imputation_method == 'median':
                            self.df[columnName] = self.df[columnName].fillna(self.df[columnName].median()) 
                            log.append(f'Replaced missing values in rows for \'{columnName}\' with median of the series (dtype: numeric)')
                        elif self.imputation_method == 'mode':
                            self.df[columnName] = self.df[columnName].fillna(self.df[columnName].mode().iloc[0]) 
                            log.append(f'Replaced missing values in rows for \'{columnName}\' with mode of the series (dtype: numeric)')
                    elif val == 'drop':
                        self.df = self.df[self.df[columnName].notna()] 
                        log.append(f'Dropped missing rows for \'{columnName}\' (dtype: numeric). Applies to all columns of the same row')
                    elif val == 'interpolate':
                        self.df[columnName] = self.df[columnName].interpolate(method = 'linear') 
                        log.append(f'Interpolated missing values for \'{columnName}\' (dtype: numeric)')

            elif is_bool_dtype(columnItems): 
                if self.df[columnName].isna().any():
                    if val == 'impute':
                        if self.imputation_method == 'mean':
                            column_average = self.df[columnName].mean()
                            if column_average >= 0.5:
                                mean_boolean = 1
                            else:
                                mean_boolean = 0
                            self.df[columnName] = self.df[columnName].fillna(bool(mean_boolean))
                            log.append(f'Filled missing values in \'{columnName}\' using mean-based imputation (\'{columnName}\' mean ≥ 0.5 → True else False. If user wants more control, manual handling of \'{columnName}\' is necessary) (dtype: boolean)')  
                        elif self.imputation_method == 'median': 
                            column_median =self.df[columnName].median()
                            if column_median == 0.5:
                                median_boolean = 1
                            else:
                                median_boolean = 0
                            self.df[columnName] = self.df[columnName].fillna(bool(median_boolean))
                            log.append(f'Filled missing values in \'{columnName}\' with median of the series (\'{columnName}\' median == 0.5 → True else False. If user wants more control, manual handling of \'{columnName}\' is necessary) (dtype: boolean)') 
                        elif self.imputation_method == 'mode':
                            self.df[columnName] = self.df[columnName].fillna(self.df[columnName].mode().iloc[0]) 
                            log.append(f'Replaced missing values in rows for \'{columnName}\' with mode of the series (dtype: boolean)')
                    elif val == 'drop':
                        self.df = self.df[self.df[columnName].notna()] 
                        log.append(f'Dropped missing rows for \'{columnName}\' (dtype: boolean). Applies to all columns of the same row')
                    elif val == 'interpolate': 
                        if columnItems.iloc[0].isna() and columnItems.iloc[-1].isna():
                            self.df[columnName] = self.df[columnName].fillna(method = 'ffill')
                            log.append(f'Interpolated missing values for \'{columnName}\' using forward fill. First value remains unfilled (NaN) due to a lack of prior valu. Requires manual handling (dtype: boolean)')
                        elif columnItems.iloc[0].isna():
                            self.df[columnName] = self.df[columnName].fillna(method = 'bfill')
                            log.append(f'Interpolated missing values for \'{columnName}\' using backward fill (dtype: boolean)')
                        else:
                            self.df[columnName] = self.df[columnName].fillna(method = 'ffill')
                            log.append(f'Interpolated missing values for \'{columnName}\' using forward fill (dtype: boolean)')
            
            elif is_datetime64_any_dtype(columnItems): 
                if self.df[columnName].isna().any():
                    if val == 'impute':
                        log.append(f'Skipped \'{columnName}\' (dtype: datetime): incompatible with strategy: \'impute\'. User must handle manually')
                    elif val == 'drop':
                        self.df = self.df[self.df[columnName].notna()]
                        log.append(f'Dropped missing rows with missing values (dtype: datetime). Applies to all \'{columnName}\' columns of the same row')
                    elif val == 'interpolate':
                        self.df[columnName] = self.df[columnName].interpolate(method = 'time')
                        log.append(f'Interpolated missing dates for \'{columnName}\' (dtype: datetime)')

            else: 
                if self.df[columnName].isna().any():
                    if val == 'impute':
                        log.append(f'Skipped \'{columnName}\' because the series is not recognized as a valid data type for imputation')
                    elif val == 'interpolate':
                        log.append(f'Skipped \'{columnName}\' because the series is not recognized as a valid data type for interpolation')
                    elif val == 'drop':
                        self.df = self.df[self.df[columnName].notna()]
                        log.append(f'Dropped missing rows with missing values (dtype: unknown/object). Applies to all \'{columnName}\' columns of the same row')

        log.append(f'Total missing values after: {self.df.isnull().sum().sum()}')
        
        print("\n==============================")
        print("🧼 MISSING VALUE HANDLING")
        print("==============================")

        time.sleep(2)
        for entry in log:
            print(f'{entry} \n')
            time.sleep(1)

    def clean(self): #verifies flags then calls the above methods

        if self.structure:

            self.clean_helper(self.deal_with_structure)

        if self.duplicates:
            self.clean_helper(self.deal_with_duplicates)

        if self.missing:
            self.clean_helper(self.deal_with_missing)

        if self.outliers:
            self.clean_helper(self.deal_with_outliers)

        return self.df
    
    def clean_helper(self, func):
        
        start_time = time.perf_counter()
        func()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"\nTime taken to execute {func.__name__}: {elapsed_time:.4f} seconds \n")
        time.sleep(5)