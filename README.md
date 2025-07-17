# CSV Data Cleaner & Analyzer

A comprehensive Django web application for cleaning and preprocessing CSV datasets, designed for data scientists, analysts, and researchers who need to quickly prepare data for analysis or machine learning.

## 🚀 Features

### Core Functionality
- **Intelligent CSV Analysis**: Automatically detects data types, missing values, outliers, and data quality issues
- **Synchronous Processing**: Real-time data cleaning without background task complexity
- **Smart Data Cleaning**: Handles missing values, data type corrections, and inconsistencies
- **Advanced Preprocessing**: Feature engineering, categorical encoding, and numeric scaling
- **Comprehensive Reporting**: Detailed cleaning reports with before/after statistics
- **Multiple Export Options**: Download cleaned data and numeric-only versions

### Key Capabilities
- **Missing Value Detection**: Identifies various missing data representations (`?`, `null`, `''`, etc.)
- **Data Type Intelligence**: Automatically converts text to numeric where appropriate
- **Outlier Detection**: Uses IQR method to identify and optionally remove outliers
- **Feature Engineering**: Creates derived features (ratios, combinations)
- **Categorical Encoding**: Label encoding and one-hot encoding options
- **Numeric Scaling**: Standard, MinMax, and Robust scaling methods

## 📋 Requirements

```
Django==5.2.3
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
celery==5.3.1
redis==4.5.5
python-dotenv==1.0.0
```

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/peter-abel/cleaner.git
cd cleaner
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py makemigrations cleaner
python manage.py migrate
```

### 5. Run the Application
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 📖 How to Use

### Step 1: Upload CSV File
1. Navigate to the home page
2. Click "Choose File" and select your CSV file
3. Click "Upload & Analyze"
4. The system will automatically analyze your data and show results

### Step 2: Review Analysis Results
The analysis page displays:
- **File Summary**: Row/column counts, basic statistics
- **Missing Values**: Columns with missing data and percentages
- **Data Types**: Detected data types for each column
- **Outliers**: Columns with outlier detection results
- **Recommendations**: Automated suggestions for cleaning

### Step 3: Configure Cleaning Options
Choose from various cleaning and preprocessing options:

#### Core Cleaning (Always Applied)
- Missing value imputation (median for numeric, mode for categorical)
- Data type correction and standardization
- Inconsistency fixes (e.g., "two" → 2 for door counts)

#### Optional Enhancements
- **Feature Engineering**: Create derived features and ratios
- **Categorical Encoding**: 
  - Label Encoding: Convert categories to numbers
  - One-Hot Encoding: Create binary columns for each category
- **Numeric Scaling**:
  - Standard Scaling: Mean=0, Std=1
  - MinMax Scaling: Scale to 0-1 range
  - Robust Scaling: Uses median and IQR
- **Outlier Removal**: Remove data points beyond IQR thresholds

### Step 4: Download Results
After processing, download:
- **Cleaned Dataset**: Full cleaned dataset with all columns
- **Numeric Dataset**: Only numeric columns (ideal for ML)
- **Cleaning Report**: Detailed log of all transformations applied

## 🎯 Best Practices

### Data Preparation
1. **File Format**: Ensure your CSV has proper headers and consistent formatting
2. **File Size**: For large files (>100MB), consider splitting into smaller chunks
3. **Encoding**: Use UTF-8 encoding to avoid character issues
4. **Backup**: Always keep a backup of your original data

### Optimal Cleaning Strategy

#### For Exploratory Data Analysis
```
✅ Enable Feature Engineering
✅ Use Label Encoding for categoricals
✅ Apply Standard Scaling
❌ Don't remove outliers (they might be important)
```

#### For Machine Learning
```
✅ Enable Feature Engineering
✅ Use One-Hot Encoding for categoricals (if few categories)
✅ Use Label Encoding for high-cardinality categoricals
✅ Apply appropriate scaling (Standard for most algorithms)
✅ Consider outlier removal (depends on algorithm)
```

#### For Statistical Analysis
```
❌ Minimal feature engineering
✅ Keep original data types where possible
❌ Avoid aggressive scaling
✅ Carefully consider outlier removal
```

### Column-Specific Recommendations

#### Numeric Columns
- **Continuous Variables**: Use Standard or Robust scaling
- **Count Data**: Consider log transformation before scaling
- **Ratios/Percentages**: MinMax scaling often works well

#### Categorical Columns
- **Low Cardinality (<10 categories)**: One-Hot Encoding
- **High Cardinality (>10 categories)**: Label Encoding
- **Ordinal Data**: Manual mapping or Label Encoding

#### Text Columns
- **Names/IDs**: Usually exclude from analysis
- **Free Text**: Consider text preprocessing (not included in this tool)

## 🔧 Advanced Features

### Feature Engineering Examples
The system automatically creates:
- **Power-to-Weight Ratio**: `horsepower / curb_weight`
- **Combined MPG**: `(city_mpg + highway_mpg) / 2`
- **Custom Ratios**: Based on detected numeric relationships

### Outlier Detection
- Uses **Interquartile Range (IQR)** method
- Default threshold: 1.5 × IQR
- Adjustable threshold in cleaning options
- Reports outlier counts and percentages

### Missing Value Strategies
- **Numeric**: Median imputation (robust to outliers)
- **Categorical**: Mode imputation (most frequent value)
- **Mixed Types**: Intelligent type detection first

## 🐛 Debugging & Troubleshooting

### Common Issues

#### "No such table" Error
```bash
python manage.py makemigrations cleaner
python manage.py migrate
```

#### CSV Reading Errors
- Check file encoding (should be UTF-8)
- Ensure consistent delimiter (comma)
- Verify no corrupted rows

#### Memory Issues with Large Files
- Process files in smaller chunks
- Increase system memory allocation
- Consider data sampling for initial analysis

### Debug Information
The application provides detailed debug information:
- File upload status and path verification
- Analysis step-by-step progress
- Cleaning operation logs
- Error tracebacks with specific line numbers

## 📊 Understanding the Output

### Cleaning Report Structure
```json
{
  "original_shape": [rows, columns],
  "cleaned_shape": [rows, columns],
  "cleaning_steps": ["step1", "step2", ...],
  "outliers_detected": {"column": {"count": N, "percentage": X}},
  "transformers_used": ["imputer", "scaler", ...]
}
```

### File Outputs
- **cleaned_[job_id].csv**: Complete cleaned dataset
- **numeric_[job_id].csv**: Only numeric columns
- Both files maintain row order from original data

## 🚀 Performance Tips

### For Best Performance
1. **Clean Data First**: Remove obviously bad rows manually
2. **Appropriate Scaling**: Choose scaling method based on data distribution
3. **Feature Selection**: Don't over-engineer features for simple analyses
4. **Iterative Approach**: Start with basic cleaning, then add complexity

### Memory Optimization
- Process large files in chunks
- Use appropriate data types (int32 vs int64)
- Remove unnecessary columns before processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the debug information in the web interface
2. Review the troubleshooting section above
3. Create an issue on GitHub with:
   - Error message and traceback
   - Sample data (anonymized)
   - Steps to reproduce

## 🔄 Version History

### v2.0.0 (Current)
- ✅ Synchronous processing (no Celery dependency)
- ✅ Enhanced debugging and error reporting
- ✅ Improved user interface with real-time feedback
- ✅ Better handling of edge cases and data types

### v1.0.0
- ✅ Basic CSV cleaning functionality
- ✅ Asynchronous processing with Celery
- ✅ Core analysis and cleaning features

---

**Happy Data Cleaning! 🧹📊**
