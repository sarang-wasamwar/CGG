# Fun Race 3D

## Computer Graphics and Gaming Semester Project

> **From pixels to parkour:** this is not only a game README. It is a
> playable timeline of how the game was designed, tested, and improved during
> the semester.

**Fun Race 3D** is a semester-long learning project for Computer Graphics and
Gaming. It started as a small two-dimensional racing experiment and gradually
became a complete 2.5D-style racing and parkour game.

Each version in this folder represents a stage of learning. Instead of using
ready-made drawing functions for every visual element, the project applies
computer graphics algorithms directly to the game: line and circle
rasterization, flood filling, transformations, camera movement, collision
detection, polygon construction, and clipping.

The sequence of versions documents how the project developed from individual
algorithms into a playable game.

## Play the final game

This README is the learning archive; it is not itself an executable game.
To play the completed project, use the separate
[`fun_race_parkour`](../fun_race_parkour/) repository or clone it from
[GitHub](https://github.com/sarang-wasamwar/fun_race_parkour).

### Run it locally

```powershell
git clone https://github.com/sarang-wasamwar/fun_race_parkour.git
cd fun_race_parkour
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

The final game includes the playable race, three levels, AI opponents, coins,
moving barriers, speed bumps, checkpoints, results screens, and the
interactive Graphics Algorithms Demo. See the
[`fun_race_parkour README`](../fun_race_parkour/README.md) for controls and
the full setup guide.

## Choose your route

| If you want to... | Start here |
| --- | --- |
| See the first playable idea | [Version 1](#version-1---from-algorithms-to-a-basic-race) |
| Understand the mathematics | [Version 3](#version-3---transformations-world-coordinates-and-a-moving-camera) |
| See when the game became complete | [Version 4](#version-4---a-complete-c-racing-game) |
| Explore the final implementation | [Final game](#final-game-repository-fun_race_parkour) |
| See the algorithms running live | [`demo.py`](../fun_race_parkour/src/demo.py) |

### Semester progress bar

```text
Version 1  [##........]  Pixel primitives
Version 2  [####......]  Circles and filling
Version 3  [######....]  Transformations and camera
Version 4  [########..]  Game systems and AI
Version 5  [##########]  Clipping and final Pygame game
```

> **Quick challenge:** while reading, try to predict which algorithm is
> responsible for each object you see: road edge, coin, racer, obstacle, and
> race banner. Then check your answer in the table near the end.

---

## Learning progression

### Version 1 - From algorithms to a basic race

`Pixel primitives | First playable prototype`

**Main files:** `Version_1/version1.cpp`, `Version_1/dda_line.cpp`,
`Version_1/brasenham_line.cpp`

The first version focused on understanding how a computer creates visible
shapes one pixel at a time.

What I learned:

- How the **DDA line algorithm** increments coordinates using floating-point
  values.
- How **Bresenham's line algorithm** draws a line efficiently with integer
  error calculations.
- How to calculate distance between two points for basic collision detection.
- How to read keyboard input and update the player's position.
- How a game loop repeatedly clears, draws, updates, and delays the screen.
- How to represent a race track using lines, lanes, finish lines, and simple
  circular players or coins.
- How to create a win condition when a racer reaches the finish.

What was applied to the game:

- A straight race track was drawn with Bresenham lines.
- The player could move left and right.
- Two computer racers moved automatically at different speeds.
- Coins could be collected and counted.
- The first player to reach the finish line won.

This version established the basic relationship between a graphics algorithm
and a gameplay feature: lines became roads and borders, circles became game
objects, and coordinate changes became movement.

---

### Version 2 - Drawing circles and improving the track

`Circular rasterization | Better game objects`

**Main files:** `Version_2/version2.cpp`, `Version_2/dda_circle.cpp`,
`Version_2/bresenham_circle.cpp`, `Version_2/midpoint_circle.cpp`

The second version extended the rasterization work from lines to circles. It
also introduced a more interesting track layout instead of only a rectangular
road.

What I learned:

- How the **DDA circle**, **midpoint circle**, and **Bresenham circle**
  approaches differ.
- How circle symmetry allows one calculated point to produce eight pixels.
- How to draw curved-looking corners using line segments and repeated
  geometric construction.
- How to separate drawing responsibilities into functions such as
  `drawTrack` and `drawRunner`.
- How to keep gameplay state separate from the code that renders it.

What was applied to the game:

- The track received wider lanes and curved-style ends.
- Racers were drawn as filled circles.
- The game loop and winner detection from Version 1 were retained.
- The project became visually clearer while keeping the rendering algorithms
  explicit.

The important lesson was that efficient primitive algorithms can be reused to
build larger game objects. A player, a coin, or a track feature can be made
from a small number of well-understood primitives.

---

### Version 3 - Transformations, world coordinates, and a moving camera

`World space | Camera movement | 2D mathematics`

**Main files:** `Version_3/version3_0.cpp`, `Version_3/version3_1.cpp`,
`Version_3/transformation.cpp`

Version 3 was the major step from a fixed screen drawing to a small world with
coordinates independent of the display. It also provided a separate
transformation experiment to understand the mathematics before applying it to
the race.

What I learned:

- How **translation**, **scaling**, and **rotation** change point coordinates.
- How homogeneous coordinates and 3x3 matrices can represent 2D
  transformations.
- How to compose multiple transformations in a chosen order.
- Why transformation order matters.
- How to describe a road as a sequence of segments and calculate a position
  from distance along the road.
- How to calculate a tangent and a perpendicular offset for lane placement.
- How to convert a world position into a screen position using camera
  translation.
- How to use elapsed time (`dt`) so movement is based on time rather than
  only on frame count.

What was applied to the game:

- The road became a long world-space route made from horizontal and vertical
  segments.
- The player and AI racers moved using a distance-along-road value.
- Three lanes were generated by applying offsets perpendicular to the road.
- The camera followed the player, creating the feeling of a larger track.
- Coins and moving obstacles were positioned in world space and converted to
  screen space before drawing.
- A HUD displayed score and controls.

This version introduced the core idea behind the later 2.5D presentation:
gameplay happens in world coordinates, while rendering projects only the
nearby part of that world onto the screen.

---

### Version 4 - A complete C++ racing game

`Integration milestone | Levels | AI | Collisions`

**Main files:** `Version_4/version4.cpp`, `Version_4/polygon.cpp`,
`Version_4/polygon_2.cpp`

Version 4 combined the earlier algorithms into a more complete game rather
than a collection of demonstrations.

What I learned:

- How to organize a larger program with structures such as `Point`,
  `Obstacle`, `Coin`, and `Racer`.
- How to represent a road as sampled points, distances, and tangent vectors.
- How to generate a curved road using incremental movement and rotation.
- How to draw a thick road as connected polygons.
- How to implement a scrolling camera and render only the visible portion of
  the world.
- How to implement game states such as menu, active race, and finish results.
- How to create multiple levels with different road styles.
- How to use checkpoints to recover a racer after a collision.
- How to update moving obstacles using speed, direction, and elapsed time.
- How to design simple AI with speed, reaction, risk, and obstacle awareness.
- How to track finish time, progress, collisions, and collected coins.
- How recursive flood fill can fill a bounded region after its border has been
  drawn.

What was applied to the game:

- A level-selection menu was added for straight, curved, and parkour roads.
- The player raced against AI-controlled opponents.
- Coins, moving obstacles, checkpoints, collision penalties, and finish
  results were added.
- The HUD displayed time, progress, coins, and controls.
- The game was separated into reusable functions for road generation,
  drawing, updating, collision handling, AI, and interface rendering.

The main learning from Version 4 was integration. Individual algorithms are
useful, but a playable game also needs state management, timing, input
handling, object data, AI behavior, and a reliable update-render loop.

---

### Version 5 - Python/Pygame, polygon clipping, and the final game

`Portable implementation | Clipping | Algorithm demonstrations`

**Main files:** `Version_5/version5.py`, `Version_5/version5.1.py`,
`Version_5/version5.1_clipping.py`, `Version_5/circule_polygon_clipping.py`

Version 5 moved the project from the older C++ graphics environment to
Python/Pygame and brought the graphics algorithms directly into the final
game architecture.

What I learned:

- How to initialize a portable game window and timing loop with Pygame.
- How to write reusable Python functions for graphics and gameplay.
- How to port Bresenham line and circle algorithms from C++ to Python.
- How to implement iterative 4-connected flood fill using a stack and a
  visited set.
- How to translate and rotate points using mathematical functions.
- How to generate and draw polylines and filled rectangles from primitives.
- How **Sutherland-Hodgman polygon clipping** removes the parts of a polygon
  outside a viewing boundary.
- How cross products determine whether a point is inside an edge's
  half-plane.
- How line intersections are calculated while clipping polygon edges.
- How the same clipping method can work with any convex clipping polygon,
  not only a square.
- How to protect pixel drawing with screen-boundary checks.
- How to use modules and data structures to make the game easier to extend.

What was applied to the game:

- The race became a Pygame application with a menu, levels, players, AI,
  coins, obstacles, camera movement, HUD, and finish states.
- Players and coins use Bresenham circles, with flood fill used for interiors.
- Road borders, lane markings, frames, and other edges use Bresenham lines.
- Translation is used for camera movement and world-to-screen conversion.
- Rotation is used for curved road generation and oriented geometry.
- Obstacles are clipped before being rendered when they cross the visible
  square window.
- The separate clipping experiment was reused in the game instead of
  remaining only as a classroom demonstration.

The final Python implementation also includes an educational graphics demo
mode. It lets the user switch between animated demonstrations of Bresenham
lines, Bresenham circles, flood fill, translation, rotation, and
Sutherland-Hodgman clipping. This makes the algorithms visible as well as
functional.

---

## How the concepts connect

| Computer graphics concept | How it appears in the game |
| --- | --- |
| DDA and Bresenham lines | Road borders, lane markings, frames, and polygon edges |
| Bresenham/midpoint circles | Player, AI, and coin outlines |
| Flood fill | Filled players, coins, rectangles, and road regions |
| Translation | Camera movement and world-to-screen conversion |
| Rotation | Curved-road construction and rotated vectors |
| Scaling and composite matrices | Transformation experiments and geometric reasoning |
| Polygon construction | Road surfaces and obstacles |
| Sutherland-Hodgman clipping | Keeping polygons inside the visible window |
| Distance calculations | Coin collection and collision checks |
| Vectors and tangents | Lane offsets and road orientation |
| Timing with `dt` | Consistent movement, AI, obstacles, and camera smoothing |
| State management | Menus, levels, racing, collisions, and finish results |

---

## Final learning outcome

By the end of the semester, I learned that a game is not built from one
algorithm. It is built by combining mathematics, rasterization, input,
animation, data structures, collision logic, AI, camera systems, and user
interface design.

The project progressed in this order:

1. Draw individual pixels and lines.
2. Build circles and simple game objects.
3. Transform coordinates and create a moving world.
4. Combine the systems into a structured racing game.
5. Port the project to Python/Pygame and add clipping and an algorithm demo.

`Fun Race 3D` is therefore both a game and a record of the learning process:
each version solved a new graphics problem and then reused that solution in
the next, more complete version.

---

## Project folders

```text
Fun_Race_3D/
├── Version_1/    Basic lines and first race
├── Version_2/    Circle algorithms and improved track
├── Version_3/    Transformations and camera-based world
├── Version_4/    Complete C++ race with levels and AI
└── Version_5/    Python/Pygame game and polygon clipping
```

The older C++ versions are preserved as milestones. Version 5 is the
culmination of the semester because it carries the learned algorithms into a
more portable, modular, and demonstrable game implementation.

---

## Final game repository: `fun_race_parkour`

The final, properly organized game is available in the
[`fun_race_parkour`](../fun_race_parkour/) repository folder. It is also
available online at
[github.com/sarang-wasamwar/fun_race_parkour](https://github.com/sarang-wasamwar/fun_race_parkour).
This project is the polished continuation of the experiments in Versions 1 to
5.

Unlike the earlier milestone files, the final repository is organized as a
modular Pygame application:

```text
fun_race_parkour/
├── main.py
├── requirements.txt
├── build_exe.bat
└── src/
    ├── game.py
    ├── levels.py
    ├── graphics_algorithms.py
    ├── clipping.py
    ├── collision.py
    ├── states.py
    ├── ui.py
    ├── resources.py
    └── demo.py
```

### What the final game includes

For installation, controls, gameplay instructions, project structure, and the
full graphics explanation, read the dedicated
[`fun_race_parkour/README.md`](../fun_race_parkour/README.md).

- Three data-driven levels: Easy, Medium, and Hard.
- A player racer competing against two AI racers.
- Individual AI reaction, speed, and risk behavior.
- Coins, moving barriers, and speed bumps.
- A 3-2-1-GO countdown, race timer, progress bar, and live ranking.
- Pause, restart, level selection, and results screens.
- A reusable graphics-algorithm demonstration mode from the main menu.
- A stable road rendering approach using pre-baked Bresenham and flood-fill
  surfaces.
- No external image assets: the visible game objects are generated by code.

### How the semester learning appears in the final repository

The final repository applies the complete learning progression in one
playable game:

- `graphics_algorithms.py` contains Bresenham line and circle drawing, flood
  fill, translation, rotation, and Bresenham polylines.
- `clipping.py` contains Sutherland-Hodgman polygon clipping and is used
  during gameplay for road-side poles, flags, and race banners.
- `collision.py` provides circle-circle and point-segment collision tests for
  racers, obstacles, coins, and track objects.
- `levels.py` stores level definitions as data instead of duplicating game
  logic for every level.
- `game.py` combines rendering, movement, camera behavior, AI, collision
  response, coins, obstacles, timing, and race results.
- `states.py` and `ui.py` separate state changes and interface behavior from
  the main game simulation.
- `demo.py` makes the algorithms directly observable for learning,
  presentation, and viva demonstration.

### Final outcome

`fun_race_parkour` is the proper final game for this semester project. The
`Fun_Race_3D` versions show the development and learning process, while
`fun_race_parkour` presents the result as a maintainable, modular, and
playable game. It demonstrates not only that the graphics algorithms were
understood, but also that they were applied consistently to gameplay,
animation, collision detection, camera movement, level design, AI, and user
interface systems.

---

## Make the README interactive

Do not read this project only from top to bottom. Use it like a small
exploration guide:

- [ ] Open the final [`fun_race_parkour`](../fun_race_parkour/) repository.
- [ ] Run the game and complete one level.
- [ ] Collect a coin and observe the score change.
- [ ] Hit a moving barrier and observe the checkpoint recovery.
- [ ] Open the **Graphics Algorithms Demo** from the main menu.
- [ ] Compare one algorithm demo with its original implementation in
      [`graphics_algorithms.py`](../fun_race_parkour/src/graphics_algorithms.py).
- [ ] Inspect polygon clipping in
      [`clipping.py`](../fun_race_parkour/src/clipping.py).
- [ ] Return to the version folders and identify where that feature first
      appeared.

<details>
<summary><strong>Click to reveal the recommended learning order</strong></summary>

1. Start with [`Version_1`](Version_1/) and trace one line from its endpoint
   calculations to the pixels on screen.
2. Open [`Version_2`](Version_2/) and compare line symmetry with circle
   symmetry.
3. Use [`Version_3`](Version_3/) to follow a point from world coordinates to
   screen coordinates.
4. Read [`Version_4`](Version_4/) and find the update functions for racers,
   obstacles, coins, and AI.
5. Finish with [`Version_5`](Version_5/) and the final
   [`fun_race_parkour`](../fun_race_parkour/) implementation.

</details>

<details>
<summary><strong>Click to reveal presentation / viva questions</strong></summary>

- Why is Bresenham useful for this project instead of drawing every line with
  a library primitive?
- How does flood fill know when it has reached the boundary?
- Why does the camera move while the road remains in world coordinates?
- How are lane positions calculated on a curved road?
- What happens when an obstacle polygon crosses the clipping window?
- Which data is level configuration, and which data changes every frame?

</details>

## One-minute project summary

> I began by drawing lines and circles pixel by pixel. I then used
> transformations to build a moving world and a camera. After that, I added
> game systems such as levels, AI racers, coins, obstacles, collisions, and
> results. Finally, I moved the project to a modular Pygame repository and
> added polygon clipping plus an interactive graphics demo. The final game is
> the result of applying every major graphics concept learned throughout the
> semester.

If you only have one minute to explain the project, show this progression:

```text
Primitive -> Object -> World -> Game system -> Complete playable game
```
