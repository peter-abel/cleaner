from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from .models import FileUpload, DataAnalysis, CleaningJob
from .utils.analyzer import CSVAnalyzer
from .utils.cleaner import DataCleaner
import json
import os
import pandas as pd
import traceback

def upload_view(request):
    """File upload page"""
    debug_info = []
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        uploaded_file = request.FILES['csv_file']
        debug_info.append(f"File uploaded: {uploaded_file.name}, Size: {uploaded_file.size}")
        
        # Validate file
        if not uploaded_file.name.endswith('.csv'):
            debug_info.append("ERROR: File is not a CSV")
            return JsonResponse({'error': 'Please upload a CSV file', 'debug': debug_info}, status=400)
        
        try:
            # Create file upload record
            file_upload = FileUpload.objects.create(
                original_file=uploaded_file,
                original_filename=uploaded_file.name,
                file_size=uploaded_file.size,
                session_key=request.session.session_key or request.session.create()
            )
            debug_info.append(f"File upload record created with ID: {file_upload.id}")
            debug_info.append(f"File saved to: {file_upload.original_file.path}")
            
            # Perform analysis synchronously
            try:
                file_path = file_upload.original_file.path
                debug_info.append(f"Starting analysis of file: {file_path}")
                
                # Check if file exists
                if not os.path.exists(file_path):
                    debug_info.append(f"ERROR: File does not exist at path: {file_path}")
                    return JsonResponse({'error': 'File not found after upload', 'debug': debug_info}, status=500)
                
                # Try to read the CSV first to check for issues
                try:
                    df_test = pd.read_csv(file_path)
                    debug_info.append(f"CSV successfully read. Shape: {df_test.shape}")
                except Exception as e:
                    debug_info.append(f"ERROR reading CSV: {str(e)}")
                    return JsonResponse({'error': f'Invalid CSV file: {str(e)}', 'debug': debug_info}, status=400)
                
                # Perform analysis
                analyzer = CSVAnalyzer(file_path)
                analysis_data = analyzer.analyze()
                debug_info.append("Analysis completed successfully")
                debug_info.append(f"Analysis results: {list(analysis_data.keys())}")
                
                # Create analysis record
                analysis = DataAnalysis.objects.create(
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
                debug_info.append(f"Analysis record created with ID: {analysis.id}")
                
                return JsonResponse({
                    'success': True,
                    'file_id': str(file_upload.id),
                    'redirect_url': f'/analyze/{file_upload.id}/',
                    'debug': debug_info
                })
                
            except Exception as e:
                debug_info.append(f"ERROR during analysis: {str(e)}")
                debug_info.append(f"Traceback: {traceback.format_exc()}")
                return JsonResponse({'error': f'Analysis failed: {str(e)}', 'debug': debug_info}, status=500)
                
        except Exception as e:
            debug_info.append(f"ERROR creating file upload record: {str(e)}")
            debug_info.append(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({'error': f'Upload failed: {str(e)}', 'debug': debug_info}, status=500)
    
    return render(request, 'cleaner/upload.html')

def analyze_view(request, file_id):
    """Data analysis and options configuration page"""
    file_upload = get_object_or_404(FileUpload, id=file_id)
    debug_info = []
    
    try:
        analysis = file_upload.dataanalysis
        debug_info.append(f"Analysis found for file: {file_upload.original_filename}")
    except DataAnalysis.DoesNotExist:
        debug_info.append(f"No analysis found for file: {file_upload.original_filename}")
        return render(request, 'cleaner/analyzing.html', {
            'file_upload': file_upload,
            'debug_info': debug_info
        })
    
    if request.method == 'POST':
        debug_info.append("Processing cleaning options...")
        
        # Process cleaning options
        cleaning_options = {
            'feature_engineering': request.POST.get('feature_engineering') == 'on',
            'encoding_method': request.POST.get('encoding_method', ''),
            'scaling_method': request.POST.get('scaling_method', ''),
            'remove_outliers': request.POST.get('remove_outliers') == 'on',
            'outlier_threshold': float(request.POST.get('outlier_threshold', 1.5)),
            'numeric_only': request.POST.get('numeric_only') == 'on'
        }
        debug_info.append(f"Cleaning options: {cleaning_options}")
        
        try:
            # Create cleaning job
            job = CleaningJob.objects.create(
                file_upload=file_upload,
                analysis=analysis,
                cleaning_options=cleaning_options
            )
            debug_info.append(f"Cleaning job created with ID: {job.id}")
            
            # Perform cleaning synchronously
            try:
                job.status = 'processing'
                job.save()
                debug_info.append("Job status set to processing")
                
                file_path = job.file_upload.original_file.path
                debug_info.append(f"Loading CSV from: {file_path}")
                
                df = pd.read_csv(file_path)
                debug_info.append(f"CSV loaded successfully. Shape: {df.shape}")
                
                cleaner = DataCleaner(job.cleaning_options)
                debug_info.append("DataCleaner initialized")
                
                cleaned_df, report = cleaner.clean_data(df)
                debug_info.append(f"Data cleaning completed. New shape: {cleaned_df.shape}")
                debug_info.append(f"Cleaning report keys: {list(report.keys())}")
                
                # Save cleaned files
                output_dir = os.path.join(settings.MEDIA_ROOT, 'cleaned')
                os.makedirs(output_dir, exist_ok=True)
                debug_info.append(f"Output directory created: {output_dir}")
                
                # Save cleaned CSV
                cleaned_path = os.path.join(output_dir, f'cleaned_{job.id}.csv')
                cleaned_df.to_csv(cleaned_path, index=False)
                debug_info.append(f"Cleaned file saved to: {cleaned_path}")
                
                # Save numeric-only version if applicable
                numeric_cols = job.analysis.numeric_columns
                numeric_path = ''
                if numeric_cols and len(numeric_cols) > 0:
                    numeric_path = os.path.join(output_dir, f'numeric_{job.id}.csv')
                    cleaned_df[numeric_cols].to_csv(numeric_path, index=False)
                    debug_info.append(f"Numeric file saved to: {numeric_path}")
                else:
                    debug_info.append("No numeric columns found, skipping numeric file")
                
                # Update job status
                job.status = 'completed'
                job.cleaned_file_path = cleaned_path
                job.numeric_file_path = numeric_path
                job.cleaning_report = report
                job.save()
                debug_info.append("Job completed successfully")
                
                return redirect('results_view', job_id=job.id)
                
            except Exception as e:
                debug_info.append(f"ERROR during cleaning: {str(e)}")
                debug_info.append(f"Traceback: {traceback.format_exc()}")
                job.status = 'failed'
                job.error_message = str(e)
                job.save()
                
                # Show error on the same page
                messages.error(request, f'Cleaning failed: {str(e)}')
                
        except Exception as e:
            debug_info.append(f"ERROR creating cleaning job: {str(e)}")
            debug_info.append(f"Traceback: {traceback.format_exc()}")
            messages.error(request, f'Failed to create cleaning job: {str(e)}')
    
    context = {
        'file_upload': file_upload,
        'analysis': analysis,
        'missing_values': analysis.missing_values_summary,
        'data_types': analysis.data_types_detected,
        'recommendations': analysis.recommendations,
        'debug_info': debug_info
    }
    
    return render(request, 'cleaner/analyze.html', context)

def process_view(request, job_id):
    """Processing status page"""
    job = get_object_or_404(CleaningJob, id=job_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': job.status,
            'progress': job.progress_percentage,
            'error': job.error_message
        })
    
    return render(request, 'cleaner/process.html', {'job': job})

def results_view(request, job_id):
    """Results and download page"""
    job = get_object_or_404(CleaningJob, id=job_id)
    
    if job.status != 'completed':
        return redirect('process_view', job_id=job_id)
    
    context = {
        'job': job,
        'cleaning_report': job.cleaning_report,
        'has_cleaned_file': bool(job.cleaned_file_path),
        'has_numeric_file': bool(job.numeric_file_path)
    }
    
    return render(request, 'cleaner/results.html', context)

def download_file(request, job_id, file_type):
    """File download endpoint"""
    job = get_object_or_404(CleaningJob, id=job_id)
    
    file_paths = {
        'cleaned': job.cleaned_file_path,
        'numeric': job.numeric_file_path
    }
    
    file_path = file_paths.get(file_type)
    if not file_path or not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    
    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_type}_data.csv"'
        return response
