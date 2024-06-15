from ovos_workshop.intents import IntentBuilder
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.skills.decorators import layer_intent, enables_layer, disables_layer, resets_layers
import os

class PathGameSkill(OVOSSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playing = False

    def initialize(self):
        # start with all game states disabled
        self.intent_layers.disable()
        
    def get_audio_path(self, filename):
        # Construct the file path for the audio file
        return os.path.join(os.path.dirname(__file__), 'mp3', filename)

    # game control
    def handle_deactivate(self, message):
        """ skill is no longer considered active by the intent service
        converse method will not be called, skills might want to reset state here

        ovos-core only + OVOS monkey patch skill
        """
        self.log.debug("game abandoned! skill kicked out of active skill list!!!")
        self.handle_game_over(message)

    @intent_handler(IntentBuilder("StartPathGameIntent"). \
                    optionally("startKeyword"). \
                    require("GameKeyword"))
    def handle_start_intent(self, message=None):
        if not self.playing:
            self.playing = True
            self.speak_dialog("start.game")
            self.handle_intro()
        else:
            self.speak_dialog("already.started")

    
        
    @layer_intent(IntentBuilder("StopPathGameIntent"). \
                  require("stopKeyword"). \
                  optionally("GameKeyword"),
                  layer_name="stop_game")
    @resets_layers()
    def handle_game_over(self, message=None):
        if self.playing:
            self.speak_dialog("stop.game")
            self.playing = False
            

    @enables_layer(layer_name="first_choice")
    @enables_layer(layer_name="stop_game")
    def handle_intro(self):
        self.speak_dialog("intro")
        self.speak_dialog("first_choice", expect_response=True)



    # Layer 1
    @layer_intent(IntentBuilder("EnterhaakIntent").require("enterhaakKeyword"),
                  layer_name="first_choice")
    def handle_enterhaak(self, message=None):
        audio_path = self.get_audio_path("1.mp3")
        self.play_audio(audio_path, wait=True)
        self.speak_dialog("enterhaak_choice", expect_response=True)


    @layer_intent(IntentBuilder("KatapultIntent").require("katapultKeyword"),
                  layer_name="fist_choice")
    @enables_layer(layer_name="katapult_choice")
    @disables_layer(layer_name="first_choice")
    def handle_katapult(self, message=None):
        self.speak_dialog("katapult")
        self.speak_dialog("katapult_choice", expect_response=True)


    # Layer 2
    
    #Enterhaak choice
    @layer_intent(IntentBuilder("Jungle3Intent").require("jungle3Keyword"),
                  layer_name="enterhaak_choice")
    @enables_layer(layer_name="jungle3_choice")
    @disables_layer(layer_name="enterhaak_choice")
    def handle_jungle3(self, message=None):
        self.speak_dialog("jungle3")
        self.handle_game_over()
        self.speak_dialog("jungle3")
        self.handle_game_over()

    @layer_intent(IntentBuilder("Rivier9Intent").require("rivier9Keyword"),
                  layer_name="enterhaak_choice")
    @enables_layer(layer_name="rivier9_choice")
    @disables_layer(layer_name="enterhaak_choice")
    def handle_rivier9(self, message=None):
        self.speak_dialog("rivier9")
        self.handle_game_over()

    # katapult choice
    @layer_intent(IntentBuilder("Jungle12Intent").require("jungle12Keyword"),
                  layer_name="katapult_choice")
    @enables_layer(layer_name="Jungle12_choice")
    @disables_layer(layer_name="katapult_choice")
    def handle_jungle12(self, message=None):
        self.speak_dialog("jungle12")
        self.handle_game_over()

    @layer_intent(IntentBuilder("Rivier7Intent").require("rivier7Keyword"),
                  layer_name="katapult_choice")
    @enables_layer(layer_name="rivier7_choice")
    @disables_layer(layer_name="katapult_choice")
    def handle_rivier7(self, message=None):
        self.speak_dialog("rivier7")
        self.handle_game_over()

    def will_trigger(self, utterance, lang):
        # will an intent from this skill trigger ?
        skill_id = IntentQueryApi(self.bus).get_skill(utterance, lang)
        if skill_id and skill_id == self.skill_id:
            return True
        return False

    # take corrective action
    def converse(self, utterances, lang="nl-nl"):
        if not self.playing:
            return False

        if not utterances:
            return True  # empty speech, happens if you write in cli answer
            # while stt is active, gets 2 converses with cli utt + None

        for utterance in utterances:
            # will an intent from this skill trigger ?
            if self.will_trigger(utterance, lang):
                # don't consume utterance, we accounted for this action with
                # some intent
                return False
            self.log.debug("Skill won't trigger, handle game action in converse")

            # take corrective action when no intent matched
            if self.intent_layers.is_active("first_choice"):
                self.speak_dialog("invalid_choice", {"choices": "enterhaak or katapult"})
            elif self.intent_layers.is_active("enterhaak_choice"):
                self.speak_dialog("invalid_choice", {"choices": "jungle3 or rivier9"})
            elif self.intent_layers.is_active("katapult_choice"):
                self.speak_dialog("invalid_choice", {"choices": "jungle12 or rivier7"})
            else:
                self.speak_dialog("invalid.command", expect_response=True)
        return True
