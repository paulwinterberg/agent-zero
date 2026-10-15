import pygame
from moviepy import VideoFileClip  # moviepy 1.x: from moviepy.editor import VideoFileClip

pygame.init()
pygame.mixer.init()

clip = VideoFileClip("assets/videos/intro.mp4")
win = pygame.display.set_mode(clip.size)

# Extract the audio once, then play it through pygame's mixer
if clip.audio:
    clip.audio.write_audiofile("temp_audio.wav")  # wav = no decode lag at startup
    pygame.mixer.music.load("temp_audio.wav")
    pygame.mixer.music.play()

clock = pygame.time.Clock()
start = pygame.time.get_ticks()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    t = (pygame.time.get_ticks() - start) / 1000
    if t >= clip.duration:
        break

    frame = clip.get_frame(t)
    surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    win.blit(surf, (0, 0))
    pygame.display.flip()
    clock.tick(30)

clip.close()
pygame.quit()