-- Setze das Arbeitsverzeichnis
set workingDirectory to "/Users/jonas/Documents/git/formular_exporter"

-- Erstelle das Kommando zum Ausf�hren der Bin�rdatei
set command to "cd " & quoted form of workingDirectory & " && ./pdf_export"

-- F�hre das Kommando im Terminal aus
do shell script command