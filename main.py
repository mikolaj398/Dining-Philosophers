import threading as th
import random
import time
import curses
from curses import textpad
N = 5

COORD_PHILOSOPHERS = []
COORD_FORKS = []
FORKS = [th.Lock() for n in range(N)]

def fill_rect(win, coords, color): # coords = [top_left_x, top_left_y, bottom_right_x, bottom_rigth_y]

    st_x = coords[0]+1
    st_y = coords[1]+1
    while (st_x<coords[2]):
        while (st_y<coords[3]):
            win.addstr(st_x,st_y, " ",curses.color_pair(color))
            st_y+=1
        st_y = coords[1]+1
        st_x+=1

class Philosopher(th.Thread):
    running = True

    def __init__(self, left_fork, right_fork, coords, left_coords, right_coords, win):
        th.Thread.__init__(self)
        self.coords = coords
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.left_fork_coords = left_coords
        self.right_fork_coords = right_coords
        self.win = win
        self.eaten = 0


    def run(self):
        while self.running:
            if self.left_fork.acquire():
                if self.right_fork.acquire():
                    self.eat()
                    self.right_fork.release()
                self.left_fork.release()
                self.think()
            else:
                self.think()

    def eat(self):
        self.eaten += 1
        fill_rect(self.win , self.coords,1) 
        fill_rect(self.win, self.left_fork_coords,1)
        fill_rect(self.win, self.right_fork_coords,1)
        time.sleep(random.uniform(1.5,2.5 ))
        fill_rect(self.win, self.left_fork_coords,2)
        fill_rect(self.win, self.right_fork_coords,2)

    def think(self):
        fill_rect(self.win , self.coords,2)
        time.sleep(random.uniform(1.5, 2.5))


def draw_philosopfers(win, win_h, win_w):
    coords = [
        [3, (win_w//2), 8, (win_w//2)+12],
        [10,(win_w//2)+12,15,(win_w//2)+24],
        [19,(win_w//2)+12,24,(win_w//2)+24],
        [19,(win_w//2)-12,24,(win_w//2)],
        [10,(win_w//2)-12,15,(win_w//2)],
    ]

    for i in range(len(coords)):
        textpad.rectangle(win, coords[i][0],coords[i][1],coords[i][2],coords[i][3])
        fill_rect(win, coords[i],2)
        win.addstr(coords[i][0],coords[i][1]+4, f"  {i+1}  ")

    coords_forks = [
        [6, (win_w//2)-6, 8, (win_w//2)-3],
        [6, (win_w//2)+15, 8, (win_w//2)+18],
        [16,(win_w//2)+15,18,(win_w//2)+18],
        [26,(win_w//2)+4,28,(win_w//2)+7],
        [16,(win_w//2)-6,18,(win_w//2)-3],
    ]

    for i in range(len(coords_forks)):
        textpad.rectangle(win, coords_forks[i][0],coords_forks[i][1],coords_forks[i][2],coords_forks[i][3])
        fill_rect(win, coords_forks[i],2)
    
    global COORD_PHILOSOPHERS
    COORD_PHILOSOPHERS = coords
    global COORD_FORKS
    COORD_FORKS = coords_forks


def init_legend(win):
    textpad.rectangle(win, 3,3,5,6)
    fill_rect(win, [3,3,5,6], 1)
    win.addstr(4,8, " - philosopher eats/fork in use")

    textpad.rectangle(win, 7,3,9,6)
    fill_rect(win,[7,3,9,6], 2)
    win.addstr(8,8, " - philosopher thinks/fork is free")

    win.addstr(26,3, f"Press ESC to exit")

def init_colours():
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_MAGENTA)   #eat
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)      #think
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLACK)     #erase

def update_philosophers_labels(win, philosophers):
    for i in range(N):
        win.addstr(14 + (i*2),3, f"Philosopher {i+1} has eaten {philosophers[i].eaten} times")

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    init_colours()
    sh, sw = stdscr.getmaxyx()

    try:
        init_legend(stdscr)
        draw_philosopfers(stdscr, sh, sw)
    except curses.error:
        print('Please enlarge your terminal. Not enough space for all components.')
        return
    
    philosophers = [Philosopher(FORKS[i % N], FORKS[(i+1) % N], COORD_PHILOSOPHERS[i],COORD_FORKS[i % N], COORD_FORKS[(i+1) % N], stdscr) for i in range(N)]

    for p in philosophers:
        p.start()

    while 1:
        stdscr.refresh()
        key = stdscr.getch()
        update_philosophers_labels(stdscr, philosophers)
        if key == 27:
            Philosopher.running = False
            print("Waiting for all threads to stop running...")
            break

curses.wrapper(main)