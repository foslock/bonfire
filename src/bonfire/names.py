import random

PROPER_NOUNS = [
    "Aldric", "Brynn", "Cedwyn", "Dorath", "Elara", "Faelan", "Gwynneth",
    "Haldor", "Isolde", "Jareth", "Kaylor", "Lucan", "Morwen", "Nythara",
    "Osric", "Percival", "Quelwyn", "Raegis", "Solaire", "Theron", "Undine",
    "Vaelith", "Wynne", "Xandros", "Ysolde", "Zarek", "Anri", "Benhart",
    "Creighton", "Dranoc", "Eygon", "Felkin", "Gavlan", "Hawkwood",
    "Irina", "Jester", "Karla", "Leonhard", "Maldron", "Nashandra",
    "Orbeck", "Patches", "Quelana", "Rosabeth", "Siegward", "Tarkus",
    "Velstadt", "Wolnir", "Artorias", "Ciaran",
]

ADJECTIVES = [
    "Benevolent", "Cursed", "Dauntless", "Exiled", "Forsaken", "Gallant",
    "Hollow", "Ironclad", "Judicious", "Kindled", "Lost", "Mournful",
    "Noble", "Obscure", "Patient", "Quiet", "Resolute", "Stalwart",
    "Tenacious", "Undying", "Valiant", "Watchful", "Zealous", "Ashen",
    "Brave", "Crestfallen", "Devout", "Embered", "Faithful", "Grim",
    "Honorable", "Intrepid", "Keen", "Lordly", "Masked", "Nameless",
    "Ordained", "Penitent", "Risen", "Silent", "Twilight", "Unbowed",
    "Verdant", "Weary", "Yielding", "Abyssal", "Sunsworn", "Darkwraith",
    "Forlorn", "Unkindled",
]


def generate_knight_name() -> str:
    noun = random.choice(PROPER_NOUNS)
    adj = random.choice(ADJECTIVES)
    return f"{noun} the {adj}"
