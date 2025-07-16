import pandas as pd
import numpy as np
from typing import Dict, List, Any

class CSVAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.analysis_results = {}
    
    def analyze(self) -> Dict[str, Any]:
        """Complete data analysis pipeline"""
        self.df = pd.read_csv(self.file_path)
        
        return {
            'basic_info': self._get_basic_info(),
            'missing_values': self._analyze_missing_values(),
            'data_types': self._detect_data_types(),
            'column_classification': self._classify_columns(),
            'outliers': self._detect_outliers(),
            'recommendations': self._generate_recommendations()
        }
    
    def _get_basic_info(self) -> Dict:
        return {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': self.df.memory_usage(deep=True).sum(),
            'duplicate_rows': self.df.duplicated().sum()
        }
    
    def _analyze_missing_values(self) -> Dict:
        missing_info = {}
        for col in self.df.columns:
            # Count various representations of missing data
            missing_count = (
                self.df[col].isna().sum() + 
                (self.df[col] == '?').sum() + 
                (self.df[col] == '').sum() +
                (self.df[col] == 'null').sum()
            )
            
            if missing_count > 0:
                missing_info[col] = {
                    'count': int(missing_count),
                    'percentage': round(missing_count / len(self.df) * 100, 2)
                }
        return missing_info
    
    def _detect_data_types(self) -> Dict:
        type_mapping = {}
        for col in self.df.columns:
            # Clean the column first
            clean_series = self.df[col].replace(['?', '', 'null', 'NULL'], np.nan)
            clean_series = clean_series.dropna()
            
            if len(clean_series) == 0:
                type_mapping[col] = 'unknown'
                continue
            
            # Try numeric conversion
            try:
                pd.to_numeric(clean_series)
                # Check if integers
                if clean_series.astype(str).str.contains('\.').sum() == 0:
                    type_mapping[col] = 'integer'
                else:
                    type_mapping[col] = 'float'
            except:
                # Check for categorical patterns
                unique_ratio = len(clean_series.unique()) / len(clean_series)
                if unique_ratio < 0.1:  # Less than 10% unique values
                    type_mapping[col] = 'categorical'
                else:
                    type_mapping[col] = 'text'
        
        return type_mapping
    
    def _classify_columns(self) -> Dict:
        data_types = self._detect_data_types()
        return {
            'numeric': [col for col, dtype in data_types.items() 
                       if dtype in ['integer', 'float']],
            'categorical': [col for col, dtype in data_types.items() 
                          if dtype == 'categorical'],
            'text': [col for col, dtype in data_types.items() 
                    if dtype == 'text']
        }
    
    def _detect_outliers(self) -> Dict:
        outliers = {}
        numeric_cols = self._classify_columns()['numeric']
        
        for col in numeric_cols:
            clean_data = pd.to_numeric(self.df[col], errors='coerce').dropna()
            if len(clean_data) > 0:
                Q1 = clean_data.quantile(0.25)
                Q3 = clean_data.quantile(0.75)
                IQR = Q3 - Q1
                outlier_count = ((clean_data < Q1 - 1.5 * IQR) | 
                               (clean_data > Q3 + 1.5 * IQR)).sum()
                
                if outlier_count > 0:
                    outliers[col] = {
                        'count': int(outlier_count),
                        'percentage': round(outlier_count / len(clean_data) * 100, 2)
                    }
        
        return outliers
    
    def _generate_recommendations(self) -> Dict:
        missing_vals = self._analyze_missing_values()
        outliers = self._detect_outliers()
        classification = self._classify_columns()
        
        recommendations = {
            'required_cleaning': ['missing_values', 'data_types', 'consistency'],
            'suggested_enhancements': [],
            'warnings': []
        }
        
        # Generate contextual recommendations
        if len(classification['numeric']) > 3:
            recommendations['suggested_enhancements'].append('feature_engineering')
        
        if len(classification['categorical']) > 0:
            recommendations['suggested_enhancements'].append('encoding')
        
        if any(info['percentage'] > 10 for info in missing_vals.values()):
            recommendations['warnings'].append('High missing data percentage detected')
        
        if len(outliers) > len(classification['numeric']) * 0.5:
            recommendations['warnings'].append('Multiple columns contain outliers')
        
        return recommendations
