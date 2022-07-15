#!/usr/bin/env python
# coding: utf-8

# Importe
try:
    import pyexcel
except ImportError:
    import pip
    pip.main(['install', '--user', 'pyexcel'])
    import pyexcel

import os, re, shutil, sys

# Variablen

xml_prefix = "<?xml version='1.0' encoding='UTF-8'?>\n<dublin_core schema='{schema}'>\n"
xml_newline_qual = '<dcvalue element="{element}" qualifier="{qualifier}" language="{lan}">{value}</dcvalue>\n'
xml_newline = '<dcvalue element="{element}" language="{lan}">{value}</dcvalue>\n'
xml_suffix = '</dublin_core>'

schema_dict = {
        'dc':'dublin_core',
        'local':'metadata_local', # hier ggf. weitere Metadaten-Schemata eintragen
        }

separator = '||'

# Funktionen

#def make_xml(newdir, schemata, row_of_metadata, n):
def make_xml(schemata, row_of_metadata, n):
    ''' erstellt pro Metadaten-Schema eine XML-Datei '''

    language = ''
    for schema in schemata:

        xml_metadata = xml_prefix.format(schema = schema)
        xml_columns = [v for v in row_of_metadata if v.split('.')[0] == schema] # Auswahl der Spalten des Schemas

        for elem in xml_columns: # z.B. elem = dc.subject.work[de] schema.element.qualifier[language]

            values_in_cell = str(row_of_metadata[elem]).split(separator)

            # Abfrage Sprache, ggf. ergänzen für weitere Sprachen
            if '[de]' in elem:
                language = 'de'
            elif '[en]' in elem:
                language = 'en'
            else:
                language = ''

            elem = re.sub('\[.*\]', '', elem)    # [] entfernen

            # taglist erstellen
            taglist = elem.split('.')

            for value in values_in_cell: # for multiple values

                element = taglist[1]

                if len(taglist) > 2:
                    qualifier = taglist[2]
                    newline = xml_newline_qual.format(element=element, qualifier=qualifier, lan=language, value=value)
                else:
                    newline = xml_newline.format(element=element, lan=language, value=value)

                xml_metadata += newline

        xml_metadata += xml_suffix

        with open(schema_dict[schema] +'.xml', 'w', encoding='utf-8') as fo:
            fo.write(xml_metadata)


def process_sheet(wdir, sheet):
    ''' liest Sheet zeilenweise aus, erstellt XML-Dateien für jedes Item (Zeile) '''

    def filter_row(row_index, row):
        """
        entfernt leere Zeilen
        """
        result = [element for element in row if element != '']
        return len(result)==0

    del sheet.row[filter_row]

    os.chdir(wdir)

    schemata = set([x.split('.')[0] for x in sheet.colnames[2:]])
    records = sheet.to_records()
    bundle_dict = {
        'pdf': '\tbundle: ORIGINAL\n',
        'webm': '\tbundle: ORIGINAL\n',
        'mp4': '\tbundle: ORIGINAL\n',
        'gif': '\tbundle: THUMBNAIL\n',
        'jpg': '\tbundle: THUMBNAIL\n',
        'png': '\tbundle: THUMBNAIL\n',
        }

    for n, row_of_metadata in enumerate(records):

        source_files = r'{}'.format(row_of_metadata['SourceFile'])
        collection = row_of_metadata['collection']

        newdir = '{collection}_item_{number}'.format(collection=collection, number=n)
        os.mkdir(newdir)
        os.chdir(os.path.join('.', newdir)) # ins Subdirectory gehen

        # erstellt XML-Dateien (1 pro Metadaten-Schema)
        #make_xml(newdir, schemata, row_of_metadata, n)
        make_xml(schemata, row_of_metadata, n)

        # erstellt CONTENT-Datei
        fo = open('contents', 'a', encoding = 'utf-8')

        for source_file in source_files.split(separator):# erstellt CONTENT-Datei
            doc_path, doc_name = os.path.split(source_file.strip('"'))
            doc_name = doc_name.strip()
            ext = doc_name.split('.')[-1].strip(' ')
            if ext not in bundle_dict:
                print('Kann das Dokument', doc_name, 'keinem Bundle zuordnen')
                sys.exit()
            else:
                fo.write(doc_name + bundle_dict[ext])

            # verschiebt Dokumente in ITEM-Ordner (cwdir)
            destination_file = os.path.join(wdir, newdir, doc_name)
            shutil.copyfile(source_file, destination_file) # neu
            print('Dateien erstellt in Ordner: ', newdir)

        fo.close() # schließt CONTENT-File
        os.chdir(wdir) # wieder hoch

# main

def main(filename):
    """
    Creates Simple Archive Packages for Batch Ingest in DSpace 6
    """

    filename = os.path.normcase(filename)
    #wdir, ods_file = os.path.split(filename)
    ods_file = os.path.basename(filename)
    wdir = os.path.abspath(os.path.dirname(filename))
    book = pyexcel.get_book(file_name=filename)

    for sheet in book:
        sheet.name_columns_by_row(0)
        if len(sheet) == 0:
            print(sheet.name, 'ist leer')
        elif sheet.name.startswith('_'):
            print(sheet.name, 'wird übersprungen')
        else:
            print(sheet.name, 'wird verarbeitet')
            process_sheet(wdir, sheet)


if __name__ == "__main__":

    import sys
    import os 
    filename = sys.argv[1]

    main(filename)
