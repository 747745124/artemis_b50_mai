import mysql.connector
from colorama import Fore, Style
import json
from maimai_best_50 import local_generate50
from maimai_best_50_alt import local_generate50_alt
import maimai_best_50
import maimai_best_50_alt


# db config
user_id = 10000 #10000 by default
db_host = "localhost"
db_user = "aime"
db_password = "" #config your password
db_database = "aime"
game_version = 21 # 19 for fes, 20 for fes plus, 21 for buddies
display_name = "Naoyuki" # this is the name to be displayed on the b50
is_save = False
is_show = True
use_alt = True # use alternative of b50 format
use_theme = 1 # the theme for b50, 0 for fes, 1 for buddies




#theme preprocess
suffix = ""
if use_theme == 0:
    suffix = "_fes"

#add suffix before .png
maimai_best_50.logoPath = maimai_best_50.logoPath.replace(".png", f"{suffix}.png")
maimai_best_50.bgPath = maimai_best_50.bgPath.replace(".png", f"{suffix}.png")
maimai_best_50_alt.logoPath_alt = maimai_best_50_alt.logoPath_alt.replace(".png", f"{suffix}.png")
maimai_best_50_alt.bgPath_alt = maimai_best_50_alt.bgPath_alt.replace(".png", f"{suffix}.png")

# constants
RANK_DEFINITIONS = [
    {"minAchv": 100.5, "factor": 22.4, "title": "sssp"},
    {"minAchv": 100.0, "factor": 21.6, "title": "sss"},
    {"minAchv": 99.5, "factor": 21.1, "title": "ssp"},
    {"minAchv": 99.0, "factor": 20.8, "title": "ss"},
    {"minAchv": 98.0, "factor": 20.3, "title": "sp"},
    {"minAchv": 97.0, "factor": 20, "title": "s"},
    {"minAchv": 94.0, "factor": 16.8, "title": "aaa"},
    {"minAchv": 90.0, "factor": 15.2, "title": "aa"},
    {"minAchv": 80.0, "factor": 13.6, "title": "a"},
    {"minAchv": 75.0, "factor": 12, "title": "bbb"},
    {"minAchv": 70.0, "factor": 11.2, "title": "bb"},
    {"minAchv": 60.0, "factor": 9.6, "title": "b"},
    {"minAchv": 50.0, "factor": 8, "title": "c"},
    {"minAchv": 0.0, "factor": 1, "title": "d"},
]

COMBO_DEFINITIONS = ['', 'fc', 'fcp', 'ap', 'app']
SYNC_DEFINITIONS = ['', 'fs', 'fsp', 'fsd', 'fsdp']

COLORS = [Fore.GREEN, Fore.YELLOW, Fore.RED, Fore.MAGENTA, Fore.WHITE]

# get song data from database
mydb = mysql.connector.connect(
    host=db_host, user=db_user, password=db_password, database=db_database
)

mycursor = mydb.cursor()
mycursor.execute(
    '''
SELECT songId, title, chartId, difficulty, comboStatus, deluxscoreMax, syncStatus
FROM mai2_score_best JOIN mai2_static_music
ON (mai2_score_best.level = mai2_static_music.chartId
and mai2_static_music.songId = mai2_score_best.musicId)
GROUP BY songId, title, chartId, difficulty, comboStatus, deluxscoreMax, syncStatus
''')

song_data = mycursor.fetchall()

# get player rating data from database
mycursor.execute(
    f"SELECT ratingList, newRatingList FROM mai2_profile_rating WHERE user = {user_id} AND version = {game_version}"
)

rawRatingLists = mycursor.fetchall()

oldRatingList = json.loads(rawRatingLists[0][0])
newRatingList = json.loads(rawRatingLists[0][1])

# print rating list
total_rating = 0

res = {
        "charts":{
        "dx":[],
        "sd":[]
        }
    }

def convert_to_maibot_data(rating_list, isDx = True):
    for i in range(len(rating_list)):
        try:
            song_info = [
                x
                for x in song_data
                if x[0] == rating_list[i]["musicId"] and x[2] == rating_list[i]["level"]
            ][0]
        except IndexError:
            print(f"找不到譜面 {rating_list[i]['musicId']} {rating_list[i]['level']}")
            continue
        
        song_id =  str(song_info[0]) if  use_alt else str(song_info[0]).zfill(5)
        song_name = song_info[1]
        difficulty = song_info[2]
        internal_lv = song_info[3]
        combo_status = COMBO_DEFINITIONS[song_info[4]]
        dx_score = song_info[5]
        sync_status = SYNC_DEFINITIONS[song_info[6]]

        achv = rating_list[i]["achievement"] / 10000
        rate = "d"

        for rank in RANK_DEFINITIONS:
            if achv >= rank["minAchv"]:
                rate = rank["title"]
                break

        level = ""
        type_t = ""
        
        data={
        "id":song_id,"title":song_name,"level_index":difficulty,"ds":internal_lv,
        "achievements":achv,"rate":rate,"fc":combo_status,"level":"","type":"", "dxScore":dx_score,
        "fs":sync_status
        }

        if isDx:
            res["charts"]["dx"].append(data)
        else:
            res["charts"]["sd"].append(data)

    return

convert_to_maibot_data(oldRatingList, False)
convert_to_maibot_data(newRatingList, True)

if use_alt:
    pic, status = local_generate50_alt(res, display_name)
else:
    pic, status = local_generate50(res, display_name)

if is_show:
    pic.show()

if is_save:
    pic.save('./maimai_best_50.png')