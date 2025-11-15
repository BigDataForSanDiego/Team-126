# Local Resources Database

This directory contains verified local resources for homeless assistance in the San Diego area.

## Dataset Files

- **healthcare_resources.json** (50 resources, 41KB) - Mental health and behavioral health services
  - ✅ Auto-generated from `Behavioral_Health_Services_San_Diego_County_*.csv`
- **shelters.json** (4 resources, 2.4KB) - Emergency shelters, day centers, transitional housing
  - ⚠️ Sample data - needs real CSV source
- **food_banks.json** (5 resources, 2.6KB) - Food banks, meal programs, food distribution sites
  - ⚠️ Sample data - needs real CSV source
- **transit_stops.json** (6,220 stops, 1.4MB) - Public transit stops for routing
  - ✅ Auto-generated from `Public_Transit_Stops%2C_San_Diego_County.csv`

## How the System Works

When a user asks for resources (e.g., "where is the nearest health care?"), the system:

1. **Detects the resource type** from keywords in the query
2. **Searches the local JSON datasets first** - these are verified, accurate resources
3. **Calculates distance** from the user's GPS coordinates
4. **Sorts results by proximity** to show the nearest resources first
5. **Falls back to web search** only if no local results are found

## Adding New Resources

To add a new resource to any dataset, follow this JSON structure:

```json
{
  "id": 6,
  "name": "Resource Name",
  "type": "healthcare|shelter|food",
  "category": "free clinic|emergency shelter|food bank",
  "description": "Brief description of services",
  "services": ["service 1", "service 2", "service 3"],
  "address": "Full street address with city, state, zip",
  "phone": "(xxx) xxx-xxxx",
  "hours": "Operating hours",
  "requirements": "Requirements or eligibility criteria",
  "coordinates": {
    "latitude": 32.7157,
    "longitude": -117.1611
  },
  "website": "https://example.org"
}
```

### Required Fields
- `name` - Name of the organization/facility
- `type` - Category (healthcare, shelter, or food)
- `address` - Physical address
- `phone` - Contact phone number
- `coordinates` - GPS coordinates for distance calculation

### Optional Fields
- `category` - Subcategory for more specific filtering
- `description` - What they offer
- `services` - Array of specific services
- `hours` - Operating hours
- `requirements` - Eligibility or what to bring
- `website` - URL for more information
- `capacity` - For shelters (e.g., "Men: 50, Women: 30")

## Getting GPS Coordinates

You can get latitude/longitude coordinates from:
- **Google Maps**: Right-click on the location → "What's here?"
- **GPS Coordinates website**: https://www.gps-coordinates.net/
- **Address to Coordinates API**: Use a geocoding service

## Dataset Coverage

Currently focused on **San Diego County, California** resources. To expand to other regions, create new JSON files following the same structure.

## Search Keywords

The system recognizes these keywords:
- **Healthcare**: health, medical, clinic, doctor, hospital, mental
- **Shelter**: shelter, housing, sleep, bed, emergency shelter
- **Food**: food, meal, hungry, eat, pantry, kitchen

## Data Quality

All resources in these datasets should be:
- ✅ Verified and currently operational
- ✅ Have accurate contact information
- ✅ Have correct GPS coordinates
- ✅ Include complete service details

## Regenerating Data from CSV Files

If you update the source CSV files or download new data, you can regenerate the JSON files:

```bash
cd backend/datasets
python convert_csv_to_json.py
```

This script will:
1. Convert `Behavioral_Health_Services_San_Diego_County_*.csv` → `healthcare_resources.json`
2. Convert `Public_Transit_Stops%2C_San_Diego_County.csv` → `transit_stops.json`
3. Show notes about missing datasets (shelters, food banks)

### CSV Source Files

The following CSV files are available in this directory:
- ✅ `Behavioral_Health_Services_San_Diego_County_1657686067853346365.csv` (535KB)
- ✅ `Public_Transit_Stops%2C_San_Diego_County.csv` (808KB)
- ❌ `Public_Transit_Routes%2C_San_Diego_County.csv` (124KB) - Not yet used
- ❌ `HousingElements_SDCounty_2021_2029_3908156892941684000.csv` (2.6MB) - Land parcels, not shelters

### Needed CSV Sources

To complete the dataset, we need CSV sources for:
- ❌ Emergency shelters and housing services
- ❌ Food banks and meal programs
- ❌ Job training programs
- ❌ Free legal services

Recommended sources: [211 San Diego](https://www.211sandiego.org/), [San Diego Food Bank](https://sandiegofoodbank.org/), [Regional Task Force on Homelessness](https://www.rtfhsd.org/)

## Contributing

When adding resources:
1. Verify the information is current (call to confirm)
2. Get accurate GPS coordinates
3. Include all required fields
4. Test by running a search query
5. Update this README if adding a new dataset file
