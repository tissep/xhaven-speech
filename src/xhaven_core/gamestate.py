import logging
import logging.handlers
import json
import threading

from numpy import character

# Create a gamestate class that will hold all the information about the current gamestate.
# - Method to update gamestate with a new gamestate from Frosthaven Application
# - Update character information (health and initiative)
# - Update monster information (health, conditions, and status)
# - Send toastmessage to Frosthaven Application

CONDITION = {
    "s": 0, #Stun
    "i": 1, #Immobilize
    "d": 2, #Disarm
    "w": 3, #Wound
    "m": 5, #Muddle
    "p": 6, #Poison
    #"b": 10, #bane
    "b": 11, #brittle
    #"s": 16, #strengthen
    #"i": 17, #invisible
    #"r": 18, #regenerate
    #"w": 19, #ward
}
    

class GameState:
    """Class to hold the gamestate information."""

    def __init__(self, character_names: dict, monster_names: dict) -> None:
        self.logger = logging.getLogger("xhaven_core.gamestate.gamestate")
        self.logger.setLevel(logging.DEBUG)
        # socket_handler = logging.handlers.SocketHandler(
        #    "localhost", 19996
        # )  # Cutelog's default port is 19996
        # self.logger.addHandler(socket_handler)

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
        """Method to set the client network."""
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

        encodexd_gamestate_message = f"S3nD:Index:{index}Description:{description}GameState:{gamestate_data}[EOM]".encode(
            "utf-8"
        )

        self.logger.debug(f"Encoded gamestate message: encoded_gamestate_message")
        return encodexd_gamestate_message

    def set_gamestate(self, raw_gamestate_message: bytes) -> None:
        """Method to set the gamestate from Frosthaven Application."""
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
            self.logger.info("Index updated to %s", new_index)
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
            #self.currentList = gamestate_dict.get("currentList")
            self.currentAbilityDecks = gamestate_dict.get("currentAbilityDecks")
            self.modifierDeck = gamestate_dict.get("modifierDeck")
            self.modifierDeckAllies = gamestate_dict.get("modifierDeckAllies")
            self.lootDeck = gamestate_dict.get("lootDeck")
            self.unlockedClasses = gamestate_dict.get("unlockedClasses")
            self.showAllyDeck = gamestate_dict.get("showAllyDeck")
            self.elementState = gamestate_dict.get("elementState")

            # Create lists for characters and monsters
            self.currentList = []

            # Loop through all characters and monsters in currentList and create objects for them
            monster_nr = 1
            character_nr = 1
            for item in gamestate_dict.get("currentList"):
                if "characterState" in item:
                    self.currentList.append(
                        Characters(item, character_names=self.character_names, character_nr=character_nr)
                    )
                    character_nr += 1
                    self.logger.debug("Character %s created, nr %s", item.get("characterClass"), character_nr)
                elif "monsterInstances" in item:
                    self.currentList.append(
                        Monsters(
                            item,
                            monster_names=self.monster_names,
                            monster_nr=monster_nr,
                        )
                    )
                    monster_nr += 1
                    self.logger.debug("Monster %s created, nr %s", item.get("type") , monster_nr)
                else:
                    self.logger.error("Unknown item in currentList")

            # Compare tmp with output from get_gamestate and assert critical error if they are not equal
            # DOES NOT WORK
            # if jsondiff.diff(tmp, self.get_gamestate()) != {}:
            #    raise AssertionError("Critical error: input and output to gamestate class are not equal.")

    def get_gamestate(self) -> str:
        """Method to get the gamestate in binary format to be sent to the Frosthaven Application."""
        # Method get the gamestate in binary format
        # to be sent to the Frosthaven Application
        new_currentList = []
        for item in self.currentList:
            if item.__class__.__name__ == "Characters":
                new_currentList.append(item.get_character())
            else:
                new_currentList.append(item.get_monster())

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
            "currentList": new_currentList,
            "currentAbilityDecks": self.currentAbilityDecks,
            "modifierDeck": self.modifierDeck,
            "modifierDeckAllies": self.modifierDeckAllies,
            "lootDeck": self.lootDeck,
            "unlockedClasses": self.unlockedClasses,
            "showAllyDeck": self.showAllyDeck,
            "elementState": self.elementState,
        }

        # Encode the gamestate message before returning it
        self.logger.debug(
            "Returning gamestate message", extra={"gamestate": gamestate_dict}
        )
        return json.dumps(gamestate_dict)

    # ----------------------------------------------
    # Update methods
    # ----------------------------------------------

    # Methods to update the gamestate
    def update_initiative(
        self, index: int = 0, name: str = "", initiative: int = 0
    ) -> bool:
        """Method to update the initiative for a character."""
        # Loop through all characters and check if the name matches the characterClass
        # then update the initiative
        with self.lock:  # Acquire the lock before modifying the gamestate
            self.logger.debug(
                "Trying to update initiative for %s%s to %s", index, name, initiative
            )
            found_character_id = None

            for item in self.currentList:
                if item.__class__.__name__ == "Characters":
                    self.logger.debug("Checking character %s", item.id)
                    self.logger.debug(
                        "Checking character %s", item.characterState.display
                    )
                    if index != 0:
                        if item.character_nr == index:
                            found_character_id = item.id
                            item.characterState.initiative = initiative
                    elif (
                        name.lower() in item.id.lower()
                        or name.lower() in item.characterState.display.lower()
                        or name.lower() in item.name.lower()
                    ):
                        found_character_id = character.id
                        item.characterState.initiative = initiative

            # If the character is not found, log an error
            if found_character_id:
                # If the character is found, update the gamestate and send it to the Frosthaven Application
                self.description = f"Set initiative of {found_character_id}"
                self._update_client_network()
                return True
            else:
                self.logger.error("Character %s not found", name)
                return False

    # def update_character_name(self, name: str, new_name: str) -> bool:
    #     """Method to update the name for a character."""
    #     # Loop through all characters and check if the name matches the characterClass
    #     # then update the initiative
    #     with self.lock:  # Acquire the lock before modifying the gamestate
    #         self.logger.debug("Trying to update name for %s to %s", name, new_name)
    #         self.logger.debug(f"Trying to update name for {name} to {new_name}")
    #         found_character_id = None
    #         for character in self.characters:
    #             self.logger.debug("Checking character %s", character.id)
    #             self.logger.debug(
    #                 "Checking character %s", character.characterState.display
    #             )
    #             if (
    #                 name.lower() in character.id.lower()
    #                 or name.lower() in character.characterState.display.lower()
    #                 or name.lower() in character.name.lower()
    #             ):
    #                 found_character_id = character.id
    #                 character.name = new_name

    #         # If the character is not found, log an error
    #         if found_character_id:
    #             # If the character is found, update the gamestate and send it to the Frosthaven Application
    #             self.description = (
    #                 f"Character {found_character_id} name changed to {new_name}"
    #             )
    #             self._update_client_network()
    #             return True
    #         else:
    #             self.logger.error(f"Character {name} not found")
    # #             return False

    # def update_character_health(self, name: str, health: int) -> bool:
    #     # Loop thrugh all characters and check if the name matches the characterClass
    #     # then update the health
    #     with self.lock:  # Acquire the lock before modifying the gamestate
    #         found_character_id = None
    #         for character in self.characters:
    #             self.logger.debug("Checking character %s", character.id)
    #             self.logger.debug(
    #                 "Checking character %s", character.characterState.display
    #             )
    #             if (
    #                 name.lower() in character.id.lower()
    #                 or name.lower() in character.characterState.display.lower()
    #                 or name.lower() in character.name.lower()
    #             ):
    #                 found_character_id = character.id
    #                 character.characterState.health = health

    #                 if character.characterState.health <= 0:
    #                     self.logger.info("Character %s killed", character.id)
    #                 elif (
    #                     character.characterState.health
    #                     > character.characterState.maxHealth
    #                 ):
    #                     character.characterState.health = (
    #                         character.characterState.maxHealth
    #                     )
    #                     self.logger.info(
    #                         "Character %s health set to maximum", character.id
    #                     )
    #                 else:
    #                     self.logger.info(
    #                         "Character %s health changed to %s",
    #                         character.id,
    #                         character.characterState.health,
    #                     )

    #         # If the character is not found, log an error
    #         if found_character_id:
    #             # If the character is found, update the gamestate and send it to the Frosthaven Application
    #             self.description = (
    #                 f"Character {found_character_id} health changed to {health}"
    #             )
    #             self._update_client_network()
    #             return True
    #         else:
    #             return False

    def update_monster(
        self, index: int, standee_nr: int, health: int, relative: bool, condition: str = ""
    ) -> bool:
        """Method to update the health for a monster."""
        # Loop through all monsters and check if the name matches the monster type
        # then check if the instance matches the monster instance
        # then change the health of the monster with the health_change

        # If the health becomes 0 or less, remove the monster instance
        # If the health becomes more than the maximum health, set the health to the maximum health
        self.toastMessage = ""
        with self.lock:
            self.logger.debug(
                "Trying to update monster index %s, standee %s, health %s",
                index,
                standee_nr,
                health,
            )
            found_monster_type = None
            found_standee_nr = 0
            new_monster_health = 0
            for item in self.currentList:
                if item.__class__.__name__ == "Monsters":
                    if index != 0:
                        if item.monster_nr == index:
                            found_monster_type = item.type
                            for monster_instance in item.monster_instances:
                                if monster_instance.standeeNr == standee_nr:
                                    found_standee_nr = standee_nr
                                    # First change condition if not empty
                                    if condition != "":
                                        if condition in CONDITION:
                                            monster_instance.conditions.append(CONDITION[condition])
                                        else:
                                            self.logger.error("Condition %s not found", condition)
                                    if relative:
                                        monster_instance.health += health
                                    else:
                                        monster_instance.health = health
                                        
                                    if monster_instance.health <= 0:
                                        item.monster_instances.remove(
                                            monster_instance
                                        )
                                        self.logger.info(
                                            "Monster %s nr %s killed",
                                            item.type,
                                            standee_nr,
                                        )
                                    elif (
                                        monster_instance.health
                                        > monster_instance.maxHealth
                                    ):
                                        monster_instance.health = (
                                            monster_instance.maxHealth
                                        )
                                        self.logger.info(
                                            "Monster %s nr %s health set to maximum",
                                            item.type,
                                            standee_nr,
                                        )
                                    else:
                                        self.logger.info(
                                            "Monster %s nr %s health changed to %s",
                                            item.type,
                                            standee_nr,
                                            monster_instance.health,
                                        )
                                    new_monster_health = monster_instance.health
                                    break


            # If the monster is not found, log an error
            if found_monster_type and found_standee_nr != 0:
                # If the monster is found, update the gamestate and send it to the Frosthaven Application
                self.description = "Monster %s nr %s health changed to %s" % (
                    found_monster_type,
                    found_standee_nr,
                    new_monster_health,
                )
                self._update_client_network()
                return True
            self.logger.error("Monster %s with instance %s not found", type, standee_nr)
            return False

    def update_monster_condition(
        self, monster_type: str, standee_nr: int, condition: str, add: bool
    ) -> bool:
        # Loop through all monsters and check if the name matches the monster type
        # then check if the instance matches the monster instance
        # then change the condition of the monster with the condition_change
        # If add is True, add the condition to the monster
        # If add is False, remove the condition from the monster

        with self.lock:
            self.logger.debug(
                "Trying to update monster %s, instance %s, condition %s",
                monster_type,
                standee_nr,
                condition,
            )
            found_monster_type = None
            found_standee_nr = 0
            for monster in self.monsters:
                if (
                    monster_type in monster.type
                    or monster_type in monster.short_name
                    or monster_type in monster.name
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
                                "Monster %s nr %s conditions changed to %s",
                                monster.type,
                                standee_nr,
                                monster_instance.conditions,
                            )
                            break

            # If the monster is not found, log an error
            if found_monster_type and found_standee_nr != 0:
                # If the monster is found, update the gamestate and send it to the Frosthaven Application
                self.description = "Monster %s nr %s conditions changed to %s" % (
                    found_monster_type,
                    found_standee_nr,
                    condition,
                )
                self._update_client_network()
                return True
            else:
                self.logger.error(
                    "Monster %s with instance %s not found",
                    type,
                    standee_nr,
                )
                return False

    def set_toast_message(self, message):
        # Set toast message
        with self.lock:  # Acquire the lock before modifying the gamestate
            self.logger.debug("Setting toast message to %s", message)
            self.description = "Setting toast message to %s" % message
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
        """Method to get the character information from the gamestate."""
        # Method to get the character information from the gamestate
        # It loops through all characters and returns a list of all characters
        # including the character id, character name, initiative, and health
        character_list = []
        for item in self.currentList:
            if item.__class__.__name__ == "Characters":
                self.logger.debug(
                    "Character %s, %s has initiative %s and health %s",
                    item.id,
                    item.characterState.display,
                    item.characterState.initiative,
                    item.characterState.health,
                )
                character_list.append(
                    (
                        item.id,
                        item.characterState.display,
                        item.name,
                    )
                )
        return character_list

    def get_character_index(self) -> dict:
        """Method to get the character names from the gamestate."""
        character_list = {}
        for item in self.currentList:
            if item.__class__.__name__ == "Characters":
                character_list[item.id] = item.character_nr

        return character_list

    def get_monster_info(self) -> list[tuple[str, int, int]]:
        # Method to get the monster information from the gamestate
        # It loops through all monsters and returns a list of all monsters
        # including the monster type, monster instance, and health
        monster_list = []
        for item in self.currentList:
            if item.__class__.__name__ == "Monsters":
                for monster_instance in item.monster_instances:
                    self.logger.debug(
                        "Monster %s nr %s has health %s",
                        item.type,
                        monster_instance.standeeNr,
                        monster_instance.health,
                    )
                    monster_list.append(
                        (
                            item.type,
                            monster_instance.standeeNr,
                            monster_instance.health,
                        )
                    )
        return monster_list

    def get_monster_index(self) -> dict:
        """Method to get the monster names from the gamestate."""
        monster_list = {}
        for item in self.currentList:
            if item.__class__.__name__ == "Monsters":
                monster_list[item.id] = item.monster_nr

        return monster_list


class Characters:
    """Class to hold the character information."""

    def __init__(self, character_dict, character_names: dict, character_nr: int) -> None:
        # Method to set the character information for each character
        self.logger = logging.getLogger("xhaven_core.gamestate.characters")
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler("xhaven_speech.log")
        file_handler.setLevel(logging.DEBUG)  # Set the level of this handler

        self.id = character_dict.get("id")
        self.turnState = character_dict.get("turnState")
        self.characterState = self._CharacterState(character_dict.get("characterState"))
        self.characterClass = character_dict.get("characterClass")
        self.name = ""

        self.logger.debug("Character %s created", self.characterClass)

        # Additional name for character, used for speech recognition and read from parameters file
        self.character_nr = character_nr
        
        if self.id in character_names:
            self.logger.debug(
                "Character %s has name %s", self.id, character_names[self.id]
            )
            self.name = character_names[self.id]
        else:
            self.name = ""

    def get_character(self):
        """Method to get the character information from the gamestate."""
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
            """Method to get the character state from the gamestate."""
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
    def __init__(self, monster_dict, monster_names, monster_nr) -> None:
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
        self.monster_nr = monster_nr
        try:
            self.name = monster_names[self.id]
            self.logger.debug("Monster %s has name %s", self.id, self.name)
        except KeyError:
            pass

        self.logger.debug("Monster %s created", self.type)

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
        """Class to hold the monster instance information."""

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
            """Method to get the monster instance information from the gamestate."""
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
