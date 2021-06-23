import auto_derby
from auto_derby import single_mode, mathtools
import logging

LOGGER = logging.getLogger(__name__)
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


class Race_Less(single_mode.Race): 
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

        fan_score = mathtools.integrate(
            ctx.fan_count,
            fan_count,
            (
                (int(expected_fan_count * 0.1), 8.0),
                (int(expected_fan_count * 0.3), 6.0),
                (int(expected_fan_count * 0.5), 4.0),
                (int(expected_fan_count), 1.0),
            ),
        ) / 600

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

        
        # 目標還是希望訓練比比賽多，低級比賽予以較重懲罰偏差，再次降低SKILL POINT重要性
        SP_bias_fan, SP_bias_prop = {
            Race.GRADE_G1: (1,1),
            Race.GRADE_G2: (0.7,1),
            Race.GRADE_G3: (0.5,0.5),
            Race.GRADE_OP: (0.3,0.5),
            Race.GRADE_PRE_OP: (0.1,0.1),
            Race.GRADE_NOT_WINNING: (1,1),
            Race.GRADE_DEBUT: (1,1),
        }[self.grade]

        
        SP_status_bias = mathtools.interpolate(
            (ctx.speed + ctx.stamina + ctx.power),
            (
                (0, 2),
                (1000, 1.5),
                (1450, 1.2),
                (1800, 1),
            ),
        )
        #不想輸!!!!
        SP_fail_penalty = mathtools.interpolate(
            estimate_order,
            (
                (1, 0),
                (3, 1),
                (5, 2),
                (6, 5),
                (12, 15),
            ),
        )
        #更低的連跑降心情可能
        SP_continuous_race_penalty = continuous_race_penalty = mathtools.interpolate(
            ctx.continuous_race_count(),
            (
                (2, 0),
                (3, 10),
                (4, 25),
                (5, 50),
            ),
        )
        original = (
            fan_score
            + prop
            + skill * 0.5
            + not_winning_score
            - continuous_race_penalty
            - fail_penalty
            - status_penality
        )
        biased = (
            ( 
                fan_score * SP_bias_fan
                + prop * SP_bias_prop
                + skill * 0.5 
            ) / SP_status_bias
            + not_winning_score
            - SP_continuous_race_penalty
            - SP_fail_penalty
            - status_penality
        )
        LOGGER.info("[Custom]%30s\torig:%2.2f\t biased:%2.2f", self, original, biased)

        return biased
#https://i.imgur.com/bgJP98N.jpg
#目標1200/500/1100/300/400
class Training_MILE(single_mode.training):
    def score(self, ctx: single_mode.Context) -> float:
        spd = mathtools.integrate(
            ctx.speed,
            self.speed,
            ((0, 2.0), (300, 1.0), (600, 0.8), (900, 0.7), (1100, 0.5)),
        )
        if ctx.speed < ctx.turn_count() / 24 * 300:
            spd *= 1.5

        sta = mathtools.integrate(
            ctx.stamina,
            self.stamina,
            (
                (0, 2.0),
                (300, ctx.speed / 600 + 0.3 * ctx.date[0] if ctx.speed > 600 else 1.0),
                (
                    600,
                    ctx.speed / 900 * 0.6 + 0.1 * ctx.date[0]
                    if ctx.speed > 900
                    else 0.6,
                ),
                (900, ctx.speed / 900 * 0.3),
            ),
        )
        pow = mathtools.integrate(
            ctx.power,
            self.power,
            (
                (0, 1.0),
                (300, 0.2 + ctx.speed / 600),
                (600, 0.1 + ctx.speed / 900),
                (900, ctx.speed / 900 / 3),
            ),
        )
        per = mathtools.integrate(
            ctx.guts,
            self.guts,
            ((0, 2.0), (300, 1.0), (400, 0.3), (600, 0.1))
            if ctx.speed > 400 / 24 * ctx.turn_count()
            else ((0, 2.0), (300, 0.5), (400, 0.1)),
        )
        int_ = mathtools.integrate(
            ctx.wisdom,
            self.wisdom,
            ((0, 3.0), (300, 1.0), (400, 0.4), (600, 0.2))
            if ctx.vitality < 0.9
            else ((0, 2.0), (300, 0.8), (400, 0.1)),
        )

        if ctx.vitality < 0.9:
            int_ += 5 if ctx.date[1:] in ((7, 1), (7, 2), (8, 1)) else 3

        skill = self.skill * 0.5

        success_rate = mathtools.interpolate(
            int(ctx.vitality * 10000),
            (
                (0, 0.15),
                (1500, 0.3),
                (4000, 1.0),
            )
            if self.wisdom > 0
            else (
                (0, 0.01),
                (1500, 0.2),
                (3000, 0.5),
                (5000, 0.85),
                (7000, 1.0),
            ),
        )
        return (spd + sta + pow + per + int_ + skill) * success_rate
class Training_Medimum(single_mode.training):
    def score(self, ctx: single_mode.Context) -> float:
        return 0.0
    
class Training_Long(single_mode.training):
    def score(self, ctx: single_mode.Context) -> float:
        return 0.0

class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_race_class = Race_Less


auto_derby.plugin.register(__name__, Plugin())
