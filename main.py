import pygame
import random

# initialize pygame
pygame.init()

# screen size and variables
WIDTH, HEIGHT = 640, 480
RESOLUTION = (WIDTH, HEIGHT)
FPS = 60
PLAYER_SPEED = 5
OBJECTIVE_SPEED = 5
OBJECTIVE_SPAWN_RATE = 1000 # in milliseconds
PLAYER_LIVES = 3
BOOST_DURATION = 5000 # in milliseconds
boost_start_time = 0
boost_active = False

# set up the display
screen = pygame.display.set_mode((RESOLUTION))
pygame.display.set_caption("Newtons Cradle")

# colors and sprites
BACKGROUND = (96, 57, 164)
OBJECTIVE = pygame.image.load('images/gold_coin.png')
BOMB = pygame.image.load('images/bomb.png')
LIGHTNING = pygame.image.load('images/lightning_boost.png')
PLAYER_HEART = pygame.image.load('images/heart.png')
PLAYABLE_CHARACTER_LEFT = pygame.image.load('images/goblin_left.png')
PLAYABLE_CHARACTER_RIGHT = pygame.image.load('images/goblin_right.png')

# resize and get the size of playabale_character sprite
goblin_new_width = PLAYABLE_CHARACTER_LEFT.get_width() * 2
goblin_new_height = PLAYABLE_CHARACTER_LEFT.get_height() * 2
PLAYABLE_CHARACTER_LEFT = pygame.transform.scale(PLAYABLE_CHARACTER_LEFT, (goblin_new_width, goblin_new_height))
PLAYABLE_CHARACTER_RIGHT = pygame.transform.scale(PLAYABLE_CHARACTER_RIGHT, (goblin_new_width, goblin_new_height))

# initialize character position
current_sprite = PLAYABLE_CHARACTER_LEFT
goblin_x = (WIDTH - goblin_new_width) // 2
goblin_y = (HEIGHT - goblin_new_height)

# resize and get the size of objectives sprite + list for holding apples
item_width, item_height = OBJECTIVE.get_width(), OBJECTIVE.get_height()

# function to create random items at random x positions to fall from top of screen
def create_falling_item():
    
    chance = random.randint(1, 100)
    
    # 10% chance for bomb
    if chance <= 10:
        item_type = 'bomb'
    # 5% chance for lightning
    elif chance <= 15:
        item_type = 'lightning'
    # 85% chance for apple
    else:
        item_type = 'gold_coin'
    
    x = random.randint(0, WIDTH - item_width)
    y = -item_height
    return [x, y, item_type]

# initialize item and last spawn time
item = None
last_spawn_time = 0
player_lives = PLAYER_LIVES

# initialize the font for displaying time and score
font = pygame.font.Font('Press_Start_2P/PressStart2P-Regular.ttf', 15)
start_time = pygame.time.get_ticks()  # record the start time
score = 0

# main game loop
game_running = True
clock = pygame.time.Clock()

while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False

    # get the keys pressed
    keys = pygame.key.get_pressed()

    # move the character 
    if keys[pygame.K_LEFT]:
        goblin_x -= PLAYER_SPEED
        current_sprite = PLAYABLE_CHARACTER_LEFT
    if keys[pygame.K_RIGHT]:
        goblin_x += PLAYER_SPEED
        current_sprite = PLAYABLE_CHARACTER_RIGHT

    # make sure character cant move out of pygame screen
    if goblin_x <= 0:
        goblin_x = 0
        current_sprite = PLAYABLE_CHARACTER_RIGHT

    if goblin_x >= WIDTH - goblin_new_width:
        goblin_x = WIDTH - goblin_new_width
        current_sprite = PLAYABLE_CHARACTER_LEFT

    # create goblin rect for collision detection
    goblin_rect = pygame.Rect(goblin_x, goblin_y, goblin_new_width, goblin_new_height)

    # get current time to spawn an item every 1 second
    current_time = pygame.time.get_ticks()

    # calculate elapsed time
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # convert to seconds

    # check if speed boost is active
    if boost_active:
        PLAYER_SPEED += 10 # increase player speed by 10
        
        # check if boost duration has passed
        if current_time - boost_start_time >= BOOST_DURATION:
            boost_active = False  # deactivate boost
    else:
        PLAYER_SPEED = 5 + (elapsed_time // 10)

    # adjust item speed based on elapsed time
    OBJECTIVE_SPEED = 5 + (elapsed_time // 10)  # increase speed every 5 seconds
    PLAYER_SPEED = 5 + (elapsed_time // 10)  # increase player speed every 10 seconds

    # adjust item spawn time based on elapsed time
    APPLES_PER_SECOND = 1 + (elapsed_time // 10)  # increase the number of apples spawned every 10 seconds
    OBJECTIVE_SPAWN_RATE = int(1000 / APPLES_PER_SECOND)  # convert to milliseconds

    # spawn an item every OBJECTIVE_SPAWN_RATE milliseconds
    if item is None and current_time - last_spawn_time > OBJECTIVE_SPAWN_RATE:
        item = create_falling_item()
        last_spawn_time = current_time

    # update item position if exists
    if item:
        item[1] += OBJECTIVE_SPEED

        # create item rect for collision detection
        item_rect = pygame.Rect(item[0], item[1], item_width, item_height)

        # check if item has hit the ground or goblin sprite
        if goblin_rect.colliderect(item_rect):
            if item[2] == 'gold_coin':
                score += 1 # increase score
            elif item[2] == 'bomb':
                player_lives -= 1
            elif item[2] == 'lightning':
                boost_active = True
                boost_start_time = pygame.time.get_ticks()

            item = None

        elif item[1] >= HEIGHT:
            if item[2] == 'gold_coin':
                player_lives -= 1
            item = None

    # check if player has lost all lives
    if player_lives == 0:
        game_running = False
        print(f"Game Over! Your score is {score}")

    # update screen and draw character sprite and set timer
    screen.fill(BACKGROUND)
    screen.blit(current_sprite, (goblin_x, goblin_y))

    # render the timer and score text
    timer_text = font.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))

    # draw the timer and score at the top
    screen.blit(timer_text, ((WIDTH - timer_text.get_width()) // 2, 10))  # center at the top of the screen
    screen.blit(score_text, (10, 10))  # top left position

    # draw the apples
    if item:
        if item[2] == 'gold_coin':
            screen.blit(OBJECTIVE, (item[0], item[1]))
        elif item[2] == 'bomb':
            screen.blit(BOMB, (item[0], item[1]))
        elif item[2] == 'lightning':
            screen.blit(LIGHTNING, (item[0], item[1]))

    # draw players hearts
    for i in range(player_lives):
        screen.blit(PLAYER_HEART, (WIDTH - 30 - i * 30, 10)) # top right position

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()