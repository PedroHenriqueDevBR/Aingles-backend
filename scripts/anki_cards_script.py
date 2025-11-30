"""
{
    "id": 0,
    "front": "",
    "back": "",
    "appears_count": 0,
    "created_at": "2025-11-09T04:39:39.105347",
    "next_review_at": "2025-11-10T04:39:39.105717",
    "author_id": "string"
}
"""


import json


def open_anki_file(file_path: str) -> list[dict[str, str]]:
    cards = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file.readlines():
            line = line.strip()
            if line:
                front, back = line.split("\t")
                cards.append({"front": front, "back": back})
    return cards


def write_aingles_cards(cards: list[dict[str, str]], output_path: str):
    jsonResponse = []
    with open(output_path, "w", encoding="utf-8") as file:
        for card in cards:
            body = {"front": card["front"], "back": card["back"]}
            jsonResponse.append(body)
        jsonData = json.dumps(jsonResponse, indent=4, ensure_ascii=False)
        file.write(jsonData)


def main(file_path: str, output_path: str):
    cards = open_anki_file(file_path)
    write_aingles_cards(cards, output_path)


if __name__ == "__main__":
    file_path = "./data/anki_cards.txt"
    output_path = "./data/anki_cards_output.json"
    main(file_path, output_path)
