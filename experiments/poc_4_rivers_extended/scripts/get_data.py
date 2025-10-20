# Step 1: Get data from DBpedia
import requests
import pandas as pd
from io import StringIO
import os

DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"

# Determine paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "raw_rivers.csv")

# Query to get US rivers and rich geographic attributes
SPARQL_QUERY = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dbp: <http://dbpedia.org/property/>

SELECT DISTINCT 
    ?river ?riverName ?abstract 
    ?length ?discharge ?watershed
    ?sourceLocation ?sourceMountain ?sourceState ?sourceElevation
    ?riverMouth ?mouthLocation ?mouthState ?mouthElevation
    ?state ?county 
    ?riverSystem
    ?leftTributary ?rightTributary
    ?country ?wikiPageID
WHERE {
    ?river a dbo:River ;
           rdfs:label ?riverName ;
           dbo:abstract ?abstract .
    
    FILTER(LANG(?riverName) = "en")
    FILTER(LANG(?abstract) = "en")
    
    # US rivers via categories
    ?river dct:subject ?category .
    FILTER(REGEX(STR(?category), "Rivers_of", "i"))
    FILTER(REGEX(STR(?category), "United_States|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New_Hampshire|New_Jersey|New_Mexico|New_York|North_Carolina|North_Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode_Island|South_Carolina|South_Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West_Virginia|Wisconsin|Wyoming", "i"))
    
    # Physical measurements
    OPTIONAL { ?river dbo:length ?length }
    OPTIONAL { ?river dbo:discharge ?discharge }
    OPTIONAL { ?river dbo:watershed ?watershed }
    
    # Source information
    OPTIONAL { ?river dbo:sourceLocation ?sourceLocation }
    OPTIONAL { ?river dbo:sourceMountain ?sourceMountain }
    OPTIONAL { ?river dbo:sourceState ?sourceState }
    OPTIONAL { ?river dbo:sourceElevation ?sourceElevation }
    
    # Mouth information (where it flows into)
    OPTIONAL { ?river dbo:riverMouth ?riverMouth }
    OPTIONAL { ?river dbo:mouthLocation ?mouthLocation }
    OPTIONAL { ?river dbo:mouthState ?mouthState }
    OPTIONAL { ?river dbo:mouthElevation ?mouthElevation }
    
    # Geographic location
    OPTIONAL { ?river dbo:state ?state }
    OPTIONAL { ?river dbo:county ?county }
    OPTIONAL { ?river dbo:country ?country }
    
    # River system (which major river system it belongs to)
    OPTIONAL { ?river dbp:riverSystem ?riverSystem }
    
    # Tributaries
    OPTIONAL { ?river dbp:leftTributary ?leftTributary }
    OPTIONAL { ?river dbp:rightTributary ?rightTributary }
    
    # Wiki ID
    OPTIONAL { ?river dbo:wikiPageID ?wikiPageID }
}
ORDER BY ?riverName
"""


def fetch_dbpedia_data():
    """Fetches US rivers data from DBpedia and saves it as a CSV."""
    headers = {"Accept": "text/csv"}
    params = {"query": SPARQL_QUERY, "format": "text/csv"}

    print("Querying DBpedia endpoint for US rivers...")
    print("This may take a minute...")
    
    try:
        response = requests.get(DBPEDIA_ENDPOINT, params=params, headers=headers, timeout=300)
        response.raise_for_status()

        # Use pandas to read the CSV data and save it
        df = pd.read_csv(StringIO(response.text))
        
        # Clean up the data
        print(f"Retrieved {len(df)} records from DBpedia")
        
        # Remove duplicates
        df = df.drop_duplicates()
        print(f"After removing duplicates: {len(df)} records")
        
        df.to_csv(OUTPUT_PATH, index=False)
        print(f"Successfully saved data to {OUTPUT_PATH}")

    except requests.exceptions.Timeout:
        print("Error: Query timed out. DBpedia might be slow. Try again later.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from DBpedia: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    fetch_dbpedia_data()