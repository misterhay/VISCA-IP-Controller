import pygame

#from camera import *
#c = Camera('192.168.0.100', 52381)

pygame.joystick.init()


if pygame.joystick.get_count() != 0:
    j = pygame.joystick.Joystick(0)
    j.init()
else:
	print('No joysticks found')

#joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
#pygame.joystick.get_count())
#pygame.joystick.Joystick(0)

clock = pygame.time.Clock()

tick = 0
done = False
while done == False:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
			continue

	print(j.get_axis(1)) # analog value
	print(j.get_axis(0))
	
	clock.tick()
pygame.quit ()