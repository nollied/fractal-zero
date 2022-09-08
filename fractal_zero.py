from ctypes import Union
from time import sleep
from typing import Optional
import gym
from data.replay_buffer import GameHistory
from fmc import FMC

import torch

from models.joint_model import JointModel



class FractalZero(torch.nn.Module):
    def __init__(self, env: gym.Env, model: JointModel):
        super().__init__()

        self.env = env
        self.model = model

        self.fmc = None

    def forward(self, observation, lookahead_steps: int = 0):
        # TODO: docstring, note that lookahead_steps == 0 means there won't be a tree search

        if lookahead_steps < 0:
            raise ValueError(f"Lookahead steps must be >= 0. Got {lookahead_steps}")

        state = self.model.representation_model.forward(observation)

        if lookahead_steps > 0:
            self.fmc.set_state(state)
            action = self.fmc.simulate(lookahead_steps)
            return action, self.fmc.root_value

        raise NotImplementedError("Action prediction not yet working.")
        action, value_estimate = self.model.prediction_model.forward(state)
        return action, value_estimate

    def play_game(self, max_steps: int, num_walkers: int, lookahead_steps: int, render: bool = False):
        # TODO: create config class

        obs = self.env.reset()
        game_history = GameHistory(obs)

        self.fmc = FMC(num_walkers, self.model)

        for _ in range(max_steps):
            obs = torch.tensor(obs, device=self.model.device)
            action, value_estimate = self.forward(obs, lookahead_steps=lookahead_steps)
            obs, reward, done, info = self.env.step(action)

            game_history.append(action, obs, reward, value_estimate)

            if done:
                break

            if render:
                self.env.render()
                sleep(0.1)

        return game_history