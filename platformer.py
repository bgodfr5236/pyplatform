#  Escape the School

import pygame
import random
import intersects
import calendar
import time
import math
from graphic_handler import *

pygame.init()

# Window settings
WIDTH = 1000
HEIGHT = 800
TITLE = "Escape the School"
FPS = 60

# Make the window
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (220, 220, 220)
DARKER_GREY = (150, 150, 150)
RED = (175, 0, 0)
PASTEL_BLUE = (26, 184, 237)

# Fonts
FONT_SM = pygame.font.Font(None, 30)
FONT_BG = pygame.font.Font(None, 80)

# Stages
START = 0
PLAYING = 1
END = 2
PAUSED = 3

# Other Documents
pause_text = FONT_BG.render("PRESS SPACE TO RESUME", True, WHITE)

# Character Images
student_img = graphic_loader("img/student.png")
teacher_img = graphic_loader("img/teacher.png")
admin_img = graphic_loader("img/admin.png")
bad_student_img = graphic_loader("img/bad_student.png")

#Background Images
front_img = graphic_loader("img/schoolfront.png")
commons_img = graphic_loader("img/commons.png")

# Item Images
laptop_img = graphic_loader("img/laptop.png")
phone_img = graphic_loader("img/phone.png")
card_img = graphic_loader("img/playing_card.png")
staffbadge_img = graphic_loader("img/staff_badge.png")
exit_img = graphic_loader("img/exit.png")
iss_img = graphic_loader("img/iss.png")
book_imgs = [graphic_loader("img/book1.png"),
             graphic_loader("img/book2.png"),
             graphic_loader("img/book3.png"),
             graphic_loader("img/book4.png"),
             graphic_loader("img/book5.png")]
# Physics
H_SPEED = 4
JUMP_POWER = 8
GRAVITY = 0.165
TERMINAL_VELOCITY = 10
SHOW_GRID = False
TIME_MOD = 0


def draw_grid():
    for i in range(25, HEIGHT, 25):
        pygame.draw.line(screen, BLACK, [0, i], [WIDTH, i])

    for i in range(25, WIDTH, 25):
        pygame.draw.line(screen, BLACK, [i, 0], [i, HEIGHT])


def fix_inventory(inventory):
    x_val = 120
    y_val = 0

    for item in inventory:

        item.can_collect = False
        item.is_visible = True

        item.x = x_val
        item.y = y_val

        item.img = graphic_absolute_resize(item.img, None, 40)

        x_val += item.img.get_width() + 15

def get_current_time():
    return calendar.timegm(time.gmtime()) - TIME_MOD


class Student:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        
        self.vx = 0
        self.vy = 0
        self.speed = H_SPEED
        self.temp_speed_changes = []
        self.has_detention = False

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def jump(self, platforms, homework):

        can_jump = False

        self.y += 1

        student_rect = self.get_rect()

        #if intersects.rect_rect(student_rect, ground.get_rect()):
            #can_jump = True

        for p in platforms:
            platform_rect = p.get_rect()

            if intersects.rect_rect(student_rect, platform_rect):
                can_jump = True

        if self.y + self.h >= HEIGHT:
            can_jump = True

        if can_jump:
            self.vy = -JUMP_POWER

            if len(homework) > 2:
                self.change_speed_temp(get_current_time() + 1, -2)
            # if self.vx < 0:
            #     self.x -= 15
            # elif self.vx > 0:
            #     self.x += 15

        self.y -= 1

    def move(self, vx):
        self.vx = vx

    def stop(self):
        self.vx = 0

    def apply_gravity(self):
         self.vy += GRAVITY
         self.vy = min(self.vy, TERMINAL_VELOCITY)

    def change_speed_temp(self, expiry_time, amount):
        self.temp_speed_changes.append({
            "expiryTime" : expiry_time,
            "changeAmount" : amount
        })

    def process_platforms(self, platforms):
        self.x += self.vx

        student_rect = self.get_rect()
        
        for p in platforms:
            platform_rect = p.get_rect()

            if intersects.rect_rect(student_rect, platform_rect):
                if self.vx > 0:
                    self.x = p.x - self.w
                elif self.vx < 0:
                    self.x = p.x + p.w
                    self.y += self.vy

        self.y += self.vy
        
        student_rect = self.get_rect()
        
        for p in platforms:
            platform_rect = p.get_rect()
            
            if intersects.rect_rect(student_rect, platform_rect):
                if self.vy > 0:
                    self.y = p.y - self.h
                if self.vy < 0:
                    self.y = p.y + p.h
                    self.vy = 0

    def check_screen_edges(self):
        if self.x < 0:
            self.x = 0
        elif self.x + self.w > WIDTH:
            self.x = WIDTH - self.w

        if self.y < 0:
            self.y = 0
            self.vy = 0
        elif self.y + self.h > HEIGHT:
            self.y = HEIGHT - self.h
    
    def check_ground(self, ground):
        if self.y + self.h > ground.y:
            self.y = ground.y - self.h
            self.vy = 0
                 
    def process_coins(self, coins):
        global score
        
        student_rect = self.get_rect()
        coins_to_remove = []
        
        for c in coins:
            coin_rect = c.get_rect()

            if intersects.rect_rect(student_rect, coin_rect):
                coins_to_remove.append(c)
                score += 1
                print(score)

        for c in coins_to_remove:
            coins.remove(c)

    def process_teachers(self, teachers, homework):
        student_rect = self.get_rect()

        is_touching = False
            
        for t in teachers:

            if t.is_touching(student_rect):
                print("bonk!")
                # is_touching = True
                # self.change_speed_temp(get_current_time() + 5, H_SPEED/2)
                if len(homework) < 15:
                    homework.append(Book())

        #print(self.speed)

    def process_admins(self, admins, detention_rect):
        global student, can_jump
        student_rect = self.get_rect()
            
        for a in admins:

            if a.is_touching(student_rect):
                self.has_detention = get_current_time() + 10
                self.tp_to_detention(detention_rect)

    def tp_to_detention(self, detention_rect):
        detention_rect = detention_rect.get_rect()

        self.y = detention_rect[2]
        self.x = random.randint(detention_rect[1], detention_rect[3])
        self.vy = 0

    def process_bad_student(self, bad_student):
        student_rect = self.get_rect()
            
        for b in bad_student:
            bad_student_rect = b.get_rect()

            if b.is_touching(student_rect):
                self.change_speed_temp(get_current_time() + 3, H_SPEED)
                print("ugh")

    def process_belongings(self, belongings, inventory):

        student_rect = self.get_rect()

        for b in belongings:
            if b.is_collectible:
                item_rect = b.get_rect()

                if intersects.rect_rect(student_rect, item_rect):
                    belongings.remove(b)
                    inventory.append(b)
                    fix_inventory(inventory)

                    if len(belongings) > 0:
                        belongings[0].activate()

    def process_speed_changes(self, homework_books):
        self.speed = H_SPEED
        current_time = get_current_time()

        self.speed -= math.ceil(len(homework_books)/2)
        self.speed = 1 if self.speed < 1 else self.speed

        for p in self.temp_speed_changes:
            if not (p['expiryTime'] < current_time):
                self.speed -= p['changeAmount']
            else:
                self.temp_speed_changes.remove(p)

        self.speed = 0 if self.speed < 0 else self.speed

        # self.speed = 1 if self.speed < 1 else self.speed

    def process_detention(self, detention_rect):
        if self.has_detention:
            if get_current_time() < self.has_detention:
                student_rect = self.get_rect()
                detention_rect = detention_rect.get_rect()

                if student_rect[1] < detention_rect[1]:
                    self.y = detention_rect[1]
                    self.vy = 0

                print("detention")
            else:
                self.has_detention = False
                print("detention dismissed")

    def check_exit(self, exit_rect, belongings):
        global stage
        exit_rect = exit_rect.get_rect()

        if (intersects.rect_absorbs_rect(self.get_rect(), exit_rect) and
            len(belongings) == 0):
            stage = END
            print("exit!")

    def update(self, platforms, teachers, admin, bad_students, belongings, inventory,
               detention_rect, exit_rect, homework_books):
        self.process_speed_changes(homework_books)
        self.apply_gravity()
        self.process_detention(detention_rect)
        self.process_platforms(platforms)
        self.check_screen_edges()
        self.check_exit(exit_rect, belongings)
        #self.check_ground()
        #self.process_coins(coins)
        self.process_teachers(teachers, homework_books)
        self.process_admins(admin, detention_rect)
        self.process_bad_student(bad_students)
        self.process_belongings(belongings, inventory)
        
    def draw(self):
        screen.blit(self.img, [self.x, self.y])


class OtherPeople:

    def __init__(self, x, y, img, vx=1, platform_bound=True):
        self.x = x
        self.y = y
        self.img = img
        self.w = self.img.get_width()
        self.h = self.img.get_height()
        self.platform_bound = platform_bound

        self.is_untouchable = False
        self.last_touch = 0

        self.vx = vx
        self.vy = 0

    def process_touchability(self):
        if self.last_touch + 5 == get_current_time():
            self.is_untouchable = False

    def is_touching(self, other_rect, dont_set_flag=False, ignore_untouchable=False):
        if (not self.is_untouchable) or ignore_untouchable:
            if intersects.rect_rect(self.get_rect(), other_rect):
                if not dont_set_flag:
                    self.is_untouchable = True
                    self.last_touch = get_current_time()

                return True

        return False

    def move_and_process_platforms(self, platforms):
        self.x += self.vx

        person_rect = self.get_rect()

        for p in platforms:
            platform_rect = p.get_rect()

            if intersects.rect_rect(person_rect, platform_rect):
                if self.vx > 0:
                    self.x = p.x - self.w
                    self.vx *= -1
                elif self.vx < 0:
                    self.x = p.x + p.w
                    self.vx *= -1

            if self.platform_bound:
                if (person_rect[0] == platform_rect[0] and
                        platform_rect[1] == person_rect[1] + person_rect[3]
                        and self.vx == -1):
                    self.vx *= -1
                elif (person_rect[0] + person_rect[2] == platform_rect[0] + platform_rect[2] and
                      person_rect[1] + person_rect[3] == platform_rect[1] and
                      self.vx == 1):
                    self.vx *= -1


        self.y += self.vy

        person_rect = self.get_rect()

        for p in platforms:
            platform_rect = p.get_rect()

            if intersects.rect_rect(person_rect, platform_rect):
                if self.vy > 0:
                    self.y = p.y - self.h
                if self.vy < 0:
                    self.y = p.y + p.h
                self.vy = 0

    def is_touching(self, other_rect, dont_set_flag=False, ignore_untouchable=False):
        if (not self.is_untouchable) or ignore_untouchable:
            if intersects.rect_rect(self.get_rect(), other_rect):
                if not dont_set_flag:
                    self.is_untouchable = True
                    self.last_touch = get_current_time()

                return True

        return False

    def check_screen_edges(self):
        if self.x < 0:
            self.x = 0
        elif self.x + self.w > WIDTH:
            self.x = WIDTH - self.w

        if self.y < 0:
            self.y = 0
            self.vy = 0
        elif self.y + self.h > HEIGHT:
            self.y = HEIGHT - self.h

    def update(self, platforms):
        self.process_touchability()
        self.move_and_process_platforms(platforms)
        self.check_screen_edges()

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def draw(self):
        screen.blit(self.img, [self.x, self.y])


class Platform:

    def __init__(self, x, y, w, h, color=PASTEL_BLUE):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def draw(self):
        pygame.draw.rect(screen, self.color, [self.x, self.y, self.w, self.h])


class Belongings:

    def __init__(self, x, y, img, is_visible=False, is_collectible=False):
        self.x = x
        self.y = y
        self.img = img

        self.is_visible = is_visible
        self.is_collectible = is_collectible

        self.w = self.img.get_width()
        self.h = self.img.get_height()

        self.value = 1

    def set_visibility(self, status):
        self.is_visible = status

    def set_collectibility(self, status):
        self.is_collectible = status

    def activate(self):
        self.is_collectible = True
        self.is_visible = True

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def draw(self):
        screen.blit(self.img, [self.x, self.y])


class BackgroundObjects:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img

        self.w = self.img.get_width()
        self.h = self.img.get_height()

        self.value = 1

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def draw(self):
        screen.blit(self.img, [self.x, self.y])


class areaRect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]


class Book:

    def __init__(self):
        global homework_books

        self.x = (120 + (len(homework_books) * 42))
        self.y = 50
        self.img = random.choice(book_imgs)

        self.w = self.img.get_width()
        self.h = self.img.get_height()

        self.value = 1

    def get_rect(self):
        return [self.x, self.y, self.w, self.h]

    def draw(self):
        screen.blit(self.img, [self.x, self.y])


def setup():
    global student, platforms, background_objects, \
        belongings, teachers, admins, bad_students, \
        done, score, stage, inventory, exit_rect, \
        detention_rect, iss_signs, homework_books

    student = Student(0, 0, student_img)
    platforms = [Platform(0, 225, 150, 10),
                 Platform(0, 475, 150, 10),
                 Platform(175, 325, 150, 10),
                 Platform(275, 550, 150, 10),
                 Platform(575, 550, 150, 10),
                 Platform(450, 375, 150, 10),
                 Platform(0, 700, 150, 10),
                 Platform(850, 700, 150, 10),
                 Platform(425, 700, 150, 10),
                 Platform(800, 100, 200, 10),
                 Platform(650, 275, 150, 10),
                 Platform(300, 175, 150, 10),
                 Platform(775, 450, 150, 10),
                 Platform(550, 150, 150, 10)]
    background_objects = [BackgroundObjects(950, 0, exit_img)]
    iss_signs = [BackgroundObjects(475, 730, iss_img),
                          BackgroundObjects(30, 730, iss_img),
                          BackgroundObjects(920, 730, iss_img),
                          BackgroundObjects(725, 730, iss_img),
                          BackgroundObjects(225, 730, iss_img)]
    belongings = [Belongings(500, 325, laptop_img),
                  Belongings(475, 650, phone_img),
                  Belongings(25, 440, staffbadge_img),
                  Belongings(25, 185, card_img)]
    teachers = [OtherPeople(0, 411, teacher_img),
                OtherPeople(450, 636, teacher_img),
                OtherPeople(805, 386, teacher_img),
                OtherPeople(60, 161, teacher_img)]
    admins = [OtherPeople(295, 486, admin_img),
              OtherPeople(950, 636, admin_img),
              OtherPeople(580, 86, admin_img)]
    bad_students = [OtherPeople(500, 311, bad_student_img),
                    OtherPeople(300, 111, bad_student_img)]
    homework_books = []
    inventory = []
    detention_rect = areaRect(0, 700, WIDTH, HEIGHT)
    exit_rect = areaRect(975, 0, 25, 100)

    belongings[0].activate()

    # Game stats
    score = 0

    # game loop
    done = False
    stage = START


def load_config():

    global opening_lines

    opening_lines = []

    # Load opening text from disk.
    with open('Open.txt', 'r') as f:
        lines = f.read().splitlines()

    for l in lines:
        opening_lines.append(FONT_SM.render(l, True, WHITE))

# Initialize variables
inventory = []
setup()
load_config()

while not done:
    # event handling

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.KEYDOWN:

            if stage == START:

                if event.key == pygame.K_SPACE:
                    stage = PLAYING
                    
            if stage == PLAYING:
                if (event.key == pygame.K_SPACE or
                        event.key == pygame.K_UP or
                        event.key == pygame.K_w):
                     student.jump(platforms, homework_books)
                elif event.key == pygame.K_p:
                    stage = PAUSED
                    PAUSE_TIME = get_current_time()
                    print(stage)

            if stage == END:
                if event.key ==pygame.K_SPACE:
                    stage = START
                    setup()

            if stage == PAUSED:
                if event.key == pygame.K_SPACE:
                    RESUME_TIME = get_current_time()
                    TIME_MOD += RESUME_TIME - PAUSE_TIME
                    stage = PLAYING
                    print(stage)

    if stage == PLAYING:
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
             student.move(student.speed)
        elif pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
             student.move(-student.speed)
        else:
            student.stop()

    # game logic
    # player.update(ground, platforms)
    if stage == PLAYING:
        student.update(platforms, teachers, admins, bad_students, belongings,
                       inventory, detention_rect, exit_rect, homework_books)

        for t in teachers:
            t.update(platforms)

        for a in admins:
            a.update(platforms)

        for b in bad_students:
            b.update(platforms)    

    # Messages
    START_TEXT = FONT_SM.render("Press space to start.", True, WHITE)
    SCORE = FONT_SM.render("Backpack:", True, WHITE)
    END_TEXT = FONT_SM.render("You Escaped! Now go home and study!(Or press Space to restart)", True, WHITE)
    HOMEWORK = FONT_SM.render("Homework:", True, WHITE)

    # Draw game objects on-screen.
    if stage == START:
        screen.blit(front_img, [0, 0])

        x_val = 0
        y_val = 50

        for line in opening_lines:
            screen.blit(line, [screen.get_rect().centerx - int(line.get_width() / 2), y_val])
            y_val += 25

    elif stage == PLAYING or stage == PAUSED:
        screen.blit(commons_img, [0, 0])

        if student.has_detention:
            for i in iss_signs:
                i.draw()

        for b in background_objects:
            b.draw()

        for p in platforms:
            p.draw()

        for b in belongings:
            if b.is_visible:
                b.draw()

        for h in homework_books:
            h.draw()

        for a in admins:
            a.draw()

        for t in teachers:
            t.draw()

        for b in bad_students:
            b.draw()

        for i in inventory:
            i.draw()

        if SHOW_GRID:
            draw_grid()

        student.draw()

        screen.blit(SCORE, [0, 0])
        screen.blit(HOMEWORK, [0, 50])

    if stage == PAUSED:
        screen.blit(pause_text, [(WIDTH/2)-(pause_text.get_width()/2), (HEIGHT/2)-(pause_text.get_height()/2)])

    if stage == END:
        screen.blit(front_img, [0, 0])
        screen.blit(END_TEXT, [(WIDTH/2)-(END_TEXT.get_width()/2), (HEIGHT/2)-(END_TEXT.get_height()/2)])
    # update screen
    pygame.display.update()
    clock.tick(FPS)

# close window on quit
pygame.quit()

