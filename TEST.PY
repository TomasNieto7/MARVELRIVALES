import requests
import time

# Reemplaza con tu Access Token de SuperHero API
ACCESS_TOKEN = "91e2e541450bf6936653103a81dacd0e"

# Lista de personajes de Marvel Rivals basada en fuentes de la comunidad
marvel_rivals_roster = [
    "Frozono","Adam Warlock", "Angela", "Black Panther", "Black Widow", "Blade", "Hulk",
    "Captain America", "Cloak and Dagger", "Doctor Strange", "Emma Frost",
    "Groot", "Hawkeye", "Hela", "Human Torch", "Invisible Woman", "Iron Fist",
    "Iron Man", "Jean Grey", "Jeff the Land Shark", "Loki", "Luna Snow",
    "Magik", "Magneto", "Mantis", "Mister Fantastic", "Moon Knight", "Namor",
    "Peni Parker", "Phoenix", "Psylocke", "Rocket Raccoon", "Scarlet Witch",
    "Spider-Man", "Squirrel Girl", "Star-Lord", "Storm", "The Punisher",
    "The Thing", "Thor", "Ultron", "Venom", "Winter Soldier", "Wolverine"
]

def get_superhero_details(hero_name):
    """
    Busca un personaje específico en la SuperHero API y devuelve el primer resultado.
    """
    url = f"https://www.superheroapi.com/api/{ACCESS_TOKEN}/search/{hero_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data.get("response") == "success" and data.get("results"):
            # Devolver solo el primer resultado de la búsqueda
            return data["results"][0]
        return None

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con SuperHero API para {hero_name}: {e}")
        return None

def process_marvel_rivals_roster():
    """
    Procesa la lista de personajes de Marvel Rivals para obtener detalles,
    incluyendo la primera aparición.
    """
    for hero_name in marvel_rivals_roster:
        hero_data = get_superhero_details(hero_name)
        
        if hero_data:
            nombre = hero_data.get('name')
            imagen_url = hero_data.get('image', {}).get('url')
            base = hero_data.get('work', {}).get('base')
            nacimiento = hero_data.get('biography', {}).get('place-of-birth')
            
            print(f"Nombre: {nombre}")
            print(f"Imagen: {imagen_url}")
            print(f"Base de operaciones: {base}")
            print(f"Lugar de nacimiento: {nacimiento}")
            print("-" * 20)
        else:
            print(f"No se encontraron resultados para {hero_name}.")
            print("-" * 20)

        # Espera un momento para evitar saturar la API
        time.sleep(1)

if __name__ == "__main__":
    process_marvel_rivals_roster()
