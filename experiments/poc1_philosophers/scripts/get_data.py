import requests
import pandas as pd
from io import StringIO
import os

DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"

# Determine paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "raw_philosophers.csv")

# The query designed to get a high-quality dataset for the experiment
SPARQL_QUERY = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT
?person?personLabel
?teacher?teacherLabel
?personBirth?personDeath
?teacherBirth?teacherDeath
WHERE {
  {?person rdf:type dbo:Philosopher. }
  UNION
  {?person rdf:type dbo:Scientist. }

 ?person dbo:influencedBy?teacher.
 ?person dbo:birthDate?personBirth;
          dbo:deathDate?personDeath.
 ?teacher dbo:birthDate?teacherBirth;
           dbo:deathDate?teacherDeath.

  FILTER (datatype(?personBirth) = xsd:date)
  FILTER (datatype(?personDeath) = xsd:date)
  FILTER (datatype(?teacherBirth) = xsd:date)
  FILTER (datatype(?teacherDeath) = xsd:date)

 ?person rdfs:label?personLabel.
 ?teacher rdfs:label?teacherLabel.
  FILTER(LANG(?personLabel) = "en").
  FILTER(LANG(?teacherLabel) = "en").
}
LIMIT 10000
"""


def fetch_dbpedia_data():
    """Fetches data from DBpedia and saves it as a CSV."""
    headers = {"Accept": "text/csv"}
    params = {"query": SPARQL_QUERY, "format": "text/csv"}

    print("Querying DBpedia endpoint...")
    try:
        response = requests.get(DBPEDIA_ENDPOINT, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Use pandas to read the CSV data and save it
        df = pd.read_csv(StringIO(response.text))
        df.to_csv(OUTPUT_PATH, index=False)

        print(f"Successfully downloaded {len(df)} records to {OUTPUT_PATH}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from DBpedia: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    fetch_dbpedia_data()

