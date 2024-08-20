import glob
import os
import shutil
import sys
import json

# Setze die Standardkodierung für die Ausgabe auf UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

config_path = 'config.json'

def get_latest_file_by_name(dir, name):
    """Findet die neueste Datei im Verzeichnis mit dem gegebenen Namen."""
    if not os.path.isdir(dir):
        sys.exit(f"Das Verzeichnis '{dir}' wurde nicht gefunden.")

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

def parse_gdt(file, kennungen, trennzeichen):
    """Parst die GDT-Datei und extrahiert die relevanten Informationen."""
    try:
        # Versuche, die Datei mit verschiedenen Kodierungen zu lesen
        encodings = ['utf-8', 'iso-8859-1', 'latin1']
        gdt_content = None
        for enc in encodings:
            try:
                with open(file, "r", encoding=enc) as f:
                    gdt_content = f.read()
                print(f"Datei erfolgreich mit Kodierung '{enc}' gelesen.")
                break
            except UnicodeDecodeError:
                print(f"Kodierung '{enc}' fehlgeschlagen, versuche nächste...")
                continue

        if gdt_content is None:
            sys.exit("Fehler: Keine geeignete Kodierung gefunden, um die GDT-Datei zu lesen.")

        inhalte = [parse_inhalt(kennung, gdt_content) for kennung in kennungen]

        if None in inhalte:
            sys.exit("Fehler beim Parsen der GDT-Datei. Nicht alle erforderlichen Informationen konnten extrahiert werden.")

        return trennzeichen.join(inhalte)

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

def main(config):
    """Hauptfunktion zur Verarbeitung und Export der Dateien."""
    input_path = config["input_path"]
    gdt_path = config["gdt_path"]
    export_path = config["export_path"]

    if not os.path.exists(export_path):
        try:
            os.makedirs(export_path)
            print(f"Exportverzeichnis '{export_path}' erstellt.")
        except Exception as e:
            sys.exit(f"Fehler beim Erstellen des Exportverzeichnisses: {e}")

    input_file = config["input_file"]
    latest_pdf_file = get_latest_file_by_name(input_path, f"{input_file}")
    latest_gdt_file = get_latest_file_by_name(gdt_path, "*.gdt")

    new_file_name = parse_gdt(latest_gdt_file, config['kennungen'], config['trennzeichen'])
    save_as(latest_pdf_file, os.path.join(export_path, f"{new_file_name}{get_file_extension(latest_pdf_file)}"))

    if config.get("delete_gdt", False):
        delete(latest_gdt_file)
    if config.get("delete_input", False):
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
