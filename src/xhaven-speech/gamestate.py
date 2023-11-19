import json
"""
Create a gamestate class that will hold all the information about the current gamestate.
- Method to update gamestate with a new gamestate from Frosthaven Application
- Gamestate shall contain the following information:
-- "level"
-- "solo"
-- "roundState"
-- "round"
-- "scenario"
-- "toastMessage"
-- "scenarioSpecialRules"
-- "scenarioSectionsAdded"
-- "currentCampaign"
-- "currentList"
-- "currentAbilityDecks"
-- "modifierDeck"
-- "modifierDeckAllies"
-- "lootDeck"
-- "unlockedClasses"
-- "showAllyDeck"
-- "elementState"
- "currentList" shall contain the following information:
-- List of characters with their information
-- List of monsters with their information
- Update character information (health and initiative)
- Update monster information (health, conditions, and status)
- Send toastmessage to Frosthaven Application
"""

class Character:
    def __init__(self):
        self.id = None
        self.turnState = None
        self.characterState = None
        self.characterClass = None

class CharacterState:
    def __init__(self):
        self.initiative = None
        self.health = None
        self.maxHealth = None
        self.level = None
        self.xp = None
        self.chill = None
        self.disarm = None
        self.summonList = None
        self.conditions = None
        self.conditionsAddedThisTurn = None
        self.conditionsAddedPreviousTurn = None

class Monster:
    def __init__(self):
        self.id = None
        self.turnState = None
        self.isActive = None
        self.type = None
        self.monsteerInstances = None
        self.isAlly = None
        self.level = None
class MonsterInstances:
    def __init__(self):
        self.health = None
        self.maxHealth = None
        self.level = None
        self.standeeNr = None
        self.move = None
        self.attack = None
        self.range = None
        self.conditions = None
        self.conditionsAddedThisTurn = None
        self.conditionsAddedPreviousTurn = None

class GameState:
    def __init__(self):
        self.level = None
        self.solo = None
        self.roundState = None
        self.round = None
        self.scenario = None
        self.toastMessage = None
        self.scenarioSpecialRules = None
        self.scenarioSectionsAdded = None
        self.currentCampaign = None
        self.currentList = None
        self.currentAbilityDecks = None
        self.modifierDeck = None
        self.modifierDeckAllies = None
        self.lootDeck = None
        self.unlockedClasses = None
        self.showAllyDeck = None
        self.elementState = None

    def get_gamestate(self):
        # Method to get gamestate from Frosthaven Application
        gamestate_dict = {
            "level": self.level,
            "solo": self.solo,
            "roundState": self.roundState,
            "round": self.round,
            "scenario": self.scenario,
            "toastMessage": self.toastMessage,
            "scenarioSpecialRules": self.scenarioSpecialRules,
            "scenarioSectionsAdded": self.scenarioSectionsAdded,
            "currentCampaign": self.currentCampaign,
            "currentList": self.currentList,
            "currentAbilityDecks": self.currentAbilityDecks,
            "modifierDeck": self.modifierDeck,
            "modifierDeckAllies": self.modifierDeckAllies,
            "lootDeck": self.lootDeck,
            "unlockedClasses": self.unlockedClasses,
            "showAllyDeck": self.showAllyDeck,
            "elementState": self.elementState
        }
        
        return json.dumps(gamestate_dict)
        

    def update_gamestate(self, new_gamestate):
        # Method to update gamestate with a new gamestate from Frosthaven Application
        gamestate_dict = json.loads(new_gamestate)
        
        self.level = gamestate_dict.get("level")
        self.solo = gamestate_dict.get("solo")
        self.roundState = gamestate_dict.get("roundState")
        self.round = gamestate_dict.get("round")
        self.scenario = gamestate_dict.get("scenario")
        self.toastMessage = gamestate_dict.get("toastMessage")
        self.scenarioSpecialRules = gamestate_dict.get("scenarioSpecialRules")
        self.scenarioSectionsAdded = gamestate_dict.get("scenarioSectionsAdded")
        self.currentCampaign = gamestate_dict.get("currentCampaign")
        self.currentList = gamestate_dict.get("currentList")
        self.currentAbilityDecks = gamestate_dict.get("currentAbilityDecks")
        self.modifierDeck = gamestate_dict.get("modifierDeck")
        self.modifierDeckAllies = gamestate_dict.get("modifierDeckAllies")
        self.lootDeck = gamestate_dict.get("lootDeck")
        self.unlockedClasses = gamestate_dict.get("unlockedClasses")
        self.showAllyDeck = gamestate_dict.get("showAllyDeck")
        self.elementState = gamestate_dict.get("elementState")
        

    def update_character_information(self, character_id, health, initiative):
        # Update character information (health and initiative)
        pass

    def update_monster_information(self, monster_id, health, conditions, status):
        # Update monster information (health, conditions, and status)
        pass

    def send_toast_message(self, message):
        # Send toast message to Frosthaven Application
        pass


