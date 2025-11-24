import os
import sys
import re

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

# Mapping for loaderclassic/loader versions based on bytes 12-14
loader_map = {
    "5f8c2d": "loaderclassic161",
    "743b2e": "loaderclassic162",
    "0a642e": "loaderclassic163",
    "4f712e": "loaderclassic164",
    "4c8f2e": "loaderclassic167",
    "72a72e": "loaderclassic168",
    "4ec92e": "loaderclassic170",
    "72fc2e": "loaderclassic174",
    "6f142f": "loaderclassic175",
    "64362f": "loaderclassic176",
    "3f5f2f": "loaderclassic177",
    "6a742f": "loaderclassic178",
    "5d832f": "loaderclassic179",
    "7c932f": "loaderclassic180",
    "5a9e2f": "loaderclassic181",
    "4d3c30": "loaderclassic182",
    "7d4430": "loaderclassic183",
    "5d5230": "loaderclassic185",
    "54aa30": "loaderclassic194",
    "45dc30": "loaderclassic196",
    "821831": "loaderclassic198",
    "865c31": "loaderclassic199",
    "728d31": "loaderclassic201",
    "890333": "loaderclassic202",
    "7b6833": "loaderclassic203",
    "73b934": "loaderclassic204",
    "51812f": "loader185",
    "69822f": "loader186",
    "8d832f": "loader187",
    "738d2f": "loader190",
    "5d7130": "loader204",
    "5f7e30": "loader211",
    "758130": "loader213",
    "818530": "loader214",
    "6b8630": "loader215",
    "6a8f30": "loader216",
    "429030": "loader217",
    "709430": "loader218",
    "759a30": "loader219",
    "489d30": "loader220",
    "81a530": "loader222",
    "47aa30": "loader223",
    "86ab30": "loader224",
    "6bb230": "loader225",
    "70c130": "loader228",
    "75c130": "loader229",
    "92c130": "loader234",
    "68c230": "loader236",
    "76c230": "loader237",
    "72c330": "loader238",
    "96c830": "loader240",
    "70ce30": "loader241",
    "71d530": "loader242",
    "4bd530": "loader243",
    "53dc30": "loader244",
    "71dd30": "loader245",
    "69ed30": "loader245",
    "71f430": "loader245",
    "59f630": "loader246",
    "6afb30": "loader247",
    "6b0231": "loader248",
    "730931": "loader249",
    "6b1831": "loader252",
    "712131": "loader253",
    "592731": "loader254",
    "6b2e31": "loader255",
    "6b3431": "loader256",
    "733b31": "loader257",
    "763c31": "loader258",
    "8b3e31": "loader259",
    "4c4531": "loader260",
    "494e31": "loader261",
    "6a5231": "loader262",
    "945231": "loader263",
    "735a31": "loader265",
    "785c31": "loader267",
    "4a6231": "loader268",
    "926431": "loader270",
    "607131": "loader273",
    "5c7731": "loader274",
    "467d31": "loader275",
    "518631": "loader276",
    "8e8731": "loader278",
    "4e8d31": "loader279",
    "5d8f31": "loader280",
    "569531": "loader282",
    "6b2532": "loader285",
    "602732": "loader287",
    "582a32": "loader288",
    "4d3132": "loader289",
    "5e3a32": "loader290",
    "5a3f32": "loader291",
    "694732": "loader292",
    "6e4832": "loader294",
    "504e32": "loader295",
    "4e5632": "loader296",
    "775732": "loader297",
    "565c32": "loader298",
    "836132": "loader299",
    "5b6732": "loader300",
    "636e32": "loader302",
    "7e6e32": "loader303",
    "557532": "loader304",
    "517d32": "loader305",
    "498432": "loader306",
    "618b32": "loader307",
    "4b9232": "loader308",
    "559932": "loader309",
    "53a432": "loader310",
    "6ba532": "loader311",
    "5ea932": "loader312",
    "53b132": "loader313",
    "6cbf32": "loader314",
    "77c132": "loader315",
    "50c632": "loader316",
    "6ecd32": "loader317",
    "4ad632": "loader318",
    "4edb32": "loader319",
    "51e532": "loader320",
    "79e732": "loader321",
    "6ceb32": "loader322",
    "46eb32": "loader323",
    "6ced32": "loader324",
    "55f232": "loader325",
    "7bf932": "loader326",
    "4f0133": "loader327",
    "4e0933": "loader328",
    "590f33": "loader329",
    "5d1633": "loader330",
    "5b1e33": "loader331",
    "881e33": "loader332",
    "6c2633": "loader333",
    "622c33": "loader334",
    "693333": "loader336",
    "793a33": "loader337",
    "5d3b33": "loader338",
    "684333": "loader339",
    "605133": "loader340",
    "685833": "loader341",
    "4a5f33": "loader342",
    "5b6833": "loader343",
    "4f6e33": "loader344",
    "4a7533": "loader345",
    "4f7c33": "loader346",
    "6a8533": "loader347",
    "4d8c33": "loader348",
    "569333": "loader349",
    "539e33": "loader350",
    "5e2a34": "loader351",
    "763034": "loader352",
    "683034": "loader353",
    "5a3334": "loader354",
    "5b3734": "loader355",
    "513e34": "loader356",
    "5e4734": "loader357",
    "715034": "loader358",
    "505134": "loader359",
    "565434": "loader360",
    "565634": "loader361",
    "6f5634": "loader362",
    "7b5b34": "loader363",
    "446734": "loader364",
    "6a6e34": "loader365",
    "497534": "loader366",
    "907534": "loader367",
    "4a7c34": "loader368",
    "608334": "loader369",
    "548a34": "loader370",
    "758a34": "loader371",
    "538c34": "loader372",
    "519234": "loader373",
    "4b9434": "loader374",
    "489834": "loader375",
    "539934": "loader376",
    "52a234": "loader377",
}

crc_map = {
    "dc058ad7": "crc186confNEW",
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
    "949c9e5a": "crc295confNEW",
    "ad3fdbed": "crc297confNEW",
    "b508f498": "crc298conf",
    "3276b47f": "crc299conf",
    "af6801a7": "crc300confNEW",
    "5ff69069": "crc303confNEW",
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
    "fed117ff": "crc321conf",
    "450bdabf": "crc324conf",
    "994db34e": "crc325conf",
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
    "e4b42786": "crc345conf",
    "76d4c217": "crc346conf",
    "aa54c948": "crc347conf",
    "7b273c06": "crc348confNEW",
    "41cbf853": "crc349conf",
    "d440bb01": "crc350conf",
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
    "31950326": "crc371confNEW",
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
    "01c3b701c3b7": "RS2config194",
    "01d7cd01d7cd": "RS2config204",
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
    "0567b40567b4": "RS2config336",
    "059284059284": "RS2config337",
    "0596d20596d2": "RS2config339",
    "05af5905af59": "RS2config340",
    "05db8205db82": "RS2config343",
    "05e94f05e94f": "RS2config345",
    "05f9fa05f9fa": "RS2config346",
    "060d2b060d2b": "RS2config347",
    "062f57062f57": "RS2config349",
    "063bf6063bf6": "RS2config350",
    "0669f20669f2": "RS2config356",
    "0665af0665af": "RS2config357",
    "06aabe06aabe": "RS2config362",
    "06b90306b903": "RS2config363",
    "072478072478": "RS2config365",
    "07440a07440a": "RS2config367",
    "0793a20793a2": "RS2config368",
    "079fa4079fa4": "RS2config369",
    "07e45707e457": "RS2config372",
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
        "025cf200b213": "config64",
        "025ff900b30e": "config65",
        "026f4600b6b6": "config66",
        "027f6100ba02": "config67",
        "029e6d00c1aa": "config68",
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
        "03b66801fb83": "land42",
        "03b6a701fbb4": "land43",
        "03c14402019d": "land46",
        "03c37e020313": "land47",
        "03c57b020426": "land49",
        "03c57b020470": "land50",
        "03df4d0211d3": "land51",
        "03d39a020c12": "land52",
        "03cbb70209f2": "land53or54",
        "03d80a020fa1": "land55",
        "03d840020ff1": "land56",
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
        "01465d007969": "maps42",
        "014690007997": "maps43",
        "017917007d0e": "maps46",
        "017afd007e4d": "maps47",
        "017eff007fdf": "maps49",
        "017e2e007f95": "maps50",
        "018834008460": "maps51",
        "0187ad008459": "maps52",
        "017858007dcf": "maps53or54",
        "17b28f0084d7": "maps55",
        "17d728008524": "maps56",
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
        "01c8a40107e9": "land50mem",
        "02e42b01bbc7": "land53mem",
        "0304f101cf7b": "land54mem",
        "033f5001f221": "land55mem",
        "03939d022421": "land58mem",
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
        "011f70007433": "maps50mem",
        "01b62e00b551": "maps53mem",
        "01c83f00bdb1": "maps54mem",
        "17ddc500c946": "maps55mem",
        "19327100da3f": "maps58mem",
        "197e1000dcf8": "maps60mem",
        "1a644b00e7af": "maps61mem",
        "1a88ba00e853": "maps62or63mem",

        "029dcf01bf0a": "sounds1(1)mem",
        "029dcf01bec1": "sounds1(2)mem",

        # RS2interface overrides
        "03385800b9ee": "RS2interface194",
        "03f01f00e753": "RS2interface204",
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
        "0a9455027814": "RS2interface355",
        "0b6f7802a0d2": "RS2interface356",
        "0b71e202a24e": "RS2interface357",
        "0bbfae02ba87": "RS2interface362",
        "0bc3a702bd5e": "RS2interface363",
        "0bf7ee02cf7e": "RS2interface365",
        "0c044102d393": "RS2interface367",
        "0c0ee102d724": "RS2interface368",
        "0c143402d96d": "RS2interface369",
        "0c155902d93e": "RS2interface372",
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
        "0227ec010d21": "RS2versionlist349",
        "022e6d01109f": "RS2versionlist350",
        "023e490116d1": "RS2versionlist355",
        "0241230118a6": "RS2versionlist356",
        "02469d011add": "RS2versionlist357",
        "0260df0127a9": "RS2versionlist362",
        "0265d9012a19": "RS2versionlist363",
        "02be67014f7f": "RS2versionlist365",
        "02c5b30152fe": "RS2versionlist367",
        "02d05c01554c": "RS2versionlist368",
        "02d7c6015762": "RS2versionlist369",
        "02e2ff015a5b": "RS2versionlist372",
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
        "01768e01768e": "media53",
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
        "023ebe023ebe": "RS2sounds345",
        "02458a02458a": "RS2sounds346",
        "025b04025b04": "RS2sounds347",
        "02864a02864a": "RS2sounds349",
        "02904c02904c": "RS2sounds350",
        "02b2d802b2d8": "RS2sounds355",
        "02ba2b02ba2b": "RS2sounds356",
        "02d31b02d31b": "RS2sounds357",
        "03073f03073f": "RS2sounds362",
        "031074031074": "RS2sounds363",
        "034429034429": "RS2sounds365",
        "0346f20346f2": "RS2sounds367",
        "034a9d034a9d": "RS2sounds368",
        "034d46034d46": "RS2sounds369",
        "035861035861": "RS2sounds372",
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
            elif pattern in config_failsafe:
                label = config_failsafe[pattern]
                backtrack = 38
                mode = "length_from_offset"
            elif pattern in crc_patterns:
                label = crc_patterns[pattern]
                backtrack = 4
                mode = "crc_logic"
            elif pattern in loader_patterns:
                label = loader_patterns[pattern]
                if pattern == "2000636c6f616465722e636c617373":
                    backtrack = 111
                elif pattern in (
                    "006c6f616465722e636c617373",
                    "007369676e2f7369676e6c696e6b2e636c617373",
                ):
                    backtrack = 29
                else:
                    print(f"Unknown loader pattern {pattern}, skipping...")
                    continue
                mode = "loader_extract"
            else:
                print(f"Unknown pattern {pattern}, skipping...")
                continue

            for offset in offsets:
                extract_start = offset - backtrack

                if extract_start < 0:
                    print(f"Skipping 0x{offset:x} (start before file)")
                    continue

                if mode == "loader_extract":
                    f.seek(extract_start)
                    header = f.read(10)
                    f.seek(extract_start)

                    if pattern == "2000636c6f616465722e636c617373":
                        if not header.startswith(b"MSCF"):
                            print(f"Skipping 0x{offset:x} (loader_cab missing MSCF header)")
                            continue
                    elif pattern in (
                        "006c6f616465722e636c617373",
                        "007369676e2f7369676e6c696e6b2e636c617373",
                    ):
                        if not header.startswith(b"PK\x03\x04\x14\x00\x08\x00\x08\x00"):
                            print(f"Skipping 0x{offset:x} (loader_jar missing PK ZIP header)")
                            continue

                    extract = f.read(20480)

                    if pattern in (
                        "006c6f616465722e636c617373",
                        "007369676e2f7369676e6c696e6b2e636c617373",
                    ) and len(extract) >= 15:
                        byte13 = extract[13]
                        byte12 = extract[12]
                        code_hex = extract[12:15].hex()
                        label = f"loader_{byte13}_{byte12}_jar"
                        if code_hex in loader_map:
                            label += "_" + loader_map[code_hex]
                        else:
                            print(f"Unknown loader signature {code_hex}, using default label")
                    elif pattern == "2000636c6f616465722e636c617373" and len(extract) >= 83:
                        byte79 = extract[79]
                        byte78 = extract[78]
                        code_hex = f"{extract[81]:02x}{extract[78]:02x}{extract[79]:02x}"
                        label = f"loader_{byte79}_{byte78}_cab"
                        if code_hex in loader_map:
                            label += "_" + loader_map[code_hex]
                        else:
                            print(f"Unknown loader signature {code_hex}, using default label")

                    out_filename = f"{label}_{extract_start:012x}.zip"
                    out_path = os.path.join(out_dir, out_filename)
                    with open(out_path, "wb") as out_file:
                        out_file.write(extract)
                    print(f"Extracted {out_filename} ({len(extract)} bytes)")
                    continue

                # Only check 4-byte exclusion for pattern 314159265359
                if pattern == "314159265359":
                    f.seek(extract_start - 4)
                    prefix_bytes = f.read(4)
                    if prefix_bytes == b"\x0d\xe0\x0c\x5f":
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

                    header6_hex = extract[:6].hex()

                    # 1) pattern-specific manual overrides
                    manual_label = manual_extracts.get(pattern, {}).get(header6_hex)

                    # 2) RS2config-wide overrides if this extraction defaults to RS2config
                    if manual_label is None and label == "RS2config":
                        manual_label = manual_rs2config_headers.get(header6_hex)

                    if pattern == "314159265359":
                        if manual_label:
                            out_filename = f"{manual_label}_{extract_start:012x}.bin"
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
                            out_filename = f"{label}_{extract_start:012x}.bin"
                    else:
                        if manual_label:
                            out_filename = f"{manual_label}_{extract_start:012x}.bin"
                        else:
                            out_filename = f"{label}_{extract_start:012x}.bin"

                elif mode == "crc_logic":
                    extract = f.read(40)
                    if len(extract) < 40:
                        print(f"Skipping 0x{offset:x} (incomplete fixed 40)")
                        continue

                    first4 = extract[:4].hex()
                    if first4 in crc_map:
                        out_filename = f"{crc_map[first4]}_{extract_start:012x}.bin"
                    else:
                        X = 1234
                        for i in range(0, 36, 4):
                            block_val = int.from_bytes(extract[i:i + 4], byteorder="big", signed=False)
                            X = X * 2 + block_val
                            X = ((X + (1 << 31)) % (1 << 32)) - (1 << 31)

                        check_val = int.from_bytes(extract[36:40], byteorder="big", signed=True)
                        if X == check_val:
                            out_filename = f"crc real {label}_{extract_start:012x}.bin"
                        else:
                            crc_check = extract[24:28].hex()
                            if crc_check in real_crc_set:
                                out_filename = f"crc real {label}_{extract_start:012x}.bin"
                            else:
                                out_filename = f"crc false {label}_{extract_start:012x}.bin"

                    if out_filename.startswith("crc false"):
                        print(f"Skipping 0x{offset:x} (crc false)")
                        continue

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
