-- Setze das Arbeitsverzeichnis
set workingDirectory to "/Users/jonas/Documents/git/formular_exporter"

-- Erstelle das Kommando zum Ausführen der Binärdatei
set command to "cd " & quoted form of workingDirectory & " && ./pdf_export"

-- Führe das Kommando im Terminal aus
do shell script command