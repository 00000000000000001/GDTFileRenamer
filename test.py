import re
import json

# Beispielhaftes Laden der Konfigurationsdatei
with open("config.json", "r") as config_file:
    config = json.load(config_file)

def apply_transformations(extracted_string, transformations):
    for transformation in transformations:
        pattern = transformation["pattern"]
        replacement = transformation["replacement"]
        # Ersetzen von $1, $2, $3 durch \1, \2, \3
        replacement = re.sub(r'\$(\d)', r'\\\1', replacement)
        extracted_string = re.sub(pattern, replacement, extracted_string)
    return extracted_string

# Angenommen, du hast einen extrahierten Datums-String
extracted_date = "28.08.2024"

# Transformationen anwenden
transformed_date = apply_transformations(extracted_date, config["transformations"])

print(transformed_date)  # Ausgabe: 2024-08-28
