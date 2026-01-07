"""
Script to initialize and save the occupation catalog
Run this to build the filtered dataset for the demo
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.data_ingestion import DataIngestionService

def main():
    """Initialize the occupation catalog"""
    print("Initializing occupation catalog...")
    
    service = DataIngestionService()
    
    # Build catalog with 50-150 occupations
    print("Building occupation catalog (50-150 occupations)...")
    catalogs = service.build_occupation_catalog(min_occupations=50, max_occupations=150)
    
    print(f"Created catalog with {len(catalogs)} occupations")
    
    # Save to JSON file
    output_dir = Path(__file__).parent.parent / "artifacts"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "occupation_catalog.json"
    
    # Convert to dict for JSON serialization
    catalogs_dict = [catalog.model_dump() for catalog in catalogs]
    
    with open(output_file, 'w') as f:
        json.dump(catalogs_dict, f, indent=2, default=str)
    
    print(f"Catalog saved to {output_file}")
    
    # Create data dictionary
    print("\nCreating data dictionary...")
    dictionaries = service.create_data_dictionary()
    
    dict_file = output_dir / "data_dictionary.json"
    dict_data = [dd.model_dump() for dd in dictionaries]
    
    with open(dict_file, 'w') as f:
        json.dump(dict_data, f, indent=2)
    
    print(f"Data dictionary saved to {dict_file}")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total occupations: {len(catalogs)}")
    
    occupations_with_skills = sum(1 for c in catalogs if len(c.skills) > 0)
    occupations_with_tasks = sum(1 for c in catalogs if len(c.tasks) > 0)
    occupations_with_bls = sum(1 for c in catalogs if c.bls_projection is not None)
    
    print(f"Occupations with skills: {occupations_with_skills}")
    print(f"Occupations with tasks: {occupations_with_tasks}")
    print(f"Occupations with BLS data: {occupations_with_bls}")
    
    # Print sample SOC codes
    print("\nSample SOC codes (first 10):")
    for catalog in catalogs[:10]:
        print(f"  {catalog.occupation.soc_code}: {catalog.occupation.name}")

if __name__ == "__main__":
    main()











