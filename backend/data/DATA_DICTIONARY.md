# Data Dictionary

This document describes all data files used in the FairPath backend, their structure, and how they are processed.

## Overview

The data layer integrates two primary data sources:
- **O*NET Database 30.1**: Occupational information, skills, tasks, and related data
- **BLS Employment Projections**: Employment projections, wage data, and growth statistics

All datasets are normalized using Standard Occupational Classification (SOC) codes as the primary key.

## Data Files

### O*NET Data Files

#### 1. Occupation Data.txt
- **Location**: `data/db_30_1_text/Occupation Data.txt`
- **Format**: Tab-separated values (TSV)
- **Source**: O*NET 30.1 Database (December 2025 Release)
- **Description**: Core occupation catalog with titles and descriptions
- **Columns**:
  - `O*NET-SOC Code` (str): O*NET Standard Occupational Classification code (format: XX-XXXX.XX)
  - `Title` (str): Official occupation title
  - `Description` (str): Detailed description of the occupation
- **Usage**: Primary source for occupation catalog. Used to build `career_id`, `name`, `soc_code`, and `description` fields.

#### 2. Skills.txt
- **Location**: `data/db_30_1_text/Skills.txt`
- **Format**: Tab-separated values (TSV)
- **Source**: O*NET 30.1 Database
- **Description**: Skills ratings for occupations, including importance and level ratings
- **Columns**:
  - `O*NET-SOC Code` (str): O*NET SOC code
  - `Element ID` (str): O*NET element identifier (e.g., "2.A.1.a")
  - `Element Name` (str): Name of the skill (e.g., "Reading Comprehension")
  - `Scale ID` (str): Rating scale type - "IM" (Importance) or "LV" (Level)
  - `Data Value` (float): Rating value
    - Importance (IM): 0-5 scale
    - Level (LV): 0-7 scale
  - `N` (int): Sample size
  - `Standard Error` (float): Statistical standard error
  - `Lower CI Bound` (float): Lower confidence interval bound
  - `Upper CI Bound` (float): Upper confidence interval bound
- **Usage**: Maps skills to occupations. Used to build occupation-skill relationships.

#### 3. Task Statements.txt
- **Location**: `data/db_30_1_text/Task Statements.txt`
- **Format**: Tab-separated values (TSV)
- **Source**: O*NET 30.1 Database
- **Description**: Task statements describing what workers do in each occupation
- **Columns**:
  - `O*NET-SOC Code` (str): O*NET SOC code
  - `Task ID` (str): Unique task identifier
  - `Task` (str): Task description
  - `Task Type` (str): "Core" or "Supplemental"
  - `Incumbents Responding` (int): Number of workers who provided this task rating
  - `Date` (str): Date of data collection
  - `Domain Source` (str): Source of the task (e.g., "Incumbent", "Occupational Expert")
- **Usage**: Maps tasks to occupations. Used to understand what workers do in each occupation.

### BLS Data Files

#### 4. occupation.xlsx
- **Location**: `data/occupation.xlsx`
- **Format**: Excel workbook with multiple sheets
- **Source**: BLS Employment Projections 2024-2034
- **Description**: Employment projections, wage data, and occupational outlook
- **Key Sheets**:
  - **Table 1.2**: Occupational projections, 2024–2034, and worker characteristics, 2024
    - Contains detailed occupation-level data including:
      - Employment in 2024 (thousands)
      - Projected employment in 2034 (thousands)
      - Change in employment (thousands)
      - Percent change 2024-2034
      - Annual average job openings
      - Median annual wage, 2024 (dollars)
      - Typical entry-level education
- **Usage**: Provides employment projections, growth rates, and wage data for occupations.

#### 5. labor-force.xlsx
- **Location**: `data/labor-force.xlsx`
- **Format**: Excel workbook
- **Source**: BLS Employment Projections
- **Description**: Labor force statistics by demographics
- **Usage**: Currently available but not actively used in initial catalog. Can be used for demographic analysis.

#### 6. education.xlsx
- **Location**: `data/education.xlsx`
- **Format**: Excel workbook
- **Source**: BLS Employment Projections
- **Description**: Education and training requirements, unemployment rates by education level
- **Usage**: Provides education requirements and outcomes data.

#### 7. skills.xlsx
- **Location**: `data/skills.xlsx`
- **Format**: Excel workbook
- **Source**: BLS Employment Projections
- **Description**: Top skills by occupational group and detailed occupation
- **Usage**: Supplementary skills data from BLS perspective.

#### 8. industry.xlsx
- **Location**: `data/industry.xlsx`
- **Format**: Excel workbook
- **Source**: BLS Employment Projections
- **Description**: Industry-level employment and projections
- **Usage**: Available for industry-level analysis.

## Data Processing

### SOC Code Normalization

All SOC codes are normalized to a consistent format: `XX-XXXX.XX`

The normalization process:
1. Removes non-digit, non-dash, non-period characters
2. Ensures major group is 2 digits (e.g., "11")
3. Ensures minor group is 4 digits (e.g., "1011")
4. Ensures broad occupation is 2 digits (e.g., "00")

Examples:
- `11-1011.00` → `11-1011.00` (already normalized)
- `11101100` → `11-1011.00` (from 8-digit format)
- `11-1011` → `11-1011.00` (adds missing broad occupation)

### Occupation Catalog Structure

The occupation catalog (`artifacts/occupation_catalog.json`) contains:

```json
{
  "occupation": {
    "career_id": "11101100",
    "name": "Chief Executives",
    "soc_code": "11-1011.00",
    "description": "Determine and formulate policies...",
    "onet_soc_code": "11-1011.00",
    "alternate_titles": [],
    "job_zone": null
  },
  "skills": [
    {
      "skill_id": "11-1011.00_2.A.1.a",
      "skill_name": "Reading Comprehension",
      "element_id": "2.A.1.a",
      "importance": 4.12,
      "level": 4.62,
      "soc_code": "11-1011.00"
    }
  ],
  "tasks": [
    {
      "task_id": "11-1011.00_8823",
      "task_description": "Direct or coordinate an organization's financial...",
      "task_type": "Core",
      "soc_code": "11-1011.00",
      "incumbents_responding": 95
    }
  ],
  "bls_projection": {
    "soc_code": "11-1011.00",
    "occupation_title": "Chief Executives",
    "employment_2024": 200000,
    "employment_2034": 210000,
    "change_2024_2034": 10000,
    "percent_change": 5.0,
    "annual_openings": 5000,
    "median_wage_2024": 189520.0,
    "typical_education": "Bachelor's degree"
  }
}
```

### Filtered Dataset

The catalog is filtered to 50-150 occupations for stable demo purposes. Selection criteria:
1. **Data completeness**: Occupations with skills, tasks, and BLS data are prioritized
2. **Score-based selection**: Each occupation is scored based on:
   - Skills data available: +2 points
   - Tasks data available: +2 points
   - BLS projection available: +1 point
3. **Top occupations**: Top 150 by score are selected
4. **Minimum guarantee**: At least 50 occupations are included even if they have less complete data

## Data Dictionary API

The data dictionary is available programmatically via:
- **Endpoint**: `GET /api/data/dictionary`
- **Returns**: List of `DataDictionary` objects describing all files

## Usage

### Initializing the Catalog

Run the initialization script to build the catalog:

```bash
python scripts/initialize_catalog.py
```

This will:
1. Load all O*NET data files
2. Load BLS projection data
3. Normalize SOC codes
4. Build occupation catalog (50-150 occupations)
5. Save to `artifacts/occupation_catalog.json`
6. Create and save data dictionary to `artifacts/data_dictionary.json`

### Accessing Data via API

- `GET /api/data/catalog` - Get all occupations (with pagination and filtering)
- `GET /api/data/catalog/{career_id}` - Get specific occupation
- `GET /api/data/dictionary` - Get data dictionary
- `GET /api/data/stats` - Get statistics about loaded data

## Data Sources

- **O*NET**: https://www.onetcenter.org/database.html
- **BLS Employment Projections**: https://www.bls.gov/emp/

## License

- **O*NET**: Creative Commons Attribution 4.0 International License
- **BLS**: Public domain (U.S. government data)











