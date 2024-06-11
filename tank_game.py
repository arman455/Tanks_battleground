import pygame
import random
pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption("Tanks Fight")

pygame.mixer.music.load("sounds//game.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)

shoot_sound = pygame.mixer.Sound("sounds//enemy_shoot.mp3")
enemy_boom_sound = pygame.mixer.Sound("sounds//enemy_boom.mp3")
heal_drop_sound = pygame.mixer.Sound("sounds//heal_drop.mp3")
heal_get_sound = pygame.mixer.Sound("sounds//heal_get.mp3")
boss_sound = pygame.mixer.Sound("sounds//boss.ogg")
tnt_boom_sound = pygame.mixer.Sound("sounds//tnt_boom.mp3")
break_sound = pygame.mixer.Sound("sounds//break.ogg")

sound_list = [shoot_sound, enemy_boom_sound, heal_drop_sound, heal_get_sound, boss_sound, tnt_boom_sound, break_sound]
for sound in sound_list:
    sound.set_volume(0.1)

class Options(): #класс для настроек (в том числе и окно)
    def __init__(self, width, height, color, image):
        self.width = width
        self.height = height
        self.color = color
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.window = pygame.display.set_mode((width, height))        
        self.all_enemies = []
        self.all_mines = []
        self.all_med_kits = []
        self.enemy_bullets = []
        self.level = []  
        self.level_x = 0
        self.level_y = 0
        self.animation_timer = 30
        self.flag_health = 0
        self.kill_counter = 0
        self.font = pygame.font.SysFont('Times New Roman', 50)
        self.enemy_spawn_timer = 600 * 10
        self.boss_go = False
        self.win = False
        self.lose = False
        
    def change_color(self):
        self.window.fill(self.color)        

    def change_image(self):
        self.window.blit(self.image, (0,0))
        self.animation_timer -= 1
        for element in self.level:
            if element.wall_type in [1, 6]:   
                pygame.Surface.blit(options.window, element.animation_textures[options.animation_timer//10], element.hitbox)     
        if self.animation_timer < 1:
            self.animation_timer = 30

    def draw_health(self, tank_health, boss_health):
        tank_text = self.font.render(str(tank_health), True, (0, 255, 0))
        flag_text = self.font.render(str(self.flag_health), True, (255, 255, 0))
        self.window.blit(tank_text, (0,0))
        self.window.blit(flag_text, (0,600))
        if self.kill_counter >= 10:
            boss_text = self.font.render(str(boss_health), True, (255, 0, 0))
            self.window.blit(boss_text, (1175,0))      
        
class Sprite(): #класс для всех объектов в игре
    def __init__(self, x, y, width, height, color, image):
        self.hitbox = pygame.Rect(x, y, width, height)
        self.color = color
        self.img = pygame.image.load(image)         
        self.image_r = pygame.transform.scale(self.img, (width, height))
        self.image_l = pygame.transform.rotate(self.image_r, 180)
        self.image_t = pygame.transform.rotate(self.image_r, 90)
        self.image_b = pygame.transform.rotate(self.image_r, 270)
        self.image = self.image_r
        
    def change_color(self, window):
        pygame.draw.rect(window, self.color, self.hitbox)

    def change_image(self, window):
        pygame.Surface.blit(window, self.image, self.hitbox)

class Bullet(Sprite):
    def __init__(self, x, y, width, height, color, image, speed, distance, damage, direction):
        super().__init__(x, y, width, height, color, image)
        self.speed = speed
        self.distance = distance
        self.damage = damage
        self.direction = direction
    
    def fly(self):
        if self.direction == "R":
            self.hitbox.x += self.speed
        if self.direction == "L":
            self.hitbox.x -= self.speed
        if self.direction == "U":
            self.hitbox.y -= self.speed
        if self.direction == "D":
            self.hitbox.y += self.speed

class Wall(Sprite):
    def __init__(self, x, y, width, height, color, image, wall_type, health, animation_textures = None):
        super().__init__(x, y, width, height, color, image)
        self.wall_type = wall_type
        self.health = health
        if animation_textures != None:
            self.animation_textures = [pygame.image.load(img) for img in animation_textures]
            self.animation_textures = [pygame.transform.scale(img, (width, height)) for img in self.animation_textures]              

class Enemy(Sprite):
    def __init__(self, x, y, width, height, color, image, health, start_direction):
        super().__init__(x, y, width, height, color, image)
        self.health = health 
        self.health_line_end = self.hitbox.x + self.hitbox.width
        self.health_line_length = self.hitbox.width
        self.speed = 2
        self.start_direction = start_direction
        self.move_counter = 0     
        self.direction = start_direction
        self.shoot_timer = 60
       
    def move(self, window,block):	
        self.health_line_end = self.hitbox.x + self.health_line_length
        pygame.draw.line(window, (255, 0, 0), (self.hitbox.x, self.hitbox.y - 7), (self.health_line_end, self.hitbox.y - 7), 2)
        
        self.move_counter += 1 

        if self.start_direction == "D":
            if self.move_counter < 50:
                self.hitbox.y += self.speed
                self.direction = "D"
            elif self.move_counter < 200:
                self.hitbox.x -= self.speed
                self.direction = "L"
            elif self.move_counter < 250:
                self.hitbox.y -= self.speed
                self.direction = "U"
            elif self.move_counter < 375:
                self.hitbox.x -= self.speed
                self.direction = "L"
            elif self.move_counter < 425:
                self.hitbox.y += self.speed
                self.direction = "D"
            elif self.move_counter < 575:
                self.hitbox.x -= self.speed
                self.direction = "L"
            elif self.move_counter < 600:
                self.hitbox.y -= self.speed
                self.direction = "U"
            elif self.move_counter < 675:
                self.hitbox.x -= self.speed
                self.direction = "L"
            else:
                self.speed = 0
                self.direction = "D"

        elif self.start_direction == "L":
            if self.move_counter < 150:
                self.hitbox.x -= self.speed
                self.direction = "L"
            elif self.move_counter < 200:
                self.hitbox.y += self.speed
                self.direction = "D"
            elif self.move_counter < 475:
                self.hitbox.x -= self.speed
                self.direction = "L"
            elif self.move_counter < 550:
                self.hitbox.y -= self.speed
                self.direction = "U"
            elif self.move_counter < 625:
                self.hitbox.x -= self.speed
                self.direction = "L"
            else:
                self.speed = 0
                self.direction = "U"
            
    def shoot(self):
        self.shoot_timer -= 1

        if self.shoot_timer <= 0:
            if self.direction == "U":
                bullet = Bullet(self.hitbox.centerx, self.hitbox.centery, 10, 10, (255, 0, 255), "images//fire.png", 10, 90, 20, self.direction)
            elif self.direction == "D":
                bullet = Bullet(self.hitbox.centerx, self.hitbox.centery, 10, 10, (255, 0, 255), "images//fire.png", 10, 90, 20, self.direction)
            elif self.direction == "L":
                bullet = Bullet(self.hitbox.centerx, self.hitbox.centery, 10, 10, (255, 0, 255), "images//fire.png", 10, 90, 20, self.direction)
            elif self.direction == "R":
                bullet = Bullet(self.hitbox.centerx, self.hitbox.centery, 10, 10, (255, 0, 255), "images//fire.png", 10, 90, 20, self.direction)
            options.enemy_bullets.append(bullet) 
            self.shoot_timer = 60

    def change_image(self, window):
        if self.direction == "U":
            self.image = self.image_t
        elif self.direction == "D":
            self.image = self.image_b
        elif self.direction == "L":
            self.image = self.image_l
        elif self.direction == "R":
            self.image = self.image_r

        pygame.Surface.blit(window, self.image, self.hitbox)
    
class Boss(Sprite):
    def __init__(self, x, y, width, height, color, image, health, damage, speed):
        super().__init__(x, y, width, height, color, image)
        self.hitbox_for_break = pygame.Rect(self.hitbox.centerx, self.hitbox.centery, 25, self.hitbox.height)  
        self.hitbox_with_health = pygame.Rect(self.hitbox.centerx, self.hitbox.centery, 25, self.hitbox.height//2)       
        self.health = health
        self.damage = damage
        self.speed = speed
        self.image = self.image_l
        self.stop = False
        self.break_delay = 60
        self.shoot_delay = 180

    def move(self, level):

        if self.hitbox.x > 400:
            for element in level:
                if element.wall_type == 2 or element.wall_type == 3 or element.wall_type == 4 or element.wall_type == 5:
                    if self.hitbox_for_break.colliderect(element.hitbox):
                        self.stop = True
                        self.break_delay -= 1
                        if self.break_delay < 1:
                            for element in level:
                                if self.hitbox_for_break.colliderect(element.hitbox):
                                    if element.wall_type == 3:
                                        texture = Wall(element.hitbox.x, element.hitbox.y, 50, 50, (0,0,255), "images//fire_0.png", 6, 1, ["images//fire_0.png", "images//fire_1.png", "images//fire_2.png"])
                                        level.append(texture) 
                                        level.remove(element)
                                        break                            
                                    level.remove(element)
                            self.stop = False                        
                            self.break_delay = 60
            
            if self.stop == False and self.break_delay == 60:
                self.hitbox.x -= self.speed
                self.hitbox_for_break.left = self.hitbox.left + self.hitbox_for_break.width
                self.hitbox_for_break.top = self.hitbox.top
                self.hitbox_with_health.left = self.hitbox.centerx + self.hitbox_with_health.width * 2
                self.hitbox_with_health.centery = self.hitbox.centery
        else:
            self.shoot_delay -= 1

            if self.shoot_delay <= 0:
                bullet = Bullet(self.hitbox.centerx, self.hitbox.centery, 20, 20, (255, 0, 255), "images//fir.png", 7, 90, self.damage, "L")
                options.enemy_bullets.append(bullet)
                self.shoot_delay = 180

    def change_image(self, window):
        pygame.Surface.blit(window, self.image, self.hitbox)
    
    def change_color(self, window):
        pygame.draw.rect(window, self.color, self.hitbox_for_break)

class Med_Kit(Sprite):
    def __init__(self, x, y, width, height, color, image, health):
        super().__init__(x, y, width, height, color, image)
        self.health = health
        
class Main_Tank(Sprite): #класс для главных героев
    def __init__(self, x, y, width, height, color, image, speed, health, money, direction):
        super().__init__(x, y, width, height, color, image) 
        self.speed = speed
        self.health = health
        self.money = money
        self.direction = direction
        self.bullet_list = []
        self.can_shoot = True
        self.bullet_delay = 40
        
    def move(self, keys, walls):
        if keys[pygame.K_w] == True:
            self.hitbox.y -= self.speed
            self.direction = "U"            
            self.image = self.image_t
        if keys[pygame.K_s] == True:
            self.hitbox.y += self.speed
            self.direction = "D"
            self.image = self.image_b
        if keys[pygame.K_a] == True:
            self.hitbox.x -= self.speed
            self.direction = "L"
            self.image = self.image_l
        if keys[pygame.K_d] == True:
            self.hitbox.x += self.speed
            self.direction = "R"
            self.image = self.image_r

        if self.hitbox.colliderect(boss.hitbox):
            if self.hitbox.right >= boss.hitbox.left and self.hitbox.right <= boss.hitbox.left + self.speed:
                self.hitbox.right = boss.hitbox.left
            if self.hitbox.left <= boss.hitbox.right and self.hitbox.left >= boss.hitbox.right - self.speed:
                self.hitbox.left = boss.hitbox.right
            if self.hitbox.top <= boss.hitbox.bottom and self.hitbox.top >= boss.hitbox.bottom - self.speed:
                self.hitbox.top = boss.hitbox.bottom
            if self.hitbox.bottom >= boss.hitbox.top and self.hitbox.bottom <= boss.hitbox.top + self.speed:
                self.hitbox.bottom = boss.hitbox.top
        
        for object in walls:            
            if self.hitbox.colliderect(object.hitbox):
                if self.hitbox.right >= object.hitbox.left and self.hitbox.right <= object.hitbox.left + self.speed:
                    self.hitbox.right = object.hitbox.left
                if self.hitbox.left <= object.hitbox.right and self.hitbox.left >= object.hitbox.right - self.speed:
                    self.hitbox.left = object.hitbox.right
                if self.hitbox.top <= object.hitbox.bottom and self.hitbox.top >= object.hitbox.bottom - self.speed:
                    self.hitbox.top = object.hitbox.bottom
                if self.hitbox.bottom >= object.hitbox.top and self.hitbox.bottom <= object.hitbox.top + self.speed:
                    self.hitbox.bottom = object.hitbox.top

    def shoot(self, keys):
        self.bullet_delay -= 1
        if keys[pygame.K_SPACE] == True:
            if self.can_shoot == True:                
                b_x = self.hitbox.centerx
                b_y = self.hitbox.centery
                bullet = Bullet(b_x, b_y, 5, 5, (255, 0, 0), "images//fire.png", 10, 90, 20, self.direction)
                self.bullet_list.append(bullet)
                self.can_shoot = False
        
        if self.bullet_delay == 0:
            self.can_shoot = True
            self.bullet_delay = 40

    def change_image(self, window):
        pygame.Surface.blit(window, self.image, self.hitbox)
            
options = Options(1250, 650, (123,123,123), "images//background.jpeg")
options_win = Options(1250, 650, (123,123,123), "images//win_img.png")   
options_lose = Options(1250, 650, (123,123,123), "images//lose_img.png")           
tank = Main_Tank(500, 50, 50, 50, (255,0,255), "images//tank_right.png", 5, 100, 0, "right")

#Пол - 0   Вода - 1   Кирпич - 2   Бетон - 3   Дерево - 4   TNT - 5   Огонь - 6   База - 7
level_schema = [
    [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3], 
    [3,1,1,2,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,1,1,1,3], 
    [3,1,1,2,0,0,0,2,0,0,0,2,2,4,0,0,0,0,5,0,0,5,1,1,3], 
    [3,2,2,4,0,0,2,4,2,0,0,0,0,0,0,0,4,2,4,0,0,0,5,1,3],
    [3,0,0,0,0,0,0,0,0,0,0,2,2,5,2,0,2,0,0,2,2,0,2,4,3], 
    [3,8,8,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3], 
    [3,7,8,0,0,2,0,2,0,0,2,0,2,0,0,0,0,2,0,0,0,0,0,0,3], 
    [3,8,8,4,0,0,0,0,0,2,0,0,0,2,0,0,0,5,2,2,0,0,0,0,3], 
    [3,0,0,0,0,0,0,0,0,0,0,0,0,4,2,2,2,2,2,0,0,0,0,4,3], 
    [3,2,2,4,0,4,2,2,0,0,0,0,0,0,2,0,0,0,0,0,0,0,5,1,3], 
    [3,1,1,2,0,5,0,0,0,0,0,0,5,2,2,0,2,0,0,0,0,5,1,1,3], 
    [3,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,1,1,1,3], 
    [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]
]

for row in level_schema: #пройтись по всем рядам
    for block in row: #пройтись по всем элементам КАЖДОГО РЯДА
        if block == 0:
            pass
        if block == 1:            
            texture = Wall(options.level_x, options.level_y, 50, 50, (0,0,255), "images//water_0.png", 1, 1, ["images//water_0.png", "images//water_1.png", "images//water_2.png"])
        if block == 2:
            texture = Wall(options.level_x, options.level_y, 50, 50, (255,0,0), "images//brick.png", 2, 80)
        if block == 3:
            texture = Wall(options.level_x, options.level_y, 50, 50, (0,0,0), "images//concrete.png", 3, 40)
        if block == 4:
            texture = Wall(options.level_x, options.level_y, 50, 50, (125,0,0), "images//crate.png", 4, 60)
        if block == 5:
            texture = Wall(options.level_x, options.level_y, 50, 50, (0,255,0), "images//barrel_tnt.png", 5, 20)
        if block == 7:
            texture = Wall(options.level_x, options.level_y, 50, 50, (0,255,255), "images//flag.png", 7, 100)
            options.flag_health = 100
        if block == 8:
            texture = Wall(options.level_x, options.level_y, 50, 50, (0,255,0), "images//brick_2.png", 8, 40)
        options.level.append(texture)
        options.level_x += 50 
    options.level_y += 50
    options.level_x = 0

boss = Boss(2000, 280, 150, 90, (0,0,0), "images//tank_boss.png", 200, 50, 2)

game_run = True
while game_run == True:    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_run = False
        
    if tank.health > 0 and options.flag_health > 0:

        if boss.health > 0:

            if options.kill_counter < 10:
                options.enemy_spawn_timer -= 1
                if options.enemy_spawn_timer % 600 == 0:
                    enemy_up = Enemy(1050, 150, 50, 50, (0,255,0), "images//tank_enemy.png", 60, "D")
                    enemy_down = Enemy(1050, 450, 50, 50, (0,255,0), "images//tank_enemy.png", 60, "L")
                    
                    options.all_enemies.append(enemy_up)
                    options.all_enemies.append(enemy_down)
     
            options.change_image()
            tank.change_image(options.window)
                
            keys = pygame.key.get_pressed()
            tank.change_image(options.window)
            tank.move(keys, options.level)
            tank.shoot(keys)   

            for wall in options.level:
                if wall.wall_type not in [1, 6]:
                    wall.change_image(options.window) 
                for bullet in tank.bullet_list:
                    if wall.hitbox.colliderect(bullet.hitbox):
                        if wall.wall_type in [2, 4, 5]:
                            wall.health -= bullet.damage
                            tank.bullet_list.remove(bullet)
                        if wall.wall_type == 3:
                            tank.bullet_list.remove(bullet)
                        if wall.wall_type == 7:
                            tank.bullet_list.remove(bullet)                             
                if wall.health <= 0:
                    if wall.wall_type == 4:
                        medkit_drop_chance = random.randint(1, 10)
                        if medkit_drop_chance == 1:
                            med_kit = Med_Kit(wall.hitbox.x + 5, wall.hitbox.y + 5, 40, 40, (0,0,0), "images//heal.png", 20)
                            options.all_med_kits.append(med_kit)
                            heal_drop_sound.play()
                    elif wall.wall_type == 5:
                        tnt_boom_sound.play()
                    else:
                        break_sound.play()
                    options.level.remove(wall)

            options.draw_health(tank.health, boss.health)
            boss.change_image(options.window)
            if options.kill_counter >= 10:
                boss.move(options.level)
                if options.boss_go == False:
                    boss_sound.play()
                    options.boss_go = True

            for med_kit in options.all_med_kits:
                med_kit.change_image(options.window)
                if med_kit.hitbox.colliderect(tank.hitbox):
                    if tank.health < 100:
                        tank.health += med_kit.health
                        options.all_med_kits.remove(med_kit)
                        if tank.health >= 100:
                            tank.health = 100
                        heal_get_sound.play()

            for bullet in tank.bullet_list:
                bullet.distance -= 1
                if bullet.distance > 0:            
                    bullet.fly()
                    bullet.change_color(options.window)
                    if bullet.hitbox.colliderect(boss.hitbox_with_health):
                        boss.health -= bullet.damage
                        tank.bullet_list.remove(bullet)
                        print(boss.health)
                        break
                    if bullet.hitbox.colliderect(boss.hitbox):
                        tank.bullet_list.remove(bullet)
                    for enemy in options.all_enemies:
                        if bullet.hitbox.colliderect(enemy.hitbox):
                            enemy.health_line_length = enemy.health_line_length - (((bullet.damage * 100 / enemy.health) / 100) * enemy.health_line_length)
                            enemy.health -= bullet.damage
                            tank.bullet_list.remove(bullet)
                            break            
                if bullet.distance == 0:
                    tank.bullet_list.remove(bullet)

            for enemy in options.all_enemies:
                enemy.change_image(options.window)
                enemy.move(options.window, tank)
                enemy.shoot()
                if enemy.health <= 0:
                    options.all_enemies.remove(enemy)
                    options.kill_counter += 1
                    enemy_boom_sound.play()
                    break


            for bullet in options.enemy_bullets:
                bullet.change_image(options.window)
                bullet.fly()
                for element in options.level:
                    if bullet.hitbox.colliderect(element.hitbox):
                        if element.wall_type == 7:
                            options.flag_health -= bullet.damage
                            element.health -= bullet.damage
                        if element.wall_type == 8:
                            element.health -= bullet.damage
                        options.enemy_bullets.remove(bullet)
                        break
            
            for bullet in options.enemy_bullets:
                if bullet.hitbox.colliderect(tank.hitbox):
                    tank.health -= bullet.damage
                    options.enemy_bullets.remove(bullet)

        else:
            options_win.change_image()
            if options.win == False:
                enemy_boom_sound.play()
                pygame.mixer.music.load("sounds//win.mp3")
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(0.05)
                options.win = True
    else:
        options_lose.change_image()
        if options.lose == False:
            pygame.mixer.music.load("sounds//lose.mp3")
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(0.05)
            options.lose = True


    pygame.display.flip()
    clock.tick(60) 