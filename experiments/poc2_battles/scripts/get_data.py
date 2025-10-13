import requests
import pandas as pd
from io import StringIO
import os

DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"

# Determine paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "raw_battles.csv")

# Query to get military battles with commanders and their lifespans
SPARQL_QUERY = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT
  ?battle ?battleLabel ?battleDate
  ?commander ?commanderLabel ?commanderBirth ?commanderDeath
  ?country ?countryLabel
WHERE {
  ?battle a dbo:MilitaryConflict ;
          rdfs:label ?battleLabel ;
          dbo:date ?battleDate ;
          dbo:commander ?commander .
  
  ?commander rdfs:label ?commanderLabel ;
             dbo:birthDate ?commanderBirth ;
             dbo:deathDate ?commanderDeath .
  
  OPTIONAL {
    ?commander dbo:nationality ?country .
    ?country rdfs:label ?countryLabel .
    FILTER(LANG(?countryLabel) = "en")
  }
  
  # Also get combatant countries from the battle
  OPTIONAL {
    ?battle dbo:combatant ?combatant .
  }
  
  FILTER(LANG(?battleLabel) = "en")
  FILTER(LANG(?commanderLabel) = "en")
  FILTER(datatype(?battleDate) = xsd:date)
  FILTER(datatype(?commanderBirth) = xsd:date)
  FILTER(datatype(?commanderDeath) = xsd:date)
  
  # Focus on the modern era for data quality (year >= 1000)
  FILTER(YEAR(?battleDate) >= 1000)
  FILTER(YEAR(?commanderBirth) >= 1000)
  FILTER(YEAR(?commanderDeath) >= 1000)
}
LIMIT 20000
"""


def fetch_dbpedia_data():
    """Fetches battle data from DBpedia and saves it as a CSV."""
    headers = {"Accept": "text/csv"}
    params = {"query": SPARQL_QUERY, "format": "text/csv"}

    print("Querying DBpedia endpoint for military battles...")
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

