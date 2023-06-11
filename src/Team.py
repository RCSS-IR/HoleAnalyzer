
class Team:
    
    def __init__(self, team_name: str):
        self.team_name: str = team_name
        self.game_count = 0
        self.game_with_hole = 0
        self.game_with_black_hole = 0
        self.step_count = 0
        self.hole_count = 0
        self.black_hole_count = 0
        self.hole_steps = {}
        self.black_hole_steps = {}
        self.games = []

    def __str__(self):
        holes_step = ''
        for k in self.hole_steps.keys():
            holes_step += k
            holes_step += ':['
            for v in self.hole_steps[k]:
                holes_step += v
                holes_step += ', '
            holes_step += '], '
        black_holes_step = ''
        for k in self.black_hole_steps.keys():
            black_holes_step += k
            black_holes_step += ':['
            for v in self.black_hole_steps[k]:
                black_holes_step += v
                black_holes_step += ', '
            black_holes_step += '], '
        r = f'''######
        team_name: {self.team_name}
        game_count: {self.game_count}
        game_with_hole: {self.game_with_hole}
        game_with_black_hole: {self.game_with_black_hole}
        step_count: {self.step_count}
        hole_count: {self.hole_count}
        black_hole_count: {self.black_hole_count}
        hole_game: {self.hole_steps.keys()}
        black_hole_game: {self.black_hole_steps.keys()}
        '''
        r += f'''
        hole_game: {holes_step}
        black_hole_game: {black_holes_step}
        '''
        return r
