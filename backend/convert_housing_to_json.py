"""
Convert Housing Elements CSV to searchable JSON format
"""
import pandas as pd
import json
from pathlib import Path

def convert_housing_csv_to_json():
    """Convert housing CSV to structured JSON"""

    csv_path = "datasets/HousingElements_SDCounty_2021_2029_3908156892941684000.csv"
    json_path = "datasets/housing_elements.json"

    print("=" * 60)
    print("Housing Elements CSV to JSON Converter")
    print("=" * 60)

    try:
        # Read CSV file
        print(f"\nReading CSV file: {csv_path}")
        df = pd.read_csv(csv_path, encoding='utf-8-sig')

        print(f"✓ Found {len(df)} housing records")
        print(f"\nColumns: {', '.join(df.columns.tolist())}")

        # Convert to list of dictionaries
        housing_data = []

        for idx, row in df.iterrows():
            # Clean and structure the data
            record = {
                "id": int(row['OBJECTID']) if pd.notna(row['OBJECTID']) else idx + 1,
                "jurisdiction": str(row['Jurisdiction']) if pd.notna(row['Jurisdiction']) else "",
                "apn": str(row['APN']) if pd.notna(row['APN']) else "",
                "vacancy_status": str(row['Vacancy']) if pd.notna(row['Vacancy']) else "Unknown",
                "units": int(row['Units']) if pd.notna(row['Units']) else 0,
                "zoning": {
                    "code": str(row['Zoning']) if pd.notna(row['Zoning']) else "",
                    "simplified": str(row['ZoningSimplified']) if pd.notna(row['ZoningSimplified']) else "",
                    "min_density": float(row['Min_Density']) if pd.notna(row['Min_Density']) else None,
                    "max_density": float(row['Max_Density']) if pd.notna(row['Max_Density']) else None,
                },
                "info_link": str(row['Links']) if pd.notna(row['Links']) else "",
                "area": {
                    "square_feet": float(row['Shape__Area']) if pd.notna(row['Shape__Area']) else 0,
                    "perimeter_feet": float(row['Shape__Length']) if pd.notna(row['Shape__Length']) else 0,
                },
                # Add searchable text for easy searching
                "searchable_text": f"{row['Jurisdiction']} {row['ZoningSimplified']} {row['Vacancy']} {row['Zoning']}".lower()
            }

            housing_data.append(record)

        # Create summary statistics
        summary = {
            "total_records": len(housing_data),
            "total_units": int(df['Units'].sum()),
            "jurisdictions": df['Jurisdiction'].unique().tolist(),
            "zoning_types": df['ZoningSimplified'].dropna().unique().tolist(),
            "vacancy_counts": {
                "vacant": len(df[df['Vacancy'] == 'Vacant']),
                "other": len(df[df['Vacancy'] != 'Vacant'])
            },
            "unit_statistics": {
                "min_units": int(df['Units'].min()),
                "max_units": int(df['Units'].max()),
                "avg_units": float(df['Units'].mean())
            }
        }

        # Create final JSON structure
        output_data = {
            "metadata": {
                "dataset_name": "San Diego County Housing Elements 2021-2029",
                "source_file": csv_path,
                "description": "Housing development sites and zoning information for San Diego County",
                "created_at": pd.Timestamp.now().isoformat()
            },
            "summary": summary,
            "data": housing_data
        }

        # Write to JSON file
        print(f"\nWriting JSON file: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Successfully created JSON file")

        # Print summary
        print("\n" + "=" * 60)
        print("Summary Statistics")
        print("=" * 60)
        print(f"Total Records:        {summary['total_records']:,}")
        print(f"Total Units:          {summary['total_units']:,}")
        print(f"Jurisdictions:        {len(summary['jurisdictions'])}")
        print(f"Vacant Properties:    {summary['vacancy_counts']['vacant']:,}")
        print(f"\nUnit Statistics:")
        print(f"  Min Units:          {summary['unit_statistics']['min_units']}")
        print(f"  Max Units:          {summary['unit_statistics']['max_units']}")
        print(f"  Avg Units:          {summary['unit_statistics']['avg_units']:.2f}")

        print(f"\nZoning Types ({len(summary['zoning_types'])}):")
        for zoning in sorted([z for z in summary['zoning_types'] if z]):
            count = len(df[df['ZoningSimplified'] == zoning])
            print(f"  - {zoning}: {count:,} records")

        print(f"\nTop 10 Jurisdictions by Units:")
        jurisdiction_units = df.groupby('Jurisdiction')['Units'].sum().sort_values(ascending=False).head(10)
        for jurisdiction, units in jurisdiction_units.items():
            print(f"  - {jurisdiction}: {int(units):,} units")

        print("\n" + "=" * 60)
        print("✅ Conversion completed successfully!")
        print("=" * 60)

        return output_data

    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    convert_housing_csv_to_json()
