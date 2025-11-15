"""
Import San Diego County datasets into PostgreSQL
This script loads health services, transit stops, transit routes, and housing data
"""

import pandas as pd
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint
from database import DATABASE_URL, Base
from dataset_models import HealthService, TransitStop, TransitRoute, HousingElement
from embeddings import generate_embedding
import urllib.parse

def import_health_services(session):
    """Import Behavioral Health Services data"""
    print("\n" + "="*60)
    print("Importing Health Services...")
    print("="*60)

    try:
        # Read CSV - handle potential encoding issues
        df = pd.read_csv(
            'datasets/Behavioral_Health_Services_San_Diego_County_1657686067853346365.csv',
            encoding='utf-8-sig'  # Handle BOM
        )

        print(f"Found {len(df)} health service records")

        # Clean column names (remove BOM and whitespace)
        df.columns = df.columns.str.strip().str.replace('\ufeff', '')

        total = len(df)
        for idx, row in df.iterrows():
            try:
                # Create text for embedding
                embedding_text = f"{row.get('Program', '')} {row.get('Description', '')} {row.get('Services', '')} {row.get('Population', '')}"
                embedding_text = embedding_text.strip()

                # Generate embedding (with progress indicator)
                if (idx + 1) % 100 == 0:
                    print(f"  Processing {idx + 1}/{total}...")

                embedding = generate_embedding(embedding_text) if embedding_text else None

                # Create health service record
                service = HealthService(
                    longitude=float(row['LONG']),
                    latitude=float(row['LAT']),
                    region=str(row.get('Region', ''))[:255] if pd.notna(row.get('Region')) else None,
                    program=str(row.get('Program', ''))[:255] if pd.notna(row.get('Program')) else None,
                    address=str(row.get('Address', '')) if pd.notna(row.get('Address')) else None,
                    phone=str(row.get('Phone', ''))[:255] if pd.notna(row.get('Phone')) else None,
                    website=str(row.get('Website', ''))[:255] if pd.notna(row.get('Website')) else None,
                    description=str(row.get('Description', '')) if pd.notna(row.get('Description')) else None,
                    taking_new_referrals=str(row.get('Taking New Referrals', ''))[:255] if pd.notna(row.get('Taking New Referrals')) else None,
                    population=str(row.get('Population', '')) if pd.notna(row.get('Population')) else None,
                    services=str(row.get('Services', '')) if pd.notna(row.get('Services')) else None,
                    language=str(row.get('Language', ''))[:255] if pd.notna(row.get('Language')) else None,
                    fid=str(row.get('FID', ''))[:255] if pd.notna(row.get('FID')) else None,
                    embedding=embedding
                )

                session.add(service)

                # Commit in batches
                if (idx + 1) % 100 == 0:
                    session.commit()

            except Exception as e:
                print(f"  ⚠ Error processing row {idx}: {str(e)}")
                continue

        # Final commit
        session.commit()

        # Update PostGIS location column
        print("  Updating PostGIS location geometries...")
        session.execute(text("""
            UPDATE health_services
            SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            WHERE location IS NULL;
        """))
        session.commit()

        # Create spatial index
        print("  Creating spatial index...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_health_services_location
            ON health_services USING GIST (location);
        """))
        session.commit()

        count = session.query(HealthService).count()
        print(f"✓ Successfully imported {count} health services")

    except Exception as e:
        print(f"✗ Error importing health services: {str(e)}")
        session.rollback()
        import traceback
        traceback.print_exc()


def import_transit_stops(session):
    """Import Public Transit Stops data"""
    print("\n" + "="*60)
    print("Importing Transit Stops...")
    print("="*60)

    try:
        # Decode URL-encoded filename
        filename = urllib.parse.unquote('datasets/Public_Transit_Stops%2C_San_Diego_County.csv')
        df = pd.read_csv(filename, encoding='utf-8-sig')

        print(f"Found {len(df)} transit stop records")

        # Clean column names
        df.columns = df.columns.str.strip().str.replace('\ufeff', '')

        for idx, row in df.iterrows():
            try:
                stop = TransitStop(
                    objectid=int(row['OBJECTID']) if pd.notna(row.get('OBJECTID')) else None,
                    stop_uid=str(row.get('stop_UID', ''))[:255] if pd.notna(row.get('stop_UID')) else None,
                    stop_agency=str(row.get('stop_agency', ''))[:255] if pd.notna(row.get('stop_agency')) else None,
                    stop_id=str(row.get('stop_id', ''))[:255] if pd.notna(row.get('stop_id')) else None,
                    stop_name=str(row.get('stop_name', ''))[:255] if pd.notna(row.get('stop_name')) else None,
                    stop_lat=float(row['stop_lat']),
                    stop_lon=float(row['stop_lon']),
                    stop_code=str(row.get('stop_code', ''))[:255] if pd.notna(row.get('stop_code')) else None,
                    location_type=str(row.get('location_type', ''))[:255] if pd.notna(row.get('location_type')) else None,
                    parent_station=str(row.get('parent_station', ''))[:255] if pd.notna(row.get('parent_station')) else None,
                    wheelchair_boarding=str(row.get('wheelchair_boarding', ''))[:255] if pd.notna(row.get('wheelchair_boarding')) else None,
                    intersection_code=str(row.get('intersection_code', ''))[:255] if pd.notna(row.get('intersection_code')) else None,
                    stop_place=str(row.get('stop_place', ''))[:255] if pd.notna(row.get('stop_place')) else None
                )

                session.add(stop)

                if (idx + 1) % 500 == 0:
                    print(f"  Processing {idx + 1}/{len(df)}...")
                    session.commit()

            except Exception as e:
                print(f"  ⚠ Error processing row {idx}: {str(e)}")
                continue

        session.commit()

        # Update PostGIS location column
        print("  Updating PostGIS location geometries...")
        session.execute(text("""
            UPDATE transit_stops
            SET location = ST_SetSRID(ST_MakePoint(stop_lon, stop_lat), 4326)
            WHERE location IS NULL;
        """))
        session.commit()

        # Create spatial index
        print("  Creating spatial index...")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transit_stops_location
            ON transit_stops USING GIST (location);
        """))
        session.commit()

        count = session.query(TransitStop).count()
        print(f"✓ Successfully imported {count} transit stops")

    except Exception as e:
        print(f"✗ Error importing transit stops: {str(e)}")
        session.rollback()
        import traceback
        traceback.print_exc()


def import_transit_routes(session):
    """Import Public Transit Routes data"""
    print("\n" + "="*60)
    print("Importing Transit Routes...")
    print("="*60)

    try:
        filename = urllib.parse.unquote('datasets/Public_Transit_Routes%2C_San_Diego_County.csv')
        df = pd.read_csv(filename, encoding='utf-8-sig')

        print(f"Found {len(df)} transit route records")

        df.columns = df.columns.str.strip().str.replace('\ufeff', '')

        for idx, row in df.iterrows():
            try:
                route = TransitRoute(
                    objectid=int(row['objectid']) if pd.notna(row.get('objectid')) else None,
                    shape_id=str(row.get('shape_id', ''))[:255] if pd.notna(row.get('shape_id')) else None,
                    route_id=str(row.get('route_id', ''))[:255] if pd.notna(row.get('route_id')) else None,
                    route_short_name=str(row.get('route_short_name', ''))[:255] if pd.notna(row.get('route_short_name')) else None,
                    route_long_name=str(row.get('route_long_name', ''))[:255] if pd.notna(row.get('route_long_name')) else None,
                    route_type=str(row.get('route_type', ''))[:255] if pd.notna(row.get('route_type')) else None,
                    agency_id=str(row.get('agency_id', ''))[:255] if pd.notna(row.get('agency_id')) else None,
                    route_desc=str(row.get('route_desc', '')) if pd.notna(row.get('route_desc')) else None,
                    route_url=str(row.get('route_url', ''))[:255] if pd.notna(row.get('route_url')) else None,
                    route_color=str(row.get('route_color', ''))[:255] if pd.notna(row.get('route_color')) else None,
                    route_text_color=str(row.get('route_text_color', ''))[:255] if pd.notna(row.get('route_text_color')) else None,
                    route_type_text=str(row.get('route_type_text', ''))[:255] if pd.notna(row.get('route_type_text')) else None,
                    routeshapename=str(row.get('routeshapename', ''))[:255] if pd.notna(row.get('routeshapename')) else None,
                    route_color_rgb=str(row.get('route_color_rgb', ''))[:255] if pd.notna(row.get('route_color_rgb')) else None,
                    route_text_color_rgb=str(row.get('route_text_color_rgb', ''))[:255] if pd.notna(row.get('route_text_color_rgb')) else None,
                    shape_length=float(row['shape_Length']) if pd.notna(row.get('shape_Length')) else None
                )

                session.add(route)

            except Exception as e:
                print(f"  ⚠ Error processing row {idx}: {str(e)}")
                continue

        session.commit()

        count = session.query(TransitRoute).count()
        print(f"✓ Successfully imported {count} transit routes")

    except Exception as e:
        print(f"✗ Error importing transit routes: {str(e)}")
        session.rollback()
        import traceback
        traceback.print_exc()


def main():
    """Main import function"""
    print("="*60)
    print("San Diego County Dataset Import")
    print("="*60)

    # Create engine and session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create all tables
        print("\nCreating database tables...")
        Base.metadata.create_all(engine)
        print("✓ Tables created")

        # Import datasets
        import_health_services(session)
        import_transit_stops(session)
        import_transit_routes(session)

        print("\n" + "="*60)
        print("✅ Dataset import completed successfully!")
        print("="*60)

        # Print summary
        print("\nDatabase Summary:")
        print(f"  Health Services: {session.query(HealthService).count()}")
        print(f"  Transit Stops:   {session.query(TransitStop).count()}")
        print(f"  Transit Routes:  {session.query(TransitRoute).count()}")

    except Exception as e:
        print(f"\n✗ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
