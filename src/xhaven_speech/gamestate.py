import json
import jsondiff
from os import name

from numpy import char

"""
Create a gamestate class that will hold all the information about the current gamestate.
- Method to update gamestate with a new gamestate from Frosthaven Application
- Update character information (health and initiative)
- Update monster information (health, conditions, and status)
- Send toastmessage to Frosthaven Application
"""
class GameState:
    def __init__(self, new_gamestate):
        self.set_gamestate(new_gamestate)

        print("init done")

        
        
    def set_gamestate(self, new_gamestate):
        # Method to update gamestate with a new gamestate from Frosthaven Application
        tmp = new_gamestate
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
        
        self.characters = []
        self.monsters = []
        
        # Loop through all characters and monsters in currentList and create objects for them
        for item in self.currentList:
            if "characterState" in item:
                self.characters.append(Characters(item))
            elif "monsterInstances" in item:
                self.monsters.append(Monsters(item))
                
        # Compare tmp with output from get_gamestate and assert critical error if they are not equal
        # DOES NOT WORK YET
        #if jsondiff.diff(tmp, self.get_gamestate()) != {}:
        #    raise AssertionError("Critical error: input and output to gamestate class are not equal.")
        

    def update_character_information(self, character_id, health, initiative):
        # Update character information (health and initiative)
        pass

    def update_monster_information(self, monster_id, health, conditions, status):
        # Update monster information (health, conditions, and status)
        pass

    def send_toast_message(self, message):
        # Send toast message to Frosthaven Application
        pass

    def get_gamestate(self):
        # Method to get gamestate from Frosthaven Application
        self.currentList = []
        for character in self.characters:
            self.currentList.append(character.get_character())
        for monster in self.monsters:
            self.currentList.append(monster.get_monster())
            
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
            "elementState": self.elementState,
        }

        return json.dumps(gamestate_dict)


class Characters:
    def __init__(self, character_dict):
        self.id = character_dict.get("id")
        self.turnState = character_dict.get("turnState")
        self.characterState = self.CharacterState(character_dict.get("characterState"))
        self.characterClass = character_dict.get("characterClass")
        
        print(f"Character {self.characterClass} created")
        
    def get_character(self):
        character_dict = {
            "id": self.id,
            "turnState": self.turnState,
            "characterState": self.characterState.get_characterstate(),
            "characterClass": self.characterClass,
        }
        return character_dict
    
    def update_initiative(self, initiative):
        self.characterState.initiative = initiative


    class CharacterState:
        def __init__(self, character_state_dict):
            self.initiative = character_state_dict.get("initiative")
            self.health = character_state_dict.get("health")
            self.maxHealth = character_state_dict.get("maxHealth")
            self.level = character_state_dict.get("level")
            self.xp = character_state_dict.get("xp")
            self.chill = character_state_dict.get("chill")
            self.display = character_state_dict.get("display")
            self.summonList = character_state_dict.get("summonList")
            self.conditions = character_state_dict.get("conditions")
            self.conditionsAddedThisTurn = character_state_dict.get("conditionsAddedThisTurn")
            self.conditionsAddedPreviousTurn = character_state_dict.get("conditionsAddedPreviousTurn")
            
        def get_characterstate(self):
            character_state_dict = {
                "initiative": self.initiative,
                "health": self.health,
                "maxHealth": self.maxHealth,
                "level": self.level,
                "xp": self.xp,
                "chill": self.chill,
                "display": self.display,
                "summonList": self.summonList,
                "conditions": self.conditions,
                "conditionsAddedThisTurn": self.conditionsAddedThisTurn,
                "conditionsAddedPreviousTurn": self.conditionsAddedPreviousTurn,
            }
            return character_state_dict


class Monsters:
    def __init__(self, monster_dict):
        self.monster_instances = []
        self.id = monster_dict.get("id")
        self.turnState = monster_dict.get("turnState")
        self.isActive = monster_dict.get("isActive")
        self.type = monster_dict.get("type")
        for monster in monster_dict.get("monsterInstances"):
            self.monster_instances.append(self.MonsterInstances(monster))
        self.isAlly = monster_dict.get("isAlly")
        self.level = monster_dict.get("level")
        
        print(f"Monster {self.type} created")
        
    def get_monster(self):
        _monster_instances = []
        for monster in self.monster_instances:
            _monster_instances.append(monster.get_monsterinstances())
        monster_dict = {
            "id": self.id,
            "turnState": self.turnState,
            "isActive": self.isActive,
            "type": self.type,
            "monsterInstances": _monster_instances, # List of MonsterInstances
            "isAlly": self.isAlly,
            "level": self.level,
        }
        return monster_dict


    class MonsterInstances:
        def __init__(self, monster_instances_dict):
            self.health = monster_instances_dict.get("health")
            self.maxHealth = monster_instances_dict.get("maxHealth")
            self.level = monster_instances_dict.get("level")
            self.standeeNr = monster_instances_dict.get("standeeNr")
            self.move = monster_instances_dict.get("move")
            self.attack = monster_instances_dict.get("attack")
            self.range = monster_instances_dict.get("range")
            self.name = monster_instances_dict.get("name")
            self.gfx = monster_instances_dict.get("gfx")
            self.roundSummoned = monster_instances_dict.get("roundSummoned")
            self.type = monster_instances_dict.get("type")
            self.chill = monster_instances_dict.get("chill")
            self.conditions = monster_instances_dict.get("conditions")
            self.conditionsAddedThisTurn = monster_instances_dict.get("conditionsAddedThisTurn")
            self.conditionsAddedPreviousTurn = monster_instances_dict.get("conditionsAddedPreviousTurn")
            
        def get_monsterinstances(self):
            monster_instances_dict = {
                "health": self.health,
                "maxHealth": self.maxHealth,
                "level": self.level,
                "standeeNr": self.standeeNr,
                "move": self.move,
                "attack": self.attack,
                "range": self.range,
                "name": self.name,
                "gfx": self.gfx,
                "roundSummoned": self.roundSummoned,
                "type": self.type,
                "chill": self.chill,
                "conditions": self.conditions,
                "conditionsAddedThisTurn": self.conditionsAddedThisTurn,
                "conditionsAddedPreviousTurn": self.conditionsAddedPreviousTurn,
            }
            return monster_instances_dict
