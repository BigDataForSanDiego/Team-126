# Housing Elements JSON Dataset

## Overview

This JSON file contains **17,358 housing development sites** across San Diego County for the 2021-2029 planning period, with **218,879 total housing units**.

**File**: `housing_elements.json` (9.3 MB)
**Source**: `HousingElements_SDCounty_2021_2029_3908156892941684000.csv`

---

## Dataset Structure

```json
{
  "metadata": {
    "dataset_name": "San Diego County Housing Elements 2021-2029",
    "source_file": "datasets/HousingElements_SDCounty_2021_2029_3908156892941684000.csv",
    "description": "Housing development sites and zoning information for San Diego County",
    "created_at": "2025-11-14T20:18:20.615670"
  },
  "summary": {
    "total_records": 17358,
    "total_units": 218879,
    "jurisdictions": [...],
    "zoning_types": [...],
    "vacancy_counts": {...},
    "unit_statistics": {...}
  },
  "data": [...]
}
```

---

## Record Structure

Each housing record has the following structure:

```json
{
  "id": 1,
  "jurisdiction": "City of San Diego",
  "apn": "5461000200",
  "vacancy_status": "Vacant",
  "units": 2,
  "zoning": {
    "code": "RM-1-1",
    "simplified": "Low Density Residential",
    "min_density": null,
    "max_density": 14.0
  },
  "info_link": "https://www.sandiego.gov/development-services/zoning",
  "area": {
    "square_feet": 5386.068359375,
    "perimeter_feet": 316.776904021351
  },
  "searchable_text": "city of san diego low density residential vacant rm-1-1"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Unique identifier for the record |
| `jurisdiction` | string | City or county jurisdiction (19 total jurisdictions) |
| `apn` | string | Assessor Parcel Number |
| `vacancy_status` | string | "Vacant" or "Unknown" |
| `units` | int | Number of housing units planned/available |
| `zoning.code` | string | Official zoning code (e.g., "RM-1-1") |
| `zoning.simplified` | string | Simplified zoning category (10 types) |
| `zoning.min_density` | float/null | Minimum units per acre |
| `zoning.max_density` | float/null | Maximum units per acre |
| `info_link` | string | URL to jurisdiction's zoning information |
| `area.square_feet` | float | Parcel area in square feet |
| `area.perimeter_feet` | float | Parcel perimeter in feet |
| `searchable_text` | string | Lowercase concatenated text for searching |

---

## Summary Statistics

### Jurisdictions (19)
- **City of San Diego**: 160,820 units (73% of total)
- **Escondido**: 8,661 units
- **Chula Vista**: 6,540 units
- **Oceanside**: 6,281 units
- **National City**: 5,890 units
- **El Cajon**: 4,444 units
- **San Diego County**: 4,376 units
- **San Marcos**: 3,051 units
- **La Mesa**: 2,962 units
- **Carlsbad**: 2,540 units
- *(and 9 others)*

### Zoning Types (10)

| Zoning Type | Records | Description |
|-------------|---------|-------------|
| **Commercial** | 5,416 | Mixed commercial/residential |
| **Low Density Residential** | 4,429 | Single-family, low-density |
| **High Density Residential** | 2,635 | Apartments, high-density |
| **Medium Density Residential** | 2,617 | Townhomes, medium-density |
| **Mixed Use** | 654 | Commercial + residential |
| **Industrial** | 258 | Industrial zoning |
| **Agricultural** | 96 | Agricultural use |
| **Transit Focus** | 93 | Transit-oriented development |
| **Residential** | 83 | General residential |
| **Open Space** | 5 | Parks, open space |

### Vacancy Status
- **Vacant**: 3,166 properties
- **Other**: 14,192 properties

### Unit Statistics
- **Minimum**: -1 units (data error)
- **Maximum**: 2,898 units (largest development)
- **Average**: 12.67 units per property

---

## Usage Examples

### Python - Load and Search

```python
import json

# Load the data
with open('datasets/housing_elements.json', 'r') as f:
    housing_data = json.load(f)

# Access summary
print(f"Total units: {housing_data['summary']['total_units']:,}")

# Search for vacant high-density residential
results = [
    record for record in housing_data['data']
    if record['vacancy_status'] == 'Vacant'
    and record['zoning']['simplified'] == 'High Density Residential'
    and record['units'] >= 10
]

print(f"Found {len(results)} vacant high-density properties with 10+ units")
```

### JavaScript/TypeScript - Frontend

```typescript
// Fetch the housing data
const response = await fetch('/datasets/housing_elements.json');
const housingData = await response.json();

// Filter by jurisdiction
const sdProperties = housingData.data.filter(
  (record: any) => record.jurisdiction === 'City of San Diego'
);

// Find affordable housing opportunities (vacant, medium-high density)
const affordableOpportunities = housingData.data.filter(
  (record: any) =>
    record.vacancy_status === 'Vacant' &&
    ['Medium Density Residential', 'High Density Residential'].includes(
      record.zoning.simplified
    ) &&
    record.units >= 5
);

console.log(`Found ${affordableOpportunities.length} affordable housing opportunities`);
```

### Using the Search Script

The repository includes a ready-to-use search script:

```bash
# Run demo searches
python search_housing.py
```

**Search function signature**:
```python
def search_housing(
    query: str = "",              # Text search
    jurisdiction: str = None,     # Filter by city/county
    vacancy_status: str = None,   # "Vacant" or other
    zoning_type: str = None,      # Simplified zoning type
    min_units: int = None,        # Minimum units
    max_units: int = None,        # Maximum units
    limit: int = 10               # Max results
) -> List[Dict]:
```

**Example searches**:
```python
# Find vacant properties in San Diego with 50+ units
results = search_housing(
    jurisdiction="City of San Diego",
    vacancy_status="Vacant",
    min_units=50,
    limit=10
)

# Find all mixed-use properties
results = search_housing(
    zoning_type="Mixed Use",
    limit=20
)

# Text search for "transit"
results = search_housing(
    query="transit",
    limit=10
)
```

---

## Common Search Patterns

### 1. Find Affordable Housing Opportunities
```python
# Vacant, high-density, with many units
results = search_housing(
    vacancy_status="Vacant",
    zoning_type="High Density Residential",
    min_units=20
)
```

### 2. Find Properties by Jurisdiction
```python
# All properties in National City
results = search_housing(
    jurisdiction="National City"
)
```

### 3. Find Transit-Oriented Development
```python
# Properties near transit
results = search_housing(
    zoning_type="Transit Focus"
)
```

### 4. Find Large Development Sites
```python
# Properties with 100+ units
results = search_housing(
    min_units=100
)
```

### 5. Find Commercial Properties
```python
# Commercial zoning
results = search_housing(
    zoning_type="Commercial",
    vacancy_status="Vacant"
)
```

---

## Use Cases

### For Homeless Assistance Chatbot
This dataset can help:

1. **Identify housing opportunities** - Find vacant properties and development sites
2. **Match zoning to needs** - Identify areas suitable for affordable housing
3. **Geographic distribution** - Show housing options across different jurisdictions
4. **Development potential** - Calculate total units available in specific areas
5. **Resource allocation** - Direct individuals to jurisdictions with more housing availability

### Example Chatbot Integration

```python
# User asks: "Where can I find affordable housing in San Diego?"

# Search for vacant medium/high density properties
affordable_housing = search_housing(
    jurisdiction="City of San Diego",
    vacancy_status="Vacant",
    zoning_type="Medium Density Residential",
    min_units=10,
    limit=5
)

# Generate response
response = f"I found {len(affordable_housing)} affordable housing development sites in San Diego:\n\n"
for site in affordable_housing:
    response += f"- {site['units']} units planned in {site['zoning']['simplified']} zone\n"
    response += f"  Max density: {site['zoning']['max_density']} units/acre\n"
    if site['info_link']:
        response += f"  More info: {site['info_link']}\n\n"
```

---

## Performance Considerations

- **File size**: 9.3 MB - suitable for server-side processing
- **Records**: 17,358 - can be searched in-memory efficiently
- **Indexing**: The `searchable_text` field enables fast text searches
- **Filtering**: Structured fields allow efficient filtering

### Optimization Tips

1. **Cache the loaded data** - Load once, reuse multiple times
2. **Index by jurisdiction** - Create a dictionary mapping for faster lookups
3. **Filter early** - Apply most restrictive filters first
4. **Limit results** - Use the `limit` parameter to avoid processing all records

---

## Data Quality Notes

1. **Missing values**: Some records have `null` for min_density or max_density
2. **Vacancy status**: Not all properties have "Vacant" status - many are "Unknown"
3. **Unit count**: One record has -1 units (data error)
4. **Area measurements**: All areas are in square feet
5. **Zoning codes**: Each jurisdiction uses different zoning code schemes

---

## Converting CSV to JSON

The conversion script is included:

```bash
python convert_housing_to_json.py
```

This script:
- Reads the original CSV file
- Cleans and structures the data
- Generates summary statistics
- Creates searchable text fields
- Outputs formatted JSON

---

## Future Enhancements

1. **Add geographic coordinates** - Enable map-based searching
2. **Add embeddings** - Enable semantic search with AI
3. **Link to transit data** - Show proximity to public transportation
4. **Add demographic data** - Include neighborhood information
5. **Historical tracking** - Track changes over time as developments progress

---

## License & Attribution

**Data Source**: San Diego County Housing Elements 2021-2029
**Jurisdictions**: 19 cities and San Diego County
**Data Period**: 2021-2029 planning cycle

For official zoning information, refer to the `info_link` URLs in each record.

---

## Contact & Support

For questions about this dataset or integration assistance, refer to the main project documentation.
