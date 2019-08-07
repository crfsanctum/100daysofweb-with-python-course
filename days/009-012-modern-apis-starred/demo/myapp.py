import json
from typing import List

from apistar import App, Route, types, validators
from apistar.http import JSONResponse

def _load_marvel_data():
    marvel = []
    with open('marvel.json') as f:
        marvel = json.loads(f.read())

    characters = {}
    for m in marvel:
        characters[int(m['page_id'])]={
            'id': int(m['page_id']),
            'name': m['name'],
            'year': int(m['Year']) if m['Year'] else None,
            'appearances': int(m['APPEARANCES']) if m['APPEARANCES'] else None
        }
    return characters


characters = _load_marvel_data()
CHARACTER_NOT_FOUND = 'Marvel character not found'
next_id = max(characters.keys()) + 1

class MarvelCharacter(types.Type):
    id = validators.Integer(allow_null=True)
    name = validators.String()
    year = validators.Integer(minimum=1900, maximum=2050, allow_null=True)
    appearances = validators.Integer(allow_null=True)


def list_characters() -> List[MarvelCharacter]:
    return [MarvelCharacter(m[1]) for m in sorted(characters.items())]


def create_character(character: MarvelCharacter) -> JSONResponse:
    global next_id
    character_id = next_id
    next_id += 1
    character['id'] = character_id
    characters[character_id] = character
    return JSONResponse(MarvelCharacter(character), status_code=201)
    

def get_character(character_id: int) -> JSONResponse:
    character = characters.get(character_id)
    if not character:
        error = {'error': CHARACTER_NOT_FOUND}
        return JSONResponse(error, status_code=404)
    
    return JSONResponse(MarvelCharacter(character), status_code=200)


def update_character(character_id: int, character: MarvelCharacter) -> JSONResponse:
    if not characters.get(character_id):
        error = {'error': CHARACTER_NOT_FOUND}
        return JSONResponse(error, status_code=404)

    character.id = character_id
    characters[character_id] = character
    return JSONResponse(MarvelCharacter(character), status_code=200)


def delete_character(character_id: int) -> JSONResponse:
    if not characters.get(character_id):
        error = {'error': CHARACTER_NOT_FOUND}
        return JSONResponse(error, status_code=404)
    
    del characters[character_id]
    return JSONResponse({}, status_code=204)


routes = [
    Route('/', method='GET', handler=list_characters),
    Route('/', method='POST', handler=create_character),
    Route('/{character_id}/', method='GET', handler=get_character),
    Route('/{character_id}/', method='PUT', handler=update_character),
    Route('/{character_id}/', method='DELETE', handler=delete_character),
]

app = App(routes=routes)


if __name__ == '__main__':
    app.serve('127.0.0.1', 5000, debug=True)