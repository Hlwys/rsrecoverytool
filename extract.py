import os
import sys
import re

# Constants
MAX_EXTRACT_SIZE = 1024 * 1024  # 1 MB

# === Extraction patterns and rules ===

six_back_patterns = {
    "000a2f032489": "RS2title", "000a62a3f043": "RS2title",
    "0034909f70f6": "RS2media", "0036909f70f6": "RS2media",
    "0037909f70f6": "RS2media", "003707811d70": "RS2media",
    "004907811d70": "RS2media", "004c07811d70": "RS2media",
    "001516c8ae55": "RS2models", "00330d66e56b": "RS2texture",
    "00046245babb": "RS2wordenc", "0004ddd362b7": "RS2wordenc",
    "0004cde16282": "RS2wordenc", "0004650456bc": "RS2wordenc",
    "00010de00c5f": "RS2sounds",
    "001034d1b7b8": "RS2config", "001234d1b7b8": "RS2config",
    "0012e14fb6af": "RS2config", "00180ae38f79": "RS2config",
    "00183d5965ac": "RS2config", "001858c1fcdc": "RS2config",
    "001893a36c54": "RS2config", "001a58c1fcdc": "RS2config",
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

crc_map = {
    "0594dfa2": "crc194conf", "b8631530": "crc204conf", "c89e323b": "crc217conf",
    "fc92443a": "crc218conf", "350ae405": "crc219conf", "03ccd61b": "crc222conf",
    "fc32b40f": "crc224conf", "ab100845": "crc225conf", "12006c4a": "crc234conf",
    "0e47c4c4": "crc237conf", "5fa26512": "crc244conf", "3e413fcb": "crc245conf",
    "0c56450a": "crc249conf", "2f9e95c6": "crc252conf", "0684d258": "crc253conf",
    "29b0d321": "crc254conf", "91f26fbf": "crc257conf", "248db1e8": "crc270conf",
    "2ed494cd": "crc274conf", "fa97bf13": "crc282conf", "fce7f1b6": "crc289conf",
    "632ec81d": "crc291conf", "01a84a66": "crc294conf", "949c9e5a": "crc295conf",
    "ad3fdbed": "crc297conf", "b508f498": "crc298conf", "3276b47f": "crc299conf",
    "af6801a7": "crc300conf", "5ff69069": "crc303conf", "a44b0dbf": "crc306conf",
    "2567f764": "crc307conf", "dec2416f": "crc308conf", "97b0f079": "crc309conf",
    "707018ce": "crc311conf", "83c0ed87": "crc312conf", "20c063d0": "crc313conf",
    "8b7c3c2b": "crc315conf", "e96fcefd": "crc316conf", "438efd17": "crc317conf",
    "6af1aa47": "crc318conf", "fed117ff": "crc321conf", "450bdabf": "crc324conf",
    "994db34e": "crc325conf", "24a9b293": "crc327conf", "c338bd98": "crc328conf",
    "87c905d2": "crc329conf", "0c023268": "crc330conf", "82ae0d4a": "crc332conf",
    "35a6fb7e": "crc333conf", "80a09bfe": "crc334conf", "228e894d": "crc336conf",
    "c076b67a": "crc339conf", "53e967f7": "crc340conf", "fa6cadde": "crc341conf",
    "b64bbbf2": "crc342conf", "bb97c996": "crc343conf", "e4b42786": "crc345conf",
    "76d4c217": "crc346conf", "aa54c948": "crc347conf", "7b273c06": "crc348conf",
    "41cbf853": "crc349conf", "d440bb01": "crc350conf", "5cdc7247": "crc353conf",
    "1c3dd621": "crc354conf", "17474ccd": "crc355conf", "9c830f2d": "crc356conf",
    "c2de0fa0": "crc357conf", "8f06f035": "crc358conf", "9a1c5053": "crc359conf",
    "298ca4ed": "crc360conf", "982d0d1e": "crc362conf", "16170922": "crc363conf",
    "f87d0121": "crc364conf", "966b4bbc": "crc365conf", "b83913e5": "crc366conf",
    "86cd43d9": "crc367conf", "e2c0923a": "crc368conf", "da33e79a": "crc369conf",
    "bf661330": "crc370conf", "31950326": "crc371conf", "f92af21e": "crc372conf",
    "bca4fe9c": "crc373conf", "1ba91ce3": "crc374conf", "16cf99d8": "crc375conf",
    "64b79bc3": "crc376conf", "b852634c": "crc377conf"
}

real_crc_set = {
    "886f289d", "8f9e2b87", "9327049f", "982e83fb", "9de32634", "e3f03995", "f49dc890",
    "00cc5ca2", "0e9ea79a", "1e87d494", "2072855c", "2226df9b", "368f1792", "658a091a",
    "69661c9a", "6b686cdb", "7372633c"
}

# Manual overrides for label naming by pattern and offset
manual_extracts = {
    "2dec5e1f00": {
        276742: "entity10", 262558: "entity11", 236443: "RSCentity12",
        236459: "entity13", 236429: "entity14or15", 236322: "entity16or17",
        237283: "entity18", 238238: "entity19",
    },
    "29edbf2901": {
        241559: "entity20", 242388: "entity21", 242354: "entity22MISSING",
        242463: "entity23", 244467: "entity24",
    },
    "2ded480a01": {
        270006: "entity4", 272105: "entity5", 271813: "entity6",
        304738: "entity7", 317081: "entity8",
    },
    "816a8a8e01": {
        26402: "entitymem12to14", 28534: "entitymem18or19",
    },
    "a38c6bba00": {
        46636: "entitymem20to22", 48212: "entitymem23or24",
    },
    "5e9c595300": {
        120733: "maps14", 128069: "maps19", 128172: "maps20", 129522: "maps21",
        128815: "maps22", 245456: "maps24", 250590: "maps25", 250743: "maps27",
    },
    "8138952900": {
        43267: "media28or29", 45629: "media30", 45971: "media31", 46713: "media32",
        47925: "media33", 48705: "media34", 48958: "media35", 49038: "media36",
        49136: "media37", 50207: "media38", 57174: "media40", 57636: "media41",
        60740: "media43", 62532: "media44", 63471: "media45", 73052: "media46",
        76412: "media47",
    },
    "29df679e00": {
        79633: "media48", 83020: "media49", 89722: "media50or51", 95892: "media53",
        98567: "media54or55", 98615: "media56or57", 98729: "media58",
    },
    "0631f93600": {
        43649: "textures10or11", 50320: "textures12", 57609: "textures13",
        59956: "textures14", 60809: "textures15", 62020: "textures7",
        43468: "textures8", 42247: "textures9",
    },
    "8384eb9200": {
        60809: "textures15", 62988: "textures16", 63685: "textures17",
    },
    "0632e32100": {
        64761: "textures5", 65790: "textures6",
    },
    "314159265359": {
        17164: "config18", 19791: "config26", 19939: "config28", 20373: "config29",
        20964: "config31", 21660: "config32", 21672: "config33", 22607: "config34",
        34861: "config37", 35045: "config38", 35414: "config41", 35548: "config42",
        35648: "config44", 39905: "config46", 32714: "config48", 34606: "config49",
        35953: "config50", 36011: "config51", 37780: "config55", 38290: "config56",
        39208: "config57", 39465: "config58", 40032: "config59", 40791: "config60or61",
        45593: "config64", 45844: "config65", 46780: "config66", 47624: "config67",
        49584: "config68", 49603: "config71", 55425: "config72", 57870: "config73",
        60500: "config74", 62634: "config75", 66839: "config77", 69231: "config78MISSING",
        71775: "config80", 58111: "config81", 58289: "config82", 58525: "config83MISSING",
        58809: "config84", 58819: "config85", 16751: "filter1", 15377: "filter2",
        15162: "jagex", 4990: "jagex(3)",
        113797: "land28", 119740: "land29or30", 11508: "landmem30",
        118718: "land31", 13755: "landmem31", 118477: "land33", 18565: "landmem33",
        118573: "land34", 20689: "landmem34", 118542: "land35", 126607: "land36or37",
        32438: "landmem37", 127676: "land38", 34425: "landmem38", 127695: "land39",
        127702: "land40", 129929: "land42", 129978: "land43", 131491: "land46",
        131865: "land47", 132214: "land50", 67567: "landmem50", 135641: "land51", 80716: "landmem51memMISSING",
        134168: "land52", 96519: "landmem52memMISSING", 113613: "landmem53", 133624: "land53or54", 118657: "landmem54",
        135079: "land55", 127527: "landmem55", 135159: "land56", 138455: "landmem56memMISSING",
        136232: "land58", 140327: "landmem58", 142215: "land59", 141999: "landmem60",
        142250: "land60or61", 153213: "landmem61", 142383: "land62or63",
        154683: "landmem62or63", 29340: "maps28", 34903: "maps29", 7685: "mapsmem29or30",
        34856: "maps30", 34334: "maps31", 8889: "mapsmem31", 34270: "maps33",
        10708: "mapsmem33", 34310: "maps34", 11559: "mapsmem34", 34322: "maps35",
        15549: "mapsmem35", 35192: "maps36", 16057: "mapsmem36", 35500: "maps37",
        18978: "mapsmem37", 36702: "maps38", 21518: "mapsmem38", 36710: "maps39",
        36704: "maps40", 31087: "maps42", 31133: "maps43", 32020: "maps46",
        24877: "mapsmem46", 32339: "maps47", 32667: "maps50", 29753: "mapsmem50",
        33894: "maps51", 34683: "mapsmem51memMISSING", 33887: "maps52", 38791: "mapsmem52memMISSING", 46423: "mapsmem53", 32213: "maps53or54",
        48567: "mapsmem54", 34013: "maps55", 51532: "mapsmem55", 34090: "maps56",
        55101: "mapsmem56memMISSING", 34820: "maps58", 55877: "mapsmem58", 36981: "maps59",
        56574: "mapsmem60", 37113: "maps60or61", 59317: "mapsmem61", 37649: "maps62",
        59481: "mapsmem62or63", 37629: "maps63", 43031: "media12", 51866: "media17",
        52066: "media18", 52637: "media19", 52684: "media20", 53449: "media21",
        52803: "media22", 54313: "media24", 55628: "media26", 52221: "media27",
        53806: "models10", 53894: "models11", 54192: "models12(1)", 54244: "models12(2)",
        57485: "models13", 58513: "models14", 58687: "models15", 61008: "models16",
        61894: "models17", 65173: "models18", 113466: "models20", 131029: "models22",
        144388: "models23", 146108: "models24", 195500: "models25", 196003: "models26",
        241919: "models27", 242647: "models28", 275848: "models29or30",
        286348: "models32", 286824: "models33or34", 288619: "models35MISSING",
        289822: "models36", 78921: "models6", 79420: "models7", 114375: "sounds1",
        114448: "sounds1",
        47604: "RS2interface194", 59225: "RS2interface204", 63833: "RS2interface217",
        64715: "RS2interface218", 69236: "RS2interface222", 69451: "RS2interface224",
        69570: "RS2interface225", 75084: "RS2interface243", 77121: "RS2interface244",
        78493: "RS2interface245.1", 78572: "RS2interface245.2", 78563: "RS2interface254",
        96320: "RS2interface270", 112178: "RS2interface289", 115463: "RS2interface291",
        118129: "RS2interface299", 122610: "RS2interface306", 127740: "RS2interface308",
        131721: "RS2interface317", 133891: "RS2interface318", 134325: "RS2interface319",
        134109: "RS2interface321", 134833: "RS2interface325", 137808: "RS2interface327",
        142555: "RS2interface330", 142456: "RS2interface332", 142796: "RS2interface333",
        147570: "RS2interface336", 135148: "RS2interface337", 148381: "RS2interface339",
        149231: "RS2interface340", 151193: "RS2interface343", 152487: "RS2interface345",
        154533: "RS2interface346", 158017: "RS2interface347", 158831: "RS2interface349",
        161416: "RS2interface350", 161818: "RS2interface355", 172248: "RS2interface356",
        172628: "RS2interface357", 178829: "RS2interface362", 179556: "RS2interface363",
        184196: "RS2interface365", 185241: "RS2interface367", 186154: "RS2interface368",
        186739: "RS2interface369", 186692: "RS2interface372", 187822: "RS2interface374",
        187799: "RS2interface376", 185731: "RS2interface377", 
        26930: "RS2versionlist243", 26963: "RS2versionlist244", 27461: "RS2versionlist245.1",
        27881: "RS2versionlist245.2", 33400: "RS2versionlist270", 37525: "RS2versionlist289",
        38849: "RS2versionlist291", 41720: "RS2versionlist299", 44404: "RS2versionlist306",
        46443: "RS2versionlist308", 52347: "RS2versionlist317", 52977: "RS2versionlist318",
        53141: "RS2versionlist319", 53284: "RS2versionlist321", 56728: "RS2versionlist325",
        59087: "RS2versionlist327", 60574: "RS2versionlist330", 61123: "RS2versionlist332",
        61245: "RS2versionlist333", 61867: "RS2versionlist336", 63299: "RS2versionlist337",
        63508: "RS2versionlist339", 64121: "RS2versionlist340", 65686: "RS2versionlist343",
        65933: "RS2versionlist345", 66457: "RS2versionlist346", 67171: "RS2versionlist347",
        68903: "RS2versionlist349", 69797: "RS2versionlist350", 71383: "RS2versionlist355",
        71852: "RS2versionlist356", 72419: "RS2versionlist357", 75695: "RS2versionlist362",
        76319: "RS2versionlist363", 85893: "RS2versionlist365", 86788: "RS2versionlist367",
        87378: "RS2versionlist368", 87912: "RS2versionlist369", 88673: "RS2versionlist372",
        90362: "RS2versionlist374", 90662: "RS2versionlist376", 91366: "RS2versionlist377",
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
                offset = int(line, 16)
                pattern_offset_map[current_pattern].append(offset)
    return pattern_offset_map

def extract_files(image_path, pattern_offsets, out_dir="extracted"):
    os.makedirs(out_dir, exist_ok=True)
    with open(image_path, "rb") as f:
        for pattern, offsets in pattern_offsets.items():
            if pattern in six_back_patterns:
                label = six_back_patterns[pattern]
                backtrack = 6
                mode = "length_from_offset"
            elif pattern in eight_back_patterns:
                label = eight_back_patterns[pattern]
                backtrack = 8
                mode = "length_from_offset"
            elif pattern in crc_patterns:
                label = crc_patterns[pattern]
                backtrack = 4
                mode = "crc_logic"
            else:
                print(f"Unknown pattern {pattern}, skipping...")
                continue

            for offset in offsets:
                extract_start = offset - backtrack

                # Only check 4-byte exclusion for pattern 314159265359
                if pattern == "314159265359":
                    f.seek(extract_start - 4)
                    prefix_bytes = f.read(4)
                    if prefix_bytes == b'\x0d\xe0\x0c\x5f':
                        print(f"Skipping 0x{offset:x} (matches exclusion prefix 0DE00C5F)")
                        continue

                f.seek(extract_start)

                if mode == "length_from_offset":
                    head = f.read(6)
                    if len(head) < 6:
                        print(f"Skipping 0x{offset:x} (too short for length read)")
                        continue
                    if pattern != "314159265359" and head[:3] != head[3:6]:
                        print(f"Skipping 0x{offset:x} (prefix repeat check failed)")
                        continue
                    length = (head[3] << 16) + (head[4] << 8) + head[5]
                    total_length = 6 + length
                    if total_length > MAX_EXTRACT_SIZE:
                        print(f"Skipping 0x{offset:x} (exceeds max size: {total_length} bytes)")
                        continue
                    f.seek(extract_start)
                    extract = f.read(total_length)

                    manual_label = manual_extracts.get(pattern, {}).get(total_length)
                    if pattern == "314159265359":
                        if manual_label:
                            out_filename = f"{manual_label}_{offset:012x}.bin"
                        else:
                            if len(extract) <= 54:
                                print(f"Skipping 0x{offset:x} (too short for all checks)")
                                continue
                            if extract[19] not in (0x7F, 0xFF):
                                print(f"Skipping 0x{offset:x} (byte 19 != 7F or FF)")
                                continue
                            if extract[0] >= 0x1B:
                                print(f"Skipping 0x{offset:x} (byte 0 >= 1B)")
                                continue
                            if extract[2] == 0x00:
                                print(f"Skipping 0x{offset:x} (byte 2 == 00)")
                                continue
                            if not (extract[53] == 0xE0 or extract[33] == 0xBF):
                                print(f"Skipping 0x{offset:x} (byte 53 != E0 and byte 33 != BF)")
                                continue
                            out_filename = f"{label}_{offset:012x}.bin"
                    else:
                        out_filename = f"{label}_{offset:012x}.bin"

                elif mode == "crc_logic":
                    extract = f.read(40)
                    if len(extract) < 40:
                        print(f"Skipping 0x{offset:x} (incomplete fixed 40)")
                        continue
                    first4 = extract[:4].hex()
                    if first4 in crc_map:
                        out_filename = f"{crc_map[first4]}_{offset:012x}.bin"
                    else:
                        crc_check = extract[24:28].hex()
                        if crc_check in real_crc_set:
                            out_filename = f"crc real {label}_{offset:012x}.bin"
                        else:
                            out_filename = f"crc false {label}_{offset:012x}.bin"
                else:
                    continue

                out_path = os.path.join(out_dir, out_filename)
                with open(out_path, "wb") as out_file:
                    out_file.write(extract)
                print(f"Extracted {out_filename} ({len(extract)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_from_image.py <image_file> <output.txt>")
        sys.exit(1)
    image_file = sys.argv[1]
    output_file = sys.argv[2]
    pattern_offsets = parse_output_file(output_file)
    extract_files(image_file, pattern_offsets)

