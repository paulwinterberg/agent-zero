from core import state_manager
from states.gameplay import Gameplay
from states.video_state import VideoState


class IntroVideo(VideoState):
    def __init__(self):
        super().__init__("assets/videos/intro.mp4", hold_time=10)

    def on_finished(self):
        state_manager.replace(Gameplay(level="tutorial"))