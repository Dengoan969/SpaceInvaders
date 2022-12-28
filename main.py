from datetime import datetime
import pygame
import pygame_menu
import random
import pickle

from game_objects import Ship, Bullet, Alien, Bunker_Block, MysteryShip, Bonus


class GameLevel:
    def __init__(self, level):
        self.screen = pygame.display.get_surface()
        self.screen_width, self.screen_height = self.screen.get_size()

        ship = Ship(self.screen_width // 2, self.screen_height - 100,
                    self.screen_width, self.screen_height)
        self.ship = pygame.sprite.GroupSingle(ship)

        self.lives = 0
        self.live_img = pygame.image.load(
            'textures/ship.png').convert()
        self.live_x_start_pos = self.screen_width - (
                self.live_img.get_size()[0] * 2 + 20)

        self.score = 0

        self.font = pygame.font.SysFont('pixeled', 40)
        self.big_font = pygame.font.SysFont('pixeled', 72)

        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens_direction = 1
        self.aliens_speed = 1

        self.mystery_spawn_time = random.randint(500, 1000)
        self.mystery = pygame.sprite.GroupSingle()
        self.bonuses = pygame.sprite.Group()
        self.active_bonuses = pygame.sprite.Group()
        self.bonuses_spawn_kills = random.randint(5, 10)

        with open('textures/BunkerShape.txt') as f:
            self.bunker_shape = f.readlines()

        self.block_size = 15
        self.blocks = pygame.sprite.Group()
        self.bunker_x_positions = [
            num * (self.screen_width / 4) for num in
            range(4)]
        self.create_level(level)

        self.laser_sound = pygame.mixer.Sound("audio/shoot_sound.wav")
        self.laser_sound.set_volume(0.3)
        self.is_lost = False
        self.is_win = False
        self.is_freeze = False

    def run(self):
        run = True
        clock = pygame.time.Clock()
        aliens_shoot_event = pygame.USEREVENT + 0
        pygame.time.set_timer(aliens_shoot_event, 1000)
        while run:
            clock.tick(60)
            if self.is_win or self.is_lost:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_game_continue()
                        run = False
                        break
                if event.type == aliens_shoot_event and not self.is_freeze:
                    self.aliens_shoot()
            self.update()

    def gameplay_draw(self):
        self.blocks.draw(self.screen)
        self.mystery.draw(self.screen)
        self.bonuses.draw(self.screen)
        self.aliens.draw(self.screen)
        self.alien_bullets.draw(self.screen)
        self.display_score()
        self.display_lives()
        self.check_win()
        self.check_lost()
        if not self.is_lost:
            self.ship.sprite.bullets.draw(self.screen)
            self.ship.draw(self.screen)

    def gameplay_update(self):
        self.ship.update()
        self.ship.sprite.bullets.update()

        self.collision_check()

        self.extra_alien_timer()
        self.active_bonuses_timer()
        self.mystery.update()
        self.bonuses.update()

        self.aliens_position_check()
        self.alien_bullets.update()
        self.aliens.update(self.aliens_direction, self.aliens_speed)

    def update(self):
        self.screen.fill((0, 0, 0))
        if not self.is_lost:
            self.gameplay_update()
            self.gameplay_draw()
        pygame.display.update()

    def collision_check(self):
        for bullet in self.ship.sprite.bullets:
            hit_aliens = pygame.sprite.spritecollide(bullet, self.aliens, True)
            for alien in hit_aliens:
                bullet.kill()
                self.bonuses_timer(alien.rect.x, alien.rect.y)
                self.score += alien.price
                self.aliens_speed += 0.1
            bunker_blocks = pygame.sprite.spritecollide(bullet, self.blocks,
                                                        False)
            for block in bunker_blocks:
                if not block.is_translucent:
                    block.kill()
                    bullet.kill()

            if pygame.sprite.spritecollide(bullet, self.mystery, True):
                bullet.kill()
                self.score += 500

        for bullet in self.alien_bullets:
            if pygame.sprite.spritecollide(bullet, self.blocks, True):
                bullet.kill()
            if pygame.sprite.spritecollide(bullet, self.ship, True):
                bullet.kill()
                self.lives -= 1
                if self.lives >= 0:
                    ship = Ship(self.screen_width // 2,
                                self.screen_height - 100,
                                self.screen_width, self.screen_height)
                    self.ship = pygame.sprite.GroupSingle(ship)

        for bonus in self.bonuses:
            if pygame.sprite.spritecollide(bonus, self.ship, False):
                bonus.kill()
                if bonus not in self.active_bonuses:
                    bonus.effect(self)
                    self.active_bonuses.add(bonus)

    def aliens_position_check(self):
        for alien in self.aliens:
            if alien.rect.right >= self.screen_width:
                self.move_aliens_down(5)
                self.aliens_direction = -1
                break
            if alien.rect.left <= 0:
                self.move_aliens_down(5)
                self.aliens_direction = 1
                break
            if alien.rect.bottom >= self.screen_height:
                self.is_lost = True
                break

    def move_aliens_down(self, distance):
        for alien in self.aliens:
            alien.rect.y += distance

    def aliens_shoot(self):
        if self.aliens.sprites():
            alien = random.choice(self.aliens.sprites())
            laser_sprite = Bullet(alien.rect.centerx, alien.rect.bottom, 0, 5,
                                  True, self.screen_height)
            self.alien_bullets.add(laser_sprite)
            self.laser_sound.play()

    alien_types = {"B": "blue", "G": "green", "P": "purple",
                   "R": "red", "S": "skin", "Y": "yellow"}
    bunker_types = {"B": False, "T": True}

    def create_level(self, level):
        with open(f"Levels\\{level}.txt") as f:
            is_bunkers = False
            lines = f.read().splitlines()
            for row_index, row in enumerate(lines):
                if row == "":
                    is_bunkers = True
                    continue
                for col_index, col in enumerate(row):
                    if col != "*":
                        if is_bunkers:
                            self.create_bunker(self.screen_width / 15,
                                               self.screen_height - 250,
                                               self.bunker_x_positions[
                                                   col_index],
                                               GameLevel.bunker_types[col])
                        else:
                            self.create_alien(col_index, row_index,
                                              GameLevel.alien_types[col])

    def create_alien(self, col_index, row_index, alien_type,
                     x_distance=80, y_distance=48, x_offset=70, y_offset=100):
        x = col_index * x_distance + x_offset
        y = row_index * y_distance + y_offset
        self.aliens.add(Alien(x, y, alien_type))

    def create_bunker(self, x_start, y_start, offset_x, is_translucent):
        for row_index, row in enumerate(self.bunker_shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = Bunker_Block(self.block_size, x, y, is_translucent)
                    self.blocks.add(block)

    def extra_alien_timer(self):
        self.mystery_spawn_time -= 1
        if self.mystery_spawn_time <= 0:
            self.mystery.add(MysteryShip(random.choice([-1, 1]),
                                         self.screen_width))
            self.mystery_spawn_time = random.randint(500, 1000)

    def bonuses_timer(self, x, y):
        self.bonuses_spawn_kills -= 1
        if self.bonuses_spawn_kills <= 0:
            self.bonuses.add(Bonus(x, y, random.choice(
                ["freeze", "fast", "life", "bullets"]), self.screen_height))
            self.bonuses_spawn_kills = random.randint(5, 10)

    def active_bonuses_timer(self):
        for bonus in self.active_bonuses:
            bonus.timer(self)

    def display_lives(self):
        for live in range(self.lives):
            x = self.live_x_start_pos + (
                    live * (self.live_img.get_size()[0] + 10))
            self.screen.blit(self.live_img, (x, 8))

    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', True, 'white')
        score_rect = score_surf.get_rect(topleft=(20, 10))
        self.screen.blit(score_surf, score_rect)

    def check_win(self):
        if not self.aliens.sprites():
            self.is_win = True

    def check_lost(self):
        if self.lives < 0:
            self.is_lost = True

    def is_game_continue(self):
        def disable_menu():
            menu.disable()
            self.run()

        mytheme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                    widget_font_size=48,
                                    title_font_size=72)
        mytheme.widget_font = pygame_menu.font.FONT_8BIT
        mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        menu = pygame_menu.Menu("", self.screen_width,

                                self.screen_height,
                                theme=mytheme)
        menu.add.button('Continue', disable_menu)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        menu.mainloop(self.screen)


def get_score_table(current_score):
    score_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    score_record = f"{current_score} {score_time}"
    try:
        with open('score_table.dat', 'rb') as file:
            score_table = pickle.load(file)
    except FileNotFoundError:
        score_table = [score_record]
    for i in range(len(score_table)):
        score = int(score_table[i].split()[0])
        if current_score > score:
            score_table.insert(i, score_record)
            break
    if len(score_table) > 5:
        score_table.pop()
    with open('score_table.dat', 'wb') as file:
        pickle.dump(score_table, file)
    return score_table


def display_score_table(score_table, menu):
    allign = -360
    for record in score_table:
        menu.add.label(
            record,
            align=pygame_menu.locals.ALIGN_LEFT, font_size=38,
            font_name=pygame_menu.font.FONT_NEVIS).translate(0, allign)
        allign += 10


class Game:
    def __init__(self):
        self.screen_size = 1350, 1080
        self.level_num = 1
        self.score = 0
        self.surface = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('Space Invaders | By Denis and Isa')
        music = pygame.mixer.Sound("audio/level_music.wav")
        music.set_volume(1)
        music.play(loops=-1)
        self.mytheme = pygame_menu.Theme(background_color=(0, 0, 0, 0),
                                         widget_font_size=48,
                                         title_font_size=72)
        self.mytheme.widget_font = pygame_menu.font.FONT_8BIT
        self.mytheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
        menu = pygame_menu.Menu("Space Invaders", self.screen_size[0],
                                self.screen_size[1],
                                theme=self.mytheme)
        menu.add.button('Play', self.run)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        menu.mainloop(self.surface)

    def run(self):
        level = GameLevel(self.level_num)
        level.run()
        self.score += level.score
        if level.is_lost:
            self.is_game_restart(self.score)
        if level.is_win:
            self.level_num += 1
            if self.level_num > 10:
                self.level_num = 1
            self.is_game_continue()

    def is_game_restart(self, current_score):
        menu = pygame_menu.Menu("", self.screen_size[0],
                                self.screen_size[1],
                                theme=self.mytheme)
        menu.add.label("Scores Table:", align=pygame_menu.locals.ALIGN_LEFT,
                       font_size=42,
                       font_name=pygame_menu.font.FONT_NEVIS).translate(0,
                                                                        -380)
        score_table = get_score_table(current_score)
        self.score = 0
        display_score_table(score_table, menu)
        menu.add.button('Restart', self.run)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        menu.mainloop(self.surface)

    def is_game_continue(self):
        menu = pygame_menu.Menu("", self.screen_size[0],
                                self.screen_size[1],
                                theme=self.mytheme)
        menu.add.button('Next Level', self.run)
        menu.add.button('Exit', pygame_menu.events.EXIT)
        menu.mainloop(self.surface)


def main():
    pygame.init()
    Game().run()


if __name__ == '__main__':
    main()
