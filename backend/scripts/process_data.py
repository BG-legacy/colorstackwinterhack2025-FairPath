"""
Script to process raw catalog data into feature vectors and structured datasets
Run this after initializing the catalog to generate processed datasets
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.data_ingestion import DataIngestionService
from services.data_processing import DataProcessingService
from models.data_models import OccupationCatalog

def main():
    """Process the occupation catalog into feature vectors"""
    print("Starting data processing...")
    
    # Load the catalog
    catalog_file = Path(__file__).parent.parent / "artifacts" / "occupation_catalog.json"
    
    if not catalog_file.exists():
        print("Catalog not found, initializing first...")
        ingestion_service = DataIngestionService()
        catalogs = ingestion_service.build_occupation_catalog(min_occupations=50, max_occupations=150)
    else:
        print(f"Loading catalog from {catalog_file}")
        with open(catalog_file, 'r') as f:
            data = json.load(f)
            catalogs = [OccupationCatalog(**item) for item in data]
    
    print(f"Loaded {len(catalogs)} occupations")
    
    # Process the data
    processing_service = DataProcessingService()
    processed_data = processing_service.process_all_catalogs(catalogs)
    
    # Save it
    output_path = processing_service.save_processed_data(processed_data)
    
    # Print some stats
    print("\n=== Processing Summary ===")
    print(f"Version: {processed_data['version']}")
    print(f"Processed: {processed_data['processed_date']}")
    print(f"Occupations: {processed_data['num_occupations']}")
    print(f"Unique skills: {processed_data['num_skills']}")
    
    # Show sample of what we generated
    sample = processed_data['occupations'][0]
    print(f"\nSample occupation: {sample['name']}")
    print(f"  Skill vector size: {len(sample['skill_vector']['combined'])}")
    print(f"  Tasks: {sample['task_features']['num_tasks']}")
    print(f"  Outlook growth: {sample['outlook_features'].get('growth_rate', 0):.1f}%")
    print(f"  Education: {sample['education_data'].get('typical_entry_education', 'N/A')}")
    
    print(f"\nProcessed data saved to: {output_path}")

if __name__ == "__main__":
    main()









