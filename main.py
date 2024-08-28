import glob
import os
import shutil
import sys
import json
import re

# Setze die Standardkodierung für die Ausgabe auf UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

config_path = 'config.json'

def find_dir(dir):
    matching_paths = glob.glob(dir)
    if not matching_paths:
        sys.exit(f"Es wurden kein Pfad '{dir}' gefunden.")
    return matching_paths


def get_latest_file_by_name(dir, name):
    """Findet die neueste Datei im Verzeichnis mit dem gegebenen Namen."""
    matching_paths = find_dir(dir)

    list_of_files = glob.glob(os.path.join(dir, name))
    if not list_of_files:
        sys.exit(f"Keine Dateien '{name}' im Verzeichnis '{dir}' gefunden.")

    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Gefundene {name}-Datei: {latest_file}")
    return latest_file

def parse_inhalt(kennung, string_content):
    """Parst die Zeilen nach einer bestimmten Kennung."""
    lines = string_content.splitlines()
    for i, line in enumerate(lines):
        if line[3:7] == kennung:
            inhalt = line[7:].strip()
            print(f"Kennung {kennung} gefunden in Zeile {i}: {inhalt}")
            return inhalt

    print(f"Für Kennung {kennung} wurde keine Zuordnung gefunden")
    return None

def parse_gdt(file, kennungen):
    """Parst die GDT-Datei und extrahiert die relevanten Informationen."""
    try:
        # Versuche, die Datei mit verschiedenen Kodierungen zu lesen
        encodings = ['utf-8', 'iso-8859-1', 'latin1']
        gdt_str_content = None
        for enc in encodings:
            try:
                with open(file, "r", encoding=enc) as f:
                    gdt_str_content = f.read()
                print(f"Datei erfolgreich mit Kodierung '{enc}' gelesen.")
                break
            except UnicodeDecodeError:
                print(f"Kodierung '{enc}' fehlgeschlagen, versuche nächste...")
                continue

        if gdt_str_content is None:
            sys.exit("Fehler: Keine geeignete Kodierung gefunden, um die GDT-Datei zu lesen.")

        inhalte = [parse_inhalt(kennung, gdt_str_content) for kennung in kennungen]

        if None in inhalte:
            sys.exit("Fehler beim Parsen der GDT-Datei. Nicht alle erforderlichen Informationen konnten extrahiert werden.")

        return inhalte

    except FileNotFoundError:
        sys.exit(f"Die Datei '{file}' konnte nicht gefunden werden.")
    except Exception as e:
        sys.exit(f"Ein unerwarteter Fehler ist beim Parsen der GDT-Datei aufgetreten: {e}")

def save_as(src, dst):
    """Speichert eine Datei unter einem neuen Namen."""
    try:
        shutil.copyfile(src, dst)
        print(f"Datei gespeichert unter: {dst}")
    except FileNotFoundError:
        sys.exit(f"Die Datei '{src}' konnte nicht gefunden werden.")
    except Exception as e:
        sys.exit(f"Ein unerwarteter Fehler ist beim Speichern der Datei aufgetreten: {e}")

def delete(file_name):
    """Löscht eine Datei."""
    try:
        os.remove(file_name)
        print(f"Datei gelöscht: {file_name}")
    except FileNotFoundError:
        print(f"Die Datei '{file_name}' konnte nicht gefunden werden.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist beim Löschen der Datei aufgetreten: {e}")

def get_file_extension(filename):
    """Gibt die Dateierweiterung zurück."""
    _, extension = os.path.splitext(filename)
    return extension

def extract_path_and_filename(full_path):
    # Extrahiere den Dateinamen aus dem Pfad
    filename = os.path.basename(full_path)

    # Extrahiere den Pfad ohne den Dateinamen
    path = os.path.dirname(full_path)

    return path, filename

import re
import json

def apply_transformations(extracted_string, transformations):
    if not isinstance(extracted_string, str):
        raise ValueError("Der übergebene String muss ein gültiger Text sein.")

    if not isinstance(transformations, list):
        raise ValueError("Transformations müssen eine Liste von Transformationen sein.")

    for transformation in transformations:
        # Überprüfen, ob alle erforderlichen Schlüssel in der Transformation vorhanden sind
        if not isinstance(transformation, dict):
            raise TypeError("Jede Transformation muss ein Dictionary sein.")

        if "pattern" not in transformation or "replacement" not in transformation:
            raise KeyError("Jede Transformation muss die Schlüssel 'pattern' und 'replacement' enthalten.")

        pattern = transformation["pattern"]
        replacement = transformation["replacement"]

        # Überprüfen, ob 'pattern' und 'replacement' gültige Strings sind
        if not isinstance(pattern, str) or not isinstance(replacement, str):
            raise ValueError("'pattern' und 'replacement' müssen Strings sein.")

        try:
            # Kompiliere das Muster, um die Anzahl der Gruppen zu ermitteln
            compiled_pattern = re.compile(pattern)
            max_group_num = compiled_pattern.groups

            # Überprüfen, ob das 'replacement' gültige Gruppenreferenzen enthält
            invalid_references = []
            for ref in re.findall(r'\$(\d+)', replacement):
                if int(ref) > max_group_num:
                    invalid_references.append(ref)

            if invalid_references:
                raise ValueError(f"Ungültige Gruppenreferenzen im 'replacement': {' '.join(invalid_references)}. "
                                 f"Das Muster enthält nur {max_group_num} Gruppen.")

            # Ersetzen von $1, $2, $3 durch \1, \2, \3
            replacement = re.sub(r'\$(\d)', r'\\\1', replacement)

            # Anwenden der Transformation auf den extrahierten String
            new_string = re.sub(compiled_pattern, replacement, extracted_string)

            # Ausgabe, wenn die Transformation erfolgreich angewendet wurde
            if new_string != extracted_string:
                print(f"Transformation erfolgreich angewendet:\nVorher: {extracted_string}\nNachher: {new_string}")

            extracted_string = new_string

        except re.error as e:
            # Fehlerbehandlung für ungültige reguläre Ausdrücke
            raise ValueError(f"Ungültiger regulärer Ausdruck in der Transformation: {e}")

    return extracted_string

def compile_name(gdt_file, config):
    suffixe = []
    suffixe.extend(parse_gdt(gdt_file, config['kennungen']))

    prefix = config.get('prefix', '')
    if prefix:
        print(f"Prefix gefunden: '{prefix}'")
        suffixe.insert(0, prefix)
    postfix = config.get('postfix', '')
    if postfix:
        print(f"Postfix gefunden: '{postfix}'")
        suffixe.append(postfix)

    transformations = config.get("transformations", None)
    if transformations:
        for i, s in enumerate(suffixe):
            suffixe[i] = apply_transformations(s, transformations)

    return config['trennzeichen'].join(suffixe)

def main(config):
    """Hauptfunktion zur Verarbeitung und Export der Dateien."""
    file_path = config["file_path"]
    gdt_path = config["gdt_path"]
    export_path = config["export_path"]

    matching_paths = find_dir(export_path)

    if not matching_paths:
        try:
            os.makedirs(export_path)
            print(f"Exportverzeichnis '{export_path}' erstellt.")
        except Exception as e:
            sys.exit(f"Fehler beim Erstellen des Exportverzeichnisses: {e}")

    file_tuple = extract_path_and_filename(file_path)
    gdt_tuple = extract_path_and_filename(gdt_path)

    latest_pdf_file = get_latest_file_by_name(file_tuple[0], f"{file_tuple[1]}")
    latest_gdt_file = get_latest_file_by_name(gdt_tuple[0], f"{gdt_tuple[1]}")

    new_file_name = compile_name(latest_gdt_file, config)
    save_as(latest_pdf_file, os.path.join(matching_paths[0], f"{new_file_name}{get_file_extension(latest_pdf_file)}"))

    if config.get("delete_gdt", False):
        delete(latest_gdt_file)
    if config.get("delete_file", False):
        delete(latest_pdf_file)

if __name__ == "__main__":
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
        sys.exit(f"Fehler beim Laden der Konfigurationsdatei: {e}")
    except Exception as e:
        sys.exit(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    main(config)

    # python3.11 -m nuitka --standalone --onefile --follow-imports main.py
