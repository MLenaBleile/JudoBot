import numpy as np
import itertools
import pandas as pd

# global variables
STM_DIM = 864
START = (2, 0)
DETERMINISTIC = True
N_VARS = 7
GRIPSL = [0,1]
GRIPSR = [0,1]
GRIPOL = [0,1]
GRIPOR = [0,1]
#0: right, 1: square, 2: left
#S: Self, O: Opponent
STANCES = [0,1,2]
STANCEO = [0,1,2]
GAME_WON = [-1,0,1]
FATIGUES = [0,1]
FATIGUEO = [0,1]
STAMINAS = 50
STAMINAO = 50
STATE_ELEMS = [GRIPSL, GRIPSR,GRIPOL, GRIPOR,STANCES,STANCEO,FATIGUES,FATIGUEO, GAME_WON]
STATE_NAMES = ["SelfLeftGrip","SelfRightGrip","OppLeftGrip","OppRightGrip","SelfStance","OppStance","SelfFatigue","OppFatigue","GameWin"]
START = np.zeros(len(STATE_NAMES))
class State:
    def __init__(self, state=START):
        ##initialize state transition matrix (STM) with key
        self.stm_key = pd.DataFrame(list(itertools.product(*STATE_ELEMS)), columns=STATE_NAMES)
        self.stm = np.zeros([STM_DIM, STM_DIM])
        self.agent_stamina = STAMINAS
        self.opp_stamina = STAMINAO
        assert (STM_DIM == len(self.stm_key.index)), "Length of power set of state elements does not match state space size"
        self.isEnd = False
        self.state = state
        self.determine = DETERMINISTIC

    def giveReward(self):
        return self.state[STATE_NAMES.index("GameWin")]

    def isEndFunc(self):
        if self.state[STATE_NAMES.index("GameWin")] != 0:
            self.isEnd = True

    def nxtPosition(self, action):
            strength = action[-1]
            if action != "mvself":
                self.agent_stamina = self.agent_stamina - 2*(strength + 1)
            if self.agent_stamina < 20:
                self.state[STATE_NAMES.index("SelfFatigue")] = 1
            ##Need to implement different transition probabilities here
            

            return self.state




# Agent of player

class Agent:

    def __init__(self):
        self.states = []
        #0 denotes low power, 1 denotes high power
        self.actions = ["gripR0", "gripL0", "breakgrip0", "mvself", "mvopp0","throwNS0","throwEW0","gripR1", "gripL1", "breakgrip1",  "mvopp1","throwNS1","throwEW1"]
        self.State = State()
        self.lr = 0.2
        self.exp_rate = 0.3

        # initial state reward
        self.state_values = {}
        for i in range(STM_DIM):
            for j in range(STM_DIM):
                self.state_values[(i, j)] = 0  # set initial value to 0

    def chooseAction(self):
        # choose action with most expected value
        mx_nxt_reward = 0
        action = ""

        if np.random.uniform(0, 1) <= self.exp_rate:
            action = np.random.choice(self.actions)
        else:
            # greedy action
            for a in self.actions:
                # if the action is deterministic
                nxt_reward = self.state_values[self.State.nxtPosition(a)]
                if nxt_reward >= mx_nxt_reward:
                    action = a
                    mx_nxt_reward = nxt_reward
        return action

    def takeAction(self, action):
        position = self.State.nxtPosition(action)
        return State(state=position)

    def reset(self):
        self.states = []
        self.State = State()

    def play(self, rounds=10):
        i = 0
        while i < rounds:
            # to the end of game back propagate reward
            if self.State.isEnd:
                # back propagate
                reward = self.State.giveReward()
                # explicitly assign end state to reward values
                self.state_values[self.State.state] = reward  # this is optional
                print("Game End Reward", reward)
                for s in reversed(self.states):
                    reward = self.state_values[s] + self.lr * (reward - self.state_values[s])
                    self.state_values[s] = round(reward, 3)
                self.reset()
                i += 1
            else:
                action = self.chooseAction()
                # append trace
                self.states.append(self.State.nxtPosition(action))
                print("current position {} action {}".format(self.State.state, action))
                # by taking the action, it reaches the next state
                self.State = self.takeAction(action)
                # mark is end
                self.State.isEndFunc()
                print("nxt state", self.State.state)
                print("---------------------")

    def showValues(self):
        for i in range(0, STM_DIM):
            print('----------------------------------')
            out = '| '
            for j in range(0, STM_DIM):
                out += str(self.state_values[(i, j)]).ljust(6) + ' | '
            print(out)
        print('----------------------------------')


if __name__ == "__main__":
    ag = Agent()
    ag.play(50)
    print(ag.showValues())
