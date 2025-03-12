import pygame
import random
import math
import time  # Add this line
from botBase import BotStatus  # Change this line

class EyeTracker:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_animating = True  # New flag for animation control

        # Screen dimensions
        self.screen_width, self.screen_height = self.screen.get_size()

        # Adjust eye dimensions and initial positions
        self.eye_width, self.eye_height = 100, 130  # Wider eyes
        self.eye_spacing = 140  # Increase spacing
        # Move eyes up by adjusting vertical position
        self.eye_vertical_offset = 100  # Distance from center to move up
        self.left_eye_x = (self.screen_width // 2) - (self.eye_spacing // 2) - self.eye_width
        self.right_eye_x = (self.screen_width // 2) + (self.eye_spacing // 2)
        self.eye_y = (self.screen_height // 2) - (self.eye_height // 2) - self.eye_vertical_offset
        self.left_eye_y = self.eye_y  # Add this line
        self.right_eye_y = self.eye_y  # Add this line

        # Eye colors with default
        self.eye_color = pygame.Color(0, 191, 255)  # DeepSkyBlue
        self.glow_color = pygame.Color(0, 191, 255, 100)

        # Remove duplicate movement_params definitions and keep only this one
        self.movement_params = {
            'base_speed': 0.008,       # Base movement speed
            'max_acceleration': 0.003,  # Maximum acceleration
            'deceleration': 0.004,     # Deceleration rate
            'jitter_scale': 0.08,      # Micro-movement scale
            'drift_speed': 0.0001,     # Very slow drift
            'transition_smoothing': 0.92,  # Higher = smoother (0.0 to 1.0)
            'drift_scale': 0.15,       # Subtle drift
            'max_distance': 60,        # Reduced max distance
            'min_look_time': 1.5,      # Shorter min look time
            'max_look_time': 3.0,      # Shorter max look time
            'transition_speed': 0.012   # Slower transitions for smoother movement
        }

        # Target positions
        self.target_left_eye_x = self.left_eye_x
        self.target_right_eye_x = self.right_eye_x
        self.target_eye_y = self.eye_y

        # Add new color transition properties
        self.target_color = self.eye_color
        self.color_transition_speed = 0.05

        # Adjust mouth parameters to follow eyes
        self.mouth_width = 100  # Wider for smoother curve
        self.mouth_height = 35
        self.mouth_x = self.screen_width // 2 - self.mouth_width // 2
        self.mouth_y = self.eye_y + self.eye_height + 30  # Position relative to eyes
        self.lip_thickness = 4  # Thicker lips
        self.mouth_curve = 0  # Controls smile/frown (-1 to 1)
        self.target_curve = 0
        self.target_mouth_x = self.mouth_x
        self.target_mouth_y = self.mouth_y
        self.mouth_color = self.eye_color
        
        # Emotion mapping for mouth expressions
        self.emotion_curves = {
            'happy': 0.8,    # Big smile
            'sad': -0.6,     # Frown
            'angry': -0.8,   # Deep frown
            'calm': 0.2,     # Slight smile
            'excited': 1.0,  # Biggest smile
            'worried': -0.3  # Slight frown
        }

        # Adjust eyebrow parameters for cuter look
        self.brow_width = 110  # Slightly shorter brows
        self.brow_height = 20
        self.brow_thickness = 7  # Slightly thicker
        self.brow_curve_intensity = 2.0  # Control curve intensity
        self.brow_inward_shift = 15  # Shift towards center
        self.brow_angle = 0  # Add this line to define brow_angle
        self.target_brow_angle = 0
        self.brow_bounce_timer = 0
        
        # Update brow positions
        self.left_brow_x = self.left_eye_x - 5  # Slightly closer to eye
        self.right_brow_x = self.right_eye_x - 5
        self.brow_y = self.eye_y - 35  # Slightly closer to eyes
        
        # Update emotion mappings for eyebrows
        self.brow_angles = {
            'happy': 18,      # More curved upward
            'sad': -22,      # Deeper curve down
            'angry': 35,     # Sharper angle
            'calm': 12,      # Gentle upward curve
            'excited': 25,   # High curve
            'worried': -18   # Worried curve
        }
        
        # Add bounce patterns for different emotions
        self.brow_bounce_patterns = {
            'happy': {'speed': 0.05, 'amplitude': 3},  # Reduced values for stability
            'excited': {'speed': 0.08, 'amplitude': 4},
            'calm': {'speed': 0.03, 'amplitude': 2}
        }

        # Add caption parameters
        self.caption_text = ""
        self.caption_font = pygame.font.Font(None, 48)  # Increase font size
        self.caption_color = pygame.Color(0, 255, 255)  # Cyan color for better contrast
        self.caption_y_offset = 100  # Move text further down
        self.caption_max_width = self.screen_width - 200  # Adjust text width
        self.caption_fade_time = 15  # Increase display time to 15 seconds
        self.caption_start_time = time.time()
        self.caption_background_color = pygame.Color(0, 0, 0)  # Solid black background

        # Add lip sync parameters
        self.is_talking = False
        self.talk_phase = 0
        self.talk_speed = 0.15
        self.max_mouth_open = 25
        self.current_mouth_open = 0
        self.target_mouth_open = 0

        # Add movement sequence properties
        self.movement_sequence = ['center', 'left', 'right', 'up', 'down', 
                                'squint_left', 'squint_right', 'squint_both']
        self.movement_index = 0
        self.movement_timer = 0
        self.movement_delay = 60  # Frames to wait between movements

    def set_eye_color(self, color: tuple):
        """Set target eye color using RGB tuple (r, g, b)"""
        self.target_color = pygame.Color(*color)
        self.mouth_color = self.target_color  # Update mouth color too
        
        # Map colors to emotions and set mouth curve
        if color == (144, 238, 144):  # Light green (happy)
            self.target_curve = self.emotion_curves['happy']
            self.target_brow_angle = self.brow_angles['happy']
        elif color == (70, 130, 180):  # Steel blue (sad)
            self.target_curve = self.emotion_curves['sad']
            self.target_brow_angle = self.brow_angles['sad']
        elif color == (255, 0, 0):     # Red (angry)
            self.target_curve = self.emotion_curves['angry']
            self.target_brow_angle = self.brow_angles['angry']
        elif color == (0, 191, 255):   # Deep sky blue (calm)
            self.target_curve = self.emotion_curves['calm']
            self.target_brow_angle = self.brow_angles['calm']
        elif color == (255, 215, 0):   # Gold (excited)
            self.target_curve = self.emotion_curves['excited']
            self.target_brow_angle = self.brow_angles['excited']
        elif color == (147, 112, 219): # Purple (worried)
            self.target_curve = self.emotion_curves['worried']
            self.target_brow_angle = self.brow_angles['worried']

    def toggle_animation(self):
        """Toggle animation state"""
        self.is_animating = not self.is_animating
        return self.is_animating

    def set_animation_state(self, state: bool):
        """Set animation state explicitly"""
        self.is_animating = state
        return self.is_animating

    def draw_eyes(self, left_x, right_x, y, width, height, color, glow_color):
        # Draw glow effect
        pygame.draw.ellipse(self.screen, glow_color, pygame.Rect(left_x - 20, int(y) - 20, width + 40, int(height) + 40))
        pygame.draw.ellipse(self.screen, glow_color, pygame.Rect(right_x - 20, int(y) - 20, width + 40, int(height) + 40))
        # Draw eyes
        pygame.draw.rect(self.screen, color, pygame.Rect(left_x, int(y), width, int(height)), border_radius=20)
        pygame.draw.rect(self.screen, color, pygame.Rect(right_x, int(y), width, int(height)), border_radius=20)

    def update_mouth_position(self):
        """Update mouth position to follow eye movements"""
        # Calculate center point between eyes
        eye_center_x = (self.left_eye_x + self.right_eye_x + self.eye_width) / 2
        
        # Update mouth target position
        self.target_mouth_x = eye_center_x - self.mouth_width / 2
        self.target_mouth_y = self.eye_y + self.eye_height + 30
        
        # Smoothly interpolate mouth position
        self.mouth_x += (self.target_mouth_x - self.mouth_x) * 0.1
        self.mouth_y += (self.target_mouth_y - self.mouth_y) * 0.1

    def draw_mouth(self):
        """Draw realistic mouth with proper symmetry"""
        self.update_mouth_position()
        
        # Update mouth animation
        if self.is_talking:
            self.talk_phase += self.talk_speed
            if self.talk_phase >= math.pi:
                self.talk_phase = 0
                self.target_mouth_open = random.uniform(0.3, 1.0) * self.max_mouth_open
                
            # Smooth mouth movement
            open_amount = abs(math.sin(self.talk_phase)) * self.target_mouth_open
            self.current_mouth_open += (open_amount - self.current_mouth_open) * 0.3
        else:
            self.current_mouth_open += (0 - self.current_mouth_open) * 0.2
            
        # Interpolate mouth curve for expressions
        self.mouth_curve += (self.target_curve - self.mouth_curve) * 0.1
        
        # Calculate center point
        center_x = self.mouth_x + self.mouth_width / 2
        center_y = self.mouth_y
        
        # Generate upper lip points
        upper_points = []
        for i in range(self.mouth_width + 1):
            x = self.mouth_x + i
            t = (x - self.mouth_x) / self.mouth_width
            
            # Symmetric curve using sine function
            curve = math.sin(t * math.pi)
            curve_height = self.mouth_curve * 20
            
            # Add talking animation offset
            if self.is_talking:
                talk_offset = -self.current_mouth_open * curve
            else:
                talk_offset = 0
                
            y = center_y + curve_height * curve + talk_offset
            upper_points.append((x, int(y)))
            
        # Generate lower lip points
        lower_points = []
        for i in range(self.mouth_width + 1):
            x = self.mouth_x + i
            t = (x - self.mouth_x) / self.mouth_width
            
            # Symmetric curve using sine function
            curve = math.sin(t * math.pi)
            curve_height = self.mouth_curve * 15  # Slightly less curved than upper lip
            
            # Add talking animation offset
            if self.is_talking:
                talk_offset = self.current_mouth_open * curve
            else:
                talk_offset = 0
                
            y = center_y + curve_height * curve + talk_offset
            lower_points.append((x, int(y)))
            
        # Draw mouth interior when open
        if self.current_mouth_open > 1:
            interior_points = upper_points + lower_points[::-1]
            pygame.draw.polygon(self.screen, (40, 40, 40), interior_points)
            
        # Draw lips with anti-aliasing
        if len(upper_points) > 2:
            pygame.draw.lines(self.screen, self.mouth_color, False, upper_points, self.lip_thickness)
        if len(lower_points) > 2:
            pygame.draw.lines(self.screen, self.mouth_color, False, lower_points, self.lip_thickness)

    def draw_led_lines(self):
        line_spacing = 5
        for i in range(0, self.screen_height, line_spacing):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, i), (self.screen_width, i), 2)

    def update_brow_position(self):
        """Update eyebrow positions to follow eye movements"""
        # Update brow target positions based on eye positions
        self.left_brow_x = self.left_eye_x - 10
        self.right_brow_x = self.right_eye_x - 10
        self.brow_y = self.eye_y - 40
        
        # Smoothly interpolate brow angle
        self.brow_angle += (self.target_brow_angle - self.brow_angle) * 0.1

    def draw_eyebrows(self):
        """Draw more expressive curved eyebrows"""
        self.update_brow_position()
        
        # Calculate bounce
        bounce = 0
        if isinstance(self.eye_color, pygame.Color):
            rgb = (self.eye_color.r, self.eye_color.g, self.eye_color.b)
            if rgb == (144, 238, 144) or rgb == (0, 191, 255):
                pattern = self.brow_bounce_patterns.get('happy' if rgb[1] > 200 else 'calm')
                if pattern:
                    self.brow_bounce_timer += pattern['speed']
                    bounce = math.sin(self.brow_bounce_timer) * pattern['amplitude']
        
        for side in ['left', 'right']:
            # Adjust x position to be closer to eye center
            base_x = self.left_brow_x if side == 'left' else self.right_brow_x
            x = base_x + (self.brow_inward_shift if side == 'left' else -self.brow_inward_shift)
            
            points = []
            steps = 35  # More points for smoother curve
            
            for i in range(steps + 1):
                t = i / steps
                
                # Enhanced bezier curve control points
                if side == 'left':
                    cp1 = (x + self.brow_width * 0.3, self.brow_y - self.brow_angle * 0.8)
                    cp2 = (x + self.brow_width * 0.7, self.brow_y - self.brow_angle * self.brow_curve_intensity)
                else:
                    cp1 = (x + self.brow_width * 0.3, self.brow_y - self.brow_angle * self.brow_curve_intensity)
                    cp2 = (x + self.brow_width * 0.7, self.brow_y - self.brow_angle * 0.8)
                
                # Cubic bezier formula with enhanced curvature
                bx = (1-t)**3 * x + \
                     3*(1-t)**2 * t * cp1[0] + \
                     3*(1-t) * t**2 * cp2[0] + \
                     t**3 * (x + self.brow_width)
                
                by = (1-t)**3 * self.brow_y + \
                     3*(1-t)**2 * t * cp1[1] + \
                     3*(1-t) * t**2 * cp2[1] + \
                     t**3 * self.brow_y + bounce
                
                points.append((int(bx), int(by)))
            
            # Draw eyebrow with enhanced gradient
            if len(points) > 1:
                # Main brow
                pygame.draw.lines(self.screen, self.eye_color, False, points, self.brow_thickness)
                # Highlight for depth
                highlight_color = (min(self.eye_color.r + 40, 255),
                                 min(self.eye_color.g + 40, 255),
                                 min(self.eye_color.b + 40, 255))
                pygame.draw.lines(self.screen, highlight_color, False, points, 2)

    def idle_eyes(self):
        if not self.is_animating:
            self.draw_eyes(self.left_eye_x, self.right_eye_x, self.eye_y, 
                          self.eye_width, self.eye_height, self.eye_color, self.glow_color)
            self.draw_eyebrows()  # Draw eyebrows after eyes but before mouth
            self.draw_mouth()  # Add mouth drawing after eyes
            return

        if self.movement_timer == 0:
            if self.movement_index == 0:
                random.shuffle(self.movement_sequence)

            direction = self.movement_sequence[self.movement_index]
            angle = 0
            if direction == 'left':
                angle = 180
            elif direction == 'right':
                angle = 0
            elif direction == 'up':
                angle = 90
            elif direction == 'down':
                angle = 270
            elif direction == 'center':
                self.target_left_eye_x = (self.screen_width // 2) - (self.eye_spacing // 2) - self.eye_width
                self.target_right_eye_x = (self.screen_width // 2) + (self.eye_spacing // 2)
                self.target_eye_y = (self.screen_height // 2) - (self.eye_height // 2) - self.eye_vertical_offset
            elif direction == 'squint_left':
                self.squint_left_eye()
            elif direction == 'squint_right':
                self.squint_right_eye()
            elif direction == 'squint_both':
                self.squint_both_eyes()

            if direction not in ['center', 'squint_left', 'squint_right', 'squint_both']:
                angle_rad = math.radians(angle)
                self.target_left_eye_x += 100 * math.cos(angle_rad)
                self.target_right_eye_x += 100 * math.cos(angle_rad)
                self.target_eye_y += 50 * math.sin(angle_rad)

            self.movement_index = (self.movement_index + 1) % len(self.movement_sequence)
            self.movement_timer = self.movement_delay
        else:
            self.movement_timer -= 1

        # Smoothly interpolate positions
        self.left_eye_x += (self.target_left_eye_x - self.left_eye_x) * 0.1
        self.right_eye_x += (self.target_right_eye_x - self.right_eye_x) * 0.1
        self.eye_y += (self.target_eye_y - self.eye_y) * 0.1

        self.draw_eyes(self.left_eye_x, self.right_eye_x, self.eye_y, 
                      self.eye_width, self.eye_height, self.eye_color, self.glow_color)
        self.draw_eyebrows()  # Draw eyebrows after eyes but before mouth
        self.draw_mouth()  # Add mouth drawing after eyes

    def sad_eyes(self):
        sad_eye_y = self.eye_y + 30
        self.draw_eyes(self.left_eye_x, self.right_eye_x, sad_eye_y, 
                      self.eye_width, self.eye_height, self.eye_color, self.glow_color)

    def squint_left_eye(self):
        squint_eye_height = self.eye_height // 2
        self.draw_eyes(self.left_eye_x, self.right_eye_x, self.eye_y, 
                      self.eye_width, squint_eye_height, self.eye_color, self.glow_color)

    def squint_right_eye(self):
        squint_eye_height = self.eye_height // 2
        self.draw_eyes(self.left_eye_x, self.right_eye_x, self.eye_y, 
                      self.eye_width, squint_eye_height, self.eye_color, self.glow_color)

    def squint_both_eyes(self):
        squint_eye_height = self.eye_height // 2
        self.draw_eyes(self.left_eye_x, self.right_eye_x, self.eye_y, 
                      self.eye_width, squint_eye_height, self.eye_color, self.glow_color)

    def bounce_eyes(self):
        """Make the eyes bounce up and down"""
        bounce_amplitude = 20
        bounce_speed = 0.1
        self.left_eye_y += bounce_amplitude * math.sin(pygame.time.get_ticks() * bounce_speed)
        self.right_eye_y -= bounce_amplitude * math.sin(pygame.time.get_ticks() * bounce_speed)
        self.draw_eyes(self.left_eye_x, self.right_eye_x, self.eye_y, 
                      self.eye_width, self.eye_height, self.eye_color, self.glow_color)

    def update_color_transition(self):
        """Smoothly transition between current and target color"""
        current_r = self.eye_color.r
        current_g = self.eye_color.g
        current_b = self.eye_color.b
        
        target_r = self.target_color.r
        target_g = self.target_color.g
        target_b = self.target_color.b
        
        # Interpolate between current and target colors
        new_r = int(current_r + (target_r - current_r) * self.color_transition_speed)
        new_g = int(current_g + (target_g - current_g) * self.color_transition_speed)
        new_b = int(current_b + (target_b - current_b) * self.color_transition_speed)
        
        self.eye_color = pygame.Color(new_r, new_g, new_b)
        self.glow_color = pygame.Color(new_r, new_g, new_b, 100)

    def set_caption(self, text: str):
        """Update the caption text"""
        self.caption_text = text
        self.caption_start_time = time.time()

    def draw_caption(self):
        """Draw caption text under the eyes with improved visibility"""
        if not self.caption_text:
            return
            
        # Calculate alpha based on time
        elapsed = time.time() - self.caption_start_time
        if elapsed > self.caption_fade_time:
            self.caption_text = ""
            return
            
        alpha = 255
        if elapsed > (self.caption_fade_time - 2):  # Start fading 2 seconds before end
            alpha = int(255 * (self.caption_fade_time - elapsed) / 2)
        
        # Draw each line with improved background
        y = self.eye_y + self.eye_height + self.caption_y_offset
        words = self.caption_text.split()
        lines = []
        current_line = []
        
        # Word wrap
        for word in words:
            current_line.append(word)
            text_surface = self.caption_font.render(" ".join(current_line), True, self.caption_color)
            if text_surface.get_width() > self.caption_max_width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        # Draw each line
        for line in lines:
            # Create text surface
            text_surface = self.caption_font.render(line, True, self.caption_color)
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.screen_width // 2
            text_rect.y = y
            
            # Create slightly larger background
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)  # Solid black background
            
            # Draw text with current alpha
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, text_rect)
            
            y += text_rect.height + 10

    def set_talking(self, is_talking):
        """Enhanced talking animation control"""
        self.is_talking = is_talking
        if is_talking:
            self.target_curve = 0.3  # Slight smile while talking
            self.talk_phase = 0
            self.target_mouth_open = random.uniform(0.3, 1.0) * self.max_mouth_open
        else:
            self.target_curve = 0.2  # Return to gentle resting smile
            self.target_mouth_open = 0

    def center_face(self):
        """Improved face centering with smooth transition"""
        self.target_left_eye_x = (self.screen_width // 2) - (self.eye_spacing // 2) - self.eye_width
        self.target_right_eye_x = (self.screen_width // 2) + (self.eye_spacing // 2)
        self.target_eye_y = (self.screen_height // 2) - (self.eye_height // 2) - self.eye_vertical_offset
        self.is_animating = False  # Pause idle animation while centered
        self.force_display = True  # Ensure face is visible

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:  # Toggle animation with spacebar
                    self.toggle_animation()
                elif event.key == pygame.K_r:  # Example: Change to red with 'r' key
                    self.set_eye_color((255, 0, 0))
                elif event.key == pygame.K_b:  # Example: Change to blue with 'b' key
                    self.set_eye_color((0, 191, 255))

        self.update_color_transition()  # Add this line before drawing
        self.screen.fill("black")
        self.idle_eyes()  # Always draw face
        self.draw_caption()
        self.draw_led_lines()
        pygame.display.flip()
        self.clock.tick(60)


