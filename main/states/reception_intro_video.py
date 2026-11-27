from core import state_manager
from states.gameplay import Gameplay
from states.video_state import VideoState


class ReceptionIntroVideo(VideoState):
    def __init__(self):
        super().__init__("assets/videos/reception_intro.mp4", start_delay=5)

    def on_finished(self):
        state_manager.replace(Gameplay(level="tutorial"))