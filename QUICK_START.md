# Quick Start Guide - CSV Data Cleaner

## 🚀 Get Started in 5 Minutes

### 1. Setup (One-time)
```bash
# Clone and setup
git clone https://github.com/peter-abel/cleaner.git
cd cleaner
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Database setup
python manage.py makemigrations cleaner
python manage.py migrate

# Run
python manage.py runserver
```

### 2. Use the Application
1. **Upload**: Go to `http://localhost:8000` → Upload CSV
2. **Analyze**: Review automatic analysis results
3. **Configure**: Choose cleaning options
4. **Download**: Get cleaned files

## 🎯 Common Use Cases

### Quick Data Exploration
```
✅ Feature Engineering: ON
✅ Encoding: Label Encoding
✅ Scaling: Standard Scaling
❌ Remove Outliers: OFF
```

### Machine Learning Prep
```
✅ Feature Engineering: ON
✅ Encoding: One-Hot (if <10 categories) or Label
✅ Scaling: Standard Scaling
✅ Remove Outliers: ON (threshold: 1.5)
```

### Statistical Analysis
```
❌ Feature Engineering: OFF
✅ Encoding: Label Encoding only
❌ Scaling: OFF
✅ Remove Outliers: Carefully consider
```

## 🔧 Key Features

| Feature | What it does | When to use |
|---------|-------------|-------------|
| **Missing Value Handling** | Fills gaps with median/mode | Always enabled |
| **Data Type Correction** | Converts text to numbers | Always enabled |
| **Feature Engineering** | Creates ratios, combinations | For ML/exploration |
| **Categorical Encoding** | Converts categories to numbers | For ML algorithms |
| **Numeric Scaling** | Normalizes number ranges | For ML algorithms |
| **Outlier Removal** | Removes extreme values | Depends on analysis goal |

## 📊 Output Files

- **cleaned_[id].csv**: Complete cleaned dataset
- **numeric_[id].csv**: Only numeric columns (ML-ready)
- **Cleaning Report**: JSON with transformation details

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "No such table" error | Run `python manage.py migrate` |
| CSV won't upload | Check file encoding (use UTF-8) |
| Memory issues | Use smaller files (<100MB) |
| Missing columns | Check original CSV headers |

## 💡 Pro Tips

1. **Always backup** your original data
2. **Start simple** - use basic cleaning first
3. **Check the debug info** if something fails
4. **Use numeric-only export** for machine learning
5. **Review the cleaning report** to understand changes

## 📈 Best Results

- **Clean headers**: No spaces, special characters
- **Consistent format**: Same date format, number format
- **UTF-8 encoding**: Avoid character issues
- **Reasonable size**: <100MB for best performance

---

Need more details? Check the full [README.md](README.md) file.
