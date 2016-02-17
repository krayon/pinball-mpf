from mpf.tests.MpfTestCase import MpfTestCase


class TestLogicBlocks(MpfTestCase):

    def getConfigFile(self):
        return 'config.yaml'

    def getMachinePath(self):
        return 'tests/machine_files/logic_blocks/'

    def _start_game(self):
        self.machine.ball_controller.num_balls_known = 0
        self.hit_switch_and_run("s_ball_switch1", 1)
        self.advance_time_and_run(2)

        # start game
        self.hit_and_release_switch("s_start")
        self.assertNotEqual(None, self.machine.game)

        self.advance_time_and_run(1)
        self.release_switch_and_run("s_ball_switch1", 1)

    def _stop_game(self):
        self.advance_time_and_run(10)
        self.hit_switch_and_run("s_ball_switch1", 1)

        self.assertEqual(None, self.machine.game)

    # TODO: should it complete again when enabled but not reset?

    def test_accruals_simple(self):
        self._start_game()
        self.mock_event("accrual1_complete1")
        self.mock_event("accrual1_complete2")

        # accrual should not yet work
        self.post_event("accrual1_step1a")
        self.post_event("accrual1_step2b")
        self.post_event("accrual1_step3c")

        self.assertEqual(0, self._events["accrual1_complete1"])
        self.assertEqual(0, self._events["accrual1_complete2"])

        # enable accrual
        self.post_event("accrual1_enable")

        # step2
        self.post_event("accrual1_step2a")
        self.assertEqual(0, self._events["accrual1_complete1"])

        # step1
        self.post_event("accrual1_step1c")
        self.post_event("accrual1_step1b")
        self.assertEqual(0, self._events["accrual1_complete1"])

        # step 3
        self.post_event("accrual1_step3c")

        # accrual should fire
        self.assertEqual(1, self._events["accrual1_complete1"])
        self.assertEqual(1, self._events["accrual1_complete2"])

        # should not work again
        self.post_event("accrual1_step1a")
        self.post_event("accrual1_step2a")
        self.post_event("accrual1_step3a")
        self.assertEqual(1, self._events["accrual1_complete1"])
        self.assertEqual(1, self._events["accrual1_complete2"])

        # reset but do not enable yet
        self.post_event("accrual1_reset")

        # nothing should happen
        self.post_event("accrual1_step1a")
        self.post_event("accrual1_step2a")
        self.post_event("accrual1_step3a")
        self.assertEqual(1, self._events["accrual1_complete1"])
        self.assertEqual(1, self._events["accrual1_complete2"])

        # enable for one step
        self.post_event("accrual1_enable")
        self.post_event("accrual1_step1a")

        # disable for next
        self.post_event("accrual1_disable")
        self.post_event("accrual1_step2a")

        # enable for third step
        self.post_event("accrual1_enable")
        self.post_event("accrual1_step3a")

        # should not complete yet
        self.assertEqual(1, self._events["accrual1_complete1"])
        self.assertEqual(1, self._events["accrual1_complete2"])

        self.post_event("accrual1_step2a")

        # but now
        self.assertEqual(2, self._events["accrual1_complete1"])
        self.assertEqual(2, self._events["accrual1_complete2"])

    def test_counter_simple_down(self):
        self._start_game()
        self.mock_event("logicblock_counter1_complete")
        self.mock_event("counter_counter1_hit")

        self.post_event("counter1_enable")
        for i in range(4):
            self.post_event("counter1_count")
            self.assertEqual(0, self._events["logicblock_counter1_complete"])

        # nothing should happen when disabled
        self.post_event("counter1_disable")
        for i in range(10):
            self.post_event("counter1_count")
            self.assertEqual(0, self._events["logicblock_counter1_complete"])
        self.post_event("counter1_enable")

        self.post_event("counter1_count")
        self.assertEqual(1, self._events["logicblock_counter1_complete"])
        self.assertEqual(5, self._events["counter_counter1_hit"])

        # it should disable
        self.post_event("counter1_count")
        self.assertEqual(1, self._events["logicblock_counter1_complete"])
        self.assertEqual(5, self._events["counter_counter1_hit"])

        self.post_event("counter1_restart")

        for i in range(4):
            self.post_event("counter1_count")

        # 4 more hits but not completed
        self.assertEqual(1, self._events["logicblock_counter1_complete"])
        self.assertEqual(9, self._events["counter_counter1_hit"])

        # reset
        self.post_event("counter1_reset")
        for i in range(4):
            self.post_event("counter1_count")

        # another 4 hits still not complete
        self.assertEqual(1, self._events["logicblock_counter1_complete"])
        self.assertEqual(13, self._events["counter_counter1_hit"])

        # and complete again
        self.post_event("counter1_count")
        self.assertEqual(2, self._events["logicblock_counter1_complete"])
        self.assertEqual(14, self._events["counter_counter1_hit"])

    def test_sequence_simple(self):
        self._start_game()
        self.mock_event("sequence1_complete")

        self.post_event("sequence1_enable")

        # wrong order
        self.post_event("sequence1_step3a")
        self.post_event("sequence1_step2a")
        self.post_event("sequence1_step1b")
        self.assertEqual(0, self._events["sequence1_complete"])

        # still not
        self.post_event("sequence1_step3b")
        self.post_event("sequence1_step1a")
        self.assertEqual(0, self._events["sequence1_complete"])

        # only 1 so far. now step2
        self.post_event("sequence1_step2a")
        self.assertEqual(0, self._events["sequence1_complete"])

        # and step 3
        self.post_event("sequence1_step3b")
        self.assertEqual(1, self._events["sequence1_complete"])

        # should be disabled
        self.post_event("sequence1_step1a")
        self.post_event("sequence1_step2a")
        self.post_event("sequence1_step3a")
        self.assertEqual(1, self._events["sequence1_complete"])

        # enable and reset
        self.post_event("sequence1_enable")
        self.post_event("sequence1_reset")

        # reset inbetween
        self.post_event("sequence1_step1a")
        self.post_event("sequence1_step2a")
        self.post_event("sequence1_reset")
        self.post_event("sequence1_step3a")

        # nothing
        self.assertEqual(1, self._events["sequence1_complete"])

        # again
        self.post_event("sequence1_step1a")
        self.assertEqual(1, self._events["sequence1_complete"])
        self.post_event("sequence1_step2a")
        self.assertEqual(1, self._events["sequence1_complete"])
        self.post_event("sequence1_step3a")
        self.assertEqual(2, self._events["sequence1_complete"])

    def test_counter_in_mode(self):
        self._start_game()
        self.mock_event("counter2_complete")
        self.mock_event("counter2_hit")

        for i in range(10):
            self.post_event("counter2_count")
            self.assertEqual(0, self._events["counter2_complete"])

        self.post_event("start_mode1")
        self.assertTrue("mode1" in self.machine.modes)

        for i in range(2):
            self.post_event("counter2_count")
            self.assertEqual(i+1, self._events["counter2_hit"])
            self.assertEqual(0, self._events["counter2_complete"])

        self.post_event("counter2_count")
        self.assertEqual(1, self._events["counter2_complete"])

        # should run again
        for i in range(2):
            self.post_event("counter2_count")
            self.assertEqual(i+4, self._events["counter2_hit"])
            self.assertEqual(1, self._events["counter2_complete"])

        self.post_event("counter2_count")
        self.assertEqual(2, self._events["counter2_complete"])

        # stop mode
        self.post_event("stop_mode1")

        # nothing should happen any more
        for i in range(10):
            self.post_event("counter2_count")
            self.assertEqual(2, self._events["counter2_complete"])
            self.assertEqual(6, self._events["counter2_hit"])

    def test_auto_enable_and_disable_in_system_config(self):
        self.mock_event("logicblock_accrual2_complete")

        # does not work before game
        self.post_event("accrual2_step1")
        self.post_event("accrual2_step2")
        self.assertEqual(0, self._events["logicblock_accrual2_complete"])

        self._start_game()
        # should work during game
        self.post_event("accrual2_step1")
        self.post_event("accrual2_step2")
        self.assertEqual(1, self._events["logicblock_accrual2_complete"])

        self._stop_game()

        # does not work after game
        self.post_event("accrual2_step1")
        self.post_event("accrual2_step2")
        self.assertEqual(1, self._events["logicblock_accrual2_complete"])

    def test_no_reset_on_complete(self):
        self.mock_event("logicblock_accrual3_complete")

        # start game
        self._start_game()
        # and enable
        self.post_event("accrual3_enable")

        # should work once
        self.post_event("accrual3_step1")
        self.post_event("accrual3_step2")
        self.assertEqual(1, self._events["logicblock_accrual3_complete"])

        # but not a second time because it disabled
        self.post_event("accrual3_step1")
        self.post_event("accrual3_step2")
        self.assertEqual(1, self._events["logicblock_accrual3_complete"])

        # enable again
        self.post_event("accrual3_enable")

        # still completed
        self.post_event("accrual3_step1")
        self.post_event("accrual3_step2")
        self.assertEqual(1, self._events["logicblock_accrual3_complete"])

        # should work after reset
        self.post_event("accrual3_reset")
        self.post_event("accrual3_step1")
        self.post_event("accrual3_step2")
        self.assertEqual(2, self._events["logicblock_accrual3_complete"])

        # disabled again
        self.post_event("accrual3_reset")
        self.post_event("accrual3_step1")
        self.post_event("accrual3_step2")
        self.assertEqual(2, self._events["logicblock_accrual3_complete"])

        # works after enable
        self.post_event("accrual3_enable")
        self.post_event("accrual3_step1")
        self.post_event("accrual3_step2")
        self.assertEqual(3, self._events["logicblock_accrual3_complete"])

    def test_no_reset_and_no_disable_on_complete(self):
        self.mock_event("logicblock_accrual4_complete")

        # start game
        self._start_game()
        # and enable
        self.post_event("accrual4_enable")

        # should work once
        self.post_event("accrual4_step1")
        self.post_event("accrual4_step2")
        self.assertEqual(1, self._events["logicblock_accrual4_complete"])

        # enabled but still completed
        self.post_event("accrual4_step1")
        self.post_event("accrual4_step2")
        self.assertEqual(1, self._events["logicblock_accrual4_complete"])

        # should work after reset
        self.post_event("accrual4_reset")
        self.post_event("accrual4_step1")
        self.post_event("accrual4_step2")
        self.assertEqual(2, self._events["logicblock_accrual4_complete"])

    def test_player_change(self):
        self.mock_event("logicblock_accrual5_complete")

        self.machine.config['game']['balls_per_game'] = 2

        self._start_game()
        # add player
        self.hit_and_release_switch("s_start")

        # should work during game - player1
        self.assertEqual(1, self.machine.game.player.number)
        self.post_event("accrual5_step1")
        self.post_event("accrual5_step2")
        self.assertEqual(1, self._events["logicblock_accrual5_complete"])

        # player2
        self.advance_time_and_run(10)
        self.hit_switch_and_run("s_ball_switch1", 1)
        self.release_switch_and_run("s_ball_switch1", 4)
        self.assertNotEqual(None, self.machine.game)
        self.assertEqual(2, self.machine.game.player.number)

        # not yet complete
        self.post_event("accrual5_step1")
        self.assertEqual(1, self._events["logicblock_accrual5_complete"])

        # player1 again
        self.advance_time_and_run(10)
        self.hit_switch_and_run("s_ball_switch1", 1)
        self.release_switch_and_run("s_ball_switch1", 4)
        self.assertNotEqual(None, self.machine.game)
        self.assertEqual(1, self.machine.game.player.number)

        # nothing should happen because its disabled and completed for player1
        self.post_event("accrual5_step1")
        self.post_event("accrual5_step2")
        self.assertEqual(1, self._events["logicblock_accrual5_complete"])

        # player2 again
        self.advance_time_and_run(10)
        self.hit_switch_and_run("s_ball_switch1", 1)
        self.release_switch_and_run("s_ball_switch1", 4)
        self.assertNotEqual(None, self.machine.game)
        self.assertEqual(2, self.machine.game.player.number)

        # complete it
        self.post_event("accrual5_step2")
        self.assertEqual(2, self._events["logicblock_accrual5_complete"])

        self._stop_game()

        # does not work after game
        self.post_event("accrual5_step1")
        self.post_event("accrual5_step2")
        self.assertEqual(2, self._events["logicblock_accrual5_complete"])