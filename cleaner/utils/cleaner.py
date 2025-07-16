import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer
from typing import Dict, Any, Tuple

class DataCleaner:
    def __init__(self, options: Dict[str, Any]):
        self.options = options
        self.cleaning_log = []
        self.transformers = {}
    
    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Main cleaning pipeline"""
        cleaned_df = df.copy()
        
        # Core cleaning (always applied)
        cleaned_df = self._handle_missing_values(cleaned_df)
        cleaned_df = self._correct_data_types(cleaned_df)
        cleaned_df = self._fix_inconsistencies(cleaned_df)
        outlier_info = self._detect_outliers(cleaned_df)
        
        # Optional enhancements
        if self.options.get('feature_engineering', False):
            cleaned_df = self._engineer_features(cleaned_df)
        
        if self.options.get('encoding_method'):
            cleaned_df = self._encode_categorical(cleaned_df)
        
        if self.options.get('scaling_method'):
            cleaned_df = self._scale_features(cleaned_df)
        
        if self.options.get('remove_outliers', False):
            cleaned_df = self._remove_outliers(cleaned_df)
        
        # Generate report
        report = {
            'original_shape': df.shape,
            'cleaned_shape': cleaned_df.shape,
            'cleaning_steps': self.cleaning_log,
            'outliers_detected': outlier_info,
            'transformers_used': list(self.transformers.keys())
        }
        
        return cleaned_df, report
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with intelligent imputation"""
        # Replace various missing representations
        df = df.replace(['?', '', 'null', 'NULL', 'nan', 'NaN'], np.nan)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Numeric imputation (median)
        if len(numeric_cols) > 0:
            numeric_imputer = SimpleImputer(strategy='median')
            df[numeric_cols] = numeric_imputer.fit_transform(df[numeric_cols])
            self.transformers['numeric_imputer'] = numeric_imputer
            self.cleaning_log.append(f"Imputed {len(numeric_cols)} numeric columns with median")
        
        # Categorical imputation (mode)
        if len(categorical_cols) > 0:
            categorical_imputer = SimpleImputer(strategy='most_frequent')
            df[categorical_cols] = categorical_imputer.fit_transform(df[categorical_cols])
            self.transformers['categorical_imputer'] = categorical_imputer
            self.cleaning_log.append(f"Imputed {len(categorical_cols)} categorical columns with mode")
        
        return df
    
    def _correct_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types"""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try numeric conversion
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if not numeric_series.isna().all():
                    df[col] = numeric_series
                    self.cleaning_log.append(f"Converted {col} to numeric")
        
        return df
    
    def _fix_inconsistencies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix common data inconsistencies"""
        text_to_numeric_mappings = {
            'num_of_doors': {'two': 2, 'four': 4},
            'num_of_cylinders': {'two': 2, 'three': 3, 'four': 4, 'five': 5, 
                               'six': 6, 'eight': 8, 'twelve': 12}
        }
        
        for col, mapping in text_to_numeric_mappings.items():
            if col in df.columns:
                df[col] = df[col].map(mapping).fillna(df[col])
                self.cleaning_log.append(f"Converted text values to numeric in {col}")
        
        return df
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict:
        """Detect outliers using IQR method"""
        outlier_info = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            if len(outliers) > 0:
                outlier_info[col] = {
                    'count': len(outliers),
                    'percentage': round(len(outliers) / len(df) * 100, 2)
                }
        
        return outlier_info
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features"""
        # Auto-detect potential ratio features
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Example: power-to-weight if both exist
        if 'horsepower' in df.columns and 'curb_weight' in df.columns:
            df['power_to_weight_ratio'] = df['horsepower'] / df['curb_weight']
            self.cleaning_log.append("Created power_to_weight_ratio feature")
        
        # Example: efficiency metrics
        if 'city_mpg' in df.columns and 'highway_mpg' in df.columns:
            df['combined_mpg'] = (df['city_mpg'] + df['highway_mpg']) / 2
            self.cleaning_log.append("Created combined_mpg feature")
        
        return df
    
    def _encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        categorical_cols = df.select_dtypes(include=['object']).columns
        encoding_method = self.options.get('encoding_method', 'label')
        
        if encoding_method == 'label':
            label_encoders = {}
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
            
            self.transformers['label_encoders'] = label_encoders
            self.cleaning_log.append(f"Label encoded {len(categorical_cols)} categorical columns")
        
        elif encoding_method == 'onehot':
            df = pd.get_dummies(df, columns=categorical_cols, prefix=categorical_cols)
            self.cleaning_log.append(f"One-hot encoded {len(categorical_cols)} categorical columns")
        
        return df
    
    def _scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numeric features"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        scaling_method = self.options.get('scaling_method', 'standard')
        
        scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        
        scaler = scalers.get(scaling_method, StandardScaler())
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
        
        self.transformers['scaler'] = scaler
        self.cleaning_log.append(f"Applied {scaling_method} scaling to {len(numeric_cols)} numeric columns")
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers based on IQR method"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        initial_rows = len(df)
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            threshold = self.options.get('outlier_threshold', 1.5)
            
            df = df[~((df[col] < Q1 - threshold * IQR) | (df[col] > Q3 + threshold * IQR))]
        
        removed_rows = initial_rows - len(df)
        self.cleaning_log.append(f"Removed {removed_rows} outlier rows")
        
        return df
