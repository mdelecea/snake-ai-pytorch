Overview:
This project consists of a q-learning implementation of the snake game, but with multiple snakes on the board at once. All snakes are controlled by the same agent, but may go in different directions when a command is given. This makes for an interesting coordination and problem solving approach, as the agent must learn to not collide with itself or the boundaries. 

Running the code:
To run the code, simply run the agent.py script. Parameters for the game can be changed within game.py, such as number/variation of snakes and collision detection on/off.

Contributions:
My contribution to this project was modifying the game to support multiple snakes. I had to make sure that collision detection, food pickup, and agent behavior would work on all snakes, as well as feeding the model the best information from all snakes at once. I also tested many different variations of the game, including expanding/shrinking the field, disabling different collision detections, and varying the amount of snakes on the field.

State Information:
The agent is generalized by feeding it only if there is an obstacle in front/sides of it, which direction the closest snake to the food is facing, and the compass direction to the food from the closest snake (using the manhattan distance). The game sets an initial epsilon (randomness) value of 100%, and decreases that down to a 5% minimum to avoid stagnation. 

Agent Behavior:
Often, the player would simply circle in place for the entirety of the game, not moving even if the food was a single tile away. This may be because of an excessively harsh penalty for failure, meaning that it was “safer” to stay in place than to move and risk losing immediately. This would mean the agent is actually un-learning, as their average score would decrease. However, with a few tweaks and ensuring that the agent could not do better moving randomly than deliberately, the model eventually starts converging.
Interestingly, sometimes the agent would recognize that a food item was impossible to reach with the closest snake to it, as the other snake would be too close to the boundary. Unfortunately, it would not move back from it, as the agent did not have enough information to work with to make that connection. It would eventually simply run into the wall in the attempt.
