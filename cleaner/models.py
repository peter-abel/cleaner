from django.db import models
import uuid
import os

class FileUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40)
    
    class Meta:
        ordering = ['-upload_timestamp']
       
        db_table = 'FileUpload'

    def __str__(self):
        return f"{self.original_filename} ({self.file_size} bytes)"

class DataAnalysis(models.Model):
    file_upload = models.OneToOneField(FileUpload, on_delete=models.CASCADE)
    total_rows = models.IntegerField()
    total_columns = models.IntegerField()
    missing_values_summary = models.JSONField()  # {column: {count, percentage}}
    data_types_detected = models.JSONField()     # {column: detected_type}
    categorical_columns = models.JSONField()     # [column_names]
    numeric_columns = models.JSONField()         # [column_names]
    outliers_detected = models.JSONField()       # {column: outlier_count}
    recommendations = models.JSONField()         # Auto-generated cleaning suggestions
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.file_upload.original_filename}"

class CleaningJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    analysis = models.ForeignKey(DataAnalysis, on_delete=models.CASCADE)
    
    # Cleaning configuration
    cleaning_options = models.JSONField()  # User-selected options
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Results
    cleaned_file_path = models.CharField(max_length=500, blank=True)
    numeric_file_path = models.CharField(max_length=500, blank=True)
    cleaning_report = models.JSONField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Job {self.id} - {self.status}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES)[self.status]
