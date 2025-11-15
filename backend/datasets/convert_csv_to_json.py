"""
Convert CSV datasets to JSON format for the homeless assistance chatbot
"""
import csv
import json
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def convert_behavioral_health_to_healthcare():
    """
    Convert Behavioral_Health_Services CSV to healthcare_resources.json
    """
    csv_file = os.path.join(SCRIPT_DIR, 'Behavioral_Health_Services_San_Diego_County_1657686067853346365.csv')
    json_file = os.path.join(SCRIPT_DIR, 'healthcare_resources.json')

    resources = []

    with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)

        for idx, row in enumerate(reader, 1):
            # Skip rows without coordinates
            if not row['LAT'] or not row['LONG']:
                continue

            # Parse services from the Services column
            services_list = []
            if row['Services']:
                services_list = [s.strip() for s in row['Services'].split('\n') if s.strip()]

            # Build resource object
            resource = {
                "id": idx,
                "name": row['Program'] if row['Program'] else "Behavioral Health Services",
                "type": "healthcare",
                "category": "behavioral health",
                "description": row['Description'] if row['Description'] else "Mental health and behavioral health services",
                "services": services_list if services_list else ["mental health", "behavioral health"],
                "address": row['Address'],
                "phone": row['Phone'] if row['Phone'] else "N/A",
                "hours": "Call for hours",
                "requirements": row['Population'] if row['Population'] else "Varies by program",
                "coordinates": {
                    "latitude": float(row['LAT']),
                    "longitude": float(row['LONG'])
                },
                "website": row['Website'] if row['Website'] else None,
                "region": row['Region'] if row['Region'] else None,
                "taking_new_referrals": row['Taking New Referrals'] if row['Taking New Referrals'] else "Unknown"
            }

            resources.append(resource)

            # Limit to first 50 resources to keep file manageable
            if len(resources) >= 50:
                break

    # Write to JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(resources, f, indent=2, ensure_ascii=False)

    print(f"✓ Converted {len(resources)} healthcare resources to {json_file}")


def convert_transit_stops():
    """
    Convert Public Transit Stops CSV to transit_stops.json
    """
    csv_file = os.path.join(SCRIPT_DIR, 'Public_Transit_Stops%2C_San_Diego_County.csv')
    json_file = os.path.join(SCRIPT_DIR, 'transit_stops.json')

    stops = []

    with open(csv_file, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)

        for row in reader:
            # Skip rows without coordinates
            if not row['stop_lat'] or not row['stop_lon']:
                continue

            stop = {
                "id": row['stop_id'],
                "name": row['stop_name'],
                "agency": row['stop_agency'],
                "coordinates": {
                    "latitude": float(row['stop_lat']),
                    "longitude": float(row['stop_lon'])
                },
                "wheelchair_accessible": row['wheelchair_boarding'] == '1',
                "stop_code": row['stop_code'] if row['stop_code'] else None
            }

            stops.append(stop)

    # Write to JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(stops, f, indent=2, ensure_ascii=False)

    print(f"✓ Converted {len(stops)} transit stops to {json_file}")


def note_missing_datasets():
    """
    Print note about missing datasets
    """
    print("\n📝 NOTES:")
    print("   - food_banks.json: Using sample data (no CSV source found)")
    print("   - shelters.json: Using sample data (no CSV source found)")
    print("   - HousingElements CSV contains land parcel data, not shelter locations")
    print("   - You may need to manually add/update shelter and food bank data")
    print("   - Consider using 211sandiego.org or similar sources for complete data")


if __name__ == "__main__":
    print("Converting CSV datasets to JSON...\n")

    # Convert behavioral health to healthcare resources
    convert_behavioral_health_to_healthcare()

    # Convert public transit stops
    convert_transit_stops()

    # Print notes about missing data
    note_missing_datasets()

    print("\n✅ Conversion complete!")
