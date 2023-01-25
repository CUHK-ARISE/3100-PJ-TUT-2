import pygame as pg
import sys

pg.init()
screen = pg.display.set_mode((1280, 480))
pg.display.set_caption("Punching the Chimpanzee")

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    pg.display.update()