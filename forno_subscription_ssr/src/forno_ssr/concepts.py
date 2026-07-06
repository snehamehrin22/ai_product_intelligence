"""
3 subscription concepts for Forno Cultura King Street location.

Each concept targets different customer behaviors and value propositions.
"""

from .schemas import SubscriptionConcept


# Define all 3 concepts
CONCEPTS = [
    SubscriptionConcept(
        concept_id="c1",
        name="King West Sandwich + Coffee Pass",
        description="""
A monthly pass for lunch regulars at Forno Cultura King Street.

WHAT'S INCLUDED:
• 8 panini sandwiches per month (any from daily menu)
• 8 premium coffees (espresso drinks, pour-over, or drip)
• Valid Monday-Friday, lunch hours (11am-3pm)
• No expiry - unused items roll over to next month for up to 60 days

PRICING: $120/month
- Regular price would be: 8 sandwiches ($12 ea) + 8 coffees ($4-5 ea) = $128-$136
- You save: $8-16/month, plus convenience of never waiting in line
        """.strip(),
        price_point="$120/month (save $8-16 vs regular pricing)",
        value_props=[
            "Skip the line - priority pickup for pass holders",
            "Flexibility - use when you want, items roll over",
            "Guaranteed availability - your lunch is reserved",
            "Works out to $15 per lunch combo vs $16-17 regular"
        ],
        target_behavior="Lunch regulars who visit 2+ times per week during work hours"
    ),

    SubscriptionConcept(
        concept_id="c2",
        name="King West Bread & Pantry Box",
        description="""
Weekly curated box of Forno's best baked goods and pantry items for home.

WHAT'S INCLUDED (delivered or pickup every Saturday):
• 1 large sourdough loaf (choice of regular or whole wheat)
• 1 focaccia (rotating flavors - rosemary, olive, garlic & herb)
• 2 pastries or sweets (seasonal selection)
• 1 pantry item (olive oil, jam, honey, or specialty item - rotates monthly)
• Recipe card featuring ways to use your items

PRICING: $55/week ($220/month for 4 deliveries)
- Comparable retail value: $65-70/week
- You save: $40-60/month, plus curated selection
        """.strip(),
        price_point="$55/week ($220/month), save $40-60/month",
        value_props=[
            "Never run out of fresh bread - weekly delivery to your door or ready for Saturday pickup",
            "Discover new items - curated selection changes with seasons",
            "Premium quality - Forno's signature sourdough and artisan baking",
            "Giftable - easily pause or send as gift to friends/family",
            "Save 15-20% vs buying these items separately"
        ],
        target_behavior="Weekend bread buyers and home cooks who value quality ingredients"
    ),

    SubscriptionConcept(
        concept_id="c3",
        name="Underground Regulars Club",
        description="""
A membership for Forno Cultura's most loyal King Street customers.

WHAT'S INCLUDED:
• 15% off all food & drink purchases at King Street location
• Free upgrade on coffee (drip → latte, latte → specialty drink)
• First access to new menu items and seasonal specials
• Monthly members-only tasting event (Thursday evenings, 6-7:30pm)
• Quarterly focaccia or sourdough-making workshop
• Bring a friend for free once per month

PRICING: $35/month
- Break-even: ~$235 in monthly purchases (most regulars spend more)
- Plus experiential benefits (tastings, workshops, community)
        """.strip(),
        price_point="$35/month (break-even at $235/month spending)",
        value_props=[
            "Pays for itself if you spend $50+/week at Forno",
            "Exclusive access - monthly tastings in the underground bakery space",
            "Learn from the bakers - hands-on workshops quarterly",
            "Community - meet other regulars at member events",
            "Flexibility - use as much or as little as you want"
        ],
        target_behavior="Super-fans who visit frequently and want community/experience beyond just transactions"
    ),
]


def get_concept_by_id(concept_id: str) -> SubscriptionConcept:
    """Retrieve a concept by ID."""
    for concept in CONCEPTS:
        if concept.concept_id == concept_id:
            return concept
    raise ValueError(f"Concept {concept_id} not found")


def get_all_concepts() -> list[SubscriptionConcept]:
    """Get all concepts."""
    return CONCEPTS
