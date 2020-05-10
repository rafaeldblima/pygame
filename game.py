import sys
from time import sleep

import pygame

from core.event_handler import EventHandler, EventType
from core.settings import Settings
from models.alien import Alien
from models.bullet import Bullet
from models.ship import Ship
from ui.button import Button
from ui.game_stats import GameStats
from ui.scoreboard import Scoreboard


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""

        pygame.init()

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        # Full screen
        # self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics, and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        self._start_event_handler()

        # MAke the play button
        self.play_button = Button(self, "Play")

    def _start_event_handler(self):
        """Start event handler"""
        self.event_handler = EventHandler()
        self._add_accepted_event_types()
        self._add_accepted_key_down_type()
        self._add_accepted_key_up_type()

    def _add_accepted_event_types(self):
        """Add available event types"""
        self.event_handler.register_types({
            pygame.QUIT: EventType(sys.exit, False),
            pygame.KEYDOWN: EventType(self._check_keydown_events, True),
            pygame.KEYUP: EventType(self._check_keyup_events, True),
            pygame.MOUSEBUTTONDOWN: EventType(self._check_play_button, False),
        })

    def _add_accepted_key_down_type(self):
        self.event_handler.register_key_down_actions({
            pygame.K_RIGHT: self.ship.move_right,
            pygame.K_LEFT: self.ship.move_left,
            pygame.K_UP: self.ship.move_up,
            pygame.K_DOWN: self.ship.move_down,
            pygame.K_SPACE: self._fire_bullet,
            pygame.K_q: sys.exit,
        })

    def _add_accepted_key_up_type(self):
        self.event_handler.register_key_up_actions({
            pygame.K_RIGHT: self.ship.stop_move_right,
            pygame.K_LEFT: self.ship.stop_move_left,
            pygame.K_UP: self.ship.stop_move_up,
            pygame.K_DOWN: self.ship.stop_move_down,
        })

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets"""
        # Update bullets position
        self.bullets.update()

        self._clear_bullets()

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, dokilla=True, dokillb=True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _clear_bullets(self):
        """Get rid of bullets that have disappeared."""
        for b in self.bullets.copy():
            if b.rect.bottom <= 0:
                self.bullets.remove(b)

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        # Redraw the screen during each pass though the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for b in self.bullets.sprites():
            b.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible.
        pygame.display.flip()

    def _check_events(self):
        """Respond to key presses and mouse events"""
        for event in pygame.event.get():
            self.event_handler.execute_event(event)

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        self.event_handler.execute_key_up(event.key)

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        self.event_handler.execute_key_down(event.key)

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """Create the fleet of aliens"""
        alien_height, number_aliens_x = self._get_alien_height_and_number_of_aliens_per_line()

        number_rows = self._get_number_of_rows_of_aliens_based_on_alien_height(alien_height)

        # Create the full fleet of aliens
        for row in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._creat_alien(alien_number, row)

    def _get_number_of_rows_of_aliens_based_on_alien_height(self, alien_height):
        """Base on screen height and alien height, calculate how many line of aliens we can have."""
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        return number_rows

    def _get_alien_height_and_number_of_aliens_per_line(self):
        """
        Get alien size, calculate the number of aliens that fit in one row
        and return the height of alien and the number.
        """
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        return alien_height, number_aliens_x

    def _creat_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _update_aliens(self):
        """
        Check if the fleet is at an edge, then update the positions of all aliens in the fleet
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached and edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""

        if self.stats.ships_left > 0:

            # Decrement ships_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _check_play_button(self):
        """Start a new game when the player clicks Play."""
        mouse_pos = pygame.mouse.get_pos()
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics
            self.stats.reset_stats()

            self.stats.game_active = True

            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
