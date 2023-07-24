import requests


def get_game_id(game_name):
    response = requests.get(f'https://www.speedrun.com/api/v1/games?name={game_name}')

    for game in response.json()['data']:
        if game['names']['international'] == game_name:
            return game['id']
        
    print("Game not found")
    return 0

def get_category_variable_uri(game_id, game_category):
    response = requests.get(f'https://www.speedrun.com/api/v1/games/{game_id}/categories')

    for category in response.json()['data']:
        if category['name'] == game_category:
            for link in category['links']:
                if link['rel'] == 'variables':
                    return link['uri']
                
    print("Category not found")
    return 0

def get_category_variables(game_name, game_category):
    try:
        game_id = get_game_id(game_name)
        if game_id == 0:
            return 0
        
        variable_uri = get_category_variable_uri(game_id, game_category)
        if variable_uri == 0:
            return 0

        response = requests.get(variable_uri)
        data = response.json()['data']

        return [variable['name'] for variable in data]
    except Exception:
        #Couldn't call SRC API
        return 0