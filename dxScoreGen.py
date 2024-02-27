import os
import xml.etree.ElementTree as ET
import json

md_cache = {}

path = ""  # like StreamingAssets\A000\music etc


def xml_to_json(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    music_data = {}

    for child in root:
        if child.tag == 'name':
            music_id = child.find('id').text
            music_data[music_id] = {}
            music_data[music_id]['id'] = music_id
            music_data[music_id]['title'] = child.find('str').text
        elif child.tag == 'notesData':
            music_data[music_id]['dxScore'] = []
            for notes in child:
                if int(notes.find('maxNotes').text) == 0:
                    continue
                music_data[music_id]['dxScore'].append(int(notes.find('maxNotes').text) * 3)

    return music_data


def process_directory(directory):
    global md_cache

    for root, dirs, files in os.walk(directory):
        for file in files:

            if file == 'Music.xml':
                xml_file = os.path.join(root, file)
                json_data = xml_to_json(xml_file)
                for music_id, data in json_data.items():
                    md_cache[music_id] = data
                    # print("Converted and added to md_cache:", json.dumps(json_data, indent=4))


process_directory(path)

with open('md_cache.json', 'w', encoding='utf-8') as f:
    json.dump(md_cache, f, ensure_ascii=False, indent=4)
