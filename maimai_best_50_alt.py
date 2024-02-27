import json
from image import DrawText
from typing import List, Optional, Tuple, Union, Dict
from PIL import Image, ImageDraw
from maimai_best_50 import computeRa

# adapted from https://github.com/Yuri-YuzuChaN/maimaiDX
# dx score not supported, rank / plate / logo not supported
pic_dir = './static/mai/pic_alt/'
cover_dir = './static/mai/cover_alt/'
rating_dir = './static/mai/rating/'
logoPath_alt = 'logo.png'
bgPath_alt = 'b40_bg.png'


def mod_string(in_str):
    in_str = in_str.upper()
    in_str = in_str.replace('P', 'p')
    return in_str


class ChartInfoAlt(object):
    def __init__(self, idNum: str, diff: int, tp: str, achievement: float, ra: int, combo: str, rate: str,
                 title: str, ds: float, lv: str, fs: str, dxScore: int):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = computeRa(ds, achievement)
        self.combo = combo
        self.rate = rate
        self.title = title
        self.ds = ds
        self.lv = lv
        self.fs = fs
        self.dxScore = dxScore

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    # ds for internal level
    # ra for track rating
    @classmethod
    def from_json_local(cls, data):
        return cls(
            idNum=data["id"],
            title=data["title"],
            diff=data["level_index"],
            ra=computeRa(data["ds"], data["achievements"]),
            ds=data["ds"],
            rate=data["rate"],
            combo=data["fc"],
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"],
            fs=data["fs"],
            dxScore=data["dxScore"]
        )


class DrawBestAlt:

    def __init__(self, sd_best, dx_best, display_name="YourName"):
        self.user_name = display_name

        self.rating = 0
        self.sdRating = 0
        self.dxRating = 0

        self.sd_best = sd_best
        self.dx_best = dx_best

        for sd in sd_best:
            self.sdRating += computeRa(sd.ds, sd.achievement)
        for dx in dx_best:
            self.dxRating += computeRa(dx.ds, dx.achievement)
        self.rating = self.sdRating + self.dxRating

        # not implemented yet
        self.plate = None

    def _findRaPic(self) -> str:
        if self.rating < 1000:
            num = '01'
        elif self.rating < 2000:
            num = '02'
        elif self.rating < 4000:
            num = '03'
        elif self.rating < 7000:
            num = '04'
        elif self.rating < 10000:
            num = '05'
        elif self.rating < 12000:
            num = '06'
        elif self.rating < 13000:
            num = '07'
        elif self.rating < 14000:
            num = '08'
        elif self.rating < 14500:
            num = '09'
        elif self.rating < 15000:
            num = '10'
        else:
            num = '11'
        return f'UI_CMN_DXRating_{num}.png'

    # currently not implemented
    def _findMatchLevel(self) -> str:
        # if self.addRating <= 10:
        #     num = f'{self.addRating:02d}'
        # else:
        #     num = f'{self.addRating + 1:02d}'
        return f'UI_DNM_DaniPlate_{0:02d}.png'

    def whiledraw(self, data: List[ChartInfoAlt], type_t: bool) -> Image.Image:
        # y为第一排纵向坐标，dy为各排间距
        y = 430 if type_t else 1670
        dy = 170

        TEXT_COLOR = [(255, 255, 255, 255), (255, 255, 255, 255), (255, 255, 255, 255), (255, 255, 255, 255),
                      (103, 20, 141, 255)]
        DXSTAR_DEST = [0, 330, 320, 310, 300, 290]

        for num, info in enumerate(data):
            if num % 5 == 0:
                x = 70
                y += dy if num != 0 else 0
            else:
                x += 416

            # if not found, use default cover
            try:
                cover = Image.open(cover_dir + f'{info.idNum}.png').resize((135, 135))
            except:
                cover = Image.open(cover_dir + '0.png').resize((135, 135))

            info.type = 'DX' if type_t else 'SD'
            version = Image.open(pic_dir + f'UI_RSL_MBase_Parts_{info.type}.png').resize((55, 19))

            rate = Image.open(pic_dir + f'UI_TTR_Rank_{mod_string(info.rate)}.png').resize((95, 44))

            self._im.alpha_composite(self._diff[info.diff], (x, y))
            self._im.alpha_composite(cover, (x + 5, y + 5))
            self._im.alpha_composite(version, (x + 80, y + 141))
            self._im.alpha_composite(rate, (x + 150, y + 98))

            if info.combo != "":
                fc = Image.open(pic_dir + f'UI_MSS_MBase_Icon_{mod_string(info.combo)}.png').resize((45, 45))
                self._im.alpha_composite(fc, (x + 260, y + 98))

            # full sync is not supported yet
            if info.fs != "":
                fs = Image.open(pic_dir + f'UI_MSS_MBase_Icon_{mod_string(info.fs)}.png').resize((45, 45))
                self._im.alpha_composite(fs, (x + 315, y + 98))

            # dx star is not supported yet
            with open("md_cache.json", "r", encoding="utf-8") as f:
                mai = json.load(f)

            try:
                # 根据id和diff获取对应难度的note数量
                dxscore = mai[str(info.idNum)]['dxScore'][info.diff]
            except KeyError:
                if info.dxScore != 0:
                    dxscore = info.dxScore
                else:
                    dxscore = 999

            # dxscore = sum(mai.total_list.by_id(str(info.idNum)).charts[info.diff].notes) * 3
            diff_sum_dx = info.dxScore / dxscore * 100
            dxtype, dxnum = dxScore(diff_sum_dx)

            for _ in range(dxnum):
                self._im.alpha_composite(self.dxstar[dxtype], (x + DXSTAR_DEST[dxnum] + 20 * _, y + 74))

            self._tb.draw(x + 40, y + 148, 20, info.idNum, anchor='mm')
            title = info.title
            if coloumWidth(title) > 18:
                title = changeColumnWidth(title, 17) + '...'
            self._siyuan.draw(x + 155, y + 20, 20, title, TEXT_COLOR[info.diff], anchor='lm')
            p, s = f'{info.achievement:.4f}'.split('.')
            r = self._tb.get_box(p, 32)
            self._tb.draw(x + 155, y + 70, 32, p, TEXT_COLOR[info.diff], anchor='ld')
            self._tb.draw(x + 155 + r[2], y + 68, 22, f'.{s}%', TEXT_COLOR[info.diff], anchor='ld')
            self._tb.draw(x + 340, y + 60, 18, f'{info.dxScore}/{dxscore}', TEXT_COLOR[info.diff], anchor='mm')
            self._tb.draw(x + 155, y + 80, 22, f'{info.ds} -> {info.ra}', TEXT_COLOR[info.diff], anchor='lm')

    def draw(self):

        basic = Image.open(pic_dir + 'b40_score_basic.png')
        advanced = Image.open(pic_dir + 'b40_score_advanced.png')
        expert = Image.open(pic_dir + 'b40_score_expert.png')
        master = Image.open(pic_dir + 'b40_score_master.png')
        remaster = Image.open(pic_dir + 'b40_score_remaster.png')
        logo = Image.open(pic_dir + logoPath_alt).resize((378, 172))
        dx_rating = Image.open(pic_dir + self._findRaPic()).resize((300, 59))
        Name = Image.open(pic_dir + 'Name.png')
        MatchLevel = Image.open(pic_dir + self._findMatchLevel()).resize((134, 55))
        ClassLevel = Image.open(pic_dir + 'UI_FBR_Class_00.png').resize((144, 87))
        rating = Image.open(pic_dir + 'UI_CMN_Shougou_Rainbow.png').resize((454, 50))
        self._diff = [basic, advanced, expert, master, remaster]

        # unsupported yet
        self.dxstar = [Image.open(pic_dir + f'UI_RSL_DXScore_Star_0{_ + 1}.png').resize((20, 20)) for _ in range(3)]

        # backgroud
        self._im = Image.open(pic_dir + bgPath_alt).convert('RGBA')

        self._im.alpha_composite(logo, (5, 130))

        if self.plate:
            plate = Image.open(pic_dir + f'{self.plate}.png').resize((1420, 230))
        else:
            plate = Image.open(pic_dir + 'UI_Plate_409504.png').resize((1420, 230))

        self._im.alpha_composite(plate, (390, 100))
        icon = Image.open(pic_dir + 'UI_Icon_409501.png').resize((214, 214))
        self._im.alpha_composite(icon, (398, 108))
        self._im.alpha_composite(dx_rating, (620, 122))
        Rating = f'{self.rating:05d}'
        for n, i in enumerate(Rating):
            self._im.alpha_composite(Image.open(pic_dir + f'UI_NUM_Drating_{i}.png').resize((28, 34)),
                                     (760 + 23 * n, 137))
        self._im.alpha_composite(Name, (620, 200))
        self._im.alpha_composite(MatchLevel, (935, 205))
        self._im.alpha_composite(ClassLevel, (926, 105))
        self._im.alpha_composite(rating, (620, 275))

        text_im = ImageDraw.Draw(self._im)
        self._meiryo = DrawText(text_im, './static/meiryo.ttc')
        self._siyuan = DrawText(text_im, './static/SourceHanSansSC-Bold.otf')
        self._tb = DrawText(text_im, './static/Torus SemiBold.otf')

        self._siyuan.draw(635, 235, 40, self.user_name, (0, 0, 0, 255), 'lm')
        self._tb.draw(847, 295, 28, f'B35: {self.sdRating} + B15: {self.dxRating} = {self.rating}', (0, 0, 0, 255),
                      'mm', 3, (255, 255, 255, 255))
        self._meiryo.draw(900, 2365, 35, f'Designed by Yuri-YuzuChaN & BlueDeer233  | Generated by ARTEMIS',
                          (103, 20, 141, 255), 'mm', 3, (255, 255, 255, 255))

        self.whiledraw(self.sd_best, True)
        self.whiledraw(self.dx_best, False)

        return self._im.resize((1760, 1920))


def dxScore(dx: int) -> Tuple[int, int]:
    """
    返回值为 `Tuple`： `(星星种类，数量)`
    """
    if dx <= 85:
        result = (0, 0)
    elif dx <= 90:
        result = (0, 1)
    elif dx <= 93:
        result = (0, 2)
    elif dx <= 95:
        result = (1, 3)
    elif dx <= 97:
        result = (1, 4)
    else:
        result = (2, 5)
    return result


def getCharWidth(o) -> int:
    widths = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
        (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
        (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1


def coloumWidth(s: str) -> int:
    res = 0
    for ch in s:
        res += getCharWidth(ord(ch))
    return res


def changeColumnWidth(s: str, len: int) -> str:
    res = 0
    sList = []
    for ch in s:
        res += getCharWidth(ord(ch))
        if res <= len:
            sList.append(ch)
    return ''.join(sList)


def local_generate50_alt(obj, username):
    sd_best = []
    dx_best = []

    dx: List[Dict] = obj["charts"]["dx"]
    sd: List[Dict] = obj["charts"]["sd"]

    for c in sd:
        sd_best.append(ChartInfoAlt.from_json_local(c))
    for c in dx:
        dx_best.append(ChartInfoAlt.from_json_local(c))

    draw_alt = DrawBestAlt(sd_best, dx_best, username)
    res = draw_alt.draw()
    return res, 0
