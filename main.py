# Aufruf: python formular_exporter.py <src> <gdt> <dst>
# Bsp.: python formular_exporter.py /Users/jonas/.tomedoCache/temporaryFiles/proxy /Users/jonas/gdt /Users/jonas/export

import glob
import os
import shutil
import sys
import json
import codecs

# Reconfigure stdout to use UTF-8
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def get_latest_file_by_name(dir, name):
    try:
        # Überprüfe, ob das Verzeichnis existiert
        if not os.path.isdir(dir):
            raise FileNotFoundError(f"Das Verzeichnis '{dir}' wurde nicht gefunden.")

        # Suche nach Dateien mit angegebenem Namen
        list_of_files = glob.glob(os.path.join(dir, name))

        # Überprüfe, ob Dateien gefunden wurden
        if not list_of_files:
            raise FileNotFoundError(f"Keine Dateien '{name}' im Verzeichnis '{dir}' gefunden.")

        # Erhalte die neueste Datei
        res = max(list_of_files, key=os.path.getctime)
        print(f"Gefundene {name}-Datei: {res}")
        return res
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)  # Beendet das Programm bei einem schwerwiegenden Fehler
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        sys.exit(1)

def parse_inhalt(kennung, lines):
    for i, line in enumerate(lines):
        if line[3:7] == kennung:
            inhalt = line[7:].strip()
            print(f"Kennung {kennung} gefunden in Zeile {i}: {inhalt}")
            return inhalt
    print(f"Für Kennung {kennung} wurde keine Zuordnung gefunden")
    return None

def parse_gdt(file, kennungen, trennzeichen):
    try:
        with open(file, "r", encoding='latin-1') as f:
            lines = f.readlines()

        inhalte = []
        for kennung in data['kennungen']:
            inhalte.append(parse_inhalt(kennung, lines))

        if None in inhalte:
            raise ValueError("Fehler beim Parsen der GDT-Datei. Nicht alle erforderlichen Informationen konnten extrahiert werden.")

        return trennzeichen.join(inhalte)
    except FileNotFoundError:
        print(f"Die Datei '{file}' konnte nicht gefunden werden.")
        sys.exit(1)
    except ValueError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist beim Parsen der GDT-Datei aufgetreten: {e}")
        sys.exit(1)

def save_as(src, dst):
    try:
        shutil.copyfile(src, dst)
        print(f"Datei gespeichert als: {dst}")
    except FileNotFoundError:
        print(f"Die Datei '{src}' konnte nicht gefunden werden.")
        sys.exit(1)
    except PermissionError:
        print(f"Keine Berechtigung, um die Datei '{dst}' zu speichern.")
        sys.exit(1)
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist beim Speichern der Datei aufgetreten: {e}")
        sys.exit(1)

def delete(file_name):
    try:
        os.remove(file_name)
        print(f"Datei gelöscht: {file_name}")
    except FileNotFoundError:
        print(f"Die Datei '{file_name}' konnte nicht gefunden werden.")
    except PermissionError:
        print(f"Keine Berechtigung, um die Datei '{file_name}' zu löschen.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist beim Löschen der Datei aufgetreten: {e}")

def get_file_extension(filename):
    # Split the filename into the base name and extension
    _, extension = os.path.splitext(filename)
    return extension

def main(config):

    input_path = config["input_path"]
    gdt_path = config["gdt_path"]
    export_path = config["export_path"]

    # Überprüfen, ob das Exportverzeichnis existiert, und bei Bedarf erstellen
    if not os.path.exists(export_path):
        try:
            os.makedirs(export_path)
            print(f"Exportverzeichnis '{export_path}' erstellt.")
        except Exception as e:
            print(f"Fehler beim Erstellen des Exportverzeichnisses: {e}")
            sys.exit(1)
    input_file = data["input_file"]
    latest_pdf_file = get_latest_file_by_name(input_path, f"{input_file}")

    latest_gdt_file = get_latest_file_by_name(gdt_path, "*.gdt")
    new_file_name = parse_gdt(latest_gdt_file, data['kennungen'], data['trennzeichen'])
    save_as(latest_pdf_file, os.path.join(export_path, f"{new_file_name}{get_file_extension(latest_pdf_file)}"))
    if data["delete_gdt"]:
        delete(latest_gdt_file)
    if data["delete_input"]:
        delete(latest_pdf_file)

if __name__ == "__main__":
    config_path = 'config.json'

    try:
        # Versuche, die Konfigurationsdatei zu öffnen
        with open(config_path, 'r') as f:
            try:
                # Versuche, die JSON-Daten zu laden
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Fehler beim Laden der JSON-Daten: {e}")
                sys.exit(1)  # Programm mit Fehlercode beenden
    except FileNotFoundError:
        print(f"Die Konfigurationsdatei '{config_path}' wurde nicht gefunden.")
        sys.exit(1)  # Programm mit Fehlercode beenden
    except PermissionError:
        print(f"Keine Berechtigung, um die Datei '{config_path}' zu lesen.")
        sys.exit(1)  # Programm mit Fehlercode beenden
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        sys.exit(1)  # Programm mit Fehlercode beenden

    # Wenn alles erfolgreich war, rufe die Hauptfunktion auf
    main(data)


# python3.11 -m nuitka --standalone --onefile --follow-imports main.py
