"""
Generalized CSV Data Reader Utility
Provides robust CSV reading with error handling and mock data fallback.
"""
import csv
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def read_csv_data(filepath: str, fallback_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Reads a CSV file and returns a list of dictionaries.
    Returns fallback data or empty list if file is missing or malformed.
    
    Args:
        filepath: Path to the CSV file
        fallback_data: Optional mock data to return if CSV reading fails
        
    Returns:
        List of dictionaries representing CSV rows
    """
    data = []
    
    try:
        if not os.path.exists(filepath):
            logger.warning(f"CSV file not found: {filepath}")
            return fallback_data or []
            
        with open(filepath, 'r', encoding='utf-8') as file:
            # Detect if file is empty
            if os.path.getsize(filepath) == 0:
                logger.warning(f"CSV file is empty: {filepath}")
                return fallback_data or []
                
            reader = csv.DictReader(file)
            data = list(reader)
            
            if not data:
                logger.warning(f"No data rows found in CSV: {filepath}")
                return fallback_data or []
                
            logger.info(f"Successfully loaded {len(data)} rows from {filepath}")
            return data
            
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading CSV {filepath}: {e}")
        return fallback_data or []
    except csv.Error as e:
        logger.error(f"CSV parsing error for {filepath}: {e}")
        return fallback_data or []
    except Exception as e:
        logger.error(f"Unexpected error reading CSV {filepath}: {e}")
        return fallback_data or []

def read_multiple_csv_files(filepaths: List[str], fallback_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Reads multiple CSV files and combines them into a single list.
    Useful for loading historical data across multiple months.
    
    Args:
        filepaths: List of CSV file paths to read
        fallback_data: Optional mock data to return if all files fail
        
    Returns:
        Combined list of dictionaries from all CSV files
    """
    combined_data = []
    
    for filepath in filepaths:
        file_data = read_csv_data(filepath)
        combined_data.extend(file_data)
    
    if not combined_data and fallback_data:
        logger.warning("No data found in any CSV files, using fallback data")
        return fallback_data
        
    return combined_data

def get_department_csv_path(department: str, filename: str) -> str:
    """
    Constructs the standard CSV file path for a department.
    
    Args:
        department: Department name (e.g., 'product', 'admin', 'back_office')
        filename: CSV filename (e.g., 'sample_product_may2025.csv')
        
    Returns:
        Full path to the CSV file
    """
    base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'knowledge_bases')
    return os.path.join(base_path, department, '_data', filename)

def extract_metrics_by_month(data: List[Dict[str, Any]], month: str) -> Dict[str, Any]:
    """
    Extracts metrics for a specific month from CSV data.
    
    Args:
        data: List of CSV row dictionaries
        month: Month to filter by (e.g., '2025-05')
        
    Returns:
        Dictionary of metrics for the specified month
    """
    metrics = {}
    
    for row in data:
        if row.get('Month') == month:
            metric_name = row.get('Metric', row.get('Task', 'Unknown'))
            metric_value = row.get('Value', row.get('Count', ''))
            metrics[metric_name] = metric_value
    
    return metrics

def create_fallback_data(department: str, month: str = "2025-05") -> List[Dict[str, Any]]:
    """
    Creates appropriate fallback/mock data for different departments.
    
    Args:
        department: Department name
        month: Month for the data
        
    Returns:
        List of mock data dictionaries
    """
    fallback_data = {
        'product': [
            {'Month': month, 'Metric': 'Features Released', 'Value': '5', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Bugs Fixed', 'Value': '15', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Test Pass Rate', 'Value': '90%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Code Coverage', 'Value': '85%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Security Vulnerabilities', 'Value': '1', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Tech Debt Score', 'Value': '15%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'API Response Time (ms)', 'Value': '120', 'Notes': 'Mock data - CSV not available'}
        ],
        'admin': [
            {'Month': month, 'Task': 'Meetings Scheduled', 'Count': '30', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Task': 'Documents Processed', 'Count': '100', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Task': 'Compliance Checks', 'Count': '3', 'Notes': 'Mock data - CSV not available'}
        ],
        'payroll': [
            {'Month': month, 'Employee': 'Sample Employee', 'Role': 'Staff', 'Gross Pay': '5000', 'Net Pay': '4000', 'Deductions': '1000', 'Bonuses': '0', 'Pay Date': f'{month}-31'}
        ],
        'marketing': [
            {'Month': month, 'Metric': 'Blog Posts', 'Value': '8', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Social Media Posts', 'Value': '45', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Email Campaigns', 'Value': '4', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Video Content', 'Value': '6', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Engagement Rate', 'Value': '4.2%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Conversion Rate', 'Value': '2.8%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Website Traffic', 'Value': '12500', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Leads Generated', 'Value': '89', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Follower Growth', 'Value': '8.5%', 'Notes': 'Mock data - CSV not available'}
        ],
        'customer': [
            {'Month': month, 'Metric': 'New Customers', 'Value': '12', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Support Tickets', 'Value': '45', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Customer Satisfaction', 'Value': '4.6', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Retention Rate', 'Value': '94.7%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Onboarding Completed', 'Value': '15', 'Notes': 'Mock data - CSV not available'}
        ],
        'back_office': [
            {'Month': month, 'Metric': 'Invoices Processed', 'Value': '234', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Payment Collections', 'Value': '98.5%', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Expense Reports', 'Value': '67', 'Notes': 'Mock data - CSV not available'},
            {'Month': month, 'Metric': 'Budget Variance', 'Value': '2.3%', 'Notes': 'Mock data - CSV not available'}
        ]
    }
    
    return fallback_data.get(department, [])