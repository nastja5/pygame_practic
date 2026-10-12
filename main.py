import pygame
import pygame_widgets
from pygame_widgets.button import Button
pygame.init()

def funcStart():
     global level
     level = 1



screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Press fish")
background_1 = pygame.image.load("back_1.png").convert()
background_2 = pygame.image.load("back_2.png").convert()

level = 0

btnStart = Button(screen, 300,500,270,80,text ="Start", onClick=funcStart )
btnScore = Button(screen, 300,300,270,80,text ="Score" )
btnExit = Button(screen, 300,400,270,80,text ="Exit", onClick= quit)

show_buttons = True


running = True
while running:
    pygame.display.update()
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and show_button:
                
                if button_rect.collidepoint(event.pos):
                    show_button = False

            
    if level == 0:
        screen.blit(background_1, (0, 0))
    elif level == 1:
        screen.blit(background_2, (0, 0))

    #screen.blit(background_1, (0, 0))
    pygame_widgets.update(event)
    pygame.display.flip()


pygame.quit()