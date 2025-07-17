# Technical Documentation - CSV Data Cleaner

## 🏗️ Architecture Overview

The application follows a standard Django MVC pattern with synchronous processing for real-time data cleaning and analysis.

### Core Components

```
cleaner/
├── models.py          # Data models (FileUpload, DataAnalysis, CleaningJob)
├── views.py           # Request handling and business logic
├── urls.py            # URL routing
├── utils/
│   ├── analyzer.py    # CSV analysis logic
│   └── cleaner.py     # Data cleaning algorithms
└── templates/         # HTML templates
```

## 📊 Data Models

### FileUpload Model
```python
class FileUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    original_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40)
```

### DataAnalysis Model
```python
class DataAnalysis(models.Model):
    file_upload = models.OneToOneField(FileUpload, on_delete=models.CASCADE)
    total_rows = models.IntegerField()
    total_columns = models.IntegerField()
    missing_values_summary = models.JSONField()
    data_types_detected = models.JSONField()
    categorical_columns = models.JSONField()
    numeric_columns = models.JSONField()
    outliers_detected = models.JSONField()
    recommendations = models.JSONField()
```

### CleaningJob Model
```python
class CleaningJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    analysis = models.ForeignKey(DataAnalysis, on_delete=models.CASCADE)
    cleaning_options = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    cleaned_file_path = models.CharField(max_length=500)
    numeric_file_path = models.CharField(max_length=500)
    cleaning_report = models.JSONField()
```

## 🔄 Processing Flow

### 1. File Upload & Analysis
```python
def upload_view(request):
    # 1. Validate CSV file
    # 2. Create FileUpload record
    # 3. Perform synchronous analysis
    # 4. Create DataAnalysis record
    # 5. Return analysis results
```

### 2. Data Analysis Pipeline
```python
class CSVAnalyzer:
    def analyze(self):
        return {
            'basic_info': self._get_basic_info(),
            'missing_values': self._analyze_missing_values(),
            'data_types': self._detect_data_types(),
            'column_classification': self._classify_columns(),
            'outliers': self._detect_outliers(),
            'recommendations': self._generate_recommendations()
        }
```

### 3. Data Cleaning Pipeline
```python
class DataCleaner:
    def clean_data(self, df):
        # Core cleaning (always applied)
        cleaned_df = self._handle_missing_values(df)
        cleaned_df = self._correct_data_types(cleaned_df)
        cleaned_df = self._fix_inconsistencies(cleaned_df)
        
        # Optional enhancements
        if self.options.get('feature_engineering'):
            cleaned_df = self._engineer_features(cleaned_df)
        if self.options.get('encoding_method'):
            cleaned_df = self._encode_categorical(cleaned_df)
        if self.options.get('scaling_method'):
            cleaned_df = self._scale_features(cleaned_df)
        if self.options.get('remove_outliers'):
            cleaned_df = self._remove_outliers(cleaned_df)
            
        return cleaned_df, report
```

## 🧠 Algorithm Details

### Missing Value Detection
```python
def _analyze_missing_values(self):
    missing_info = {}
    for col in self.df.columns:
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
```

### Data Type Detection
```python
def _detect_data_types(self):
    type_mapping = {}
    for col in self.df.columns:
        clean_series = self.df[col].replace(['?', '', 'null'], np.nan).dropna()
        
        try:
            pd.to_numeric(clean_series)
            if clean_series.astype(str).str.contains('\.').sum() == 0:
                type_mapping[col] = 'integer'
            else:
                type_mapping[col] = 'float'
        except:
            unique_ratio = len(clean_series.unique()) / len(clean_series)
            if unique_ratio < 0.1:
                type_mapping[col] = 'categorical'
            else:
                type_mapping[col] = 'text'
    return type_mapping
```

### Outlier Detection (IQR Method)
```python
def _detect_outliers(self):
    outliers = {}
    for col in numeric_cols:
        clean_data = pd.to_numeric(self.df[col], errors='coerce').dropna()
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
```

## 🔧 Extending the Application

### Adding New Cleaning Methods

1. **Add to DataCleaner class**:
```python
def _custom_cleaning_method(self, df):
    # Your custom logic here
    self.cleaning_log.append("Applied custom cleaning method")
    return df
```

2. **Update cleaning pipeline**:
```python
def clean_data(self, df):
    # ... existing code ...
    if self.options.get('custom_method'):
        cleaned_df = self._custom_cleaning_method(cleaned_df)
    # ... rest of pipeline ...
```

3. **Add UI option** in `analyze.html`:
```html
<div class="form-check form-switch mb-3">
    <input class="form-check-input" type="checkbox" 
           id="customMethod" name="custom_method">
    <label class="form-check-label" for="customMethod">
        Enable Custom Method
    </label>
</div>
```

### Adding New Analysis Features

1. **Extend CSVAnalyzer**:
```python
def _custom_analysis(self):
    # Your analysis logic
    return analysis_results

def analyze(self):
    return {
        # ... existing analyses ...
        'custom_analysis': self._custom_analysis()
    }
```

2. **Update DataAnalysis model**:
```python
class DataAnalysis(models.Model):
    # ... existing fields ...
    custom_analysis_results = models.JSONField(blank=True, null=True)
```

3. **Create and run migration**:
```bash
python manage.py makemigrations cleaner
python manage.py migrate
```

### Adding New File Formats

1. **Create new analyzer class**:
```python
class ExcelAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
    
    def analyze(self):
        # Similar to CSVAnalyzer but for Excel
        pass
```

2. **Update upload validation**:
```python
def upload_view(request):
    # ... existing code ...
    if not (uploaded_file.name.endswith('.csv') or 
            uploaded_file.name.endswith('.xlsx')):
        return JsonResponse({'error': 'Please upload a CSV or Excel file'})
    
    # Choose appropriate analyzer
    if uploaded_file.name.endswith('.xlsx'):
        analyzer = ExcelAnalyzer(file_path)
    else:
        analyzer = CSVAnalyzer(file_path)
```

## 🎨 Frontend Customization

### Adding New UI Components

1. **Extend base template** (`templates/cleaner/base.html`):
```html
<!-- Add custom CSS/JS -->
<link rel="stylesheet" href="{% static 'cleaner/custom.css' %}">
<script src="{% static 'cleaner/custom.js' %}"></script>
```

2. **Create custom templates**:
```html
<!-- templates/cleaner/custom_analysis.html -->
{% extends "cleaner/base.html" %}
{% block content %}
<!-- Your custom content -->
{% endblock %}
```

3. **Add new URL patterns**:
```python
# urls.py
urlpatterns = [
    # ... existing patterns ...
    path('custom-analysis/<uuid:file_id>/', views.custom_analysis_view, name='custom_analysis'),
]
```

## 🔍 Debugging Features

### Debug Information Structure
```python
debug_info = [
    "File uploaded: filename.csv, Size: 12345",
    "File upload record created with ID: uuid",
    "Starting analysis of file: /path/to/file",
    "CSV successfully read. Shape: (100, 10)",
    "Analysis completed successfully",
    "Analysis results: ['basic_info', 'missing_values', ...]"
]
```

### Error Handling Pattern
```python
try:
    # Operation
    debug_info.append("Operation successful")
except Exception as e:
    debug_info.append(f"ERROR: {str(e)}")
    debug_info.append(f"Traceback: {traceback.format_exc()}")
    return JsonResponse({'error': str(e), 'debug': debug_info}, status=500)
```

## 📊 Performance Considerations

### Memory Optimization
```python
# Use appropriate data types
df = df.astype({
    'int_column': 'int32',  # Instead of int64
    'float_column': 'float32'  # Instead of float64
})

# Process in chunks for large files
chunk_size = 10000
for chunk in pd.read_csv(file_path, chunksize=chunk_size):
    process_chunk(chunk)
```

### Database Optimization
```python
# Use select_related for foreign keys
job = CleaningJob.objects.select_related('file_upload', 'analysis').get(id=job_id)

# Use bulk operations for multiple records
CleaningJob.objects.bulk_create([job1, job2, job3])
```

## 🧪 Testing

### Unit Test Example
```python
# tests.py
from django.test import TestCase
from cleaner.utils.analyzer import CSVAnalyzer
import pandas as pd
import tempfile

class CSVAnalyzerTest(TestCase):
    def test_missing_value_detection(self):
        # Create test CSV
        df = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': ['a', 'b', '?', 'd']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            
            analyzer = CSVAnalyzer(f.name)
            results = analyzer.analyze()
            
            self.assertIn('col1', results['missing_values'])
            self.assertIn('col2', results['missing_values'])
```

### Integration Test Example
```python
def test_full_cleaning_pipeline(self):
    # Upload file
    response = self.client.post('/', {
        'csv_file': SimpleUploadedFile('test.csv', b'col1,col2\n1,a\n2,b')
    })
    
    # Check analysis
    file_id = response.json()['file_id']
    response = self.client.get(f'/analyze/{file_id}/')
    self.assertEqual(response.status_code, 200)
    
    # Test cleaning
    response = self.client.post(f'/analyze/{file_id}/', {
        'feature_engineering': 'on',
        'encoding_method': 'label'
    })
    self.assertEqual(response.status_code, 302)  # Redirect to results
```

## 🚀 Deployment

### Production Settings
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Use PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cleaner_db',
        'USER': 'db_user',
        'PASSWORD': 'db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_ROOT = '/path/to/static/'
MEDIA_ROOT = '/path/to/media/'
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

This technical documentation provides the foundation for understanding, extending, and maintaining the CSV Data Cleaner application.
