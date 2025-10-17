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
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT
  ?river ?riverLabel
  ?country
  ?state
  ?source ?sourceLabel ?sourceElevation
  ?mouth ?mouthLabel
  ?length ?discharge ?basin
  ?tributary
WHERE {
  ?river a dbo:River ;
         rdfs:label ?riverLabel .
  FILTER(LANG(?riverLabel) = "en")

  # Country filter: United States
  OPTIONAL { ?river dbo:country dbr:United_States . BIND(dbr:United_States AS ?country) }
  OPTIONAL { ?river dbp:country dbr:United_States . BIND(dbr:United_States AS ?country) }
  OPTIONAL { ?river dbo:mouthCountry dbr:United_States . BIND(dbr:United_States AS ?country) }
  OPTIONAL {
    ?river dbo:state ?stateUS .
    ?stateUS dbo:country dbr:United_States .
    BIND(dbr:United_States AS ?country)
  }

  # US States traversed (dbo:state or dbo:locatedInArea links)
  OPTIONAL {
    { ?river dbo:state ?state } UNION { ?river dbo:locatedInArea ?state } UNION { ?river dbp:state ?state }
    FILTER(STRSTARTS(STR(?state), STR(dbr:)))
  }

  # Source features
  OPTIONAL {
    { ?river dbo:source ?source } UNION { ?river dbp:source ?source } UNION { ?river schema:source ?source }
    OPTIONAL { ?source rdfs:label ?sourceLabel . FILTER(LANG(?sourceLabel) = "en") }
  }
  OPTIONAL { ?river dbo:sourceElevation ?sourceElevation }

  # Mouth features
  OPTIONAL {
    { ?river dbo:mouth ?mouth } UNION { ?river dbp:mouth ?mouth } UNION { ?river schema:tributaryOf ?mouth }
    OPTIONAL { ?mouth rdfs:label ?mouthLabel . FILTER(LANG(?mouthLabel) = "en") }
  }

  # Physical attributes
  OPTIONAL { ?river dbo:length ?length }
  OPTIONAL { ?river dbp:length ?length }
  OPTIONAL { ?river dbo:discharge ?discharge }
  OPTIONAL { ?river dbp:discharge ?discharge }
  OPTIONAL { ?river dbo:drainageBasin ?basin }
  OPTIONAL { ?river dbp:basin ?basin }

  # Tributaries
  OPTIONAL { ?river dbo:tributary ?tributary }
  OPTIONAL { ?river dbp:tributaries ?tributary }

  # US inference via parent river's country
  OPTIONAL {
    ?parentRiver dbo:tributary ?river .
    { ?parentRiver dbo:country dbr:United_States } UNION { ?parentRiver dbp:country dbr:United_States } .
    BIND(dbr:United_States AS ?country)
  }

  # Exclude non-river hydrological features occasionally mis-typed
  FILTER NOT EXISTS { ?river a dbo:Lake }
  FILTER NOT EXISTS { ?river a dbo:Bay }
  FILTER NOT EXISTS { ?river a dbo:Sea }
  FILTER NOT EXISTS { ?river a dbo:Strait }
  FILTER NOT EXISTS { ?river a dbo:Ship }

  # Ensure it's US-related and has at least one of source/mouth/state/tributary
  FILTER(BOUND(?country))
  FILTER(BOUND(?state) || BOUND(?source) || BOUND(?mouth) || BOUND(?tributary))
}
LIMIT 5000
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

