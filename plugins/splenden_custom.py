import auto_derby
from auto_derby import single_mode, mathtools

class Example_Training(single_mode.Training):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        ret += self.stamina * 0.3
        return ret

class Example_Race(single_mode.Race):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        if self.name == "有馬記念":
            ret += 10
        return ret


class Race(single_mode.Race): 
    def score(self, ctx: single_mode.Context) -> float:
        estimate_order = self.estimate_order(ctx)
        if estimate_order == 1:
            prop, skill = {
                Race.GRADE_G1: (10, 45),
                Race.GRADE_G2: (8, 35),
                Race.GRADE_G3: (8, 35),
                Race.GRADE_OP: (5, 35),
                Race.GRADE_PRE_OP: (5, 35),
                Race.GRADE_NOT_WINNING: (0, 0),
                Race.GRADE_DEBUT: (0, 0),
            }[self.grade]
        elif 2 <= estimate_order <= 5:
            prop, skill = {
                Race.GRADE_G1: (5, 40),
                Race.GRADE_G2: (4, 30),
                Race.GRADE_G3: (4, 30),
                Race.GRADE_OP: (2, 20),
                Race.GRADE_PRE_OP: (2, 20),
                Race.GRADE_NOT_WINNING: (0, 0),
                Race.GRADE_DEBUT: (0, 0),
            }[self.grade]
        else:
            prop, skill = {
                Race.GRADE_G1: (4, 25),
                Race.GRADE_G2: (3, 20),
                Race.GRADE_G3: (3, 20),
                Race.GRADE_OP: (0, 10),
                Race.GRADE_PRE_OP: (0, 10),
                Race.GRADE_NOT_WINNING: (0, 0),
                Race.GRADE_DEBUT: (0, 0),
            }[self.grade]

        fan_count = self.fan_counts[estimate_order - 1]

        expected_fan_count = max(
            ctx.target_fan_count,
            mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 0),
                    (24, 8000),
                    (48, 10000),
                    (54, 100000),
                    (72, 150000),
                ),
            ),
        )

        fan_score = (
            mathtools.integrate(
                ctx.fan_count,
                fan_count,
                (
                    (int(expected_fan_count * 0.1), 8.0),
                    (int(expected_fan_count * 0.3), 6.0),
                    (int(expected_fan_count * 0.5), 4.0),
                    (int(expected_fan_count), 1.0),
                ),
            )
            / 600
        )

        not_winning_score = 0 if ctx.is_after_winning else 1.5 * ctx.turn_count()

        continuous_race_penalty = mathtools.interpolate(
            ctx.continuous_race_count(),
            (
                (2, 0),
                (3, 5),
                (4, 25),
                (5, 50),
            ),
        )
        fail_penalty = mathtools.interpolate(
            estimate_order,
            (
                (5, 0),
                (6, 5),
                (12, 15),
            ),
        )

        status_penality = 0
        if self.distance_status(ctx) < ctx.STATUS_B:
            status_penality += 10
        if self.ground_status(ctx) < ctx.STATUS_B:
            status_penality += 10

        SP_bias_fan, SP_bias_prop = {
            Race.GRADE_G1: (1,1),
            Race.GRADE_G2: (0.5,0.8),
            Race.GRADE_G3: (0.3,0.5),
            Race.GRADE_OP: (0.1,0.3),
            Race.GRADE_PRE_OP: (0.1,0.1),
            Race.GRADE_NOT_WINNING: (1,1),
            Race.GRADE_DEBUT: (1,1),
        }[self.grade]

        return (
            fan_score * SP_bias_fan
            + prop * SP_bias_prop
            + skill * 0.5
            + not_winning_score
            - continuous_race_penalty
            - fail_penalty
            - status_penality
        )

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        # auto_derby.config.SINGLE_MODE_TRAINING_CLASS = Example_Training
        # auto_derby.config.SINGLE_MODE_RACE_CLASS = Example_Race
        auto_derby.config.SINGLE_MODE_RACE_CLASS = Race


auto_derby.plugin.register(__name__, Plugin())
