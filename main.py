import pygame
pygame.init()

screen = pygame.display.set_mode((1000, 600))

background = pygame.image.load("back_1.png").convert()
# При необходимости подгоняем размер под экран:
background = pygame.transform.scale(background, (1000, 600))

pygame.display.set_caption("Press fish")

running = True
while running:
    screen.fill("#88C2DB")
    pygame.display.update()
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    screen.blit(background, (0, 0))
    pygame.display.flip()


pygame.quit()