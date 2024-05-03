import os

overpassql = """\
// Important note: SubArea: Japan/Tokyo
[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;\
"""

base_dir = "./data/administrative/"


def search_target_dir(query):
    # overpassqlからSubAreaを含む行を取得
    query_lines = query.split('\n')
    area_lines = [line for line in query_lines if 'SubArea' in line]
    # 空白で区切った末尾を取得
    area_name_path = area_lines[0].split()[-1]
    # area_name_pathからtarget_dirを探す
    target_dir_path = os.path.join(base_dir, area_name_path)
    # base_dir_pathにディレクトリが存在しない場合、作成
    os.makedirs(target_dir_path, exist_ok=True)
    return target_dir_path


target_dir = search_target_dir(overpassql)

print("target_dir:", target_dir)

# ./data/administrative/Japan/Tokyo
# のような文字列から
# Japan, Tokyo
# のような文字列を生成
new_trident_string = ", ".join(
    reversed(target_dir.replace(base_dir, "").split('/')))

print("new_trident_string:", new_trident_string)

exit(0)

area_names = []


def get_names_of_elements(query):
    import httpx

    params = {
        'data': query
    }
    overpass_api_endpoint = "https://z.overpass-api.de/api/interpreter"
    response = httpx.get(overpass_api_endpoint, params=params, timeout=None)
    response_json = response.json()

    elements = response_json['elements']
    for element in elements:
        if 'tags' in element and 'name:en' in element['tags']:
            area_names.append(element['tags']['name:en'])


get_names_of_elements(overpassql)

for area in area_names:
    print(area)
    # ./data/administrative/Japan/Tokyo/ にディレクトリが存在しない場合、作成
    os.makedirs(f"{target_dir}/{area}", exist_ok=True)
    # input-trident.txt に書き込み
    with open(f"{target_dir}/{area}/input-trident.txt", 'w') as f:
        f.write(f"Area: {area}, {new_trident_string}\n")
