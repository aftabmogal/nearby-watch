"""Seeds demo data so the map isn't empty on first run.

Run with:  python -m app.seed

IMPORTANT: change CENTER_LAT / CENTER_LNG below to your own city's
coordinates before running, or the demo posts will show up around Mumbai.
"""

import asyncio

from app.core.security import hash_password
from app.database import init_db
from app.models.post import GeoJSONPoint, Post
from app.models.user import User

# Mumbai, India — change to your city's coordinates.
CENTER_LAT = 19.0674419
CENTER_LNG = 72.8789000

DEMO_USER_EMAIL = "demo@localfinder.dev"
DEMO_USER_PASSWORD = "Demo@1234"

# (lat_offset, lng_offset) is roughly in degrees; ~0.01 deg ~= 1.1km
DEMO_POSTS = [
    {
        "type": "lost_pet",
        "title": "Lost golden retriever near Bandstand",
        "description": "Answers to 'Bruno', last seen near Bandra Bandstand wearing a red collar. Very friendly, please call if spotted.",
        "address_label": "Bandra Bandstand",
        "offset": (0.010, 0.008),
    },
    {
        "type": "found_item",
        "title": "Found a set of keys with a blue keychain",
        "description": "Found near Andheri station gate 2. Small blue elephant keychain, 3 keys.",
        "address_label": "Andheri Station, Gate 2",
        "offset": (-0.022, 0.015),
    },
    {
        "type": "lost_item",
        "title": "Lost black backpack on the 42 bus route",
        "description": "Contains a laptop and some notebooks. Left it on the bus around 6pm.",
        "address_label": "Near Kurla Bus Depot",
        "offset": (0.031, -0.020),
    },
    {
        "type": "alert",
        "title": "Streetlight out on Linking Road, be careful at night",
        "description": "The stretch near the flyover has been dark for a week. Watch your step.",
        "address_label": "Linking Road",
        "offset": (0.004, 0.022),
    },
    {
        "type": "lost_pet",
        "title": "Missing orange tabby cat, 'Simba'",
        "description": "Indoor cat, got out through a window. Skittish around strangers.",
        "address_label": "Khar West",
        "offset": (-0.008, -0.012),
    },
    {
        "type": "found_item",
        "title": "Found a wallet near the market",
        "description": "Has an ID card and some cash. Trying to reach the owner directly.",
        "address_label": "Bandra Market",
        "offset": (0.015, 0.003),
    },
    {
        "type": "lost_item",
        "title": "Lost prescription glasses in a brown case",
        "description": "Tortoiseshell frames, brown hard case with a pharmacy logo.",
        "address_label": "Near Carter Road",
        "offset": (0.006, -0.018),
    },
    {
        "type": "alert",
        "title": "Loose stray dog pack near the park, exercise caution",
        "description": "A group of 3-4 dogs has been more aggressive than usual this week.",
        "address_label": "Joggers Park",
        "offset": (-0.014, 0.009),
    },
    {
        "type": "lost_pet",
        "title": "Lost parrot, green with a yellow head",
        "description": "Flew off from an open balcony. Responds to whistling.",
        "address_label": "Santacruz West",
        "offset": (0.024, 0.011),
    },
    {
        "type": "found_item",
        "title": "Found a kid's bicycle, unlocked, near the school",
        "description": "Left leaning against the fence for two days now. Holding it at the school office.",
        "address_label": "Near St. Andrew's School",
        "offset": (-0.019, -0.006),
    },
    {
        "type": "lost_item",
        "title": "Lost a silver bracelet with an engraved name",
        "description": "Sentimental value — engraved 'Aria'. Lost somewhere between the station and the mall.",
        "address_label": "Near Infinity Mall",
        "offset": (0.002, 0.017),
    },
    {
        "type": "alert",
        "title": "Water-logging reported on the service road",
        "description": "Ankle-deep water after the rain, avoid two-wheelers on this stretch tonight.",
        "address_label": "SV Road service lane",
        "offset": (-0.005, 0.020),
    },
    {
        "type": "lost_pet",
        "title": "Lost small white dog, no collar",
        "description": "Very small, possibly a Pomeranian mix. Scared of loud noises.",
        "address_label": "Near Chimbai Village",
        "offset": (0.018, -0.009),
    },
    {
        "type": "found_item",
        "title": "Found a phone with a cracked screen",
        "description": "Locked, but has a distinctive floral case. Left a note on it in case owner passes by.",
        "address_label": "Near Turner Road",
        "offset": (-0.011, 0.013),
    },
    {
        "type": "lost_item",
        "title": "Lost a folder of important documents",
        "description": "Blue folder, mostly ID copies and a rental agreement. Please reach out if found.",
        "address_label": "Near Bandra Talao",
        "offset": (0.009, -0.021),
    },
]


async def seed() -> None:
    await init_db()

    demo_user = await User.find_one(User.email == DEMO_USER_EMAIL)
    if not demo_user:
        demo_user = User(
            email=DEMO_USER_EMAIL,
            name="Demo Reporter",
            hashed_password=hash_password(DEMO_USER_PASSWORD),
            is_verified=True,
        )
        await demo_user.insert()
        print(f"Created demo user: {DEMO_USER_EMAIL} / {DEMO_USER_PASSWORD}")

    already = await Post.find(Post.author_id == demo_user.id).count()
    if already > 0:
        print(f"Seed data already present ({already} posts). Skipping — delete them first to reseed.")
        return

    for item in DEMO_POSTS:
        lat = CENTER_LAT + item["offset"][0]
        lng = CENTER_LNG + item["offset"][1]
        post = Post(
            author_id=demo_user.id,
            type=item["type"],
            title=item["title"],
            description=item["description"],
            location=GeoJSONPoint(coordinates=[lng, lat]),
            address_label=item["address_label"],
        )
        await post.insert()

    print(f"Seeded {len(DEMO_POSTS)} demo posts around ({CENTER_LAT}, {CENTER_LNG}).")


if __name__ == "__main__":
    asyncio.run(seed())
