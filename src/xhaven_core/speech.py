import logging
import logging.handlers
import threading
import winsound
import speech_recognition as sr

# create a recognizer object
r = sr.Recognizer()


class speech:
    """A speech recognition system for XHaven."""

    def __init__(self, game_class) -> None:
        self.game_class = game_class
        self.logger = logging.getLogger("xhaven_core.speech")
        self.logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler("xhaven_speech.log")
        file_handler.setLevel(logging.DEBUG)  # Set the level of this handler
        self.logger.info("Starting speech recognition...")

        # Start a new thread to handle receiving data
        threading.Thread(target=self.start_recognition).start()

    def start_recognition(self):
        """Start speech recognition."""
        # use the default microphone as the audio source
        while True:
            with sr.Microphone() as source:
                # listen for audio and store it in audio_data variable
                audio_data = r.listen(source)
                print("Processing...")

            # recognize speech using Google Speech Recognition
            gamestate_updated = False
            try:
                # text = r.recognize_whisper(audio_data)
                text = r.recognize_google(audio_data)
                self.logger.debug("You said: %s", text)
                if text is not None and type(text) == str:
                    text_line = text.split(" ")

                    # Check if the first word is "spelare"
                    if text_line[0] == "player" and len(text_line) in [3, 4]:
                        # Update character initiative with the given value
                        # Example: Player Hatchet 10
                        try:
                            name = text_line[1]
                            initiative = int(text_line[2])
                            gamestate_updated = self.game_class.update_initiative(
                                name, initiative
                            )
                            self.logger.debug("Update spelare initiativ: %s", text)
                        except ValueError:
                            try:
                                name = text_line[2]
                                initiative = int(text_line[1])
                                gamestate_updated = self.game_class.update_initiative(
                                    name, initiative
                                )
                            except ValueError:
                                pass

                    # Check if the first word is "monster"
                    if text_line[0] == "monster" and len(text_line) in [4, 5]:
                        # Update monster health with the given value
                        # Example: monster Adam 3 skada/minus/damage 10-> Helath -= 10
                        # Example: monster Adam 3 plus/hela 10 -> Health += 10
                        # Example: monster Adam 3 gift/poison -> Poison monster
                        # Example: monster Adam 3 10 -> Health = 10
                        # Example: monster Adam 3 död/döda -> Health = 0

                        try:
                            monster_name = text_line[1]
                            monster_nr = int(text_line[2])
                            if (
                                "skada" in text_line[3]
                                or "minus" in text_line[3]
                                or "damage" in text_line[3]
                            ):
                                try:
                                    monster_health = -int(text_line[4])
                                    gamestate_updated = (
                                        self.game_class.update_monster_health(
                                            monster_name,
                                            monster_nr,
                                            monster_health,
                                            True,
                                        )
                                    )
                                except ValueError:
                                    pass
                            elif "plus" in text_line[3] or "heal" in text_line[3]:
                                try:
                                    monster_health = int(text_line[4])
                                    gamestate_updated = (
                                        self.game_class.update_monster_health(
                                            monster_name,
                                            monster_nr,
                                            monster_health,
                                            True,
                                        )
                                    )
                                except ValueError:
                                    pass
                            elif "dead" in text_line[3] or "death" in text_line[3]:
                                gamestate_updated = (
                                    self.game_class.update_monster_health(
                                        monster_name, monster_nr, 0, False
                                    )
                                )
                            elif "poisin" in text_line[3] or "gift" in text_line[3]:
                                condition = "poison"
                                gamestate_updated = (
                                    self.game_class.update_monster_condition(
                                        monster_name, monster_nr, condition, True
                                    )
                                )
                            elif len(text_line) == 4:
                                try:
                                    monster_health = int(text_line[3])
                                    gamestate_updated = (
                                        self.game_class.update_monster_health(
                                            monster_name,
                                            monster_nr,
                                            monster_health,
                                            False,
                                        )
                                    )
                                except ValueError:
                                    pass
                        except ValueError:
                            pass

            except sr.UnknownValueError:
                self.logger.debug("Sorry, I could not understand what you said.")
            except sr.RequestError as e:
                self.logger.debug(
                    "Could not request results from Google Speech Recognition service; %s",
                    e,
                )

            if gamestate_updated:
                winsound.PlaySound("ping.wav", winsound.SND_FILENAME)

    def stop_recognition(self):
        """Stop speech recognition."""
        self.logger.info("Stopping speech recognition...")
        self.thread.join()
        self.logger.info("Speech recognition stopped")
