# DSpace Python Packager
Das Skript erstellt Ordner im [DSpace Simple Archive Format](https://wiki.lyrasis.org/display/DSDOC7x/Importing+and+Exporting+Items+via+Simple+Archive+Format) für den Batch-Upload in ein DSpace-Repositorium.
Entwickelt wurde das Skript für das **Open-Access-Repositorium der Medienwissenschaft** [media/rep/](https://mediarep.org)

## Voraussetzungen
- Administrativer Zugang zu einer [DSpace-Instanz](https://github.com/DSpace/DSpace)
- Tabelle mit Metadaten
- Python3
- Abhängigkeiten: [Pyexcel-Modul](https://github.com/pyexcel/pyexcel) ggf. mit den Ergänzungen für ODS-, XSLX-Dateien

## Vorbereitung
Eine Metadaten-Tabelle (.csv, .ods, .xlsx) wird nach folgendem Schema angelegt:

SourceFile | collection | dc.element1 | dc.element2 | dc.element1 …
-------- | -------- | -------- | -------- | --------
pfad-zu-datei1 | Name der sammlung (*optional*) | Wert | Wert | Wert …
pfad-zu-datei2 | Name der sammlung (*optional*) | Wert1\|\|Wert2 | Wert | Wert | Wert …

Die Spalten mit den Metadaten werden wie folgt benannt:
- `dc.element` oder
- `dc.element.qualifier` oder 
- `dc.element.qualifier[language]`. \[Anmerkung: Aktuell sind hier nur 'de' oder 'en' als Werte erlaubt. Weitere Sprachen können im Skript aber ergänzt werden.\]

DSpace schreibt vor, dass **Dublin Core-Elemente** genutzt werden müssen; weitere zusätzliche Metadatenschemata sind erlaubt.
Das Skript unterstützt beliebige **weitere** (auch lokale) Metadatenschemata. Diese müssen im Skript in die Variable `schema_dict` eingetragen werden.

*Beispiel*

SourceFile | collection | dc.creator | dc.title | local.deutschertitel\[de\]| dc.date.issued
-------- | -------- | -------- | -------- | -------- | --------
/home/files/life-of-brian.pdf | Drehbuecher | Jones, Terry | The Life of Brian | Das Leben des Brian | 1979 | 
/home/files/holy-grail.pdf | Drehbuecher | Jones, Terry\|\|Gilliam, Terry | Monty Python and the Holy Grail | Die Ritter der Kokosnuss | 1975
/home/files/altenloh_soziologie.pdf | Filmsoziologie | Altenloh, Emilie | Zur Soziologie des Kino |  | 1913

- Die Spalten **SourceFile** und **collection** müssen vorhanden sein.

- In der Spalte **SourceFile** muss ein Wert vorhanden sein.

- Der Wert in der Spalte **collection** ist optional. Falls vorhanden, wird er Teil des Ordner-Namens

- Mindestens eine Spalte sollte das prefix "dc." für Dublin Core enthalten.

- Mehrere Werte in einem Feld werden durch die **Double Pipe '||' getrennt** (*Alternativ kann im Skript ein anderer Wert als Separator gesetzt werden*).


### Was ist das DSpace Simple Archive Format?

Das DSpace Simple Archive Format (SAV) erlaubt den **Batch Ingest** von mehreren Items (Dokumente + Metadaten) in eine DSpace-Sammlung.
**Für jede Zeile** in einer Tabelle erstellt das Skript einen Ordner (_item_0, _item_1, _item_2…). GGf. wird der Ordnername durch den jeweiligen Wert in 'collection" ergänzt (Drehbuecher_item_0, Drehbuecher_item_1, Filmsoziologie_item_0)
Durch die einheitliche Benennung können anschließend mehrere Items, die in _eine_ Sammlung hochgeladen werden sollen, auf einfache Weise in einer ZIP-Datei zusammengefasst werden.

#### Ordnerstruktur
Pro Ordner werden folgende Dateien angelegt:
- dublin_core.xml         -- Dublin Core Metadaten für Temadaten-Felder, die mit "dc." beginnen (muss vorhanden sein)
- `metadaten-schema`.xml  -- Metadaten aus anderen Schemata, z.B. dcterms, local usw. (optional. Diese Schemata in der DSpace-Instanz registriert sein.)
- contents                -- Textdatei, gibt die hochzuladenden Dateien an. Je eine Zeile pro Dateiname.
- file_1, file2           -- Eine oder mehrere Dateien für den Upload.


#### XML-Dateien

In der XML-Datei **dublin_core.xml** erhält jedes vergebene Metadaten-Element seinen eigenen Eintrag in einem <dcvalue>-Tag, mit den Attributen:
* element - Dublin Core Element
* qualifier - Qualifier des Elements
* language - (optional) Angabe der Sprache nach ISO

*Beispiel*
    <dublin_core>
        <dcvalue element="creator" qualifier="none">Jones, Terry</dcvalue>
        <dcvalue element="title" qualifier="none">The Life of Brian</dcvalue>
        <dcvalue element="date" qualifier="issued">1979</dcvalue>
    </dublin_core>

Entsprechendes gilt für optionale weitere XML-Dateien zu anderen Metadaten-Schemata.

### Aufruf:

`python packager.py pfad-zu-tabelle.csv`

bzw.

`python3 packager.py pfad-zu-tabelle.csv`

Nach dem Aufruf erstellt das Skript einen Ordner für jede Metadaten-Zeile / jedes Item in der Tabelle. Alle Ordner müssen anschließend (manuell) gezippt werden. 
Ordner, die in die selbe DSpace-Sammlung hochgeladen werden sollen, können in _einem_ ZIP-Archiv verbunden werden.

*Beispiel*
- Drehbuecher_item_0
- Drehbuecher_item_1
  
  → drehbuecher.zip
- Filmsoziologie_item_2
  
  → filmsoziologie.zip

Der **UI Batch Import** in DSpace [wird hier erklärt](https://wiki.lyrasis.org/display/DSDOC7x/Importing+and+Exporting+Items+via+Simple+Archive+Format#ImportingandExportingItemsviaSimpleArchiveFormat-UIBatchImport)

### Spezial: Mehrere Tabellen auslesen

Das Skript liest lle Tabellen (Sheets) in einer Excel-Datei aus (Ausname: Tabellen, deren Namen mit einem Unterstrich '\_' beginnen). Auf diese Weise ist es möglich, verschiedene Dokumenttypen (etwa Artikel, Buch, Graue Literatur usw.), die jeweils verschiedene Metadatenfelder benötigen, auf verschiedene Tabellen in einer Datei zu verteilen. Tabellen, die nicht ausgelesen werden sollten, werden `'_NAME'` benannt.


### Spezial: Upload von Video-Dateien mit Thumbnails

Da media/rep/ auch [Videos](https://mediarep.org/handle/doc/5228) (Vortragsaufzeichnungen, Vorlesungen, Videoessays) sammelt, können Videodateien
gemeinsam mit einem Thumbnail hochgeladen werden. In diesem Fall werden die Pfade zur Videodatei (.mp4, .webm) und zum Thumbnail (.jpg, .png, .gif) gemeinsam in die Spalte SoureFile (getrennt durch '\|\|') eingetragen.
