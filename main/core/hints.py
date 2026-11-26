import pygame


_message = None
_should_pause_game = False
_remaining_time = 0.0
_font = None


def display(text: str, should_pause_game: bool = False, display_time: float = 5):
    global _message, _should_pause_game, _remaining_time

    if display_time < 0:
        raise ValueError("display_time must be non-negative")

    _message = text
    _should_pause_game = should_pause_game
    _remaining_time = display_time


def _update(dt: float, events: list) -> bool:
    global _message, _remaining_time

    if _message is None:
        return False

    if _should_pause_game:
        if any(
            event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
            for event in events
        ):
            _message = None
        return True

    _remaining_time = max(0.0, _remaining_time - dt)
    if _remaining_time == 0:
        _message = None
    return False


def _is_active() -> bool:
    return _message is not None


def _draw(screen: pygame.Surface):
    global _font

    if _message is None:
        return

    if _font is None:
        _font = pygame.font.Font("assets/fonts/PixelifySans-Medium.ttf", 22)

    max_text_width = max(1, min(900, screen.get_width() - 64))
    lines = []
    current_line = ""
    for word in _message.split():
        candidate = f"{current_line} {word}".strip()
        if current_line and _font.size(candidate)[0] > max_text_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)
    if not lines:
        lines.append("")
    if _should_pause_game:
        lines.append("Press SPACE to continue.")

    line_height = _font.get_linesize()
    text = pygame.Surface(
        (
            max(_font.size(line)[0] for line in lines),
            line_height * len(lines),
        ),
        pygame.SRCALPHA,
    )
    for index, line in enumerate(lines):
        rendered_line = _font.render(line, True, (255, 255, 255))
        text.blit(rendered_line, (0, index * line_height))

    padding = 18
    panel = pygame.Surface(
        (text.get_width() + padding * 2, text.get_height() + 16),
        pygame.SRCALPHA,
    )
    pygame.draw.rect(panel, (20, 25, 29, 225), panel.get_rect(), border_radius=5)
    accent = (240, 180, 75) if "verschlossen" in _message else (95, 205, 145)
    pygame.draw.rect(panel, accent, panel.get_rect(), 2, border_radius=5)
    panel_rect = panel.get_rect(
        midbottom=(screen.get_width() // 2, screen.get_height() - 32)
    )
    screen.blit(panel, panel_rect)
    screen.blit(text, text.get_rect(center=panel_rect.center))
