# JudoBot: A Reinforcement Learning Agent For Basic Judo Mechanics

*by MaryLena Bleile*

I have trained a reinforcement learning agent to play Judo using a basic simulated environment. The environment mechanics include gripping, stance, stamina, and win conditions between a "Tori" (self) and an "Uke" (opponent). It does not currently differentiate between specific throws (e.g. Seioi Nage, Tai otoshi), but broadly categorizes throws as North-South (NS, typically resulting in a fall to the back) and East-West (EW, resulting in a fall to the side). 
## Environment class


The JudoBot simulation environment is a stylized, discrete-time model of tactical interactions in Judo. Each state encodes a configuration of grip control, stance, fatigue, and game status for both the agent (Tori) and its opponent (Uke). The state space is defined as a Cartesian product of the following variables:

 - **Self grip** (left, right): {0, 1}

- **Opponent grip** (left, right): {0, 1}

- **Self stance**: {right, square, left}

- **Opponent stance**: {right, square, left}

 - **Self fatigue**: {0, 1}

- **Opponent fatigue**: {0, 1}

- **Game outcome**: {-1, 0, 1} (loss, ongoing, win)

Each episode begins in a neutral state and proceeds for a maximum of T rounds. During each round, the opponent first takes an action from a fixed or stochastic policy, and then the agent chooses its action. Legal actions include movement, gripping, breaking grips, and executing throws. Fatigue stats (0 or 1) and stamina (0 to 20) are tracked separately from one another: If a player is fatigued, then throw effectiveness is reduced. 

### Main mechanistic functions

**get_valid_actions()**
Some actions can only be attempted in specific states. For example, "breakgripL", corresponding to breaking uke's left grip, is only available if uke has a left grip. Similarly, throws cannot be attempted with no grips. The "get valid action" function retrieves the valid actions that JB can take, while "get valid opp actions" retrieves the valid actions that uke (the opponent) can take.

**giveReward()**
The environment rewards are sparse: +1 for victory, -1 for loss, and 0 otherwise. Loss occurs if uke throws JB or if the episode times out without no throws. giveReward function retrieves the reward status from the state. This function could be elaborated upon if we desired, for example, to give intermediary rewards for successful grips and such.


**_build_throw_success_table()**
Success of JB's throws is determined via a probabilistic lookup table conditioned on stance, fatigue, and grip configuration; this table is constructed once upon environment class initiation using the function _build_throw_success_table(). Starting the function name with an underscore makes it an "internal" function to the object class. 

**apply_opp_action()**
This function modifies the state based on uke's action. For simplicity, uke's throw success is deterministic: if uke has both hands on, throws always succeed. However, uke chooses actions randomly. This loosely represents the case where uke is a true black belt who is choosing to "play down" his/her skills so that JB can learn.  


**nxtPosition()**
This function applies the state transition dynamics. JB moves first, then uke. We first check what valid actions exist in the state using get_valid_actions function, then JB picks what it thinks is the best one out of those values. Next, the opponent's valid actions are found using get_valid_opp_actions, and the action is chosen randomly from that valid action set. The opponent's action is applied using apply_opp_action.

**reset()**
This function resets the environment to default state with no grips and right-foot-forward stance for both players. It will be called in training at the end of each episode (game).

### Helper functions

**visualize_state()**
We visualize what JB is doing by creating an annotated cartoon depiction of each state. This function creates the plot for each specific state and saves it to a directory. At the end, we can knit them all together into a stop-motion animation.

**_qualitative_throw_label()**
This is a helper function for translating numeric probabilities to human-readable labels. For now, JB's throws can have low, medium, or high probability of success. This is another internal function, called only by _build_throw_success_table().

**get_index()**
This function retrieves the state element index from the state name. For example whether or not JB has left grip  ("SelfLeftGrip") is the first element in the state vector, so get_index("SelfLeftGrip") returns the value 0. This function is not completely necessary, but I find it is helpful for making the code more readable.


## Agent class 

The agent class configures and executes the learning process. Agent can be initialized with flexible training parameters:
* min_eps: Minimum threshold on exploration rate - keeping this > 0 during training ensures measurability of the action space.
* alpha: Learning rate. Higher values cause JB to assign more meaning to rewards at each timepoint. If success was not deterministic, meaning that hrows either always succeed or always fail in certain cases, then we would set the learning rate to 0.99 or something very close to 1.
* gamma: Discount factor (should be 0 < gamma < 1) which calibrates the amount of importance JB assigns to short-term vs long-term rewards.

Upon initialization, the agent class also constructs a Q-table representing the "goodness" of each state-action combination. Values in this table are subsequently based on the agent's experience.

The agent chooses actions using **choose_action()** function. We use epsilon-greedy exploration, which means that the agent will choose what it thinks is the best action according to Q table with probability 1-epsilon, and a random action otherwise. Takes as input the current state index s_idx. A testing version also exists, which is the same except there is no chance of taking a random action. 

**run_episode()** is the most important function on this object. This function runs a single "game" of Judo, for up to a prespecified number of rounds (max_steps attribute of Env, set here to 10), after which the game "times out". The run_episode function is written as follows: First, we reset the environment using env.reset(). Then, for each step from 1 to env.max_steps, JB applies an action and observes the resulting environment change, as implemented in env.nxtPosition(). Note that the opponent's action is part of the "environment" from JB's perspective: as such, the opponent action and state updated is encoded into the nxtPosition environment updated. After that, JB's internal "belief" about the goodness of each state-action pair, as quantified in the Q table. The update rule for Q table elements is where the Reinforcement Learning magic happens; this is indicated in the comment surrounding the update rule :) 

**run_test_episode** is the same as run_episode with two exceptions: i) is no Q-update and ii) actions are chosen completely deterministically according to the learned policy Q. This function is used for additional plays for validation and visualization once learning is complete.

## Training

We initialize the agent and train it. Env is builtin to Agent. Plotting the reward curve we see that JB has moderate success learning to throw uke.


Thanks for watching! If you use this work please cite the following:

MaryLena Bleile. *Optimal Control Using Causal Agents* (CRC Press). Forthcoming, 2027.

## Simulation

We further validate by training across 100 random seeds and averaging results. It looks like while we did actually hit a pretty good seed in the intial train, JudoBot still does learn to outperform the random opponent by a substantial margin. Note also that the "Game Win Rate" compares wins to total outcomes, not wins to losses: Since the win rate is lower than the average reward curve, we know that the games JB didn't win are mostly draws (otherwise the -1s from losses would drag the average reward below the game win rate).

