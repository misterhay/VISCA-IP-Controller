import pygame

#from camera import *
#c = Camera('192.168.0.100', 52381)

pygame.init()
pygame.joystick.init()

from time import sleep

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

	#print('1: ',j.get_axis(1)) # analog value for forward -1  backward 1
	#print('0: ',j.get_axis(0)) # left -1  right 1
	#print('2: ',j.get_axis(2)) # throttle -1 full forward  1 full back
	clock.tick()
	tick += 1
	#if tick > 20000:
	#	done = True
	#	continue
pygame.quit ()