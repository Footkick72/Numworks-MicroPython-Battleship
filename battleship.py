import kandinsky
import ion
import time
from math import *

PIXEL_SIZE = 10
GAME_RECT = (0, 0, 10, 10)
SCREEN_SIZE = (320, 240)

ship_types = [
  [(0,0),(0,1)],
  [(-1,0),(0,0),(1,0)],
  [(-1,0),(0,0),(1,0)],
  [(-1,0),(0,0),(1,0),(2,0)],
  [(-2,0),(-1,0),(0,0),(1,0),(2,0)]
]

class Board():
  def __init__(self):
    self.ships = []
    self.placing_ship = Ship(ship_types[0],(0,0),0, True)
    self.shots = {}
    self.cursor_pos = [0,0]
  
  def is_ready(self):
    return len(self.ships) == 5
  
  def is_valid_shot(self):
    return not (self.cursor_pos[0], self.cursor_pos[1]) in self.shots
  
  def move_cursor(self,x,y):
    if self.placing_ship != None:
      self.placing_ship.draw(erase = True)
    self.draw_cursor(erase = True)
    self.cursor_pos[0] += x
    self.cursor_pos[1] += y
    self.cursor_pos[0] = max(0, min(GAME_RECT[2]-1, self.cursor_pos[0]))
    self.cursor_pos[1] = max(0, min(GAME_RECT[3]-1, self.cursor_pos[1]))
    if self.placing_ship != None:
      self.placing_ship.position = (self.cursor_pos[0], self.cursor_pos[1])
    for ship in self.ships:
      ship.draw()
    self.draw_cursor()
    if self.placing_ship != None:
      self.placing_ship.draw()
  
  def rotate_ship(self, theta):
    self.placing_ship.draw(erase = True)
    self.placing_ship.rotation += theta
    for ship in self.ships:
      ship.draw()
    self.placing_ship.draw()
  
  def place_ship(self):
    if self.placing_ship.is_invalid(self.ships):
      return
    
    self.ships.append(Ship(self.placing_ship.shape, self.placing_ship.position, self.placing_ship.rotation, False))
    for ship in self.ships:
      ship.draw()
    if len(self.ships) < 5:
      self.placing_ship = Ship(ship_types[len(self.ships)],self.cursor_pos,0,True)
      self.placing_ship.draw()
    else:
      self.placing_ship = None
  
  def test_shot(self, shot_pos):
    for ship in self.ships:
      if ship.test_shot(shot_pos):
        return True
  
  def is_dead(self):
    return all([ship.sunk for ship in self.ships])
  
  def report_shot(self, state):
    xfst = int(SCREEN_SIZE[0]/2 - (PIXEL_SIZE * GAME_RECT[2]/2))
    pos = (self.cursor_pos[0], self.cursor_pos[1])
    self.shots[pos] = state
    color = kandinsky.color(255,0,0) if state else kandinsky.color(128,128,128)
    kandinsky.fill_rect(xfst+pos[0]*PIXEL_SIZE+3, pos[1]*PIXEL_SIZE+3, PIXEL_SIZE-5, PIXEL_SIZE-5, color)
  
  def draw(self):
    xfst = int(SCREEN_SIZE[0]/2 - (PIXEL_SIZE * GAME_RECT[2]/2))
    kandinsky.fill_rect(xfst,0,GAME_RECT[2]*PIXEL_SIZE + 1,(GAME_RECT[3]+1)*PIXEL_SIZE + GAME_RECT[3]*PIXEL_SIZE + 1,kandinsky.color(0,0,0))
    for x in range(GAME_RECT[2]):
      for y in range(GAME_RECT[3]):
        kandinsky.fill_rect(xfst+x*PIXEL_SIZE-1 + 2, y*PIXEL_SIZE-1 + 2, PIXEL_SIZE-1, PIXEL_SIZE-1, kandinsky.color(255,255,255))
        kandinsky.fill_rect(xfst+x*PIXEL_SIZE-1 + 2, (GAME_RECT[3]+1)*PIXEL_SIZE+y*PIXEL_SIZE-1 + 2, PIXEL_SIZE-1, PIXEL_SIZE-1, kandinsky.color(255,255,255))
    
    for ship in self.ships:
      ship.draw()
    
    if self.placing_ship != None:
      self.placing_ship.draw()
    
    for pos in self.shots:
      state = self.shots[pos]
      color = kandinsky.color(255,0,0) if state else kandinsky.color(128,128,128)
      kandinsky.fill_rect(xfst+pos[0]*PIXEL_SIZE+3, pos[1]*PIXEL_SIZE+3, PIXEL_SIZE-5, PIXEL_SIZE-5, color)
    
    self.draw_cursor()
  
  def draw_cursor(self, erase=False):
    xfst = int(SCREEN_SIZE[0]/2 - (PIXEL_SIZE * GAME_RECT[2]/2))
    yfst = 0 if self.is_ready() else (GAME_RECT[3]+1)*PIXEL_SIZE
    x, y = self.cursor_pos
    color = kandinsky.color(255,255,255) if erase else kandinsky.color(255,0,0)
    kandinsky.fill_rect(xfst+x*PIXEL_SIZE+1, yfst+y*PIXEL_SIZE+1, int(PIXEL_SIZE/4), int(PIXEL_SIZE/4), color)
    kandinsky.fill_rect(xfst+(x+1)*PIXEL_SIZE-int(PIXEL_SIZE/4), yfst+y*PIXEL_SIZE+1, int(PIXEL_SIZE/4), int(PIXEL_SIZE/4), color)
    kandinsky.fill_rect(xfst+x*PIXEL_SIZE+1, yfst+(y+1)*PIXEL_SIZE-int(PIXEL_SIZE/4), int(PIXEL_SIZE/4), int(PIXEL_SIZE/4), color)
    kandinsky.fill_rect(xfst+(x+1)*PIXEL_SIZE-int(PIXEL_SIZE/4), yfst+(y+1)*PIXEL_SIZE-int(PIXEL_SIZE/4), int(PIXEL_SIZE/4), int(PIXEL_SIZE/4), color)

class Ship():
  def __init__(self, ship_type, pos, rot, is_place):
    self.position = pos
    self.rotation = rot
    self.shape = ship_type
    self.hits = [False for _ in range(len(self.shape))]
    self.sunk = False
    self.is_place = is_place
  
  def get_real_shape(self):
    x = []
    for segment in self.shape:
      rsegment = (segment[0], segment[1])
      if self.rotation % 4 == 1:
        rsegment = (segment[1], -segment[0])
      elif self.rotation % 4 == 2:
        rsegment = (-segment[0], -segment[1])
      elif self.rotation % 4 == 3:
        rsegment = (-segment[1], segment[0])
      x.append((rsegment[0] + self.position[0], rsegment[1] + self.position[1]))
    return x
  
  def is_invalid(self, others):
    for pos in self.get_real_shape():
      if pos[0] < 0:
        return True
      if pos[0] > GAME_RECT[2]-1:
        return True
      if pos[1] < 0:
        return True
      if pos[1] > GAME_RECT[3]-1:
        return True
      for ship in others:
        for opos in ship.get_real_shape():
          if pos == opos:
            return True
  
  def test_shot(self, shot_pos):
    for i,pos in enumerate(self.get_real_shape()):
      if shot_pos[0] == pos[0] and shot_pos[1] == pos[1]:
        self.hits[i] = True
        if all(self.hits):
          self.sunk = True
        return True
  
  def draw(self, erase=False):
    xfst = int(SCREEN_SIZE[0]/2 - (PIXEL_SIZE * GAME_RECT[2]/2))
    yfst = (GAME_RECT[3]+1)*PIXEL_SIZE
    for i,pos in enumerate(self.get_real_shape()):
      color = kandinsky.color(255,0,0) if self.hits[i] else kandinsky.color(128,128,128)
      if erase:
        color = kandinsky.color(255,255,255)
      inset = 3 if self.is_place else 1
      kandinsky.fill_rect(xfst + pos[0] * PIXEL_SIZE + inset, yfst + pos[1] * PIXEL_SIZE + inset, PIXEL_SIZE - inset*2+1, PIXEL_SIZE - inset*2+1, color)

player1 = Board()
player2 = Board()

just_shot = False
lcount = 0
rcount = 0
ucount = 0
dcount = 0
rlcount = 0
rrcount = 0
cursor_speed = 8

for player in [player1, player2]:
  kandinsky.fill_rect(0,0,SCREEN_SIZE[0],SCREEN_SIZE[1], kandinsky.color(255,255,255))
  player.draw()
  while not player.is_ready():
    if ion.keydown(ion.KEY_LEFT):
      lcount += 1
      if lcount > cursor_speed:
        lcount = 0
        player.move_cursor(-1,0)
    if ion.keydown(ion.KEY_RIGHT):
      rcount += 1
      if rcount > cursor_speed:
        rcount = 0
        player.move_cursor(1,0)
    if ion.keydown(ion.KEY_DOWN):
      dcount += 1
      if dcount > cursor_speed:
        dcount = 0
        player.move_cursor(0,1)
    if ion.keydown(ion.KEY_UP):
      ucount += 1
      if ucount > cursor_speed:
        ucount = 0
        player.move_cursor(0,-1)
    if ion.keydown(ion.KEY_RIGHTPARENTHESIS):
      rrcount += 1
      if rrcount > cursor_speed:
        rrcount = 0
        player.rotate_ship(1)
    if ion.keydown(ion.KEY_LEFTPARENTHESIS):
      rlcount += 1
      if rlcount > cursor_speed:
        rlcount = 0
        player.rotate_ship(-1)
    if ion.keydown(ion.KEY_OK):
      if not just_shot:
        player.place_ship()
      just_shot = True
    else:
      just_shot = False

kandinsky.fill_rect(0,0,SCREEN_SIZE[0],SCREEN_SIZE[1], kandinsky.color(255,255,255))
player = player2
player.draw()

winner = None
waiting = 0
while True:
  if waiting != 0:
    if ion.keydown(ion.KEY_OK):
      if not just_shot:
        waiting += 1
        if waiting == 2:
          if winner:
            break
          kandinsky.fill_rect(0,0,SCREEN_SIZE[0],SCREEN_SIZE[1], kandinsky.color(255,255,255))
          kandinsky.draw_string("SWAP PLAYERS", 94, 90)
          kandinsky.draw_string("PRESS OK WHEN READY", 60, 110)
        if waiting == 3:
          waiting = 0
          lcount = 0
          rcount = 0
          ucount = 0
          dcount = 0
          kandinsky.fill_rect(0,0,SCREEN_SIZE[0],SCREEN_SIZE[1], kandinsky.color(255,255,255))
          player.draw()
      just_shot = True
    else:
      just_shot = False
  else:
    if ion.keydown(ion.KEY_LEFT):
      lcount += 1
      if lcount > cursor_speed:
        lcount = 0
        player.move_cursor(-1,0)
    if ion.keydown(ion.KEY_RIGHT):
      rcount += 1
      if rcount > cursor_speed:
        rcount = 0
        player.move_cursor(1,0)
    if ion.keydown(ion.KEY_DOWN):
      dcount += 1
      if dcount > cursor_speed:
        dcount = 0
        player.move_cursor(0,1)
    if ion.keydown(ion.KEY_UP):
      ucount += 1
      if ucount > cursor_speed:
        ucount = 0
        player.move_cursor(0,-1)
    if ion.keydown(ion.KEY_OK):
      if not just_shot and player.is_valid_shot():
        if player == player2:
          player = player1
          success = player1.test_shot(player2.cursor_pos)
          player2.report_shot(success)
          if player1.is_dead():
            winner = "2"
        else:
          player = player2
          success = player2.test_shot(player1.cursor_pos)
          player1.report_shot(success)
          if player2.is_dead():
            winner = "1"
        waiting = 1
      just_shot = True
    else:
      just_shot = False

kandinsky.fill_rect(0,0,SCREEN_SIZE[0],SCREEN_SIZE[1], kandinsky.color(255,255,255))
kandinsky.draw_string("PLAYER " + winner + " WINS!", 96, 100)
