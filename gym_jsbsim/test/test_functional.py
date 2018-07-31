import unittest
import numpy as np
from gym_jsbsim.agents import RandomAgent
from gym_jsbsim.environment import JsbSimEnv
from gym_jsbsim.tasks import SteadyLevelFlightTask


class AgentEnvInteractionTest(unittest.TestCase):
    """ Tests for agents interacting with env. """

    def test_random_agent_steady_level_task_setup(self):
        # we create an environment with the steady level flight task
        agent_interaction_hz = 5
        env = JsbSimEnv(task_type=SteadyLevelFlightTask,
                        agent_interaction_freq=agent_interaction_hz)
        self.assertIsInstance(env.task, SteadyLevelFlightTask)

        # we interact at 5 Hz, so we expect the sim to run 12 timesteps per
        #   interaction since it runs at 120 Hz
        self.assertEqual(12, env.sim_steps)

        # we init a random agent with a seed
        agent = RandomAgent(action_space=env.action_space)
        self.assertEqual(env.action_space, agent.action_space)

        # this task has an action space of three controls: aileron, elevator, rudder
        expected_num_actions = 3
        self.assertEqual(expected_num_actions, len(agent.action_space.low))
        # we see that the action space has the correct low and high range of +-1.0
        expect_low = np.array([-1.0] * expected_num_actions)
        expect_high = np.array([1.0] * expected_num_actions)
        np.testing.assert_array_almost_equal(expect_high, env.action_space.high)
        np.testing.assert_array_almost_equal(expect_low, env.action_space.low)

        # we reset the env and receive the first state; the env is now ready
        state = env.reset()
        self.assertEqual(len(env.observation_space.low), len(state))

        # we close the env and JSBSim closes with it
        env.close()
        self.assertIsNone(env.sim.sim)

    def test_random_agent_steady_level_task_run(self):
        # we create an environment and agent for the steady level flight task
        agent_interaction_hz = int(JsbSimEnv.DT_HZ / 10)
        env = JsbSimEnv(task_type=SteadyLevelFlightTask,
                        agent_interaction_freq=agent_interaction_hz)
        agent = RandomAgent(action_space=env.action_space)

        # we set up for a loop through one episode
        first_state = env.reset()
        total_reward = 0

        # we take a single step
        action = agent.act(first_state)
        state, reward, done, info = env.step(action)

        # we see the state has changed
        self.assertEqual(first_state.shape, state.shape)
        self.assertTrue(np.any(np.not_equal(first_state, state)),
                        msg='state should have changed after simulation step')
        time_step = 1.0 / agent_interaction_hz
        self.assertAlmostEqual(time_step, env.sim.get_sim_time())
        self.assertFalse(done, msg='episode is terminal after only a single step')

        # the aircraft engines are running, as per initial conditions
        self.assertNotAlmostEqual(env.sim['propulsion/engine/thrust-lbs'], 0)