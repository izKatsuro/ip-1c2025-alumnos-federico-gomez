# capa de servicio/lógica de negocio

from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user

# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages():
    # debe ejecutar los siguientes pasos:
    # 1) traer un listado de imágenes crudas desde la API (ver transport.py)
    pokeImages = transport.getAllImages()
    images = []
    for poke in pokeImages:  
        # 2) convertir cada img. en una card.      
        card = translator.fromRequestIntoCard(poke)
        types = card.types
        type_icons = []
        for t in types:
            icon_url = get_type_icon_url_by_name(t)
            if icon_url:
                icon_img = f'<img src="{icon_url}" alt="{t}" title="{t}" height="24" />'
                type_icons.append(icon_img)
        card.types = type_icons
        first_type = types[0] if types else 'other' 
        card.border_class = "border-warning"     
        if first_type == "grass":
            card.border_class = "border-success"
        if first_type == "fire":
            card.border_class = "border-danger"
        if first_type == "water":
            card.border_class = "border-primary" 
        # Guardamos los types como texto para usarlos como filtro mas adelante ya que el existente lo cambiamos  
        card.typestext = types  
        # 3) añadirlas a un nuevo listado que, finalmente, se retornará con todas las card encontradas.
        images.append(card)
    return images
    #pass

# función que filtra según el nombre del pokemon.
def filterByCharacter(name):
    filtered_cards = []

    for card in getAllImages():
        # debe verificar si el name está contenido en el nombre de la card, antes de agregarlo al listado de filtered_cards.
        # hacemos lower todos los valores tanto el escrito como el que viene por la api para realizar el match
        if name.lower() in card.name.lower():
            filtered_cards.append(card)

    return filtered_cards

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    filtered_cards = []
    type_filter = type_filter.lower()  # normalizamos por si el valor, viene mal formateado

    for card in getAllImages():
        if type_filter in [t.lower() for t in card.typestext]: #comparamos haciendo lower tambien al valor que viene de la api
            filtered_cards.append(card)

    return filtered_cards

# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request):
    fav = translator.fromTemplateIntoCard(request) # transformamos un request en una Card (ver translator.py)
    fav.user = get_user(request) # le asignamos el usuario correspondiente.

    return repositories.save_favourite(fav) # lo guardamos en la BD.

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    if not request.user.is_authenticated:
        return []
    else:
        user = get_user(request)

        favourite_list = repositories.get_all_favourites(user) # buscamos desde el repositories.py TODOS Los favoritos del usuario (variable 'user').
        mapped_favourites = []

        for favourite in favourite_list:
            #print(favourite)
            card = translator.fromFavouriteIntoCard(favourite) # convertimos cada favorito en una Card, y lo almacenamos en el listado de mapped_favourites que luego se retorna.
            mapped_favourites.append(card)

        return mapped_favourites

def deleteFavourite(request):
    favId = request.POST.get('id')
    return repositories.delete_favourite(favId) # borramos un favorito por su ID

#obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    #print(transport.get_type_icon_url_by_id(type_id))
    return transport.get_type_icon_url_by_id(type_id)