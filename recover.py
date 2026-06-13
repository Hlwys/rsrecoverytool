from __future__ import print_function
import os
import sys
import re
import time
import threading
import binascii

hex_patterns = [
    "000a2f032489", #title",
    "000a62a3f043", #title",
    "0034909f70f6", #media",
    "0036909f70f6", #media",
    "0037909f70f6", #media",
    "003707811d70", #media",
    "004907811d70", #media",
    "004c07811d70", #media",
    "001516c8ae55", #models",
    "00330d66e56b", #texture",
    "00046245babb", #wordenc",
    "0004ddd362b7", #wordenc",
    "0004cde16282", #wordenc",
    "0004650456bc", #wordenc",
    "00010de00c5f", #sounds",
    "001034d1b7b8", #config",
    "001234d1b7b8", #config",
    "0012e14fb6af", #config",
    "00180ae38f79", #config",
    "00183d5965ac", #config",
    "001858c1fcdc", #config",
    "001893a36c54", #config",
    "001a58c1fcdc", #config",
    "314159265359", #wholearchive
    "0632e32100",   #"textures5to7",
    "0631f93600",   #"textures8to15",
    "29df679e00",   #"media48to58",
    "29edbf2901",   #"entity20to24",
    "2dec5e1f00",   #"entity10to19",
    "2ded480a01",   #"entity4to8",
    "5e9c595300",   #"maps14to27",
    "8138952900",   #"media28to47",
    "816a8a8e01",   #"entity12to19mem",
    "8384eb9200",   #"textures15to17",
    "a38c6bba00",   #"entity20to24mem",
    "d0fab5f400",   #"entity7",
    "078d67ba",     #"243 245 june2004",
    "1874c632",     #"274 november2004",
    "2c3910d6",     #"324 325 july2005",
    "3cd1cf37",     #"270 november2004",
    "46c2823c",     #"254 september2004",
    "9509ece5",     #"365 377 2006",
    "de5b3345",     #"289 347 2005",
    "e652d358",     #"186 225 beta2004",
    "e8059684",     #"350 363 2006", 
    "ec8aa7b6",     #"349 december2005",
    "08fd540b0002", #"config failsafe",
    "2000636c6f616465722e636c617373", #"loadercab"
    "006c6f616465722e636c617373", #"loaderjarRSC"
    "007369676e2f7369676e6c696e6b2e636c617373", #loaderjarRS2"
]


# Convert to byte patterns without bytes.fromhex(), for Python 2.7 compatibility
patterns = [binascii.unhexlify(p) for p in hex_patterns]

progress = {
    "bytes_scanned": 0,
    "start_time": time.time(),
    "done": False,
    "file_size": 0,
    "file_size_known": True,
}

def resolve_path_or_drive(arg):
    if os.name == "nt":
        if len(arg) == 3 and arg[1] == ":" and (arg[2] == "\\" or arg[2] == "/"):
            arg = arg[:2]
        if len(arg) == 2 and arg[1] == ":":
            return "\\\\.\\{}:".format(arg[0].upper())
    return arg

def report_progress():
    if progress["done"]:
        return
    scanned = progress["bytes_scanned"]
    total = progress["file_size"]
    known = progress.get("file_size_known", True)
    elapsed = time.time() - progress["start_time"]
    if known and total > 0:
        percent = (float(scanned) / float(total)) * 100.0 if total else 0.0
        remaining_seconds = (elapsed / scanned * (total - scanned)) if scanned else 0
        minutes, seconds = divmod(int(remaining_seconds), 60)
        filled = int(percent / 5.0)
        if filled < 0: filled = 0
        if filled > 20: filled = 20
        bar = "#" * filled + "-" * (20 - filled)
        print("[{0}s] [{1}] {2:.2f}% - Scanned {3:.2f} MB - Est. time remaining: {4}m {5}s".format(
            int(elapsed), bar, percent, scanned / (1024.0 * 1024.0), minutes, seconds))
    else:
        print("[{0}s] Scanned {1:.2f} MB (size unknown)".format(int(elapsed), scanned / (1024.0 * 1024.0)))
    t = threading.Timer(30.0, report_progress)
    try:
        t.daemon = True
    except Exception:
        pass
    t.start()

def scan_image(file_path, patterns):
    offsets_found = {binascii.hexlify(pattern).decode('ascii'): [] for pattern in patterns}
    chunk_size = 1024 * 1024
    max_pattern_len = max(len(p) for p in patterns)
    try:
        file_size = os.path.getsize(file_path)
        progress["file_size_known"] = True
    except OSError:
        file_size = 0
        progress["file_size_known"] = False
    progress["file_size"] = file_size
    with open(file_path, 'rb') as f:
        overlap = max_pattern_len - 1
        position = 0
        prev_data = b''
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            data = prev_data + chunk
            for pattern in patterns:
                start = 0
                pattern_hex = binascii.hexlify(pattern).decode('ascii')
                while True:
                    index = data.find(pattern, start)
                    if index == -1:
                        break
                    absolute_offset = position - len(prev_data) + index
                    print("Found pattern {0} at offset 0x{1:012x}".format(pattern_hex, absolute_offset))
                    offsets_found[pattern_hex].append(absolute_offset)
                    start = index + 1
            prev_data = data[-overlap:]
            position += len(chunk)
            progress["bytes_scanned"] = position
    progress["done"] = True
    return offsets_found

def write_output(results, output_path):
    with open(output_path, 'w') as out:
        for pattern, offsets in results.items():
            if offsets:
                out.write("Pattern {0} found at offsets:\n".format(pattern))
                for offset in offsets:
                    out.write("  0x{0:012x}\n".format(offset))
                out.write("\n")


# Constants
MAX_EXTRACT_SIZE = 1024 * 1024  # 1 MB

# === Extraction patterns and rules ===

six_back_patterns = {
    "000a2f032489": "RS2title",
    "000a62a3f043": "RS2title",
    "0034909f70f6": "RS2media",
    "0036909f70f6": "RS2media",
    "0037909f70f6": "RS2media",
    "003707811d70": "RS2media",
    "004907811d70": "RS2media",
    "004c07811d70": "RS2media",
    "001516c8ae55": "RS2models",
    "00330d66e56b": "RS2texture",
    "00046245babb": "RS2wordenc",
    "0004ddd362b7": "RS2wordenc",
    "0004cde16282": "RS2wordenc",
    "0004650456bc": "RS2wordenc",
    "00010de00c5f": "RS2sounds",
    "001034d1b7b8": "RS2config",
    "001234d1b7b8": "RS2config",
    "0012e14fb6af": "RS2config",
    "00180ae38f79": "RS2config",
    "00183d5965ac": "RS2config",
    "001858c1fcdc": "RS2config",
    "001893a36c54": "RS2config",
    "001a58c1fcdc": "RS2config",
    "314159265359": "wholearchive",
}

eight_back_patterns = {
    "0632e32100": "textures5to7",
    "0631f93600": "textures8to15",
    "29df679e00": "media48to58",
    "29edbf2901": "entity20to24",
    "2dec5e1f00": "entity10to19",
    "2ded480a01": "entity4to8",
    "5e9c595300": "maps14to27",
    "8138952900": "media28to47",
    "816a8a8e01": "entitymem12to19",
    "8384eb9200": "textures15to17",
    "a38c6bba00": "entitymem20to24",
    "d0fab5f400": "entity7",
}

config_failsafe = {
    "08fd540b0002": "RS2config",
}

crc_patterns = {
    "078d67ba": "243_245_june2004",
    "1874c632": "274_nov2004",
    "2c3910d6": "324_325_july2005",
    "3cd1cf37": "270_nov2004",
    "46c2823c": "254_sept2004",
    "9509ece5": "365_377_2006",
    "de5b3345": "289_347_2005",
    "e652d358": "186_225_beta2004",
    "e8059684": "350_363_2006",
    "ec8aa7b6": "349_dec2005",
}

loader_patterns = {
    "2000636c6f616465722e636c617373": "loader_cab",
    "006c6f616465722e636c617373": "loader_jar",
    "007369676e2f7369676e6c696e6b2e636c617373": "loader_jar",
}

crc_map = {
    "dc058ad7": "crc20031202confNEW",
    "538e362e": "crc186conf",
    "0594dfa2": "crc194conf",
    "b8631530": "crc204conf",
    "9bede11f": "crc215conf",
    "8735d0d9": "crc216conf",
    "c89e323b": "crc217conf",
    "fc92443a": "crc218conf",
    "350ae405": "crc219conf",
    "03ccd61b": "crc222conf",
    "fc32b40f": "crc224conf",
    "ab100845": "crc225conf",
    "12006c4a": "crc234confNEW",
    "0e47c4c4": "crc237confNEW",
    "5fa26512": "crc244conf",
    "3e413fcb": "crc245aconf",
    "31cf9007": "crc245bconf",
    "0c56450a": "crc249confNEW",
    "2f9e95c6": "crc252confNEW",
    "0684d258": "crc253confNEW",
    "29b0d321": "crc254conf",
    "91f26fbf": "crc257confNEW",
    "2bba6b63": "crc260confNEW",
    "248db1e8": "crc270conf",
    "2ed494cd": "crc274conf",
    "fa97bf13": "crc282confNEW",
    "fce7f1b6": "crc289conf",
    "632ec81d": "crc291conf",
    "01a84a66": "crc294confNEW",
    "949c9e5a": "crc295conf",
    "ad3fdbed": "crc297confNEW",
    "b508f498": "crc298conf",
    "3276b47f": "crc299conf",
    "af6801a7": "crc300confNEW",
    "5ff69069": "crc303conf",
    "6bdd71a8": "crc304conf",
    "a44b0dbf": "crc306conf",
    "2567f764": "crc307confNEW",
    "dec2416f": "crc308conf",
    "97b0f079": "crc309confNEW",
    "707018ce": "crc311confNEW",
    "83c0ed87": "crc312conf",
    "20c063d0": "crc313confNEW",
    "8b7c3c2b": "crc315confNEW",
    "e96fcefd": "crc316conf",
    "438efd17": "crc317conf",
    "6af1aa47": "crc318conf",
    "8a6dbab2": "crc319conf",
    "6de1f970": "crc320confNEW",
    "fed117ff": "crc321conf",
    "450bdabf": "crc324conf",
    "994db34e": "crc325conf",
    "508f41ed": "crc326conf",
    "24a9b293": "crc327conf",
    "c338bd98": "crc328confNEW",
    "87c905d2": "crc329confNEW",
    "0c023268": "crc330conf",
    "82ae0d4a": "crc332conf",
    "35a6fb7e": "crc333conf",
    "80a09bfe": "crc334conf",
    "228e894d": "crc336conf",
    "3d8b21f6": "crc338conf",
    "c076b67a": "crc339conf",
    "53e967f7": "crc340conf",
    "fa6cadde": "crc341conf",
    "b64bbbf2": "crc342conf",
    "bb97c996": "crc343conf",
    "bc9d3258": "crc344conf",
    "e4b42786": "crc345conf",
    "76d4c217": "crc346conf",
    "aa54c948": "crc347conf",
    "7b273c06": "crc348confNEW",
    "41cbf853": "crc349conf",
    "d440bb01": "crc350conf",
    "240dcb04": "crc351conf",
    "5cdc7247": "crc353confNEW",
    "1c3dd621": "crc354confNEW",
    "17474ccd": "crc355conf",
    "9c830f2d": "crc356conf",
    "c2de0fa0": "crc357conf",
    "8f06f035": "crc358conf",
    "9a1c5053": "crc359conf",
    "298ca4ed": "crc360confNEW",
    "982d0d1e": "crc362conf",
    "16170922": "crc363conf",
    "f87d0121": "crc364confNEW",
    "966b4bbc": "crc365conf",
    "b83913e5": "crc366conf",
    "86cd43d9": "crc367conf",
    "e2c0923a": "crc368conf",
    "da33e79a": "crc369conf",
    "bf661330": "crc370confNEW",
    "31950326": "crc371conf",
    "f92af21e": "crc372conf",
    "bca4fe9c": "crc373conf",
    "1ba91ce3": "crc374conf",
    "16cf99d8": "crc375confNEW",
    "64b79bc3": "crc376conf",
    "b852634c": "crc377conf",
}

real_crc_set = {
    "886f289d",
    "8f9e2b87",
    "9327049f",
    "982e83fb",
    "9de32634",
    "e3f03995",
    "f49dc890",
    "00cc5ca2",
    "0e9ea79a",
    "1e87d494",
    "2072855c",
    "2226df9b",
    "368f1792",
    "658a091a",
    "69661c9a",
    "6b686cdb",
    "7372633c",
    "343445df",
}

# Manual overrides that apply to any extraction whose default label is RS2config
manual_rs2config_headers = {
    "019d59019d59": "RS2config186",
    "01c3b701c3b7": "RS2config194",
    "01d7cd01d7cd": "RS2config204",
    "01e8ac01e8ac": "RS2config215",
    "01f68c01f68c": "RS2config217",
    "01f82c01f82c": "RS2config218",
    "0200b20200b2": "RS2config222",
    "0200fc0200fc": "RS2config224",
    "020752020752": "RS2config225",
    "020c67020c67": "RS2config240",
    "020e08020e08": "RS2config243",
    "020dc3020dc3": "RS2config244",
    "021738021738": "RS2config245.1",
    "021ebf021ebf": "RS2config245.2",
    "024edf024edf": "RS2config254",
    "026f59026f59": "RS2config260",
    "02adc502adc5": "RS2config270",
    "02c42a02c42a": "RS2config274",
    "02f4c102f4c1": "RS2config280",
    "0312ed0312ed": "RS2config289",
    "032812032812": "RS2config290",
    "033677033677": "RS2config291",
    "035254035254": "RS2config295",
    "037789037789": "RS2config299",
    "038cde038cde": "RS2config303",
    "03a4bd03a4bd": "RS2config304",
    "03b41103b411": "RS2config306",
    "03d89003d890": "RS2config308",
    "045102045102": "RS2config316",
    "045be6045be6": "RS2config317",
    "0468b50468b5": "RS2config318",
    "047a02047a02": "RS2config319",
    "047ed9047ed9": "RS2config321",
    "04f90a04f90a": "RS2config325",
    "050519050519": "RS2config326",
    "051a32051a32": "RS2config327",
    "0545a90545a9": "RS2config330",
    "05555e05555e": "RS2config332",
    "055a9e055a9e": "RS2config333",
    "055a70055a70": "RS2config334",
    "0567b40567b4": "RS2config336",
    "059284059284": "RS2config337",
    "0592f10592f1": "RS2config338",
    "0596d20596d2": "RS2config339",
    "05af5905af59": "RS2config340",
    "05db8205db82": "RS2config343",
    "05e94f05e94f": "RS2config345",
    "05f9fa05f9fa": "RS2config346",
    "060d2b060d2b": "RS2config347",
    "062f57062f57": "RS2config349",
    "063bf6063bf6": "RS2config350",
    "06458b06458b": "RS2config351",
    "0669f20669f2": "RS2config356",
    "0665af0665af": "RS2config357",
    "06aabe06aabe": "RS2config362",
    "06b90306b903": "RS2config363",
    "072478072478": "RS2config365",
    "07440a07440a": "RS2config367",
    "0793a20793a2": "RS2config368",
    "079fa4079fa4": "RS2config369",
    "07e45707e457": "RS2config371or372",
    "07fb8107fb81": "RS2config373",
    "07fd1007fd10": "RS2config374",
    "0817e60817e6": "RS2config376",
    "0825ea0825ea": "RS2config377",
}

# Manual overrides for label naming by pattern and first 6 bytes (12 hex chars)
manual_extracts = {
    "314159265359": {
        "0151f4004306": "config18",
        "018a8a004d49": "config26",
        "018ce5004ddd": "config28",
        "0194ea004f8f": "config29",
        "01a5200051de": "config31",
        "01b389005496": "config32",
        "01b3950054a2": "config33",
        "01c05c005849": "config34",
        "023cbc008827": "config37",
        "023eb10088df": "config38",
        "0241e4008a50": "config41",
        "0242ec008ad6": "config42",
        "024385008b3a": "config44",
        "02b33b009bdb": "config46",
        "01976e007fc4": "config48",
        "01b38c008728": "config49",
        "01c19f008c6b": "config50",
        "01c25d008ca5": "config51",
        "01e15f00938e": "config55",
        "01e8d400958c": "config56",
        "01f9d5009922": "config57",
        "01ffb0009a23": "config58",
        "020885009c5a": "config59",
        "021711009f51": "config60or61",
        "02405700a90c": "config63",
        "025cf200b213": "config64",
        "025ff900b30e": "config65",
        "026f4600b6b6": "config66",
        "027f6100ba02": "config67",
        "029e6d00c1aa": "config68",
        "029e6b00c18a": "config69",
        "029ec300c1bc": "config70",
        "029ef200c1bd": "config71",
        "02fecb00d87b": "config72",
        "0331cd00e208": "config73",
        "03663200ec4e": "config74",
        "03883000f4a4": "config75",
        "03d06f010511": "config77",
        "041b7d011859": "config80",
        "0395e600e2f9": "config81",
        "03974500e3ab": "config82",
        "039b6c00e497": "config83",
        "039e7f00e5b3": "config84",
        "039ee900e5bd": "config85",

        "008815004169": "filter1",
        "005cea003c0b": "filter2",
        "016470003b34": "jagex",
        "006274001378": "jagex(3)",

        "03549301bc7f": "land28",
        "037d6601d3b6": "land29or30",
        "0377bf01cfb8": "land31",
        "03766501cec7": "land33",
        "0376d601cf27": "land34",
        "0376db01cf08": "land35",
        "03ad0301ee89": "land36or37",
        "03b43a01f2b6": "land38",
        "03b43e01f2c9": "land39",
        "03b44701f2d0": "land40",
        "03b28101f84f": "land41",
        "03b66801fb83": "land42",
        "03b6a701fbb4": "land43",
        "03c14402019d": "land46",
        "03c37e020313": "land47",
        "03c4a50203c2": "land48",
        "03c57b020426": "land49",
        "03c57b020470": "land50",
        "03df4d0211d3": "land51",
        "03d39a020c12": "land52",
        "03cbb70209f2": "land53or54",
        "03d80a020fa1": "land55",
        "03d840020ff1": "land56",
        "03d8ad020fee": "land57",
        "03df29021422": "land58",
        "040a09022b81": "land59",
        "040a01022ba4": "land60or61",
        "040a9d022c29": "land62or63",

        "013c41007296": "maps28",
        "017bf8008851": "maps29",
        "017bf9008822": "maps30",
        "0178fa008618": "maps31",
        "0177130085d8": "maps33",
        "017754008600": "maps34",
        "01778500860c": "maps35",
        "01828e008972": "maps36",
        "0184fc008aa6": "maps37",
        "018faf008f58": "maps38",
        "018fb7008f60": "maps39",
        "018fb9008f5a": "maps40",
        "0141210076b6": "maps41",
        "01465d007969": "maps42",
        "014690007997": "maps43",
        "017917007d0e": "maps46",
        "017afd007e4d": "maps47",
        "017b40007e70": "maps48",
        "017eff007fdf": "maps49",
        "017e2e007f95": "maps50",
        "018834008460": "maps51",
        "0187ad008459": "maps52",
        "017858007dcf": "maps53or54",
        "17b28f0084d7": "maps55",
        "17d728008524": "maps56",
        "17d7300085a4": "maps57",
        "18230c0087fe": "maps58",
        "18beb700906f": "maps59",
        "18e3470090f3": "maps60or61",
        "18e57900930b": "maps62",
        "18e5790092f7": "maps63",

        "05892000a811": "media12",
        "06b83c00ca94": "media17",
        "06b83c00cb5c": "media18",
        "06b83c00cd97": "media19",
        "06b83c00cdc6": "media20",
        "06b83c00d0c3": "media21",
        "06b83c00ce3d": "media22",
        "06c6aa00d423": "media24",
        "0705c600d946": "media26",
        "0705c600cbf7": "media27",

        "06b2a8013443": "models6",
        "06bb45013636": "models7",
        "02cd6400d228": "models10",
        "02ce3400d280": "models11",
        "02d1ac00d3aa": "models12(1)",
        "02d27800d3de": "models12(2)",
        "02fdd700e087": "models13",
        "030d5a00e48b": "models14",
        "030ee200e539": "models15",
        "032b5e00ee4a": "models16",
        "033f6a00f1c0": "models17",
        "035f0600fe8f": "models18",
        "0569e601bb34": "models20",
        "06109901ffcf": "models22",
        "06a8710233fe": "models23",
        "06d50002378d": "models24(1)",
        "06bf8f023ab6": "models24(2)",
        "09331b02fba6": "models25",
        "09399502fd9d": "models26",
        "0affce03b0f9": "models27",
        "0b0b6003b3d1": "models28",
        "0c91d7043582": "models29or30",
        "0d1a31045e86": "models32",
        "0d4207046062": "models33or34",
        "0d5869046765": "models35",
        "0d61db046c18": "models36",

        "00456b002cee": "land30mem",
        "0053470035b5": "land31mem",
        "0074d000487f": "land33mem",
        "0082470050cb": "land34mem",
        "00acc70069ca": "land36mem",
        "00d4cf007eb0": "land37mem",
        "00e19e008673": "land38mem",
        "01c8a40107e9": "land49mem",
        "01c8a40107e9": "land50mem",
        "02e42b01bbc7": "land53mem",
        "0304f101cf7b": "land54mem",
        "033f5001f221": "land55mem",
        "039367022414": "land57mem",        
        "03939d022421": "land58mem",
        "039dc8022a67": "land59mem",
        "039dd8022aa9": "land60mem",
        "03e467025677": "land61mem",
        "03ee58025c35": "land62or63mem",

        "0048af001dff": "maps29or30mem",
        "00521d0022b3": "maps31mem",
        "0067ed0029ce": "maps33mem",
        "007087002d21": "maps34mem",
        "009fa7003cb7": "maps35mem",
        "00a394003eb3": "maps36mem",
        "00c48f004a1c": "maps37mem",
        "00dca3005408": "maps38mem",
        "00f213006127": "maps46mem",
        "011fa2007474": "maps49mem",
        "011f70007433": "maps50mem",
        "01b62e00b551": "maps53mem",
        "01c83f00bdb1": "maps54mem",
        "17ddc500c946": "maps55mem",
        "190e0800da45": "maps57mem",
        "19327100da3f": "maps58mem",
        "197e1000dcf8": "maps59mem",
        "197e1000dcf8": "maps60mem",
        "1a644b00e7af": "maps61mem",
        "1a88ba00e853": "maps62or63mem",

        "029dcf01bf0a": "sounds1(1)mem",
        "029dcf01bec1": "sounds1(2)mem",

        # RS2interface overrides
        "02c286009e07": "RS2interface186",
        "03385800b9ee": "RS2interface194",
        "03f01f00e753": "RS2interface204",
        "0447af00f92c": "RS2interface215",
        "0448d600f953": "RS2interface216or217",
        "0457a900fcc5": "RS2interface218or219",
        "0487e0010e6e": "RS2interface222",
        "0489ca010f45": "RS2interface224",
        "048b2d010fbc": "RS2interface225",
        "04f2b3012546": "RS2interface243",
        "051b67012d3b": "RS2interface244",
        "052cb8013297": "RS2interface245.1",
        "0556090132e6": "RS2interface245.2",
        "0579ac0132dd": "RS2interface254",
        "068edb01783a": "RS2interface270",
        "0714340191ed": "RS2interface274",
        "07a62b01b62c": "RS2interface289",
        "07d47801c301": "RS2interface291",
        "07eb1a01cae3": "RS2interface295",
        "07f32701cd6b": "RS2interface299",
        "08150c01d581": "RS2interface303",
        "0835a801dd28": "RS2interface304",
        "083a4801deec": "RS2interface306",
        "089d4b01f2f6": "RS2interface308",
        "08fba50202b7": "RS2interface316",
        "08fbe8020283": "RS2interface317",
        "090fea020afd": "RS2interface318",
        "091901020caf": "RS2interface319",
        "091b00020bd7": "RS2interface321",
        "0923b5020fe6": "RS2interface324",
        "092015020eab": "RS2interface325",
        "0945e502195b": "RS2interface326",
        "0948d4021a4a": "RS2interface327",
        "098744022cd5": "RS2interface330",
        "098ebb022c72": "RS2interface332",
        "099239022dc6": "RS2interface333",
        "0993bd022f29": "RS2interface334",
        "09e07702406c": "RS2interface336",
        "09e4dd024397": "RS2interface339",
        "09f70f0246e9": "RS2interface340",
        "0a0d82024e93": "RS2interface343",
        "0a24670253a1": "RS2interface345",
        "0a337a025b9f": "RS2interface346",
        "0a62af02693b": "RS2interface347",
        "0a6a7a026c69": "RS2interface349",
        "0a8fa1027682": "RS2interface350",
        "0a935202777e": "RS2interface351",
        "0a9455027814": "RS2interface355",
        "0b6f7802a0d2": "RS2interface356",
        "0b71e202a24e": "RS2interface357",
        "0bbfae02ba87": "RS2interface362",
        "0bc3a702bd5e": "RS2interface363",
        "0bf7ee02cf7e": "RS2interface365",
        "0c044102d393": "RS2interface367",
        "0c0ee102d724": "RS2interface368",
        "0c143402d96d": "RS2interface369",
        "0c155902d93e": "RS2interface371or372",
        "0c251602dda8": "RS2interface373or374",
        "0c245802dd91": "RS2interface376",
        "0c0f6002d57d": "RS2interface377",

        # RS2versionlist overrides
        "00ca6700692c": "RS2versionlist243",
        "00ca8300694d": "RS2versionlist244",
        "00cdfe006b3f": "RS2versionlist245.1",
        "00d195006ce3": "RS2versionlist245.2",
        "00e11d007433": "RS2versionlist254",
        "00fb44008272": "RS2versionlist270",
        "0103cb0086c6": "RS2versionlist274",
        "011ccb00928f": "RS2versionlist289",
        "012b400097bb": "RS2versionlist291",
        "0134e7009cdd": "RS2versionlist295",
        "013f7800a2f2": "RS2versionlist299",
        "01519d00ab23": "RS2versionlist304",
        "0156be00ad6e": "RS2versionlist306",
        "0169ce00b565": "RS2versionlist308",
        "0172b500b8fb": "RS2versionlist311",
        "01938000ca17": "RS2versionlist316",
        "0198ea00cc75": "RS2versionlist317",
        "01a22200ceeb": "RS2versionlist318",
        "01a50200cf8f": "RS2versionlist319",
        "01a63e00d01e": "RS2versionlist321",
        "01bb9500dd92": "RS2versionlist325",
        "01c55100e326": "RS2versionlist326",
        "01cc6f00e6c9": "RS2versionlist327",
        "01d99300ec98": "RS2versionlist330",
        "01dd8500eebd": "RS2versionlist332",
        "01dee400ef37": "RS2versionlist333",
        "01e8a100f1a5": "RS2versionlist336",
        "01f41300f73d": "RS2versionlist337",
        "01f48200f743": "RS2versionlist338",
        "01f59800f80e": "RS2versionlist339",
        "01fa9b00fa73": "RS2versionlist340",
        "020b72010090": "RS2versionlist343",
        "020e5c010187": "RS2versionlist345",
        "021275010393": "RS2versionlist346",
        "0217c201065d": "RS2versionlist347",
        "022004010997": "RS2versionlist348",
        "0227ec010d21": "RS2versionlist349",
        "022e6d01109f": "RS2versionlist350",
        "0231dc0111ff": "RS2versionlist351",
        "023e490116d1": "RS2versionlist355",
        "0241230118a6": "RS2versionlist356",
        "02469d011add": "RS2versionlist357",
        "0260df0127a9": "RS2versionlist362",
        "0265d9012a19": "RS2versionlist363",
        "02be67014f7f": "RS2versionlist365",
        "02c5b30152fe": "RS2versionlist367",
        "02d05c01554c": "RS2versionlist368",
        "02d7c6015762": "RS2versionlist369",
        "02e2ff015a5b": "RS2versionlist371or372",
        "02ed80015e18": "RS2versionlist373",
        "02f2f70160f4": "RS2versionlist374",
        "02f618016220": "RS2versionlist376",
        "02fbac0164e0": "RS2versionlist377",
    },

    "2ded480a01": {
        "041eb0041eb0": "entity4",
        "0426e30426e3": "entity5",
        "0425bf0425bf": "entity6",
        "04a65c04a65c": "entity7",
        "04d69304d693": "entity8",
    },

    "2dec5e1f00": {
        "043900043900": "entity10",
        "040198040198": "entity11",
        "039b95039b95": "entity12",
        "039ba5039ba5": "entity13",
        "039b87039b87": "entity14or15",
        "039b1c039b1c": "entity16or17",
        "039edd039edd": "entity18",
        "03a29803a298": "entity19",
    },

    "29edbf2901": {
        "03af9103af91": "entity20",
        "03b2ce03b2ce": "entity21",
        "03b2ac03b2ac": "entity22",
        "03b31903b319": "entity23",
        "03baed03baed": "entity24",
    },

    "5e9c595300": {
        "01d79701d797": "maps14",
        "01f43f01f43f": "maps19",
        "01f4a601f4a6": "maps20",
        "01f9ec01f9ec": "maps21",
        "01f72901f729": "maps22",
        "03beca03beca": "maps24",
        "03d2d803d2d8": "maps25",
        "03d37103d371": "maps27",
    },

    "8138952900": {
        "00a8fd00a8fd": "media28or29",
        "00b23700b237": "media30",
        "00b38d00b38d": "media31",
        "00b67300b673": "media32",
        "00bb2f00bb2f": "media33",
        "00be3b00be3b": "media34",
        "00bf3800bf38": "media35",
        "00bf8800bf88": "media36",
        "00bfea00bfea": "media37",
        "00c41900c419": "media38",
        "00c9b000c9b0": "media39",
        "00df5000df50": "media40",
        "00e11e00e11e": "media41",
        "00ed3e00ed3e": "media43",
        "00f43e00f43e": "media44",
        "00f7e900f7e9": "media45",
        "011d56011d56": "media46",
        "012a76012a76": "media47",
    },

    "29df679e00": {
        "01370b01370b": "media48",
        "014446014446": "media49",
        "015e74015e74": "media50or51",
        "01768e01768e": "media52or53",
        "018101018101": "media54or55",
        "018131018131": "media56or57",
        "0181a30181a3": "media58",
    },

    "0632e32100": {
        "00fcf300fcf3": "textures5",
        "0100f80100f8": "textures6",
    },

    "0631f93600": {
        "00f23e00f23e": "textures7",
        "00a9c600a9c6": "textures8",
        "00a50100a501": "textures9",
        "00aa7b00aa7b": "textures10or11",
        "00c48a00c48a": "textures12",
        "00e10300e103": "textures13",
        "00ea2e00ea2e": "textures14",
        "00ed8300ed83": "textures15(1)",
    },

    "8384eb9200": {
        "00ed8300ed83": "textures15(2)",
        "00f60600f606": "textures16",
        "00f8bf00f8bf": "textures17",
    },

    "816a8a8e01": {
        "00671c00671c": "entity12to14mem",
        "006f70006f70": "entity18or19mem",
    },

    "a38c6bba00": {
        "00b62600b626": "entity20to22mem",
        "00bc4e00bc4e": "entity23or24mem",
    },

    "00010de00c5f": {
        "003e1a003e1a": "RS2sounds204",
        "0043dd0043dd": "RS2sounds215",
        "0047f40047f4": "RS2sounds216or217",
        "00499b00499b": "RS2sounds218",
        "0055e30055e3": "RS2sounds222",
        "005900005900": "RS2sounds224",
        "00592d00592d": "RS2sounds225",
        "007179007179": "RS2sounds243",
        "00763c00763c": "RS2sounds244",
        "007c93007c93": "RS2sounds245.1",
        "00850e00850e": "RS2sounds245.2",
        "009e28009e28": "RS2sounds254",
        "00bf7c00bf7c": "RS2sounds270",
        "00e0c700e0c7": "RS2sounds274",
        "00f15600f156": "RS2sounds289",
        "0100f10100f1": "RS2sounds291",
        "011345011345": "RS2sounds295",
        "012bfa012bfa": "RS2sounds299",
        "01360c01360c": "RS2sounds303",
        "013852013852": "RS2sounds304",
        "01423f01423f": "RS2sounds306",
        "014521014521": "RS2sounds308",
        "015217015217": "RS2sounds311",
        "0171ab0171ab": "RS2sounds316",
        "01750d01750d": "RS2sounds317",
        "01c9dc01c9dc": "RS2sounds318",
        "01d70401d704": "RS2sounds319",
        "01dffd01dffd": "RS2sounds321",
        "01edf501edf5": "RS2sounds325",
        "01f6f301f6f3": "RS2sounds326",
        "02042d02042d": "RS2sounds327",
        "020b8d020b8d": "RS2sounds330",
        "020efa020efa": "RS2sounds332or333",
        "0218ff0218ff": "RS2sounds336",
        "021fe7021fe7": "RS2sounds337",
        "0221a70221a7": "RS2sounds338",
        "0227d20227d2": "RS2sounds339",
        "0232ba0232ba": "RS2sounds340",
        "023b47023b47": "RS2sounds341to343",
        "023ebe023ebe": "RS2sounds344or345",
        "02458a02458a": "RS2sounds346",
        "025b04025b04": "RS2sounds347",
        "02864a02864a": "RS2sounds349",
        "02904c02904c": "RS2sounds350",
        "029617029617": "RS2sounds351",
        "02b2d802b2d8": "RS2sounds355",
        "02ba2b02ba2b": "RS2sounds356",
        "02d31b02d31b": "RS2sounds357",
        "03073f03073f": "RS2sounds362",
        "031074031074": "RS2sounds363",
        "034429034429": "RS2sounds365",
        "0346f20346f2": "RS2sounds367",
        "034a9d034a9d": "RS2sounds368",
        "034d46034d46": "RS2sounds369",
        "035861035861": "RS2sounds371or372",
        "035bbd035bbd": "RS2sounds373",
        "035c99035c99": "RS2sounds374",
        "035d88035d88": "RS2sounds376",
        "0369d20369d2": "RS2sounds377",
    },
}



def parse_output_file(path):
    pattern_offset_map = {}
    with open(path, "r") as f:
        current_pattern = None
        for line in f:
            line = line.strip()
            match = re.match(r"Pattern ([0-9a-fA-F]+) found at offsets:", line)
            if match:
                current_pattern = match.group(1).lower()
                pattern_offset_map[current_pattern] = []
            elif line.startswith("0x") and current_pattern:
                pattern_offset_map[current_pattern].append(int(line, 16))
    return pattern_offset_map

def read_at(f, offset, size):
    f.seek(offset)
    return f.read(size)

def extract_files(image_path, pattern_offsets, out_dir="extracted"):
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(image_path, "rb") as f:
        for pattern, offsets in pattern_offsets.items():
            if pattern in six_back_patterns:
                label, backtrack, mode = six_back_patterns[pattern], 6, "length_from_offset"
            elif pattern in eight_back_patterns:
                label, backtrack, mode = eight_back_patterns[pattern], 8, "length_from_offset"
            elif pattern in config_failsafe:
                label, backtrack, mode = config_failsafe[pattern], 38, "length_from_offset"
            elif pattern in crc_patterns:
                label, backtrack, mode = crc_patterns[pattern], 4, "crc_logic"
            elif pattern in loader_patterns:
                label, mode = loader_patterns[pattern], "loader_extract"
                if pattern == "2000636c6f616465722e636c617373":
                    backtrack = 111
                elif pattern in ("006c6f616465722e636c617373", "007369676e2f7369676e6c696e6b2e636c617373"):
                    backtrack = 29
                else:
                    print("Unknown loader pattern {0}, skipping...".format(pattern)); continue
            else:
                print("Unknown pattern {0}, skipping...".format(pattern)); continue

            for offset in offsets:
                extract_start = offset - backtrack
                if extract_start < 0:
                    print("Skipping 0x{0:x} (start before file)".format(offset)); continue

                if mode == "loader_extract":
                    header = read_at(f, extract_start, 10)
                    if pattern == "2000636c6f616465722e636c617373" and not header.startswith(b"MSCF"):
                        print("Skipping 0x{0:x} (loader_cab missing MSCF header)".format(offset)); continue
                    if pattern in ("006c6f616465722e636c617373", "007369676e2f7369676e6c696e6b2e636c617373") and not header.startswith(b"PK\x03\x04\x14\x00\x08\x00\x08\x00"):
                        print("Skipping 0x{0:x} (loader_jar missing PK ZIP header)".format(offset)); continue
                    extract = read_at(f, extract_start, 20480)
                    if pattern == "2000636c6f616465722e636c617373":
                        date_backtrack, ext = 4, "cab"
                    else:
                        date_backtrack, ext = 17, "jar"
                    date_offset = offset - date_backtrack
                    if date_offset < 0:
                        print("Skipping 0x{0:x} (date offset before file)".format(offset)); continue
                    date_bytes = read_at(f, date_offset, 2)
                    if len(date_bytes) != 2:
                        print("Skipping 0x{0:x} (could not read 2 date bytes)".format(offset)); continue
                    date_val = ord(date_bytes[0:1]) + (ord(date_bytes[1:2]) << 8)
                    year = (date_val >> 9) + 1980; month = (date_val >> 5) & 0xF; day = date_val & 0x1F
                    label2 = "loader_{0:04d}_{1:02d}_{2:02d}".format(year, month, day)
                    target_dir = os.path.join(out_dir, "loaders") if year >= 2004 else out_dir
                    if not os.path.isdir(target_dir): os.makedirs(target_dir)
                    out_filename = "{0}_{1:012x}.{2}".format(label2, extract_start, ext)
                    with open(os.path.join(target_dir, out_filename), "wb") as out_file: out_file.write(extract)
                    print("Extracted {0} ({1} bytes)".format(out_filename, len(extract)))
                    continue

                if pattern == "314159265359":
                    prefix_bytes = read_at(f, extract_start - 4, 4)
                    if prefix_bytes == b"\x0d\xe0\x0c\x5f":
                        print("Skipping 0x{0:x} (matches exclusion prefix 0DE00C5F)".format(offset)); continue

                if mode == "length_from_offset":
                    head = read_at(f, extract_start, 6)
                    if len(head) < 6:
                        print("Skipping 0x{0:x} (too short for length read)".format(offset)); continue
                    hv = [ord(head[i:i+1]) for i in range(6)]
                    if pattern != "314159265359" and head[:3] != head[3:6]:
                        print("Skipping 0x{0:x} (prefix repeat check failed)".format(offset)); continue
                    length = (hv[3] << 16) + (hv[4] << 8) + hv[5]
                    total_length = 6 + length
                    if total_length > MAX_EXTRACT_SIZE:
                        print("Skipping 0x{0:x} (exceeds max size: {1} bytes)".format(offset, total_length)); continue
                    extract = read_at(f, extract_start, total_length)
                    header6_hex = binascii.hexlify(extract[:6]).decode('ascii')
                    manual_label = manual_extracts.get(pattern, {}).get(header6_hex)
                    if manual_label is None and label == "RS2config":
                        manual_label = manual_rs2config_headers.get(header6_hex)
                    if pattern == "314159265359" and not manual_label:
                        if len(extract) <= 54:
                            print("Skipping 0x{0:x} (too short for all checks)".format(offset)); continue
                        ev = [ord(extract[i:i+1]) for i in range(len(extract))]
                        if ev[19] not in (0x7F, 0xFF):
                            print("Skipping 0x{0:x} (byte 19 != 7F or FF)".format(offset)); continue
                        if ev[0] >= 0x1B:
                            print("Skipping 0x{0:x} (byte 0 >= 1B)".format(offset)); continue
                        if ev[2] == 0x00:
                            print("Skipping 0x{0:x} (byte 2 == 00)".format(offset)); continue
                        if not (ev[53] == 0xE0 or ev[33] == 0xBF):
                            print("Skipping 0x{0:x} (byte 53 != E0 and byte 33 != BF)".format(offset)); continue
                    out_filename = "{0}_{1:012x}.bin".format(manual_label or label, extract_start)
                elif mode == "crc_logic":
                    extract = read_at(f, extract_start, 40)
                    if len(extract) < 40:
                        print("Skipping 0x{0:x} (incomplete fixed 40)".format(offset)); continue
                    first4 = binascii.hexlify(extract[:4]).decode('ascii')
                    if first4 in crc_map:
                        out_filename = "{0}_{1:012x}.bin".format(crc_map[first4], extract_start)
                    else:
                        X = 1234
                        for i in range(0, 36, 4):
                            block_val = int(binascii.hexlify(extract[i:i+4]), 16)
                            X = X * 2 + block_val
                            X = ((X + (1 << 31)) % (1 << 32)) - (1 << 31)
                        check_raw = int(binascii.hexlify(extract[36:40]), 16)
                        check_val = check_raw - (1 << 32) if check_raw >= (1 << 31) else check_raw
                        crc_check = binascii.hexlify(extract[24:28]).decode('ascii')
                        if X == check_val or crc_check in real_crc_set:
                            out_filename = "crc real {0}_{1:012x}.bin".format(label, extract_start)
                        else:
                            print("Skipping 0x{0:x} (crc false)".format(offset)); continue
                else:
                    continue
                with open(os.path.join(out_dir, out_filename), "wb") as out_file: out_file.write(extract)
                print("Extracted {0} ({1} bytes)".format(out_filename, len(extract)))

def is_txt_file(path):
    return path.lower().endswith(".txt")

def is_raw_drive_arg(arg):
    if len(arg) == 2 and arg[1] == ":":
        return True
    if len(arg) == 3 and arg[1] == ":" and (arg[2] == "\\" or arg[2] == "/"):
        return True
    return False

def running_as_admin():
    if os.name != "nt":
        return True
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        # Windows XP may not expose this reliably in all Python builds.
        return None

def print_usage():
    print("Usage:")
    print("  recover_xp.exe <image_file_or_drive_letter> [output_directory]")
    print("  recover_xp.exe <image_file_or_drive_letter> <results.txt> [output_directory]")
    print("  recover_xp.exe <image_file_or_drive_letter> -i results.txt [-o output_directory]")
    print("  recover_xp.exe <image_file_or_drive_letter> --scan-only [-s results.txt]")
    print("  recover_xp.exe <image_file_or_drive_letter> --extract-only -i results.txt [-o output_directory]")
    print("")
    print("Examples:")
    print("  recover_xp.exe disk.img")
    print("  recover_xp.exe F:")
    print("  recover_xp.exe F: output.txt")
    print("  recover_xp.exe F: output.txt recovered_files")
    print("  recover_xp.exe F: -i output.txt -o recovered_files")
    print("  recover_xp.exe --extract-only F: -i output.txt -o recovered_files")

def parse_args(argv):
    # Small hand-rolled parser to keep Python 2.7/Windows XP packaging simple.
    opts = {
        "source_arg": None,
        "out_dir": "extracted",
        "input_txt": None,
        "scan_output_txt": "output.txt",
        "scan_only": False,
        "extract_only": False,
    }
    positional = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help", "/?"):
            opts["help"] = True
            return opts
        elif a == "--scan-only":
            opts["scan_only"] = True
        elif a == "--extract-only":
            opts["extract_only"] = True
        elif a in ("-i", "--input", "--input-results"):
            i += 1
            if i >= len(argv):
                raise ValueError("Missing filename after {0}".format(a))
            opts["input_txt"] = argv[i]
        elif a in ("-o", "--output", "--output-dir"):
            i += 1
            if i >= len(argv):
                raise ValueError("Missing directory after {0}".format(a))
            opts["out_dir"] = argv[i]
        elif a in ("-s", "--scan-output"):
            i += 1
            if i >= len(argv):
                raise ValueError("Missing filename after {0}".format(a))
            opts["scan_output_txt"] = argv[i]
        else:
            positional.append(a)
        i += 1

    # Allow --extract-only F: ... or F: --extract-only ...
    if positional:
        opts["source_arg"] = positional[0]

    # Backwards-compatible positional handling:
    #   recover_xp.exe F: recovered_files
    #   recover_xp.exe F: output.txt
    #   recover_xp.exe F: output.txt recovered_files
    if len(positional) >= 2:
        if is_txt_file(positional[1]):
            opts["input_txt"] = positional[1]
        else:
            opts["out_dir"] = positional[1]
    if len(positional) >= 3:
        opts["out_dir"] = positional[2]
    if len(positional) > 3:
        raise ValueError("Too many positional arguments")

    if opts["scan_only"] and opts["extract_only"]:
        raise ValueError("Use either --scan-only or --extract-only, not both")
    if opts["extract_only"] and not opts["input_txt"]:
        raise ValueError("--extract-only requires -i results.txt")
    if not opts["source_arg"]:
        raise ValueError("Missing image file or drive letter")
    return opts

def main(argv):
    try:
        opts = parse_args(argv)
    except ValueError as e:
        print("Error: {0}".format(e))
        print("")
        print_usage()
        return 1

    if opts.get("help"):
        print_usage()
        return 0

    source_arg = opts["source_arg"]
    out_dir = opts["out_dir"]
    target_path = resolve_path_or_drive(source_arg)

    if os.name == "nt" and is_raw_drive_arg(source_arg):
        admin = running_as_admin()
        if admin is False:
            print("Warning: raw drive access normally requires an Administrator account/console.")
        elif admin is None:
            print("For raw drives, run this from an Administrator account/console.")

    # If an input txt is supplied, skip scanning and extract from it.
    if opts["input_txt"]:
        input_txt = opts["input_txt"]
        if not os.path.isfile(input_txt):
            print("Error: input results file not found: {0}".format(input_txt))
            return 1
        print("Input results file supplied: {0}".format(input_txt))
        print("Skipping scan phase.")
        pattern_offsets = parse_output_file(input_txt)
        print("Starting extraction from {0} to {1} ...".format(target_path, out_dir))
        extract_files(target_path, pattern_offsets, out_dir)
        print("Done.")
        return 0

    output_txt = opts["scan_output_txt"]
    print("Starting scan on {0} ...".format(target_path))
    progress["start_time"] = time.time(); progress["done"] = False; progress["bytes_scanned"] = 0
    report_progress()
    results = scan_image(target_path, patterns)
    write_output(results, output_txt)
    print("Scan complete. Results written to {0}.".format(output_txt))

    if opts["scan_only"]:
        print("Scan-only mode selected. Extraction skipped.")
        return 0

    pattern_offsets = parse_output_file(output_txt)
    print("Starting extraction to {0} ...".format(out_dir))
    extract_files(target_path, pattern_offsets, out_dir)
    print("Done.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
