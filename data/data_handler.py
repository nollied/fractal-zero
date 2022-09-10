from typing import Tuple
import gym
import torch
import numpy as np
from data.replay_buffer import ReplayBuffer
from utils import get_space_shape


class DataHandler:
    def __init__(
        self, env: gym.Env, replay_buffer: ReplayBuffer, device, max_batch_size: int = 8
    ):
        self.replay_buffer = replay_buffer
        self.device = device

        # TODO: config
        self.max_batch_size = max_batch_size

        self.observation_shape = get_space_shape(env.observation_space)
        self.action_shape = get_space_shape(env.action_space)

        # TODO: expert dataset

    def get_batch(
        self, num_frames: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # TODO: a version of this that allows non-uniform numbers of frames per batch

        assert num_frames > 0

        batch_size = min(len(self.replay_buffer), self.max_batch_size)

        observations = np.zeros(
            (batch_size, num_frames, *self.observation_shape), dtype=float
        )
        actions = np.zeros(
            (batch_size, num_frames, *self.action_shape), dtype=float
        )
        auxiliaries = np.zeros(
            (
                batch_size,
                num_frames,
            ),
            dtype=float,
        )
        values = np.zeros(
            (
                batch_size,
                num_frames,
            ),
            dtype=float,
        )

        for i in range(batch_size):
            (
                gobservations,
                gactions,
                grewards,
                gvalues,
            ) = self.replay_buffer.sample_game_clip(num_frames, pad_to_num_frames=True)

            observations[i, :] = gobservations
            actions[i] = np.expand_dims(
                gactions, -1
            )  # TODO: fix action shape to avoid this expanddims
            auxiliaries[i] = grewards  # auxiliary is a generalization of reward.
            values[i] = gvalues

        # TODO: put these on the correct device sooner?
        return (
            torch.tensor(observations, device=self.device).float(),
            torch.tensor(actions, device=self.device).float(),
            torch.tensor(auxiliaries, device=self.device).unsqueeze(-1).float(),
            torch.tensor(values, device=self.device).unsqueeze(-1).float(),
        )
