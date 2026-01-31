import requests
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()
token = os.getenv("DISCORD_TOKEN")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

# ============================================================================
# API HELPER FUNCTIONS
# ============================================================================


def search_taxa(animal_name, limit=10):
    """
    Searches for taxa matching the given animal name.

    Args:
        animal_name: The animal name to search for
        limit: Number of results to return

    Returns:
        list: list of taxon dictionaries found or empty list if none found
    """
    base_url = "https://api.inaturalist.org/v1/taxa"

    # From https://api.inaturalist.org/v1/docs/
    params = {
        "q": animal_name,
        "per_page": limit,
        "is_active": "true",
        "iconic_taxa": "Animalia",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["total_results"] == 0:
            return []

        animal_results = []
        for taxon in data["results"]:
            iconic_taxon = taxon.get("iconic_taxon_name", "")
            if iconic_taxon not in ["Plantae", "Fungi", "Chromista", "Protozoa"]:
                animal_results.append(taxon)

        return animal_results[:limit]

    except requests.exceptions.RequestException as e:
        print(f"Taxa search failed: {e}")
        return []


def find_best_taxon_id(animal_name):
    """
    Ranks taxon ID search results to find the best match for an animal name.
    Rankings:
    1. Exact common name match
    2. Exact scientific name match
    3. Partial common name match
        a) Species rank
        b) Other ranks (genus, family, etc.)
    4. First result from original search

    Args:
        animal_name: The animal name to search for

    Returns:
        str: Best matching taxon ID or None if not found
    """
    animal_results = search_taxa(animal_name, limit=20)

    if not animal_results:
        return None

    animal_name_lower = animal_name.lower()

    # 1: Exact common name match
    for taxon in animal_results:
        common_name = taxon.get("preferred_common_name", "").lower()
        if common_name == animal_name_lower:
            print(
                f"Found exact common name match: {taxon['name']} ({taxon.get('preferred_common_name')})"
            )
            return taxon["id"]

    # 2: Exact scientific name match
    for taxon in animal_results:
        scientific_name = taxon["name"].lower()
        if scientific_name == animal_name_lower:
            print(f"Found exact scientific name match: {taxon['name']}")
            return taxon["id"]

    # 3: Partial common name match
    species_matches = []
    other_matches = []

    for taxon in animal_results:
        common_name = taxon.get("preferred_common_name", "").lower()

        if animal_name_lower in common_name:
            if taxon["rank"] == "species":
                species_matches.append(taxon)
            else:
                other_matches.append(taxon)

    # a) Species rank
    if species_matches:
        print(
            f"Found species-level partial match: {species_matches[0]['name']} ({species_matches[0].get('preferred_common_name')})"
        )
        return species_matches[0]["id"]

    # b) Other ranks
    if other_matches:
        print(
            f"Found partial match: {other_matches[0]['name']} ({other_matches[0].get('preferred_common_name')})"
        )
        return other_matches[0]["id"]

    # 4: First result from original search
    print(
        f"No exact match, using first animal result: {animal_results[0]['name']} ({animal_results[0].get('preferred_common_name')})"
    )
    return animal_results[0]["id"]


def get_random_observation(taxon_id, photo_required=True):
    """
    Gets a random observation from iNaturalist for a given animal.

    Args:
        taxon_id: The taxon ID to search for
        photo_required: Only return observations with photos

    Returns:
       dict: Observation data dictionary or None if not found
    """
    base_url = "https://api.inaturalist.org/v1/observations"

    params = {
        "taxon_id": taxon_id,
        "photos": "true" if photo_required else "false",
        "quality_grade": "research",
        "per_page": 100,
        "order_by": "random",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["total_results"] == 0:
            return None

        observations = data["results"]

        if not observations:
            return None

        observation = random.choice(observations)
        return observation

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


# ============================================================================
# BOT COMMANDS
# ============================================================================


@bot.command(
    name="animal",
    help="Sends a random wildlife sighting photo of any animal. Usage: !animal [animal_name]",
)
async def random_animal(ctx, *, animal_name: str):
    """
    Discord command that sends a random wildlife sighting photo for any animal.
    Includes common name, scientific name, location, date, observer, and link to original iNaturalist page.

    Args:
        ctx: Discord message context argument
        animal_name: The animal name to search for
    """
    await ctx.send(f"🔍 On it! Searching for {animal_name} sightings...")

    taxon_id = find_best_taxon_id(animal_name)

    if taxon_id is None:
        await ctx.send(
            f"Sorry, couldn't find any animal matching '{animal_name}' in the database. Try !taxonhelp {animal_name} for suggestions."
        )
        return

    observation = get_random_observation(taxon_id)

    if observation is None:
        await ctx.send(
            f"Sorry, couldn't find any {animal_name} observations. Check your spelling or try !taxonhelp {animal_name}."
        )
        return

    photo_url = observation["photos"][0]["url"].replace("square", "medium")
    place = observation.get("place_guess", "Unknown location")
    observer = observation["user"]["login"]
    obs_url = f"https://www.inaturalist.org/observations/{observation['id']}"
    observed_on = observation.get("observed_on_string", "Unknown date")

    species_name = observation["taxon"]["name"]
    common_name = observation["taxon"].get("preferred_common_name", species_name)

    embed = discord.Embed(
        title=f"🐾 Random {common_name.title()} Sighting",
        description=f"*{species_name}*\nObserved on {observed_on}",
        color=0x74AC00,  # iNaturalist brand color
        url=obs_url,
    )

    embed.set_image(url=photo_url)
    embed.add_field(name="Location", value=place, inline=True)
    embed.add_field(name="Observer", value=observer, inline=True)

    embed.set_footer(text=f"Not the right animal? Try !taxonhelp {animal_name}")

    await ctx.send(embed=embed)


@bot.command(
    name="taxonhelp",
    help="Shows scientific names for a given animal's common name. Usage: !taxonhelp [animal_name]",
)
async def taxon_help(ctx, *, animal_name: str):
    """
    Returns multiple taxon matches for a given animal's common name so users can find the animal they were looking for.

    Args:
        ctx: Discord message context argument
        animal_name: The animal name to search for
    """
    await ctx.send(f"🔍 On it! Searching taxonomy for '{animal_name}'...")

    animal_results = search_taxa(animal_name, limit=10)

    if not animal_results:
        await ctx.send(
            f"No taxa found for '{animal_name}'. Try checking your spelling."
        )
        return

    embed = discord.Embed(
        title=f"🔬 Taxonomy Results for '{animal_name}'",
        description="Here are the top matches. Trying using one of these scientific names for more accurate searches!",
        color=0x74AC00,
    )

    for taxon in animal_results:
        common_name = taxon.get("preferred_common_name", "No common name")
        scientific_name = taxon["name"]
        rank = taxon["rank"]

        field_name = f"{common_name} ({rank.capitalize()})"
        field_value = (
            f"Scientific: `{scientific_name}`\nTry: `!animal {scientific_name}`"
        )

        embed.add_field(name=field_name, value=field_value, inline=False)

    await ctx.send(embed=embed)


@bot.command(name="deer", help="Sends a random deer sighting photo.")
async def random_deer(ctx):
    """
    Discord command that sends a random wildlife sighting photo for deer specifically.
    Includes common name, scientific name, location, date, observer, and link to original iNaturalist page.

    Args:
        ctx: Discord message context argument
    """

    await ctx.send("🦌 Searching the forests for a deer...")

    taxon_id = find_best_taxon_id("deer")

    if taxon_id is None:
        await ctx.send(
            "Sorry, I couldn't find any deer in the forest! Please try again later."
        )
        return

    observation = get_random_observation(taxon_id)

    if observation is None:
        await ctx.send(
            "Sorry, I think the deer are really good at hiding. Try again later!"
        )
        return

    photo_url = observation["photos"][0]["url"].replace("square", "medium")
    place = observation.get("place_guess", "Unknown location")
    observer = observation["user"]["login"]
    obs_url = f"https://www.inaturalist.org/observations/{observation['id']}"
    observed_on = observation.get("observed_on_string", "Unknown date")

    embed = discord.Embed(
        title="🦌 BLEAT!",
        description=f"Observed on {observed_on}",
        color=0x74AC00,
        url=obs_url,
    )

    embed.set_image(url=photo_url)
    embed.add_field(name="Location", value=place, inline=True)
    embed.add_field(name="Observer", value=observer, inline=True)

    await ctx.send(embed=embed)


# ============================================================================


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


bot.run(token)
