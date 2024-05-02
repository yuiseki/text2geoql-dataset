import os
import sys
import yaml
import httpx


def load_yaml(file_path):
    # 指定されたファイルパスからyamlファイルを読み込む
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data

def get_number_of_elements(query):
    params = {
        'data': query
    }

    overpass_api_endpoint = "https://z.overpass-api.de/api/interpreter"
    response = httpx.get(overpass_api_endpoint, params=params)
    response_json = response.json()

    number_of_elements = len(response_json['elements'])
    return number_of_elements


# 実行時の1番目の引数
file_path = sys.argv[1]
data = load_yaml(file_path)


query = data['Output']
params = {
    'data': query
}

overpass_api_endpoint = "https://z.overpass-api.de/api/interpreter"
response = httpx.get(overpass_api_endpoint, params=params)
response_json = response.json()

number_of_elements = len(response_json['elements'])
print(number_of_elements)
