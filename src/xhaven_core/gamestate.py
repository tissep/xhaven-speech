import logging
import logging.handlers
import json
from math import log
from os import name
import re
import threading
from turtle import st

from numpy import char
from traitlets import default

# Create a gamestate class that will hold all the information about the current gamestate.
# - Method to update gamestate with a new gamestate from Frosthaven Application
# - Update character information (health and initiative)
# - Update monster information (health, conditions, and status)
# - Send toastmessage to Frosthaven Application


short_names = [
    "Adam",
    "Bertil",
    "Caesar",
    "David",
    "Erik",
    "Filip",
    "Gustav",
    "Helge",
    "Ivar",
    "Johan",
    "Kalle",
    "Ludvig",
    "Martin",
    "Niklas",
    "Olof",
    "Petter",
    "Qvintus",
    "Rudolf",
    "Sigurd",
    "Tore",
    "Urban",
    "Viktor",
    "William",
    "Xerxes",
    "Yngve",
    "Zäta",
]


class GameState:
    def __init__(self, character_names: dict, monster_names: dict) -> None:
        self.logger = logging.getLogger("xhaven_core.gamestate.gamestate")
        self.logger.setLevel(logging.INFO)
        socket_handler = logging.handlers.SocketHandler(
            "localhost", 19996
        )  # Cutelog's default port is 19996
        self.logger.addHandler(socket_handler)

        file_handler = logging.FileHandler("xhaven_speech.log")
        file_handler.setLevel(logging.DEBUG)
        self.logger.info("Starting gamestate...")

        self.index: int = -1
        self.description = ""
        self.lock = threading.Lock()

        self.character_names = character_names
        self.monster_names = monster_names

        # Initialize all the gamestate variables
        self.characters = []
        self.monsters = []
        self.level = 0
        self.solo = False
        self.roundState = 0
        self.round = 0
        self.scenario = 0
        self.toastMessage = ""
        self.scenarioSpecialRules = []
        self.scenarioSectionsAdded = []
        self.currentCampaign = 0
        self.currentList = []
        self.currentAbilityDecks = []
        self.modifierDeck = []
        self.modifierDeckAllies = []
        self.lootDeck = []
        self.unlockedClasses = []
        self.showAllyDeck = False
        self.elementState = []

        # Client Network is set to None by default
        # It is set to the client network class when the client network is initialized
        self.client_network: None

        self.logger.info("Init of GameState done")

    def set_client_network(self, client_network) -> None:
        self.client_network = client_network

    def _decode_gamestate(self, raw_gamestate_message: bytes) -> tuple[int, str, str]:
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
        self.logger.debug(
            "Received new gamestate message to decode",
            extra={"raw_gamestate_message": raw_gamestate_message},
        )
        if not b"GameState:" in raw_gamestate_message:
            raise ValueError("Invalid gamestate message, does not contain GameState:")

        gamestate_index = int(
            raw_gamestate_message.split(b"Index:")[1].split(b"Description:")[0]
        )
        gamestate_description = bytes(
            raw_gamestate_message.split(b"Description:")[1].split(b"GameState:")[0]
        )
        gamestate_description = gamestate_description.decode("utf-8")
        gamestate_data = bytes(
            raw_gamestate_message.split(b"GameState:")[1].split(b"[EOM]")[0]
        )
        gamestate_data = gamestate_data.decode("utf-8")

        # Log the decoded gamestate message
        self.logger.debug("Decoded gamestate message. Index: %s", gamestate_index)
        self.logger.debug(
            "Decoded gamestate message. Description: %s", gamestate_description
        )
        self.logger.debug("Decoded gamestate message. GameState: %s", gamestate_data)

        # Return the decoded gamestate message
        return (gamestate_index, gamestate_description, gamestate_data)

    def _encode_gamestate(
        self, index: int, description: str, gamestate_data: str
    ) -> bytes:
        # Helper method to encode gamestate message
        # This message is sent to the Frosthaven Application and contains the gamestate message
        # See _decode_gamestate for more information about the format
        # The message should be returned as bytes

        # Log the decoded gamestate message
        self.logger.debug("Encode gamestate message. Index: %s", index)
        self.logger.debug("Encode gamestate message. Description: %s", description)
        self.logger.debug("Encode gamestate message. GameState: %s", gamestate_data)

        encodexd_gamestate_message = f"S3nD:Index:{index}Description::{description}GameState:{gamestate_data}[EOM]".encode(
            "utf-8"
        )

        self.logger.debug(f"Encoded gamestate message: encoded_gamestate_message")
        return encodexd_gamestate_message

    def set_gamestate(self, raw_gamestate_message: bytes) -> None:
        # Method to set the gamestate from Frosthaven Application
        # This method is called from the network class when a new gamestate is received
        # If the index is equal to the index of the current gamestate, the update from the
        # speech recognition system is invalid and should be ignored (race condition)

        with self.lock:  # Acquire the lock before modifying the gamestate
            # Decode the gamestate message
            self.logger.info(
                "Received new gamestate message",
                extra={"gamestate": raw_gamestate_message},
            )
            [new_index, new_description, new_gamestate] = self._decode_gamestate(
                raw_gamestate_message
            )

            # If index is equal to the index of the current gamestate, the update from the
            # speech recognition is wrong and an error should be logged (race condition)
            if self.index == new_index:
                self.logger.error("Gamestate update is invalid, index not updated")

            self.index = new_index
            self.logger.info(f"Index updated to {new_index}")
            self.description = new_description

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
            monster_nr = 0
            for item in self.currentList:
                if "characterState" in item:
                    self.characters.append(
                        Characters(item, character_names=self.character_names)
                    )
                elif "monsterInstances" in item:
                    self.monsters.append(
                        Monsters(
                            item,
                            short_name=short_names[monster_nr],
                            monster_names=self.monster_names,
                        )
                    )
                    monster_nr += 1
                else:
                    self.logger.error("Unknown item in currentList")

            # Compare tmp with output from get_gamestate and assert critical error if they are not equal
            # DOES NOT WORK
            # if jsondiff.diff(tmp, self.get_gamestate()) != {}:
            #    raise AssertionError("Critical error: input and output to gamestate class are not equal.")

    def get_gamestate(self) -> str:
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
        self.logger.debug(
            "Returning gamestate message", extra={"gamestate": gamestate_dict}
        )
        return json.dumps(gamestate_dict)

    # ----------------------------------------------
    # Update methods
    # ----------------------------------------------

    # Methods to update the gamestate
    def update_initiative(self, name: str, initiative: int) -> bool:
        # Loop through all characters and check if the name matches the characterClass
        # then update the initiative
        with self.lock:  # Acquire the lock before modifying the gamestate
            self.logger.debug(f"Trying to update initiative for {name} to {initiative}")
            found_character_id = None
            for character in self.characters:
                self.logger.debug(f"Checking character {character.id}")
                self.logger.debug(
                    f"Checking character {character.characterState.display}"
                )
                if (
                    name.lower() in character.id.lower()
                    or name.lower() in character.characterState.display.lower()
                    or name.lower() in character.name.lower()
                ):
                    found_character_id = character.id
                    character.characterState.initiative = initiative

            # If the character is not found, log an error
            if found_character_id:
                # If the character is found, update the gamestate and send it to the Frosthaven Application
                self.description = (
                    f"Character {found_character_id} initiative changed to {initiative}"
                )
                self._update_client_network()
                return True
            else:
                self.logger.error(f"Character {name} not found")
                return False

    def update_character_health(self, name: str, health: int) -> bool:
        # Loop thrugh all characters and check if the name matches the characterClass
        # then update the health
        with self.lock:  # Acquire the lock before modifying the gamestate
            found_character_id = None
            for character in self.characters:
                self.logger.debug(f"Checking character {character.id}")
                self.logger.debug(
                    f"Checking character {character.characterState.display}"
                )
                if (
                    name.lower() in character.id.lower()
                    or name.lower() in character.characterState.display.lower()
                    or name.lower() in character.name.lower()
                ):
                    found_character_id = character.id
                    character.characterState.health = health

                    if character.characterState.health <= 0:
                        self.logger.info(f"Character {character.id} killed")
                    elif (
                        character.characterState.health
                        > character.characterState.maxHealth
                    ):
                        character.characterState.health = (
                            character.characterState.maxHealth
                        )
                        self.logger.info(
                            f"Character {character.id} health set to maximum"
                        )
                    else:
                        self.logger.info(
                            f"Character {character.id} health changed to {character.characterState.health}"
                        )

            # If the character is not found, log an error
            if found_character_id:
                # If the character is found, update the gamestate and send it to the Frosthaven Application
                self.description = (
                    f"Character {found_character_id} health changed to {health}"
                )
                self._update_client_network()
                return True
            else:
                return False

    def update_monster_health(
        self, type: str, standee_nr: int, health: int, relative: bool
    ) -> bool:
        # Loop through all monsters and check if the name matches the monster type
        # then check if the instance matches the monster instance
        # then change the health of the monster with the health_change

        # If the health becomes 0 or less, remove the monster instance
        # If the health becomes more than the maximum health, set the health to the maximum health
        with self.lock:
            self.logger.debug(
                "Trying to update monster %s, instance %s, health %s",
                type,
                standee_nr,
                health,
            )
            found_monster_type = None
            found_standee_nr = 0
            new_monster_health = 0
            for monster in self.monsters:
                if (
                    type in monster.type
                    or type in monster.short_name
                    or type in monster.name
                ):
                    found_monster_type = monster.type
                    for monster_instance in monster.monster_instances:
                        if monster_instance.standeeNr == standee_nr:
                            found_standee_nr = standee_nr
                            if relative:
                                monster_instance.health += health
                            else:
                                monster_instance.health = health
                            if monster_instance.health <= 0:
                                monster.monster_instances.remove(monster_instance)
                                self.logger.info(
                                    f"Monster {monster.type} nr {standee_nr} killed"
                                )
                            elif monster_instance.health > monster_instance.maxHealth:
                                monster_instance.health = monster_instance.maxHealth
                                self.logger.info(
                                    f"Monster {monster.type} nr {standee_nr} health set to maximum"
                                )
                            else:
                                self.logger.info(
                                    f"Monster {monster.type} nr {standee_nr} health changed to {monster_instance.health}"
                                )
                            new_monster_health = monster_instance.health
                            break

            # If the monster is not found, log an error
            if found_monster_type and found_standee_nr != 0:
                # If the monster is found, update the gamestate and send it to the Frosthaven Application
                self.description = f"Monster {found_monster_type} nr {found_standee_nr} health changed to {new_monster_health}"
                self._update_client_network()
                return True
            else:
                self.logger.error(
                    f"Monster {type} with instance {standee_nr} not found"
                )
                return False

    def update_monster_condition(
        self, type: str, standee_nr: int, condition: str, add: bool
    ) -> bool:
        # Loop through all monsters and check if the name matches the monster type
        # then check if the instance matches the monster instance
        # then change the condition of the monster with the condition_change
        # If add is True, add the condition to the monster
        # If add is False, remove the condition from the monster

        with self.lock:
            self.logger.debug(
                "Trying to update monster %s, instance %s, condition %s",
                type,
                standee_nr,
                condition,
            )
            found_monster_type = None
            found_standee_nr = 0
            for monster in self.monsters:
                if (
                    type in monster.type
                    or type in monster.short_name
                    or type in monster.name
                ):
                    found_monster_type = monster.type
                    for monster_instance in monster.monster_instances:
                        if monster_instance.standeeNr == standee_nr:
                            found_standee_nr = standee_nr
                            if add:
                                monster_instance.conditions.append(condition)
                            else:
                                monster_instance.conditions.remove(condition)
                            self.logger.info(
                                f"Monster {monster.type} nr {standee_nr} conditions changed to {monster_instance.conditions}"
                            )
                            break

            # If the monster is not found, log an error
            if found_monster_type and found_standee_nr != 0:
                # If the monster is found, update the gamestate and send it to the Frosthaven Application
                self.description = f"Monster {found_monster_type} nr {found_standee_nr} conditions changed to {condition}"
                self._update_client_network()
                return True
            else:
                self.logger.error(
                    f"Monster {type} with instance {standee_nr} not found"
                )
                return False

    def set_toast_message(self, message):
        # Set toast message
        with self.lock:  # Acquire the lock before modifying the gamestate
            self.logger.debug(f"Setting toast message to {message}")
            self.description = f"Setting toast message to {message}"
            self.toastMessage = message
            self._update_client_network()

    def _update_client_network(self):
        # Method to update the client network with the new gamestate
        # This method is called when a variable in the gamestate class is updated
        # The client network will then send the new gamestate to the Frosthaven Application
        if self.client_network:
            self.index += 1
            new_gamestate = self._encode_gamestate(
                self.index,
                self.description,
                self.get_gamestate(),
            )
            self.client_network.send_data(new_gamestate)

    # ----------------------------------------------
    # Get data methods
    # ----------------------------------------------
    def get_character_info(self) -> list[tuple[str, str, int, int]]:
        # Method to get the character information from the gamestate
        # It loops through all characters and returns a list of all characters
        # including the character id, character name, initiative, and health
        if self.characters == []:
            return []

        character_list = []
        for character in self.characters:
            self.logger.debug(
                f"Character {character.id}, {character.characterState.display} has initiative {character.characterState.initiative} and health {character.characterState.health}"
            )
            character_list.append(
                (
                    character.id,
                    character.characterState.display,
                    character.characterState.name,
                )
            )
        return character_list

    def get_character_names(self) -> dict:
        if self.characters == []:
            return {}

        character_list = {}
        for character in self.characters:
            character_list[character.id] = character.name

        return character_list

    def get_monster_info(self) -> list[tuple[str, int, int]]:
        # Method to get the monster information from the gamestate
        # It loops through all monsters and returns a list of all monsters
        # including the monster type, monster instance, and health
        if self.monsters == []:
            return []

        monster_list = []
        for monster in self.monsters:
            for monster_instance in monster.monster_instances:
                self.logger.debug(
                    f"Monster {monster.type} nr {monster_instance.standeeNr} has health {monster_instance.health}"
                )
                monster_list.append(
                    (monster.type, monster.short_name, len(monster.monster_instances))
                )
        return monster_list

    def get_monster_names(self) -> dict:
        if self.monsters == []:
            return {}

        monster_list = {}
        for monster in self.monsters:
            monster_list[monster.id] = monster.short_name

        return monster_list


class Characters:
    def __init__(self, character_dict, character_names: dict) -> None:
        # Method to set the character information for each character
        self.logger = logging.getLogger("xhaven_core.gamestate.characters")
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler("xhaven_speech.log")
        file_handler.setLevel(logging.DEBUG)  # Set the level of this handler

        self.id = character_dict.get("id")
        self.turnState = character_dict.get("turnState")
        self.characterState = self._CharacterState(character_dict.get("characterState"))
        self.characterClass = character_dict.get("characterClass")

        self.logger.debug(f"Character {self.characterClass} created")

        # Additional name for character, used for speech recognition and read from parameters file

        if self.id in character_names:
            self.logger.debug(
                f"Character {self.id} has name {character_names[self.id]}"
            )
            self.name = character_names[self.id]
        else:
            self.name = ""

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
    def __init__(self, monster_dict, short_name, monster_names) -> None:
        self.logger = logging.getLogger("xhaven_core.gamestate.monsters")
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler("xhaven_speech.log")
        file_handler.setLevel(logging.DEBUG)  # Set the level of this handler

        self.monster_instances = []
        self.id = monster_dict.get("id")
        self.turnState = monster_dict.get("turnState")
        self.isActive = monster_dict.get("isActive")
        self.type = monster_dict.get("type")
        for monster in monster_dict.get("monsterInstances"):
            self.monster_instances.append(self.MonsterInstances(monster))
        self.isAlly = monster_dict.get("isAlly")
        self.level = monster_dict.get("level")

        # These parameters have been added to make it easier for speech recognition
        self.short_name = short_name
        try:
            self.name = monster_names[self.id]
            self.logger.debug(f"Monster {self.id} has name {self.name}")
        except KeyError:
            pass

        self.logger.debug(f"Monster {self.type} created")

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
