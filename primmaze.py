import random
import pygame
import heapq
import sys

def neighbors(maze, ic, jc):
	final = []

	for i in range(4):
		n = [ic, jc]

		delta = (i // 2) * 2
		if delta == 0:
			delta = -2
		n[i % 2] += delta
		
		if n[0] < len(maze) and n[1] < len(maze[0]) and n[0] > 0 and n[1] > 0:
			if maze[n[0]][n[1]] == 1:
				final.append(n)

	return final

def primmaze(width, height, maze):

	if width > 1:
		maze[0][1] = 0
		yield ("carve", 0, 1)

	start = [
		random.randrange(1, height, 2),
		random.randrange(1, width, 2),
	]
	
	maze[start[0]][start[1]] = 0
	yield ("carve", start[0], start[1])

	open_cells = [start]

	while len(open_cells) != 0:
		index = random.randrange(len(open_cells))
		cell = open_cells[index]
		n = neighbors(maze, cell[0], cell[1])

		if not n:
			open_cells.pop(index)
			continue
		choice = random.choice(n)
		open_cells.append(choice)
		mr = (choice[0] + cell[0]) // 2
		mc = (choice[1] + cell[1]) // 2

		maze[mr][mc] = 0
		yield ("carve", mr, mc)
		
		maze[choice[0]][choice[1]] = 0
		yield ("carve", choice[0], choice[1])

	if width > 2:
		maze[height-1][width-2] = 0
		yield ("carve", height - 1, width - 2)
		maze[height - 2][width - 2] = 0
		yield ("carve", height - 2, width - 2)
	
	return maze

def astar_solve(maze, start, goal):
	height, width = len(maze), len(maze[0])
	sr, sc = start
	gr, gc = goal
	
	def is_open(r, c):
		return 0 <= r < height and 0 <= c < width and maze[r][c] == 0

	def h(r, c):
		return abs(r - gr) + abs(c - gc)

	open_heap = []
	heapq.heappush(open_heap, (h(sr, sc), 0, (sr, sc)))
	gscore = {(sr, sc): 0}
	parent = {(sr, sc): None}
	closed = set()

	dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	
	yield("visit", sr, sc)

	while open_heap:
		f, g, (r, c) = heapq.heappop(open_heap)

		if (r, c) in closed:
			continue

		closed.add((r, c))
		yield ("pop", r, c)
		
		if (r, c) == (gr, gc):
			path = []
			cur = (r, c)
			while cur is not None:
				path.append(cur)
				cur = parent[cur]

			path.reverse()

			for pr, pc in path:
				yield ("path", pr, pc)
			return path

		for dr, dc in dirs:
			nr, nc = r + dr, c + dc
			if not is_open(nr, nc):
				continue

			tentative_g = g + 1
			if tentative_g < gscore.get((nr, nc), float("inf")):
				gscore[(nr, nc)] = tentative_g
				parent[(nr, nc)] = (r, c)
				heapq.heappush(open_heap, (tentative_g + h(nr,nc), tentative_g, (nr, nc)))
				yield ("visit", nr, nc)

	yield ("fail", None, None)
	return None



def dfs_solve(maze, start, goal):
	height, width = len(maze), len(maze[0])
	sr, sc = start
	gr, gc = goal

	def is_open(r, c):
		return 0 <= r < height and 0 <= c < width and maze[r][c] == 0

	stack = [(sr, sc)]
	visited = set([(sr, sc)])	
	parent = { (sr, sc): None }
	dirs = [(1,0), (-1,0), (0,1), (0,-1)]
	
	yield ("visit", sr, sc)
	
	while stack:
		r, c = stack.pop()
		yield ("pop", r, c)
		if (r, c) == (gr, gc):
			path = []
			cur = (r, c)
			while cur is not None:
				path.append(cur)
				cur = parent[cur]
			path.reverse()
			for pr, pc in path:
				yield ("path", pr, pc)
			return path

		for dr, dc in dirs:
			nr, nc = r + dr, c + dc
			if is_open(nr, nc) and (nr, nc) not in visited:
				visited.add((nr, nc))
				parent[(nr, nc)] = (r, c)
				stack.append((nr, nc))
				yield ("visit", nr, nc)

	return None
	
def animate_gen(width=101, height=101, cell_size=7, steps_per_frame=4, solver_fn=None):
	pygame.init()
	screen = pygame.display.set_mode((width * cell_size, height * cell_size))
	clock = pygame.time.Clock()

	if solver_fn is None:
		solver_fn = dfs_solve
	
	def draw_cell(r, c, color):
		rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
		pygame.draw.rect(screen, color, rect)
	 
	grid = [[1 for _ in range(width)] for _ in range(height)]
	maze = [[1 for _ in range(width)] for _ in range(height)]
	steps = primmaze(width, height, maze)
	running = True
	done = False
	solveDone = False
	solver_steps = None
	screen.fill((0,0,0))
	pygame.display.flip()
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		if not done:
			try:
				for _ in range(steps_per_frame):
					kind, r, c = next(steps)
					if kind == "carve":
						grid[r][c] = 0
						rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
						pygame.draw.rect(screen,(255,255,255), rect)
			except StopIteration:
				done = True
				solver_steps = solver_fn(maze, (0, 1), (height - 1, width - 2))
				draw_cell(0, 1, (0, 200, 0))
				draw_cell(height - 1, width - 2, (200, 0, 0))
				

		if done and not solveDone:
			try:
				for _ in range(4):
					kind, r, c = next(solver_steps)
					if kind == "visit":
						draw_cell(r, c, (180,220,255))
					elif kind == "pop":
						pass
					elif kind == "path":
						draw_cell(r,c, (255,215,0))
					elif kind == "fail":
						done = True
						break

				draw_cell(0, 1, (0, 200, 0))
				draw_cell(height - 1, width - 2, (200, 0, 0))
			except StopIteration:
				solveDone = True
				

		pygame.display.flip()
		clock.tick(60)

	pygame.quit()

if __name__ == "__main__":
	solver_map = {
		"dfs": dfs_solve,
		"astar": astar_solve
	}
	solver_name = sys.argv[1] if len(sys.argv) > 1 else "dfs"

	if solver_name not in solver_map:
		sys.exit(1)
	
	solver = solver_map[solver_name] 
	
	animate_gen(solver_fn=solver)
