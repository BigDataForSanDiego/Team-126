"""
Demo script to search the housing JSON file
"""
import json
from typing import List, Dict, Optional

def load_housing_data() -> Dict:
    """Load the housing JSON data"""
    with open('datasets/housing_elements.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def search_housing(
    query: str = "",
    jurisdiction: Optional[str] = None,
    vacancy_status: Optional[str] = None,
    zoning_type: Optional[str] = None,
    min_units: Optional[int] = None,
    max_units: Optional[int] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Search housing data with various filters

    Args:
        query: Text search in searchable_text field
        jurisdiction: Filter by jurisdiction
        vacancy_status: Filter by vacancy status (Vacant, etc.)
        zoning_type: Filter by simplified zoning type
        min_units: Minimum number of units
        max_units: Maximum number of units
        limit: Maximum results to return

    Returns:
        List of matching housing records
    """
    data = load_housing_data()
    results = []

    query_lower = query.lower() if query else ""

    for record in data['data']:
        # Text search
        if query and query_lower not in record['searchable_text']:
            continue

        # Jurisdiction filter
        if jurisdiction and record['jurisdiction'].lower() != jurisdiction.lower():
            continue

        # Vacancy status filter
        if vacancy_status and record['vacancy_status'] != vacancy_status:
            continue

        # Zoning type filter
        if zoning_type and record['zoning']['simplified'].lower() != zoning_type.lower():
            continue

        # Units filter
        if min_units is not None and record['units'] < min_units:
            continue

        if max_units is not None and record['units'] > max_units:
            continue

        results.append(record)

        if len(results) >= limit:
            break

    return results

def print_housing_results(results: List[Dict]):
    """Pretty print housing search results"""
    print(f"\nFound {len(results)} results:\n")
    print("=" * 80)

    for idx, record in enumerate(results, 1):
        print(f"\n{idx}. {record['jurisdiction']} - {record['zoning']['simplified']}")
        print(f"   Units: {record['units']}")
        print(f"   Status: {record['vacancy_status']}")
        print(f"   Zoning: {record['zoning']['code']}")
        if record['zoning']['max_density']:
            print(f"   Max Density: {record['zoning']['max_density']} units/acre")
        if record['info_link']:
            print(f"   Info: {record['info_link']}")
        print(f"   Area: {record['area']['square_feet']:,.0f} sq ft")

def demo_searches():
    """Run several demo searches"""

    print("=" * 80)
    print("Housing Elements Search Demo")
    print("=" * 80)

    # Search 1: Find vacant high-density residential properties
    print("\n\n1️⃣  SEARCH: Vacant high-density residential properties")
    print("-" * 80)
    results = search_housing(
        vacancy_status="Vacant",
        zoning_type="High Density Residential",
        limit=5
    )
    print_housing_results(results)

    # Search 2: Find properties in City of San Diego with 50+ units
    print("\n\n2️⃣  SEARCH: City of San Diego properties with 50+ units")
    print("-" * 80)
    results = search_housing(
        jurisdiction="City of San Diego",
        min_units=50,
        limit=5
    )
    print_housing_results(results)

    # Search 3: Find commercial zoning properties
    print("\n\n3️⃣  SEARCH: Commercial zoning properties")
    print("-" * 80)
    results = search_housing(
        zoning_type="Commercial",
        limit=5
    )
    print_housing_results(results)

    # Search 4: Find mixed-use properties
    print("\n\n4️⃣  SEARCH: Mixed-use properties")
    print("-" * 80)
    results = search_housing(
        zoning_type="Mixed Use",
        limit=5
    )
    print_housing_results(results)

    # Search 5: Text search for "transit"
    print("\n\n5️⃣  SEARCH: Properties near transit (text search)")
    print("-" * 80)
    results = search_housing(
        query="transit",
        limit=5
    )
    print_housing_results(results)

    # Print summary statistics
    data = load_housing_data()
    print("\n\n" + "=" * 80)
    print("Dataset Summary")
    print("=" * 80)
    print(f"\nTotal Records:     {data['summary']['total_records']:,}")
    print(f"Total Units:       {data['summary']['total_units']:,}")
    print(f"Jurisdictions:     {len(data['summary']['jurisdictions'])}")
    print(f"Vacant Properties: {data['summary']['vacancy_counts']['vacant']:,}")
    print(f"\nZoning Types: {', '.join(data['summary']['zoning_types'])}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    demo_searches()
