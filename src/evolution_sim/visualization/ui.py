"""User interface components for the simulation."""
import pygame
from typing import Callable, Optional, Tuple, List
from ..config import config


class Button:
    """Interactive button UI element."""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        text: str,
        callback: Callable,
        color: Tuple[int, int, int] = (70, 130, 180),
        hover_color: Tuple[int, int, int] = (100, 160, 210),
        text_color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """
        Initialize a button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            callback: Function to call when clicked
            color: Normal button color
            hover_color: Color when mouse hovers
            text_color: Text color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.font = pygame.font.Font(None, 24)
        self.hovered = False
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update button state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position (x, y)
        """
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.hovered else self.color
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.
        
        Args:
            event: Pygame event
            
        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()
                return True
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the button.
        
        Args:
            surface: Surface to draw on
        """
        # Draw button background
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class Slider:
    """Slider UI element for adjusting values."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        min_value: float,
        max_value: float,
        initial_value: float,
        label: str,
        callback: Optional[Callable] = None
    ):
        """
        Initialize a slider.
        
        Args:
            x: X position
            y: Y position
            width: Slider width
            min_value: Minimum value
            max_value: Maximum value
            initial_value: Starting value
            label: Slider label
            callback: Function to call when value changes
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = 10
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.callback = callback
        
        self.rect = pygame.Rect(x, y, width, self.height)
        self.handle_radius = 8
        self.dragging = False
        self.font = pygame.font.Font(None, 20)
        
        # Calculate handle position
        self._update_handle_pos()
    
    def _update_handle_pos(self) -> None:
        """Update handle position based on current value."""
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        self.handle_x = self.x + int(ratio * self.width)
    
    def _value_from_pos(self, x: int) -> float:
        """Calculate value from x position."""
        ratio = max(0, min(1, (x - self.x) / self.width))
        return self.min_value + ratio * (self.max_value - self.min_value)
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool) -> None:
        """
        Update slider state.
        
        Args:
            mouse_pos: Current mouse position
            mouse_pressed: Whether mouse button is pressed
        """
        handle_rect = pygame.Rect(
            self.handle_x - self.handle_radius,
            self.y - self.handle_radius + self.height // 2,
            self.handle_radius * 2,
            self.handle_radius * 2
        )
        
        if mouse_pressed:
            if handle_rect.collidepoint(mouse_pos) or self.dragging:
                self.dragging = True
                self.value = self._value_from_pos(mouse_pos[0])
                self._update_handle_pos()
                if self.callback:
                    self.callback(self.value)
        else:
            self.dragging = False
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the slider.
        
        Args:
            surface: Surface to draw on
        """
        # Draw label
        label_surface = self.font.render(
            f"{self.label}: {self.value:.2f}", 
            True, 
            (255, 255, 255)
        )
        surface.blit(label_surface, (self.x, self.y - 25))
        
        # Draw track
        pygame.draw.rect(surface, (100, 100, 100), self.rect)
        
        # Draw filled portion
        filled_width = int((self.value - self.min_value) / 
                          (self.max_value - self.min_value) * self.width)
        filled_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
        pygame.draw.rect(surface, (70, 130, 180), filled_rect)
        
        # Draw handle
        pygame.draw.circle(
            surface,
            (200, 200, 200),
            (self.handle_x, self.y + self.height // 2),
            self.handle_radius
        )
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (self.handle_x, self.y + self.handle_radius // 2),
            self.handle_radius,
            2
        )


class ToggleButton:
    """Toggle button (checkbox) UI element."""
    
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        label: str,
        initial_state: bool = False,
        callback: Optional[Callable] = None
    ):
        """
        Initialize a toggle button.
        
        Args:
            x: X position
            y: Y position
            size: Size of checkbox
            label: Label text
            initial_state: Initial on/off state
            callback: Function to call when toggled
        """
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.state = initial_state
        self.callback = callback
        self.font = pygame.font.Font(None, 20)
        self.hovered = False
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update toggle state based on mouse position."""
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.
        
        Args:
            event: Pygame event
            
        Returns:
            True if toggle was clicked
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.state = not self.state
                if self.callback:
                    self.callback(self.state)
                return True
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the toggle button."""
        # Draw checkbox
        color = (70, 180, 130) if self.state else (100, 100, 100)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Draw checkmark if enabled
        if self.state:
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (self.rect.x + 5, self.rect.centery),
                (self.rect.centerx, self.rect.bottom - 5),
                3
            )
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (self.rect.centerx, self.rect.bottom - 5),
                (self.rect.right - 5, self.rect.top + 5),
                3
            )
        
        # Draw label
        label_surface = self.font.render(self.label, True, (255, 255, 255))
        surface.blit(label_surface, (self.rect.right + 10, self.rect.y))


class Panel:
    """Container for UI elements."""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        background_color: Tuple[int, int, int] = (40, 40, 40, 200)
    ):
        """
        Initialize a panel.
        
        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            title: Panel title
            background_color: Background color (RGBA)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.background_color = background_color
        self.elements: List = []
        self.visible = True
        self.font = pygame.font.Font(None, 24)
    
    def add_element(self, element) -> None:
        """Add a UI element to the panel."""
        self.elements.append(element)
    
    def update(self, mouse_pos: Tuple[int, int], mouse_pressed: bool = False) -> None:
        """Update all elements in the panel."""
        if not self.visible:
            return
        
        for element in self.elements:
            if isinstance(element, Slider):
                element.update(mouse_pos, mouse_pressed)
            elif hasattr(element, 'update'):
                element.update(mouse_pos)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all elements."""
        if not self.visible:
            return False
        
        for element in self.elements:
            if hasattr(element, 'handle_event'):
                if element.handle_event(event):
                    return True
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the panel and all elements."""
        if not self.visible:
            return
        
        # Draw semi-transparent background
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(200)
        s.fill(self.background_color[:3])
        surface.blit(s, (self.rect.x, self.rect.y))
        
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)
        
        # Draw title
        if self.title:
            title_surface = self.font.render(self.title, True, (255, 255, 255))
            surface.blit(title_surface, (self.rect.x + 10, self.rect.y + 5))
        
        # Draw all elements
        for element in self.elements:
            element.draw(surface)


class UIManager:
    """Manages all UI elements."""
    
    def __init__(self):
        """Initialize the UI manager."""
        self.panels: List[Panel] = []
        self.buttons: List[Button] = []
        self.active = True
    
    def add_panel(self, panel: Panel) -> None:
        """Add a panel to the manager."""
        self.panels.append(panel)
    
    def add_button(self, button: Button) -> None:
        """Add a standalone button."""
        self.buttons.append(button)
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update all UI elements."""
        if not self.active:
            return
        
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        for panel in self.panels:
            panel.update(mouse_pos, mouse_pressed)
        
        for button in self.buttons:
            button.update(mouse_pos)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame event.
        
        Returns:
            True if event was handled by UI
        """
        if not self.active:
            return False
        
        for panel in self.panels:
            if panel.handle_event(event):
                return True
        
        for button in self.buttons:
            if button.handle_event(event):
                return True
        
        return False
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all UI elements."""
        if not self.active:
            return
        
        for panel in self.panels:
            panel.draw(surface)
        
        for button in self.buttons:
            button.draw(surface)
    
    def toggle_visibility(self) -> None:
        """Toggle UI visibility."""
        self.active = not self.active


class InfoBox:
    """Information display box."""
    
    def __init__(self, x: int, y: int, width: int):
        """
        Initialize an info box.
        
        Args:
            x: X position
            y: Y position
            width: Box width
        """
        self.x = x
        self.y = y
        self.width = width
        self.font = pygame.font.Font(None, 18)
        self.lines: List[str] = []
        self.padding = 5
    
    def set_lines(self, lines: List[str]) -> None:
        """Set the lines to display."""
        self.lines = lines
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the info box."""
        if not self.lines:
            return
        
        line_height = 20
        height = len(self.lines) * line_height + self.padding * 2
        
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, height)
        s = pygame.Surface((self.width, height))
        s.set_alpha(180)
        s.fill((40, 40, 40))
        surface.blit(s, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)
        
        # Draw text lines
        for i, line in enumerate(self.lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            surface.blit(
                text_surface, 
                (self.x + self.padding, self.y + self.padding + i * line_height)
            )
