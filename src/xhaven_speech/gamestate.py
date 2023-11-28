import logging
import json
from math import log
import threading

from . import ClientNetwork

"""
Create a gamestate class that will hold all the information about the current gamestate.
- Method to update gamestate with a new gamestate from Frosthaven Application
- Update character information (health and initiative)
- Update monster information (health, conditions, and status)
- Send toastmessage to Frosthaven Application
"""

client_network: ClientNetwork
class GameState:
    def __init__(self):
        logging.info("Initialization done")
        self.index: int = 0
        self.description = ""
        self.lock = threading.Lock()
        # Client Network is set to None by default
        # It is set to the client network class when the client network is initialized
        self.client_network: ClientNetwork

    def set_client_network(self, client_network):
        self.client_network = client_network

    def _decode_gamestate(self, raw_gamestate_message) -> tuple[int, str, str]:
        # Helper method to decode gamestate message
        # This message is sent from the Frosthaven Application and contains the gamestate in byte format
        # It returns a tuple with the following information: index, description, gamestate
        # The incoming message is in the following format:
        # S3nD:Index:0Description::Testing DescriptionGameState:{}[EOM]
        # Where {} is the gamestate in JSON format
        # The message is split into three parts:
        # 1. Index:
        # 2. Description:
        # 3. GameState:
        # The incoming message is in bytes, so it needs to be decoded to strings
        print(type(raw_gamestate_message))
        if not b"GameState:" in raw_gamestate_message:
            raise ValueError("Invalid gamestate message")
        gamestate_index = int(
            raw_gamestate_message.split(b"Index:")[1].split(b"Description:")[0]
        )
        gamestate_description = str(
            raw_gamestate_message.split(b"Description:")[1].split(b"GameState:")[0]
        )
        gamestate_data = str(
            raw_gamestate_message.split(b"GameState:")[1].split(b"[EOM]")[0]
        )
        # Log the decoded gamestate message
        logging.info(
            f"Decoded gamestate message: {gamestate_index}, {gamestate_description}, {gamestate_data}"
        )
        return (gamestate_index, gamestate_description, gamestate_data)

    def _encode_gamestate(self, index: int, description: str, gamestate_data) -> bytes:
        # Helper method to encode gamestate message
        # This message is sent to the Frosthaven Application and contains the gamestate message
        # See _decode_gamestate for more information about the format
        # The message should be returned as bytes
        logging.info(
            f"Encoded gamestate message: {index}, {description}, {gamestate_data}"
        )
        return f"S3nD:Index:{index}Description::{description}GameState:{gamestate_data}[EOM]".encode(
            "utf-8"
        )

    def set_gamestate(self, new_gamestate):
        # Method to set the gamestate from Frosthaven Application
        # This method is called from the network class when a new gamestate is received
        # If the index is equal to the index of the current gamestate, the update from the
        # speech recognition system is invalid and should be ignored (race condition)

        with self.lock:  # Acquire the lock before modifying the gamestate
            # Decode the gamestate message
            [index, self.description, new_gamestate] = self._decode_gamestate(
                bytes(new_gamestate)
            )

            # If index is equal to the index of the current gamestate, the update from the
            # speech recognition is wrong and an error should be logged (race condition)
            if index == self.index:
                logging.error(
                    "Gamestate update from speech recognition system is invalid"
                )
            self.index = index
            logging.info(
                f"New gamestate received with index {self.index} and description {self.description}"
            )

            # Update all the gamestate variables
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

            # Create lists for characters and monsters
            self.characters = []
            self.monsters = []

            # Loop through all characters and monsters in currentList and create objects for them
            for item in self.currentList:
                if "characterState" in item:
                    self.characters.append(Characters(item))
                elif "monsterInstances" in item:
                    self.monsters.append(Monsters(item))

            # Compare tmp with output from get_gamestate and assert critical error if they are not equal
            # DOES NOT WORK
            # if jsondiff.diff(tmp, self.get_gamestate()) != {}:
            #    raise AssertionError("Critical error: input and output to gamestate class are not equal.")

    def get_gamestate(self):
        # Method get the gamestate in binary format
        # to be sent to the Frosthaven Application
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

        self.updated_gamestate = False
        # Encode the gamestate message before returning it
        return self._encode_gamestate(
            self.index,
            self.description,
            json.dumps(gamestate_dict),
        )

    # Methods to update the gamestate
    # After an update, the
    def update_initiative(self, name, initiative):
        # Loop thrugh all characters and check if the name matches the characterClass
        # then update the initiative
        with self.lock:  # Acquire the lock before modifying the gamestate
            character_updated = False
            for character in self.characters:
                if character.characterClass == name:
                    character.characterState.initiative = initiative
                    logging.info(f"Initiative updated for {name} to {initiative}")
                    character_updated = True

            # If the character is not found, log an error
            if not character_updated:
                logging.error(f"Character {name} not found")
            else:
                # If the character is found, update the gamestate and send it to the Frosthaven Application
                # also create a toast message (TODO: to be removed later)
                self.set_toast_message(f"Initiative updated for {name} to {initiative}")
                self._update_client_network()

    def update_monster_health(self, name, instance, health_change):
        # Loop through all monsters and check if the name matches the monster type
        # then check if the instance matches the monster instance
        # then change the health of the monster with the health_change

        # If the health becomes 0 or less, remove the monster instance
        # If the health becomes more than the maximum health, set the health to the maximum health
        with self.lock:
            monster_updated = False
            for monster in self.monsters:
                if monster.type == name:
                    for monster_instance in monster.monster_instances:
                        if monster_instance.standeeNr == instance:
                            monster_instance.health += health_change
                            if monster_instance.health <= 0:
                                monster.monster_instances.remove(monster_instance)
                                logging.info(
                                    f"Monster {name} with instance {instance} removed"
                                )
                            elif monster_instance.health > monster_instance.maxHealth:
                                monster_instance.health = monster_instance.maxHealth
                                logging.info(
                                    f"Monster {name} with instance {instance} health set to maximum"
                                )
                            else:
                                logging.info(
                                    f"Monster {name} with instance {instance} health changed by {health_change}"
                                )

            # If the monster is not found, log an error
            if not monster_updated:
                logging.error(f"Monster {name} with instance {instance} not found")
            else:
                # If the monster is found, update the gamestate and send it to the Frosthaven Application
                # Also create a toast message (TODO: to be removed later)
                self.set_toast_message(
                    f"Monster {name} with instance {instance} health changed by {health_change}"
                )
                self._update_client_network()

    def set_toast_message(self, message):
        # Set toast message
        self.toastMessage = message
        self._update_client_network()

    def clear_toast_message(self):
        # Clear toast message by setting the toastMessage variable to an empty string
        with self.lock:  # Acquire the lock before modifying the gamestate
            self.toastMessage = ""

            # Update the gamestate and send it to the Frosthaven Application
            self._update_client_network()

    def _update_client_network(self):
        # Method to update the client network with the new gamestate
        # This method is called when a variable in the gamestate class is updated
        # The client network will then send the new gamestate to the Frosthaven Application
        if self.client_network:
            new_gamestate = self._encode_gamestate(
                self.index,
                self.description,
                self.get_gamestate(),
            )
            self.client_network.send_data(new_gamestate)


class Characters:
    def __init__(self, character_dict):
        # Method to set the character information for each character
        self.id = character_dict.get("id")
        self.turnState = character_dict.get("turnState")
        self.characterState = self._CharacterState(character_dict.get("characterState"))
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

    class _CharacterState:
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
            self.conditionsAddedThisTurn = character_state_dict.get(
                "conditionsAddedThisTurn"
            )
            self.conditionsAddedPreviousTurn = character_state_dict.get(
                "conditionsAddedPreviousTurn"
            )

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
            "monsterInstances": _monster_instances,  # List of MonsterInstances
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
            self.conditionsAddedThisTurn = monster_instances_dict.get(
                "conditionsAddedThisTurn"
            )
            self.conditionsAddedPreviousTurn = monster_instances_dict.get(
                "conditionsAddedPreviousTurn"
            )

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
