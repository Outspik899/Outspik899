import os
from dataclasses import dataclass
import pygame, pytmx, pyscroll

@dataclass
class Portal:
    from_stage1: str
    origin_point: str
    target_stage: str
    teleport_point: str


@dataclass
class Map:
    name: str
    walls: list[pygame.Rect]
    group: pyscroll.PyscrollGroup
    tmx_data: pytmx.TiledMap
    portals: list[Portal]


class MapManager:

     def __init__(self, screen, player):
        self.maps = dict()
        self.screen = screen
        self.player = player
        self.current_map = "stage1"

        self.register_map("stage1", portals=[
            Portal(from_stage1="stage1", origin_point="enter_stage2", target_stage="stage2", teleport_point="spawn_stage2")
        ])
        self.register_map("stage2", portals=[
            Portal(from_stage1="stage2", origin_point="enter_stage3", target_stage="stage3", teleport_point="spawn_stage3"), Portal(from_stage1="stage2", origin_point="exit_stage2", target_stage="stage1", teleport_point="enter_stage2_exit")
        ])

        self.teleport_player("player")

     def check_collisions(self):
         #portals
         for portal in self.get_map().portals:
             if portal.from_stage1 == self.current_map:
                 point = self.get_object(portal.origin_point)
                 rect = pygame.Rect(point.x, point.y, point.width, point.height)

                 if self.player.feet.colliderect(rect):
                     copy_portal = portal
                     self.current_map = portal.target_stage
                     self.teleport_player(copy_portal.teleport_point)

         #collision
         for sprite in self.get_group().sprites():
             if sprite.feet.collidelist(self.get_walls())> -1:
                 sprite.move_back()

     def teleport_player(self, name):
         point = self.get_object(name)
         self.player.position[0] = point.x
         self.player.position[1] = point.y
         self.player.save_location()
     def register_map(self, name, portals=[]):

         #ajouter chatgpt
         current_directory = os.path.dirname(__file__)
         tmx_path = os.path.join(current_directory, '..', 'map', f'{name}.tmx')

         # charger la carte (tmx)
         tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
         map_data = pyscroll.data.TiledMapData(tmx_data)
         map_layer = pyscroll.orthographic.BufferedRenderer(map_data,self.screen.get_size())
         map_layer.zoom = 2

         # definir liste de collision
         walls = []

         for obj in tmx_data.objects:
             if obj.type == "collision":
                 walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

         # dessiner le groupe de calques
         group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=4)
         group.add(self.player)

         #Enregistrer la nouvelle carte chargée
         self.maps[name] = Map(name, walls, group, tmx_data, portals)

     def get_map(self): return self.maps[self.current_map]

     def get_group(self): return self.get_map().group

     def get_walls(self): return self.get_map().walls

     def get_object(self, name): return self.get_map().tmx_data.get_object_by_name(name)

     def draw(self):
         self.get_group().draw(self.screen)
         self.get_group().center(self.player.rect.center)

     def update(self):
         self.get_group().update()
         self.check_collisions()
