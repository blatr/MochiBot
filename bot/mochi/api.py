import httpx


class MochiClient:
    def __init__(self, client, token: str):
        self.token = token
        self.base_url = "https://app.mochi.cards/"
        self.headers = {"Content-Type": "application/json"}
        self.client = client

    async def list_all_decks(self):
        decks_list = await self.client.get(
            "https://app.mochi.cards/api/decks/",
            auth=(self.token, ""),
            headers={"Content-Type": "application/json"},
        )
        deck_entries = []
        for deck in decks_list.json()["docs"]:
            template_entry = None
            if 'template-id' in deck:
                template_entry = await self.get_template(deck["template-id"])
            deck_entries.append(Deck(**deck, template=template_entry))
        return deck_entries

    async def get_template(self, template_id):
        template = await self.client.get(
            f"https://app.mochi.cards/api/templates/{template_id}",
            auth=(self.token, ""),
            headers={"Content-Type": "application/json"},
        )
        return Template(**template.json())

    async def add_card(self, card):
        return await self.client.post(
            "https://app.mochi.cards/api/cards/",
            auth=(self.token, ""),
            headers={"Content-Type": "application/json"},
            json=card.json(),
        )


class Deck:
    def __init__(self, id, name, template, **kwargs):
        self.id = id
        self.name = name
        self.template = template
    
    def __str__(self):
        return f"Deck {self.name} with template {self.template.name}"


class Template:
    def __init__(self, id, name, fields, content, **kwargs):
        self.id = id
        self.name = name
        self.fields = [Field(**fields[field]) for field in fields]
        self.content = content
    
    def __str__(self):
        return f"Template {self.name} with {len(self.fields)} fields"


class Field:
    def __init__(self, id, name, value=None, **kwargs):
        self.id = id
        self.name = name
        self.value = value

    def add_value(self, value):
        self.value = value

    def json(self):
        return {"id": self.id, "value": self.value if self.value != '.' else ""}
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class Card:
    def __init__(self, deck, **kwargs):
        self.deck = deck

    def add_field_value(self, field_name, value):
        for field in self.deck.template.fields:
            if field.name == field_name:
                field.add_value(value)
                return

    def json(self):
        return {
            "content": self.deck.template.content,
            "deck-id": self.deck.id,
            "template-id": self.deck.template.id,
            "fields": {field.id:field.json() for field in self.deck.template.fields},
            "review-reverse?": True,
            "archived?": False,
        }
    
    def get_next_empty_field(self):
        for field in self.deck.template.fields:
            if field.value is None:
                return field
        return None

    def __str__(self):
        return f"Card for deck {self.deck.name} with {len(self.deck.template.fields)} fields"

def get_deck_by_name(decks_list, deck_name):
    for deck in decks_list:
        if deck.name == deck_name:
            return deck
    return None
