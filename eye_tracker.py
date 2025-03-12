import pygame
import math
import random
import time
from enum import Enum

class EyeTracker:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.clock = pygame.time.Clock()  # Add clock initialization
        
        # Set up display
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Robot Eyes")
        
        # Eye properties
        self.eye_width = 100
        self.eye_height = 130
        self.eye_spacing = 140
        self.eye_color = (0, 191, 255)  # DeepSkyBlue
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # Remove all loading-related variables
        self.animation_active = True
        self.current_pos = {'x': 0, 'y': 0}
        self.target_pos = {'x': 0, 'y': 0}
        
        # Simplified movement parameters
        self.movement_params = {
            'transition_smoothing': 0.98,  # Very smooth transitions
            'max_distance': 30
        }
        
        # Remove unnecessary movement states
        self.emotions = {
            'neutral': {'movement_range': 0},
            'happy': {'movement_range': 0},
            'curious': {'movement_range': 0},
            'focused': {'movement_range': 0}
        }

        # Static LED line properties
        self.line_spacing = 4  # Space between lines
        self.line_color = (10, 10, 10)  # Very dark gray
        self.num_lines = self.height // self.line_spacing

        # Modify idle movement properties for smoother acceleration
        self.idle_timer = time.time()
        self.idle_interval = random.uniform(2.0, 4.0)  # Slightly longer pauses
        self.idle_directions = [
            {'x': 60, 'y': 0},    # Reduced movement range
            {'x': -60, 'y': 0},
            {'x': 0, 'y': 40},
            {'x': 0, 'y': -40},
        ]
        self.return_to_center = False
        self.center_delay = 0.8  # Longer pause before returning

        # Add simple emotions without movement
        self.emotions = {
            'neutral': {},
            'happy': {},
            'curious': {},
            'focused': {}
        }
        self.current_emotion = 'neutral'

        # Keep only required position tracking
        self.look_pos = [0, 0]  # x, y offset for looking around
        self.current_pos = {'x': 0, 'y': 0}
        self.target_pos = {'x': 0, 'y': 0}

        # Add required attributes for talking state
        self.is_talking = False

        # Bloom effect properties
        self.bloom_layers = 3  # Number of bloom layers
        self.bloom_intensity = 0.4  # Bloom brightness
        self.bloom_size = 4  # How much larger each bloom layer is

        # Add color transition properties
        self.target_color = (0, 191, 255)  # Default blue
        self.current_color = list(self.target_color)
        self.color_transition_speed = 0.05
        
        # Add happy animation properties
        self.happy_bounce_timer = time.time()
        self.happy_bounce_interval = random.uniform(5.0, 7.0)
        self.happy_bounce_amount = 0
        self.happy_bounce_target = 0
        self.happy_shape_points = []  # Store U-shape points

        # Update color transition properties
        self.current_color = [0, 191, 255]  # Starting blue color
        self.target_color = [0, 191, 255]  # Target color
        self.color_transition_speed = 0.05
        
        # Make happy animations more frequent during idle
        self.emotion_timer = time.time()
        self.emotion_interval = random.uniform(3.0, 5.0)  # More frequent emotion changes
        self.current_emotion = 'happy'  # Start with happy emotion

        # Add Cosmo-style animation properties
        self.blink_timer = time.time()
        self.blink_duration = 0.2  # Seconds for blink animation
        self.blink_progress = 0  # 0 to 1
        self.is_blinking = False
        self.current_shape = 'neutral'
        
        # Eye shape animation parameters
        self.shape_params = {
            'neutral': {
                'blink_interval': (3.0, 5.0),
                'height_scale': 1.0,
                'curve_top': 20,
                'curve_bottom': 20
            },
            'happy': {
                'blink_interval': (2.0, 3.0),
                'height_scale': 0.9,
                'bounce_interval': (5.0, 7.0),
                'bounce_amount': 8,
                'curve_top': 30,
                'curve_bottom': 10
            },
            'excited': {
                'blink_interval': (1.0, 2.0),
                'height_scale': 1.2,
                'pop_duration': 0.1,
                'pop_scale': 1.3,
                'curve_top': 25,
                'curve_bottom': 5
            },
            'sad': {
                'blink_interval': (4.0, 6.0),
                'height_scale': 0.85,
                'droop_interval': (6.0, 8.0),
                'droop_amount': 10,
                'curve_top': 15,
                'curve_bottom': 25
            }
        }
        
        self.next_effect_time = time.time()
        self.effect_progress = 0
        self.current_effect = None
        self.bounce_amount = 0

        # Add laughing animation properties
        self.laugh_timer = time.time()
        self.laugh_interval = 3.0  # Laugh every 3 seconds (increased)
        self.laugh_duration = 2.0  # Laugh for 2 seconds (increased)
        self.is_laughing = False
        self.laugh_bounce = 0
        self.laugh_bounce_speed = 0.3  # Faster bouncing
        self.laugh_bounce_amount = 10  # Maximum bounce height
        self.laugh_start_time = 0  # Track when laugh started

        # Update laugh timing
        self.laugh_timer = time.time()
        self.laugh_interval = random.uniform(10.0, 20.0)  # Longer interval between laughs
        
        # Add thinking animation properties
        self.think_timer = time.time()
        self.think_interval = 3.0
        self.is_thinking = False
        self.think_duration = 2.0
        self.think_start_time = 0
        self.think_bounce = 0
        self.think_x_offset = 0
        self.think_direction = 1
        self.think_speed = 0.2
        self.is_plus_shape = False

        # Update thinking animation properties
        self.think_timer = time.time()
        self.think_interval = random.uniform(20.0, 30.0)  # Longer interval
        self.is_thinking = False
        self.think_duration = 5.0  # Increase to 5 seconds
        self.think_start_time = 0
        self.think_bounce = 0
        self.think_x_offset = 0
        self.think_direction = 1
        self.think_speed = 0.2
        self.is_plus_shape = False
        self.question_offset_y = -120  # Move question mark higher
        
        # Question mark properties
        self.question_font = pygame.font.Font(None, 80)  # Larger font
        self.question_bounce_speed = 0.15
        self.question_bounce_amount = 15

        # Add fly animation properties
        self.fly_timer = time.time()
        self.fly_interval = 3.0
        self.is_fly_active = False
        self.fly_pos = [0, 0]
        self.fly_target = [0, 0]
        self.fly_speed = 0.1
        self.fly_size = 8
        self.is_zapping = False
        self.zap_duration = 0.3
        self.zap_start = 0
        self.zap_points = []
        self.dead_fly_pos = None
        self.dead_fly_timer = 0
        self.dead_fly_duration = 1.0

        # Add required zapping attributes
        self.close_start_time = 0  # Add missing attribute
        self.zap_start = 0
        self.is_zapping = False
        self.zap_duration = 0.3
        self.dead_fly_pos = None
        self.dead_fly_timer = 0

        # Update initial animation timers to delay startup
        self.laugh_timer = time.time() + random.uniform(10, 15)  # Start laugh after 10-15s
        self.think_timer = time.time() + random.uniform(12, 18)  # Start thinking after 12-18s
        self.fly_timer = time.time() + random.uniform(15, 20)    # Start fly after 15-20s
        self.emotion_timer = time.time() + random.uniform(10, 13)  # Start emotions after 10-13s
        
        # Update fly behavior properties
        self.fly_escape_chance = 0.3  # Lower escape chance
        self.min_fly_lifetime = 5.0   # Set fixed lifetime to 5 seconds
        self.max_fly_lifetime = 5.0   # Add max lifetime equal to min
        self.zap_range = 150   # Increased zap range
        self.required_close_time = 0.5  # Reduced time needed to be close

        # Add animation priority control
        self.is_green = False
        self.animation_blocked = False
        self.last_animation_time = time.time()
        self.animation_cooldown = 2.0  # Wait between animations

        # Update fly timing
        self.fly_timer = time.time() + random.uniform(40, 45)  # First fly appears after 40-45s
        self.fly_interval = random.uniform(35, 45)  # Next fly appears every 35-45s
        self.fly_escape_chance = 0.5  # Reduce escape chance so fly gets zapped more often

        # Add sheep counting animation properties
        self.sheep_timer = time.time() + random.uniform(15, 20)  # Start after initial delay
        self.sheep_interval = 5.0  # Every 5 seconds
        self.is_counting_sheep = False
        self.sheep_count = 0
        self.sheep_start_time = 0
        self.sheep_positions = []
        self.drowsiness = 0  # 0 to 1 for eye drooping
        self.sheep_number_font = pygame.font.Font(None, 100)
        self.sheep_duration = 4.0  # Duration of entire animation
        self.max_sheep = 3  # Number of sheep to count before sleeping

        # Update sheep counting animation properties
        self.sheep_timer = time.time() + random.uniform(15, 20)
        self.sheep_interval = 5.0
        self.is_counting_sheep = False
        self.sheep_count = 0
        self.sheep_rows = 3  # Number of rows of sheep
        self.sheep_per_row = 10  # Number of active sheep per row
        self.sheep_row_spacing = 50  # Vertical space between rows
        self.sheep_positions = [[] for _ in range(self.sheep_rows)]  # Sheep for each row
        self.sheep_directions = [1 if i % 2 == 0 else -1 for i in range(self.sheep_rows)]  # Alternate directions
        self.drowsiness = 0
        self.sheep_number_font = pygame.font.Font(None, 100)
        self.sheep_duration = 15.0  # Longer animation duration
        self.max_sheep = 99  # Count more sheep
        self.sheep_speed = 2  # Speed of sheep movement

        # Fix sheep animation properties initialization
        self.sheep_rows = 3
        self.sheep_per_row = 10
        self.sheep_row_spacing = 50
        self.sheep_positions = [[] for _ in range(self.sheep_rows)]  # Initialize properly
        self.sheep_directions = [1 if i % 2 == 0 else -1 for i in range(self.sheep_rows)]
        self.is_counting_sheep = False
        self.sheep_count = 0
        self.sheep_duration = 15.0
        self.max_sheep = 99
        self.sheep_speed = 2
        self.drowsiness = 0
        self.sheep_number_font = pygame.font.Font(None, 100)

        # Fix sheep animation properties - remove duplicates and set proper initialization
        self.sheep_rows = 3
        self.sheep_per_row = 10
        self.sheep_row_spacing = 50
        self.sheep_positions = [[] for _ in range(self.sheep_rows)]  # Initialize rows
        self.sheep_directions = [1 if i % 2 == 0 else -1 for i in range(self.sheep_rows)]
        self.sheep_speed = 2
        self.sheep_duration = 15.0
        self.sheep_interval = 5.0
        self.sheep_timer = time.time() + random.uniform(15, 20)
        self.sheep_start_time = 0
        self.sheep_count = 0
        self.max_sheep = 99
        self.drowsiness = 0
        self.is_counting_sheep = False
        self.sheep_number_font = pygame.font.Font(None, 100)

        # Update sheep animation timing
        self.sheep_interval = 3.0  # Run every 3 seconds after finishing
        self.sheep_duration = 15.0  # Animation lasts 15 seconds
        self.sheep_timer = time.time() + random.uniform(15, 20)  # Initial delay

        # Update fly timing settings
        self.min_fly_lifetime = 5.0  # Fixed 5 second lifetime before zap
        self.max_fly_lifetime = 5.0  # Force zap after exactly 5 seconds
        self.fly_speed = 0.08  # Slightly slower movement

        # Update sheep animation timings
        self.sheep_interval = 3.0  # Run every 3 seconds after finishing
        self.sheep_duration = 15.0  # Animation lasts 15 seconds
        self.sheep_timer = time.time() + 10.0  # Start after 10 seconds
        self.sheep_start_time = 0
        self.sheep_count = 0
        self.is_counting_sheep = False
        self.sheep_positions = [[] for _ in range(self.sheep_rows)]

        # Update sheep animation timing to start after 1 minute
        self.sheep_timer = time.time() + 60.0  # Start after 60 seconds
        self.sheep_duration = 15.0  # Animation lasts 15 seconds
        self.sheep_interval = 3.0  # Run every 3 seconds after finishing
        self.sheep_start_time = 0
        self.is_counting_sheep = False
        self.eyes_squinted = False  # New flag to track squinted state

        # Update laugh timing for more frequent laughs
        self.laugh_timer = time.time() + random.uniform(5, 8)  # First laugh after 5-8s
        self.laugh_interval = random.uniform(8.0, 12.0)  # Laugh every 8-12 seconds
        self.laugh_duration = 2.0  # Keep same duration

        # Update thinking animation timing
        self.think_timer = time.time() + random.uniform(3, 6)  # First think after 3-6s
        self.think_interval = random.uniform(10.0, 15.0)  # Think every 10-15 seconds
        self.think_duration = 5.0  # Keep same duration

        # Update fly timing for more frequent appearances
        self.fly_timer = time.time() + 30.0  # First fly after 30s exactly
        self.fly_interval = 30.0  # Appear every 30 seconds exactly
        self.min_fly_lifetime = 5.0  # Keep same lifetime
        self.max_fly_lifetime = 5.0  # Keep same lifetime

        # Add evil laugh animation properties
        self.evil_timer = time.time() + 3.0
        self.evil_interval = 3.0
        self.is_evil = False
        self.evil_duration = 5.0
        self.evil_start_time = 0
        self.evil_bounce = 0
        self.evil_bounce_speed = 0.3
        self.evil_bounce_amount = 15
        self.flame_particles = []
        self.evil_color = (255, 69, 0)  # Orange-red for evil mode

    def draw_led_lines(self):
        """Draw static lines across entire window"""
        for i in range(self.num_lines):
            y_pos = i * self.line_spacing
            try:
                pygame.draw.line(self.screen, self.line_color,
                               (0, y_pos), (self.width, y_pos), 1)
            except pygame.error:
                pass  # Ignore any pygame drawing errors

    def _generate_u_shape(self, x, y, width, height):
        """Generate points for U-shaped eye"""
        points = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            # Create U curve using parametric equations
            px = x + width * t
            py = y + height * (0.5 - 0.5 * math.sin(t * math.pi))
            points.append((int(px), (int(py))))
        return points

    def _generate_v_shape(self, x, y, width, height):
        """Generate points for a proper upside-down V shape"""
        # Calculate key points
        left_point = (x, y + height)  # Bottom left
        peak_point = (x + width//2, y)  # Top center (peak of upside-down V)
        right_point = (x + width, y + height)  # Bottom right
        
        # Generate points along the lines for smooth rendering
        points = []
        steps = 20
        
        # Left line of V
        for i in range(steps):
            t = i / steps
            px = left_point[0] + (peak_point[0] - left_point[0]) * t
            py = left_point[1] + (peak_point[1] - left_point[1]) * t
            points.append((int(px), int(py)))
        
        # Add peak point
        points.append(peak_point)
        
        # Right line of V
        for i in range(steps + 1):
            t = i / steps
            px = peak_point[0] + (right_point[0] - peak_point[0]) * t
            py = peak_point[1] + (right_point[1] - peak_point[1]) * t
            points.append((int(px), int(py)))
        
        return points

    def _generate_plus_shape(self, x, y, width, height):
        """Generate points for plus-shaped eye"""
        vertical_rect = pygame.Rect(
            x + width//3,
            y,
            width//3,
            height
        )
        horizontal_rect = pygame.Rect(
            x,
            y + height//3,
            width,
            height//3
        )
        return vertical_rect, horizontal_rect

    def _generate_evil_shape(self, x, y, width, height):
        """Generate sharp evil eye shape"""
        points = []
        steps = 20
        
        # Top curve (sharp point)
        for i in range(steps // 2):
            t = i / (steps // 2)
            px = x + width * t
            py = y + height * (0.3 * math.sin(t * math.pi))
            points.append((int(px), int(py)))
            
        # Bottom curve (sharp point)
        for i in range(steps // 2):
            t = i / (steps // 2)
            px = x + width * (1 - t)
            py = y + height * (1 - 0.3 * math.sin(t * math.pi))
            points.append((int(px), int(py)))
            
        return points

    def update_flames(self):
        """Update flame particle effects"""
        # Add new particles
        if random.random() < 0.3:
            base_x = random.randint(0, self.width)
            self.flame_particles.append({
                'x': base_x,
                'y': self.height + 10,
                'speed': random.uniform(5, 8),
                'life': 1.0,
                'size': random.uniform(10, 20)
            })
        
        # Update existing particles
        for p in self.flame_particles[:]:
            p['y'] -= p['speed']
            p['life'] -= 0.02
            if p['life'] <= 0:
                self.flame_particles.remove(p)

    def draw_flames(self):
        """Draw animated flame effects"""
        for p in self.flame_particles:
            # Calculate flame color based on life
            intensity = int(255 * p['life'])
            color = (255, intensity, 0, int(255 * p['life']))
            
            # Draw flame particle
            size = int(p['size'] * p['life'])
            points = [
                (p['x'], p['y']),
                (p['x'] - size, p['y'] + size * 2),
                (p['x'] + size, p['y'] + size * 2)
            ]
            pygame.draw.polygon(self.screen, color, points)

    def draw_thinking_symbol(self, x, y):
        """Draw animated question mark centered between eyes"""
        # Render question mark in eye color
        question_mark = self.question_font.render("?", True, self.current_color)
        
        # Calculate center point between eyes
        center_x = self.center_x  # Use screen center instead of individual eye position
        
        # Calculate bobbing motion
        self.think_bounce += self.think_speed
        y_offset = math.sin(self.think_bounce) * self.question_bounce_amount
        
        # Position above and between eyes
        question_rect = question_mark.get_rect()
        question_x = center_x - question_rect.width//2  # Center horizontally
        question_y = y + self.question_offset_y + y_offset
        
        # Draw question mark
        self.screen.blit(question_mark, (question_x, question_y))

    def draw_eye(self, x, y):
        current_time = time.time()
        is_blue = tuple(self.current_color[:3]) == (0, 191, 255)
        
        # Handle evil animation first and override normal eye drawing
        if is_blue and not self.animation_blocked:
            if not self.is_evil and current_time >= self.evil_timer:
                self.is_evil = True
                self.evil_start_time = current_time
                self.evil_bounce = 0
                self.is_laughing = False
                self.is_thinking = False
                self.is_blinking = False
                self.animation_blocked = True
                self.flame_particles = []
                return  # Skip normal eye drawing when starting evil mode
                
            if self.is_evil:
                progress = (current_time - self.evil_start_time) / self.evil_duration
                if progress >= 1.0:
                    self.is_evil = False
                    self.evil_timer = current_time + self.evil_interval
                    self.animation_blocked = False
                else:
                    # Evil bounce animation
                    self.evil_bounce += self.evil_bounce_speed
                    bounce_offset = math.sin(self.evil_bounce) * self.evil_bounce_amount
                    
                    # Draw evil eyes with bloom effect
                    points = self._generate_evil_shape(
                        x - self.eye_width//2,
                        y - self.eye_height//2 + bounce_offset,
                        self.eye_width,
                        self.eye_height
                    )
                    
                    # Draw bloom layers
                    if len(points) > 2:
                        for i in range(self.bloom_layers):
                            size_increase = self.bloom_size * (i + 1)
                            opacity = int(255 * self.bloom_intensity / (i + 1))
                            bloom_color = (*self.evil_color, opacity)
                            pygame.draw.polygon(self.screen, bloom_color, points)
                        
                        # Draw main evil eye shape
                        pygame.draw.polygon(self.screen, self.evil_color, points)
                        
                    return  # Skip normal eye drawing during evil mode

        if is_blue:
            # Check for thinking animation first
            if not self.is_thinking and current_time >= self.think_timer:
                self.is_thinking = True
                self.think_timer = current_time + self.think_interval
                self.think_start_time = current_time
                self.think_bounce = 0
                self.is_plus_shape = True
            
            # Handle thinking animation
            if self.is_thinking:
                if current_time - self.think_start_time > self.think_duration:
                    self.is_thinking = False
                    self.is_plus_shape = False
                    self.think_timer = current_time + self.think_interval
                else:
                    # Draw plus-shaped eyes instead of regular eyes
                    vert_rect, horiz_rect = self._generate_plus_shape(
                        x - self.eye_width//2,
                        y - self.eye_height//2,
                        self.eye_width,
                        self.eye_height
                    )
                    
                    # Draw bloom effect for plus shape
                    for i in range(self.bloom_layers):
                        size_increase = self.bloom_size * (i + 1)
                        opacity = int(255 * self.bloom_intensity / (i + 1))
                        bloom_color = (*self.current_color, opacity)
                        
                        # Bloom for vertical part
                        vert_bloom = vert_rect.inflate(size_increase, size_increase)
                        pygame.draw.rect(self.screen, bloom_color, vert_bloom, border_radius=10)
                        
                        # Bloom for horizontal part
                        horiz_bloom = horiz_rect.inflate(size_increase, size_increase)
                        pygame.draw.rect(self.screen, bloom_color, horiz_bloom, border_radius=10)
                    
                    # Draw main plus shape
                    pygame.draw.rect(self.screen, self.current_color, vert_rect, border_radius=10)
                    pygame.draw.rect(self.screen, self.current_color, horiz_rect, border_radius=10)
                    
                    # Draw thinking symbol only once after both eyes are drawn
                    if x == self.center_x + self.eye_spacing//2:  # After drawing right eye
                        self.draw_thinking_symbol(self.center_x, y)
                    return  # Skip normal eye drawing

            # Rest of existing eye drawing code...
            # Check if it's time to laugh
            if not self.is_laughing and current_time >= self.laugh_timer:
                self.is_laughing = True
                self.laugh_timer = current_time + self.laugh_interval
                self.laugh_bounce = 0
                self.laugh_start_time = current_time

            # Handle laughing animation
            if self.is_laughing:
                # Check if laugh should end
                if current_time - self.laugh_start_time > self.laugh_duration:
                    self.is_laughing = False
                else:
                    # Calculate bounce with easing
                    self.laugh_bounce += self.laugh_bounce_speed
                    bounce_offset = math.sin(self.laugh_bounce) * self.laugh_bounce_amount
                    
                    # Draw V-shaped eyes with bounce
                    for i in range(self.bloom_layers):
                        size_increase = self.bloom_size * (i + 1)
                        opacity = int(255 * self.bloom_intensity / (i + 1))
                        bloom_color = (*self.current_color, opacity)
                        
                        # Use current eye position for V shapes
                        points = self._generate_v_shape(
                            x - self.eye_width//2,
                            y - self.eye_height//2 + bounce_offset,
                            self.eye_width,
                            self.eye_height
                        )
                        if len(points) > 2:  # Ensure enough points to draw
                            pygame.draw.aalines(self.screen, bloom_color, False, points)

                    # Draw main V-shaped eye
                    points = self._generate_v_shape(
                        x - self.eye_width//2,
                        y - self.eye_height//2 + bounce_offset,
                        self.eye_width,
                        self.eye_height
                    )
                    if len(points) > 2:
                        # Draw filled V shape
                        pygame.draw.polygon(self.screen, self.current_color, points)
                        # Add outline for crisp edges
                        pygame.draw.lines(self.screen, self.current_color, False, points, 4)
                    return  # Skip normal eye drawing when laughing
                    
            else:
                # Regular eye drawing code
                # Handle blinking
                if not self.is_blinking and current_time >= self.blink_timer:
                    self.is_blinking = True
                    self.blink_progress = 0
                    interval = random.uniform(*self.shape_params[self.current_shape]['blink_interval'])
                    self.blink_timer = current_time + interval
                
                if self.is_blinking:
                    delta_time = self.clock.get_time() / 1000.0  # Get proper time delta
                    self.blink_progress += delta_time / self.blink_duration
                    if self.blink_progress >= 1:
                        self.is_blinking = False
                        self.blink_progress = 0
                
                # Calculate shape modifications
                height_scale = self.shape_params[self.current_shape]['height_scale']
                if self.is_blinking:
                    # Apply blink squish
                    blink_curve = math.sin(self.blink_progress * math.pi)
                    height_scale *= 1 - blink_curve
                
                # Apply happy bounce effect
                if self.current_shape == 'happy':
                    if current_time >= self.next_effect_time:
                        self.bounce_amount = self.shape_params['happy']['bounce_amount']
                        self.next_effect_time = current_time + random.uniform(*self.shape_params['happy']['bounce_interval'])
                    self.bounce_amount *= 0.9  # Smooth decay
                    
                    y += self.bounce_amount
                    
                # Draw bloom effect
                for i in range(self.bloom_layers):
                    size_increase = self.bloom_size * (i + 1)
                    opacity = int(255 * self.bloom_intensity / (i + 1))
                    bloom_color = (*self.current_color, opacity)
                    
                    height = self.eye_height * height_scale
                    
                    rect = pygame.Rect(
                        x - (self.eye_width + size_increase)//2,
                        y - (height + size_increase)//2,
                        self.eye_width + size_increase,
                        height + size_increase
                    )
                    
                    # Use shape-specific corner radii
                    pygame.draw.rect(self.screen, bloom_color, rect,
                                   border_radius=self.shape_params[self.current_shape]['curve_top'])
                
                # Draw main eye
                rect = pygame.Rect(
                    x - self.eye_width//2,
                    y - (self.eye_height * height_scale)//2,
                    self.eye_width,
                    self.eye_height * height_scale
                )
                
                pygame.draw.rect(self.screen, self.current_color, rect,
                               border_radius=self.shape_params[self.current_shape]['curve_top'])

        else:
            # Use normal eye drawing when not blue
            rect = pygame.Rect(x - self.eye_width//2, y - self.eye_height//2,
                             self.eye_width, self.eye_height)
            pygame.draw.rect(self.screen, self.current_color, rect, border_radius=20)

        if is_blue:
            # Check for thinking animation
            if not self.is_thinking and current_time >= self.think_timer:
                self.is_thinking = True
                self.think_timer = current_time + self.think_interval
                self.think_start_time = current_time
                self.think_bounce = 0
                self.is_plus_shape = True
                
            # Handle thinking animation
            if self.is_thinking:
                if current_time - self.think_start_time > self.think_duration:
                    self.is_thinking = False
                    self.is_plus_shape = False
                    self.think_timer = current_time + self.think_interval  # Reset timer
                else:
                    # Draw plus-shaped eyes
                    vert_rect, horiz_rect = self._generate_plus_shape(
                        x - self.eye_width//2,
                        y - self.eye_height//2,
                        self.eye_width,
                        self.eye_height
                    )
                    
                    # Draw bloom effect for plus shape
                    for i in range(self.bloom_layers):
                        size_increase = self.bloom_size * (i + 1)
                        opacity = int(255 * self.bloom_intensity / (i + 1))
                        bloom_color = (*self.current_color, opacity)
                        
                        # Bloom for vertical part
                        vert_bloom = vert_rect.inflate(size_increase, size_increase)
                        pygame.draw.rect(self.screen, bloom_color, vert_bloom, border_radius=10)
                        
                        # Bloom for horizontal part
                        horiz_bloom = horiz_rect.inflate(size_increase, size_increase)
                        pygame.draw.rect(self.screen, bloom_color, horiz_bloom, border_radius=10)
                    
                    # Draw main plus shape
                    pygame.draw.rect(self.screen, self.current_color, vert_rect, border_radius=10)
                    pygame.draw.rect(self.screen, self.current_color, horiz_rect, border_radius=10)
                    
                    # Draw thinking symbol above first eye only
                    if x == self.center_x - self.eye_spacing//2:
                        self.draw_thinking_symbol(x, y)
                    
                    return

            # Check for laugh animation with updated timing
            if not self.is_laughing and current_time >= self.laugh_timer:
                self.is_laughing = True
                self.laugh_timer = current_time + random.uniform(10.0, 20.0)  # Random interval
                self.laugh_bounce = 0
                self.laugh_start_time = current_time

    def update_color_transition(self):
        """Smooth color transition"""
        for i in range(3):
            self.current_color[i] += (self.target_color[i] - self.current_color[i]) * self.color_transition_speed
            self.current_color[i] = max(0, min(255, self.current_color[i]))  # Clamp values
        
        # Update actual eye color from current transition color
        self.eye_color = tuple(int(c) for c in self.current_color)

    def update_happy_animation(self):
        """Update happy state animations"""
        if self.current_emotion == 'happy' and not self.is_laughing:
            current_time = time.time()
            
            # Handle bounce effect
            if current_time >= self.happy_bounce_timer:
                self.happy_bounce_target = random.randint(3, 8)
                self.happy_bounce_timer = current_time + random.uniform(5.0, 7.0)
            
            # Smooth bounce transition
            self.happy_bounce_amount += (self.happy_bounce_target - self.happy_bounce_amount) * 0.1
            
            # Reset bounce
            if abs(self.happy_bounce_amount - self.happy_bounce_target) < 0.1:
                self.happy_bounce_target = 0
        else:
            # Reset bounce when not happy
            self.happy_bounce_amount = 0
            self.happy_bounce_target = 0

    def update_eye_position(self):
        """Updated eye position handling with return to center"""
        current_time = time.time()
        
        # Handle idle movement
        if self.animation_active and current_time >= self.idle_timer:
            if not self.return_to_center:
                # Move to random direction
                new_target = random.choice(self.idle_directions)
                self.slide_to_position(new_target['x'], new_target['y'], easing='cubic')
                self.return_to_center = True
                self.idle_timer = current_time + self.center_delay
            else:
                # Return to center
                self.slide_to_position(0, 0, easing='cubic')
                self.return_to_center = False
                self.idle_timer = current_time + self.idle_interval
                self.idle_interval = random.uniform(1.5, 3.0)

        # Update current position through transition manager
        if hasattr(self, 'transition_manager'):
            pos = self.transition_manager.get_current_position()
            if pos:
                self.current_pos['x'], self.current_pos['y'] = pos
        
        self.look_pos[0] = self.current_pos['x']
        self.look_pos[1] = self.current_pos['y']

        # Update shape when blue
        if tuple(self.current_color[:3]) == (0, 191, 255):
            current_time = time.time()
            # Randomly switch between neutral and happy when idle
            if current_time >= self.emotion_timer:
                self.current_shape = random.choice(['neutral', 'happy'])
                self.emotion_timer = current_time + random.uniform(4.0, 8.0)

    def update_fly_position(self):
        """Update fly movement with more natural behavior"""
        if not self.is_fly_active:
            return

        current_time = time.time()
        
        # Move fly towards target
        dx = self.fly_target[0] - self.fly_pos[0]
        dy = self.fly_target[1] - self.fly_pos[1]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 10:  # Pick new target when close
            # More random movement patterns
            if random.random() < 0.3:  # 30% chance to move to screen edges
                edge = random.choice(['top', 'bottom', 'left', 'right'])
                if edge == 'top':
                    self.fly_target = [random.randint(0, self.width), 0]
                elif edge == 'bottom':
                    self.fly_target = [random.randint(0, self.width), self.height]
                elif edge == 'left':
                    self.fly_target = [0, random.randint(0, self.height)]
                else:
                    self.fly_target = [self.width, random.randint(0, self.height)]
            else:
                self.fly_target = [
                    random.randint(0, self.width),
                    random.randint(0, self.height)
                ]
        
        # Update position with slight randomness
        self.fly_pos[0] += (dx * self.fly_speed + random.uniform(-0.5, 0.5))
        self.fly_pos[1] += (dy * self.fly_speed + random.uniform(-0.5, 0.5))

    def draw_fly(self):
        """Draw fly and laser effects"""
        if not self.is_fly_active and not self.dead_fly_pos:
            return

        current_time = time.time()

        if self.is_zapping:
            # Draw laser beams from eyes
            left_eye_center = (self.center_x - self.eye_spacing//2, self.center_y)
            right_eye_center = (self.center_x + self.eye_spacing//2, self.center_y)
            
            # Draw laser with bloom effect
            for i in range(3):
                offset = i * 2
                laser_color = (*self.current_color[:3], 100 - i*30)
                pygame.draw.line(self.screen, laser_color, left_eye_center, 
                               (self.fly_pos[0], self.fly_pos[1]), 3+offset)
                pygame.draw.line(self.screen, laser_color, right_eye_center, 
                               (self.fly_pos[0], self.fly_pos[1]), 3+offset)

            if current_time - self.zap_start > self.zap_duration:
                self.is_zapping = False
                self.dead_fly_pos = self.fly_pos.copy()
                self.dead_fly_timer = current_time
                self.is_fly_active = False

        if self.dead_fly_pos:
            # Draw dead fly (X_X)
            if current_time - self.dead_fly_timer < self.dead_fly_duration:
                pygame.draw.line(self.screen, (255,0,0), 
                               (self.dead_fly_pos[0]-5, self.dead_fly_pos[1]-5),
                               (self.dead_fly_pos[0]+5, self.dead_fly_pos[1]+5), 2)
                pygame.draw.line(self.screen, (255,0,0),
                               (self.dead_fly_pos[0]-5, self.dead_fly_pos[1]+5),
                               (self.dead_fly_pos[0]+5, self.dead_fly_pos[1]-5), 2)
            else:
                self.dead_fly_pos = None

        elif self.is_fly_active:
            # Draw active fly
            pygame.draw.circle(self.screen, (100,100,100), 
                             (int(self.fly_pos[0]), int(self.fly_pos[1])), 
                             self.fly_size)
            # Draw wings
            wing_offset = math.sin(time.time() * 30) * 3
            pygame.draw.ellipse(self.screen, (150,150,150), 
                              (self.fly_pos[0]-8, self.fly_pos[1]-5+wing_offset, 6, 4))
            pygame.draw.ellipse(self.screen, (150,150,150), 
                              (self.fly_pos[0]+2, self.fly_pos[1]-5+wing_offset, 6, 4))

    def draw_sheep(self, x, y, direction=1):
        """Draw a simple sheep shape"""
        # Flip sheep based on direction
        offset = 20 if direction > 0 else -20
        
        # Draw fluffy body
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), 15)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x-10), int(y-5)), 12)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x+10), int(y-5)), 12)
        
        # Draw head in proper direction
        head_x = x + offset
        pygame.draw.circle(self.screen, (200, 200, 200), (int(head_x), int(y+5)), 8)
        
        # Draw legs with walking animation
        leg_offset = math.sin(time.time() * 10) * 3
        pygame.draw.line(self.screen, (200, 200, 200), 
                        (x-5, y+15), (x-5, y+25+leg_offset), 2)
        pygame.draw.line(self.screen, (200, 200, 200),
                        (x+5, y+15), (x+5, y+25-leg_offset), 2)

    def update_sheep_animation(self):
        """Handle sheep counting animation with updated timing"""
        if not self.is_counting_sheep:
            return

        current_time = time.time()
        progress = (current_time - self.sheep_start_time) / self.sheep_duration

        # Reset animation when complete
        if progress >= 1.0:
            self.is_counting_sheep = False
            self.sheep_timer = current_time + 3.0  # Next animation in 3 seconds
            self.sheep_positions = [[] for _ in range(self.sheep_rows)]
            self.sheep_count = 0
            return

        # Safely update each row
        for row in range(self.sheep_rows):
            # Add new sheep if needed and row exists
            if row < len(self.sheep_positions):
                if len(self.sheep_positions[row]) < self.sheep_per_row:
                    if random.random() < 0.02:  # Random sheep spawning
                        direction = self.sheep_directions[row]
                        start_x = -50 if direction > 0 else self.width + 50
                        self.sheep_positions[row].append({
                            'x': start_x,
                            'y': self.center_y + 100 + (row * self.sheep_row_spacing),
                            'counted': False
                        })

                # Update existing sheep in this row
                i = 0
                while i < len(self.sheep_positions[row]):
                    sheep = self.sheep_positions[row][i]
                    sheep['x'] += self.sheep_speed * self.sheep_directions[row]
                    
                    # Count sheep when passing center
                    if not sheep['counted']:
                        if ((self.sheep_directions[row] > 0 and sheep['x'] > self.center_x) or
                            (self.sheep_directions[row] < 0 and sheep['x'] < self.center_x)):
                            sheep['counted'] = True
                            self.sheep_count += 1

                    # Remove if off screen
                    if sheep['x'] < -100 or sheep['x'] > self.width + 100:
                        self.sheep_positions[row].pop(i)
                    else:
                        i += 1

        # Update drowsiness
        self.drowsiness = min(1.0, progress * 1.2)

    def draw_sheep_counting(self):
        """Draw sheep counting animation elements without counter"""
        if not self.is_counting_sheep or not self.sheep_positions:
            return

        # Draw sheep for each row
        for row in range(self.sheep_rows):
            for sheep in self.sheep_positions[row]:
                self.draw_sheep(sheep['x'], sheep['y'], self.sheep_directions[row])

        # Keep eyes squinted until wake word
        if self.drowsiness > 0:
            self.eye_height = int(130 * (1 - self.drowsiness * 0.8))

    def run(self):
        """Main display loop with error handling"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

            self.screen.fill((26, 26, 26))
            
            if hasattr(self, 'transition_manager'):
                self.update_eye_position()
            
            # Update color and animations
            self.update_color_transition()
            self.update_happy_animation()
            
            # Force happy emotion during idle
            current_time = time.time()
            if current_time >= self.emotion_timer:
                self.current_emotion = 'happy'
                self.emotion_timer = current_time + self.emotion_interval
            
            # Draw basic eyes
            left_eye_x = self.center_x - self.eye_spacing//2
            right_eye_x = self.center_x + self.eye_spacing//2
            try:
                self.draw_eye(left_eye_x + self.look_pos[0], self.center_y + self.look_pos[1])
                self.draw_eye(right_eye_x + self.look_pos[0], self.center_y + self.look_pos[1])
                
                # Update and draw flames if in evil mode
                if self.is_evil:
                    self.update_flames()
                    self.draw_flames()
                    
                # Draw LED lines last
                self.draw_led_lines()
                
            except pygame.error:
                pass  # Ignore any pygame drawing errors
                
            current_time = time.time()
            is_blue = tuple(self.current_color[:3]) == (0, 191, 255)
            self.is_green = tuple(self.current_color[:3]) == (144, 238, 144)
            
            # Check if animations should be blocked
            self.animation_blocked = (
                self.is_green or 
                self.is_laughing or 
                self.is_thinking or 
                current_time - self.last_animation_time < self.animation_cooldown
            )
            
            # Update fly spawn timing to be exactly 30 seconds
            if is_blue and not self.animation_blocked:
                if not self.is_fly_active and not self.is_zapping and \
                   not self.dead_fly_pos and current_time >= self.fly_timer:
                    self.is_fly_active = True
                    self.fly_pos = [self.width//2, 0]
                    self.fly_target = [
                        random.randint(self.width//4, 3*self.width//4),
                        random.randint(self.height//4, 3*self.height//4)
                    ]
                    self.fly_timer = current_time + 30.0  # Exactly 30 seconds
                    self.fly_start_time = current_time
                    self.last_animation_time = current_time

            # Block other animations during sheep
            if not self.is_counting_sheep:
                # Update fly if active
                if self.is_fly_active and not self.is_zapping:
                    self.update_fly_position()
                    
                    # Force zap after 5 seconds
                    current_time = time.time()
                    if current_time - self.fly_start_time >= self.max_fly_lifetime:
                        self.is_zapping = True
                        self.zap_start = current_time
                        self.last_animation_time = current_time
                    elif not self.is_green:
                        # Regular zap check logic
                        eye_center = (self.center_x, self.center_y)
                        dx = self.fly_pos[0] - eye_center[0]
                        dy = self.fly_pos[1] - eye_center[1]
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        if dist < self.zap_range:
                            if self.close_start_time == 0:
                                self.close_start_time = current_time
                            elif current_time - self.close_start_time > self.required_close_time:
                                self.is_zapping = True
                                self.zap_start = current_time
                                self.last_animation_time = current_time

                # Draw fly effects
                if not self.is_green:  # Don't show fly when green
                    self.draw_fly()

            # Check for sheep counting animation
            if is_blue and not self.animation_blocked and not self.eyes_squinted:
                if not self.is_counting_sheep and current_time >= self.sheep_timer:
                    # Block all other animations when sheep starts
                    self.is_counting_sheep = True
                    self.sheep_start_time = current_time
                    self.drowsiness = 0
                    self.sheep_positions = [[] for _ in range(self.sheep_rows)]
                    self.animation_blocked = True
                    self.is_laughing = False
                    self.is_thinking = False
                    self.is_fly_active = False
                    self.is_zapping = False
                    self.animation_active = False  # Stop eye movement

            # Update sheep animation if active
            if self.is_counting_sheep:
                self.update_sheep_animation()
                self.draw_sheep_counting()
                if current_time - self.sheep_start_time >= self.sheep_duration:
                    self.eyes_squinted = True  # Keep eyes squinted after animation

            # Force squinted eyes after sheep animation
            if self.eyes_squinted:
                self.eye_height = int(130 * 0.2)  # Keep eyes at 20% height
                self.animation_active = False  # Keep eyes from moving

            self.clock.tick(60)  # Control frame rate
            pygame.display.flip()
            return True
            
        except Exception as e:
            print(f"Error in run loop: {e}")
            return True  # Continue running despite errors

    def set_animation_state(self, state):
        """Set the animation state of the eye tracker"""
        self.animation_active = state

    def set_eye_color(self, color):
        """Set the color of the eyes with proper RGB values"""
        self.target_color = list(color)
        if tuple(color) == (144, 238, 144):  # Green color
            # Reset all animation states
            self.is_laughing = False
            self.is_thinking = False
            self.is_fly_active = False
            self.is_zapping = False
            self.dead_fly_pos = None
            self.animation_blocked = True

    def set_emotion(self, emotion_name, smooth=False):
        """Simple emotion setter without animations"""
        if emotion_name in self.emotions:
            self.current_emotion = emotion_name
            if hasattr(self, 'transition_manager') and smooth:
                self.transition_manager.start_transition(
                    (self.current_pos['x'], self.current_pos['y']),
                    (0, 0)  # Always move to center for now
                )

    def slide_to_position(self, target_x, target_y, easing='cubic'):
        """Start a smooth transition to a new position with acceleration"""
        if hasattr(self, 'transition_manager'):
            # Use cubic easing for smooth acceleration/deceleration
            self.transition_manager.set_easing('cubic')
            self.transition_manager.start_transition(
                (self.current_pos['x'], self.current_pos['y']),
                (target_x, target_y)
            )
            self.target_pos = {'x': target_x, 'y': target_y}

    def set_talking(self, state):
        """Set talking state"""
        self.is_talking = state

    def cleanup(self):
        """Clean up Pygame resources"""
        pygame.quit()
