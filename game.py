import pygame as pg
import time

FPS_LIMIT     = 60
INTERVAL_TIME = 1 / FPS_LIMIT

class UI:
	core = None
	dpad_map = []

	ui_pressed_events = {
		"dpad_0": False,
		"dpad_1": False,
		"dpad_2": False,
		"dpad_3": False
	}
	
	ui_theme = {
		"dpad_pressed": (255, 255, 157, 50),
		"dpad_background": (220, 83, 24)
	}
	
	def quit(event):
		return event.type == pg.QUIT	
	
	def finger(event):
		return event.x * core.screen_w, event.y * core.screen_h
		
	def pressed(UI, ui_element):
		return UI.ui_pressed_events[ui_element]
	
	def ui_sync_with_entity(UI, entity):
		if entity is None:
			pass
		
		if UI.pressed(UI, "dpad_0"):
			entity.mot_x += 5
			
		if UI.pressed(UI, "dpad_1"):
			entity.mot_x -= 5
		
		if UI.pressed(UI, "dpad_2"):
			entity.mot_y += 5
		
		if UI.pressed(UI, "dpad_3"):
			entity.mot_y -= 5
	
	def create_dpad(UI, x, y, size):
		UI.dpad_map = [
			# Left:
			[x, y + size, size, size],
			
			# Right:
			[x + size + size, y + size, size, size],
			
			# Top:
			[x + size, y, size, size],
			
			# Bottom:
			[x + size, y + size + size, size, size]
		]
		
	def collide(x, y, map):
		return x > map[0] and y > map[1] and x < map[0] + map[2] and y < map[1] + map[3]
	
	def get_theme(UI, ui_theme, ui_element):
		return UI.ui_theme[ui_theme + "_pressed"]  if UI.ui_pressed_events[ui_element] else UI.ui_theme[ui_theme + "_background"]
	
	def render_dpad(UI, surface):
		surface.fill(UI.get_theme(UI, "dpad", "dpad_0"), UI.dpad_map[0])
		surface.fill(UI.get_theme(UI, "dpad", "dpad_1"), UI.dpad_map[1])
		surface.fill(UI.get_theme(UI, "dpad", "dpad_2"), UI.dpad_map[2])
		surface.fill(UI.get_theme(UI, "dpad", "dpad_3"), UI.dpad_map[3])
	
	def callback_dpad_event(UI, event):
		if event.type == pg.FINGERDOWN or event.type == pg.FINGERUP:
			x, y = UI.finger(event)
			
			for i in range(0, 4):
				ui_string = "dpad_" +  str(i)
				
				if UI.collide(x, y, UI.dpad_map[i]) or event.type == pg.FINGERUP:
					UI.ui_pressed_events[ui_string] = event.type == pg.FINGERDOWN;
	
class Shape:
	def __init__(self):
		self.rect = [0, 0, 0, 0]
		self.texture_id = 0
		self.entity_id = 0
		self.update = 0
		
	def update_rect(self, x, y, w, h):
		if x == self.rect[0] and y == self.rect[1] and w == self.rect[2] and h == self.rect[2]:
			return
		
		self.rect = [x, y, w, h]
		self.update = 1

class Entity:
	def __init__(self, name):
		self.name = name;
		self.is_dead = 0
		self.pos_x = 0
		self.pos_y = 0
		self.mot_x = 0
		self.mot_y = 0
		self.gravity = 1
		self.id = 0
		self.width = 0
		self.height = 0
		self.shape_index = 0
		
		self.side_collided = {
			"top": False,
			"bottom": False, 
			"left": False,
			"right": False
		}
		
		self.moving = 0
		self.hand_offset = 0
	
	def set_dead(self):
		pass

	def set_pos(self, x, y):
		self.pos_x = x
		self.pos_y = y
	
	def set_velocity(self, mx, my):
		self.mot_x = mx
		self.mot_y = my

	def update_entity(self):
		pass
	
	def update(self, world_render):
		self.pos_x -= self.mot_x * 0.5
		self.pos_y -= self.mot_y * 0.5	
		
		shape = world_render.shape_list[self.shape_index]
		shape.update_rect(self.pos_x,  self.pos_y, self.width, self.height);

		self.set_velocity(0, 0)
	
class EntityPlayer(Entity):
	def __init__(self, name, ruid):
		Entity.__init__(self, name)
		
		# Real User Identification.
		self.ruid = ruid
		
		self.health = 0.0
		self.mana = 0.0
		self.food = 0.0
	
	def spawn(self, world):
		self.health = 20.0
		self.mana = 20.0
		self.food = 20.0
		self.is_dead = False
		
		# add it if needed.
		world.add_entity_direct(self)
	
	def set_dead(self):
		self.health = 0.0
		Entity.set_dead(self)
	
	def set_health(self, level):
		if level > 0.0:
			self.health = level;
			self.is_dead = True
		else:
			self.set_dead()
	
	def set_food(self, level):
		self.food = level
	
	def set_mana(self, level):
		self.mana = level
	
	def update(self, world_render):	
		Entity.update(self, world_render)
		
class WorldRender:
	def __init__(self):
		self.shape_list = []
		self.camera_x, self.camera_y = 0, 0
	
	def add_shape(self, entity):
		shape = Shape()
		shape.entity_id = entity.id
		shape.update_rect(entity.pos_x, entity.pos_y, entity.width, entity.height)
		
		self.shape_list.append(shape)
		
		i = self.index_of(entity.id)
		
		if i != -1:
			entity.shape_index = i
		
	def index_of(self, entity_id):
		for i in range(0, len(self.shape_list)):
			if self.shape_list[i].entity_id == entity_id:
				return i
		
		return -1
	
	def define(self, world_in):
		self.shape_list.clear()
		
		for entity in world_in.entity_list:
			if not entity.is_dead:
				self.add_shape(entity)
	
	def end_render_world(self):
		self.shape_list.clear()
		
	def set_camera_pos(self, x, y):
		self.camera_x = x
		self.camera_y = y
	
	def camera_follow_entity(self, entity):
		self.camera_x = entity.pos_x + (entity.width / 2) - (UI.core.screen_w / 2)
		self.camera_y = entity.pos_y + (entity.height / 2) - (UI.core.screen_h / 2)
	
	def render(self, surface):
		for shape in self.shape_list:
			shape.rect[0] -= self.camera_x
			shape.rect[1] -= self.camera_y

			surface.fill((244, 85, 92, 10), shape.rect)

			shape.rect[0] += self.camera_x
			shape.rect[1] += self.camera_y
				
class World:
	def __init__(self, name):
		# The name of this world.
		self.name = name
		
		# Entities in world.
		self.entity_list = []
		
		# Instead itterate every entity at world,
		# get a maximum id based in value size.
		self.id_max = 0
	
	def contains(self, entity_or_id):
		if type(entity_or_id) is int:
				for i in range(0, len(self.entity_list) - 1):
					entity = self.entity_list[i];
					
					if entity.id == entity_or_id:
						return i
				return -1
		else:
				return self.entity_world.__contains__(entity)
	
	def add_entity_direct(self, entity):
		if self.contains(entity.id) == -1:
			self.id_max += 1
			
			entity.id = self.id_max # unsigned
			self.entity_list.append(entity);
			
	def remove_entity_from_world(self, id):
		i = self.contains(id)
		
		if i != 0:
			del self.entity_list[i]

		return i != 0
	
	def update(self, world_render):
		for entity in self.entity_list:
			entity.update(world_render)
	
	def end_world(self):
		self.entity_list.clear()
	
	def start_world(self):
		pass

class AkillsCore:
	def __init__(self):
		self.screen = None
		self.screen_w = 0
		self.screen_h = 0
		self.exit = 0
		self.player = None
		self.world = None
		self.world_render = None
		self.enable_ui = False
		self.camera = True
		
		self.previous_time = 0
		self.frames_elapsed = 0
		self.fps  = 0
	
	def create_new_world(self, name):
		self.world = World(name);
		self.world.start_world()
	
	def close_world(self):
		self.world_render.end_render_world()
		self.world.end_world()
		
		self.world_render = None
		self.world = None
	
	def create_new_player(self, name, ruid):
		self.player = EntityPlayer(name, ruid)
		self.player.set_pos(200, 200)
		self.player.width = 100
		self.player.height = 100	
	
	def open_world(self):
		if self.world == None:
			return

		if self.player != None:
			self.player.spawn(self.world)

		dpad_offset = 20
		dpad_size = 70 * 3
		
		UI.create_dpad(UI, x = dpad_offset, y = self.screen_h - dpad_size - dpad_offset, size = 70)
		self.enable_ui = True
				
		x = -200
		for i in range(0, 56):
			entity = Entity("eu dou limda" + str(i))
			entity.set_pos(x, 200)
			entity.width = 50
			entity.height = 50
			
			self.world.add_entity_direct(entity)
			x += entity.width
		
		self.world_render = WorldRender()
		self.world_render.define(self.world)

	def prepare_context(self):
		pg.init()
		
		k = pg.display.Info()
		
		self.screen_w = k.current_w
		self.screen_h = k.current_h
		
		self.screen = pg.display.set_mode((self.screen_w, self.screen_h), pg.FULLSCREEN | pg.DOUBLEBUF)
		
	def run(self):
		while self.exit == 0:
			self.event()	
			self.update()
			self.render()
			
			# Sleep da thread.
			time.sleep(INTERVAL_TIME)
		
	def event(self):
			for event in pg.event.get():
				self.exit = UI.quit(event)
				
				if self.enable_ui:
					UI.callback_dpad_event(UI, event)
		
	def render(self):
		self.screen.fill([190, 190, 190])
		
		if self.world_render != None:
			if self.player != None and self.camera:
				self.world_render.camera_follow_entity(self.player)
			self.world_render.render(self.screen)
			
		if self.enable_ui:
			UI.render_dpad(UI, self.screen)
	
		# Count FPS.
		self.frames_elapsed += 1

		# Swap buffers.
		pg.display.flip()
	
	def update(self):
		if self.previous_time > 20:
			self.fps = self.frames_elapsed
			self.frames_elapsed = 0
		
		if self.enable_ui  and self.player is not None:
			UI.ui_sync_with_entity(UI, self.player)
		
		if self.world is not None:
			self.world.update(self.world_render)
		
	def shutdown(self):
		pg.quit()

def init_akillscube():
	return AkillsCore()

#
# Main game process start.
# 
core = init_akillscube()
core.prepare_context()

# Init UI.
UI.core = core;

core.create_new_player("rima", "872-242-971")
core.create_new_world("teste")
core.open_world()

core.run()
core.shutdown()