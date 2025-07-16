from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
import os
import pandas as pd
from .models import FileUpload, DataAnalysis, CleaningJob
from .utils.analyzer import CSVAnalyzer
from .utils.cleaner import DataCleaner

logger = get_task_logger(__name__)

@shared_task(bind=True)
def analyze_file(self, file_upload_id):
    """Background task to analyze uploaded CSV file"""
    file_upload = FileUpload.objects.get(id=file_upload_id)
    file_path = file_upload.original_file.path
    
    try:
        analyzer = CSVAnalyzer(file_path)
        analysis_data = analyzer.analyze()
        
        DataAnalysis.objects.create(
            file_upload=file_upload,
            total_rows=analysis_data['basic_info']['rows'],
            total_columns=analysis_data['basic_info']['columns'],
            missing_values_summary=analysis_data['missing_values'],
            data_types_detected=analysis_data['data_types'],
            categorical_columns=analysis_data['column_classification']['categorical'],
            numeric_columns=analysis_data['column_classification']['numeric'],
            outliers_detected=analysis_data['outliers'],
            recommendations=analysis_data['recommendations']
        )
        
        return True
    except Exception as e:
        logger.error(f"Analysis failed for {file_upload_id}: {str(e)}")
        raise

@shared_task(bind=True)
def clean_data(self, job_id):
    """Background task to clean data based on user options"""
    job = CleaningJob.objects.get(id=job_id)
    job.status = 'processing'
    job.save()
    
    try:
        file_path = job.file_upload.original_file.path
        df = pd.read_csv(file_path)
        
        cleaner = DataCleaner(job.cleaning_options)
        cleaned_df, report = cleaner.clean_data(df)
        
        # Save cleaned files
        output_dir = os.path.join(settings.MEDIA_ROOT, 'cleaned')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save cleaned CSV
        cleaned_path = os.path.join(output_dir, f'cleaned_{job.id}.csv')
        cleaned_df.to_csv(cleaned_path, index=False)
        
        # Save numeric-only version if applicable
        numeric_cols = job.analysis.numeric_columns
        if numeric_cols:
            numeric_path = os.path.join(output_dir, f'numeric_{job.id}.csv')
            cleaned_df[numeric_cols].to_csv(numeric_path, index=False)
        
        # Update job status
        job.status = 'completed'
        job.cleaned_file_path = cleaned_path
        job.numeric_file_path = numeric_path if numeric_cols else ''
        job.cleaning_report = report
        job.save()
        
        return True
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        logger.error(f"Cleaning failed for job {job_id}: {str(e)}")
        raise
