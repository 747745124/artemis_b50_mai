import os
import xml.etree.ElementTree as ET
import json

md_cache = {}

path = ""  # like Sinmai_Data\StreamingAssets\
opt_path = ""  # like options


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


def process(directory):
    global md_cache

    for root, dirs, files in os.walk(directory):
        for file in files:

            if file == 'Music.xml':
                xml_file = os.path.join(root, file)
                json_data = xml_to_json(xml_file)
                for music_id, data in json_data.items():
                    md_cache[music_id] = data


def process_folder(tag_path):
    for subdir in os.listdir(tag_path):

        if os.path.isdir(os.path.join(tag_path, subdir)):
            if subdir.startswith(('A', 'H')) and subdir[1:].isdigit():
                music_path = os.path.join(tag_path, subdir, "Music")

                if os.path.exists(music_path) and os.path.isdir(music_path):
                    process(music_path)


process_folder(path)
if opt_path != "":
    process_folder(opt_path)
#
with open('md_cache.json', 'w', encoding='utf-8') as f:
    json.dump(md_cache, f, ensure_ascii=False, indent=4)

