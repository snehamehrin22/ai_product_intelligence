"""
8 King Street personas based on observed Forno Cultura customer types.

These represent the mix of office workers, creatives, students, locals,
and food enthusiasts who frequent the King West location.
"""

from .schemas import Persona, IncomeLevel


# Define all 8 personas
PERSONAS = [
    Persona(
        persona_id="p1",
        age=27,
        role="software engineer at a King West startup",
        income_level=IncomeLevel.COMFORTABLE,
        visit_frequency="3-4 lunches per week",
        current_behavior="gets panini and cappuccino for lunch, sometimes works there in afternoon",
        location="works on King West, lives in Liberty Village"
    ),

    Persona(
        persona_id="p2",
        age=34,
        role="creative director at advertising agency",
        income_level=IncomeLevel.AFFLUENT,
        visit_frequency="2 times per week (lunch + weekend)",
        current_behavior="buys sourdough bread and pastries on weekends, occasional lunch meetings",
        location="works downtown, lives in Trinity Bellwoods"
    ),

    Persona(
        persona_id="p3",
        age=22,
        role="design student at OCAD",
        income_level=IncomeLevel.STRUGGLING,
        visit_frequency="2-3 afternoons per week",
        current_behavior="gets a latte and sometimes a cookie, sits and studies for a few hours",
        location="student, lives near campus"
    ),

    Persona(
        persona_id="p4",
        age=42,
        role="couple (one works in finance, one is a teacher)",
        income_level=IncomeLevel.AFFLUENT,
        visit_frequency="once per week on Friday evenings",
        current_behavior="picks up fresh bread and focaccia on way to weekend dinner plans",
        location="lives in Parkdale, King West is on their route"
    ),

    Persona(
        persona_id="p5",
        age=30,
        role="remote tech worker (works from home)",
        income_level=IncomeLevel.COMFORTABLE,
        visit_frequency="4-5 times per week for coffee",
        current_behavior="walks to Forno for morning coffee as part of work-from-home routine, sometimes gets sandwich for lunch",
        location="lives in King West neighborhood"
    ),

    Persona(
        persona_id="p6",
        age=48,
        role="local resident, works in healthcare",
        income_level=IncomeLevel.MANAGING,
        visit_frequency="Saturday mornings, occasionally one weeknight",
        current_behavior="weekend ritual: buys sourdough and pastries for family breakfast",
        location="lives in the neighborhood, shops locally"
    ),

    Persona(
        persona_id="p7",
        age=26,
        role="fitness instructor / personal trainer",
        income_level=IncomeLevel.MANAGING,
        visit_frequency="once or twice per week, sporadic",
        current_behavior="post-workout treat - gets espresso and occasionally a healthier option",
        location="trains clients in King West area gyms"
    ),

    Persona(
        persona_id="p8",
        age=56,
        role="food writer and consultant",
        income_level=IncomeLevel.AFFLUENT,
        visit_frequency="1-2 times per week, but loyal for years",
        current_behavior="comes for specific items (their focaccia, specialty breads), often brings visiting food industry friends",
        location="lives in Roncesvalles, makes special trips to Forno"
    ),

    # NEW PERSONAS - Added June 15, 2026 based on King West demographic analysis

    Persona(
        persona_id="p9",
        age=29,
        role="financial analyst commuting to Financial District",
        income_level=IncomeLevel.COMFORTABLE,
        visit_frequency="5 mornings per week (7:30-8:30am)",
        current_behavior="grabs coffee and croissant before heading to office, quick 5-minute transaction, avoids office coffee",
        location="commutes from Leslieville, stops at Forno on way to Bay Street office"
    ),

    Persona(
        persona_id="p10",
        age=35,
        role="account executive at SaaS company (sales/business development)",
        income_level=IncomeLevel.AFFLUENT,
        visit_frequency="2-3 client coffee meetings per week",
        current_behavior="uses Forno as neutral ground for sales calls and client meetings, usually 10am-2pm slots, stays 45-90 minutes",
        location="works hybrid from King West condo, needs professional meeting space"
    ),

    Persona(
        persona_id="p11",
        age=28,
        role="product designer at Shopify (works next door at King-Portland Centre)",
        income_level=IncomeLevel.COMFORTABLE,
        visit_frequency="daily coffee, 2-3 lunches per week, occasional afternoon break",
        current_behavior="walks 1 minute from office for morning coffee, team lunches, afternoon escape from open office",
        location="works at 602-620 King West, lives in Liberty Village"
    ),

    Persona(
        persona_id="p12",
        age=32,
        role="marketing manager working fully remote",
        income_level=IncomeLevel.COMFORTABLE,
        visit_frequency="4-5 times per week (morning coffee Mon-Fri, weekend bread pickup)",
        current_behavior="morning coffee ritual to escape 650 sq ft condo, works on laptop 2-3 hours Mon/Fri, grabs bread and pantry items for small kitchen",
        location="lives in King West Entertainment District condo, no cooking space"
    ),

    Persona(
        persona_id="p13",
        age=40,
        role="corporate lawyer commuting from suburbs",
        income_level=IncomeLevel.AFFLUENT,
        visit_frequency="2-3 times per week around 6pm",
        current_behavior="stops after work to grab focaccia, bread, and panini for family dinner instead of cooking",
        location="works downtown, lives in Oakville, Forno is on commute route home"
    ),

    Persona(
        persona_id="p14",
        age=26,
        role="junior marketing coordinator",
        income_level=IncomeLevel.MANAGING,
        visit_frequency="Saturday brunch or Sunday morning, once per week",
        current_behavior="visits King West Entertainment District for nightlife and weekend brunch, comes to Forno for Instagram-worthy coffee and pastries",
        location="lives in North York, visits King West as destination on weekends"
    ),
]


def get_persona_by_id(persona_id: str) -> Persona:
    """Retrieve a persona by ID."""
    for persona in PERSONAS:
        if persona.persona_id == persona_id:
            return persona
    raise ValueError(f"Persona {persona_id} not found")


def get_all_personas() -> list[Persona]:
    """Get all personas."""
    return PERSONAS
