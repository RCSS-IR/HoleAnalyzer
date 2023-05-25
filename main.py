# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from typing import List, Dict
from tabulate import tabulate
import copy
import re

errors = []
class Game:
    def __init__(self, rcl_path, left_team, right_team):
        self.rcl_path: str = rcl_path
        self.left_team: str = left_team
        self.right_team: str = right_team
        self.step_count: int = 0
        self.hole_count: int = 0
        self.black_hole_count: int = 0
        self.left_hole_step_count: int = 0
        self.left_black_step_count: int = 0
        self.right_hole_step_count: int = 0
        self.right_black_step_count: int = 0
        self.left_hole_steps: List[str] = []
        self.left_black_hole_steps: List[str] = []
        self.right_hole_steps: List[str] = []
        self.right_black_hole_steps: List[str] = []

    def __str__(self):
        res = f'''######
        left_team: {self.left_team}
        right_team: {self.right_team}
        step_count: {self.step_count}
        hole_count: {self.hole_count}
        black_hole_count: {self.black_hole_count}
        left_hole_step_count: {self.left_hole_step_count}
        left_black_step_count: {self.left_black_step_count}
        right_hole_step_count: {self.right_hole_step_count}
        right_black_step_count: {self.right_black_step_count}
        left_hole_steps: {len(self.left_hole_steps)}
        left_black_hole_steps: {len(self.left_black_hole_steps)}
        right_hole_steps: {len(self.right_hole_steps)}
        right_black_hole_steps: {len(self.right_black_hole_steps)}
        '''
        return res

    @staticmethod
    def read_rcl(rcl_path):
        print(rcl_path)
        lines = open(rcl_path, 'r').readlines()
        lines = [line.replace('\t', ' ').split(' ') for line in lines]
        left_team = ''
        right_team = ''
        for line in lines:
            if left_team != '' and right_team != '':
                break
            if str(line).find('referee') > -1:
                continue
            team = ''.join(line[2].split('_')[:-1])
            if left_team == '':
                left_team = team
                continue
            if team != left_team:
                right_team = team
        if left_team == '' or right_team == '':
            print(f'{rcl_path} does not include left({left_team}) or right({right_team}).')
            errors.append(f'{rcl_path} does not include left({left_team}) or right({right_team}).')
            return None
            # raise Exception(f'{rcl_path} does not include left({left_team}) or right({right_team}).')
        g = Game(rcl_path, left_team, right_team)
        step = ''
        left_agents = []
        right_agents = []
        steps = []
        for line in lines:
            if line[0].startswith('0'):
                continue
            if line[0].startswith('6000'):
                break
            if line[1].startswith('(referee'):
                continue
            if step != line[0]:
                if step != '':
                    steps.append({'step': step,
                                  'left': len(left_agents), 'left_set': len(set(left_agents)),
                                  'left_agents': copy.copy(left_agents),
                                  'right': len(right_agents), 'right_set': len(set(right_agents)),
                                  'right_agents': copy.copy(right_agents)})
                    left_agents.clear()
                    right_agents.clear()

                step = line[0]
            team = ''.join(line[2].split('_')[:-1])
            agent = line[2].split('_')[-1]
            if agent != 'Coach' and agent != 'Coach:':
                if team == left_team:
                    left_agents.append(int(agent.replace(':', '')))
                else:
                    right_agents.append(int(agent.replace(':', '')))
        left_kills = {}
        for u in range(1, 12):
            for index in range(len(steps) - 1, -1, -1):
                if u in steps[index]['left_agents']:
                    left_kills[u] = index
                    break
        left_counts = {}
        for index in range(len(steps)):
            left_counts[index] = len([i for i in left_kills.values() if i >= index])

        right_kills = {}
        for u in range(1, 12):
            for index in range(len(steps) - 1, -1, -1):
                if u in steps[index]['right_agents']:
                    right_kills[u] = index
                    break
        right_counts = {}
        for index in range(len(steps)):
            right_counts[index] = len([i for i in right_kills.values() if i >= index])
        g.step_count = len(steps)
        index = 0
        last_hole = -1
        while index < len(steps):
            if steps[index]['left'] == left_counts[index] and steps[index]['left_set'] == left_counts[index]:
                pass
            if steps[index]['left_set'] < left_counts[index]:
                g.hole_count += 1
                g.left_hole_step_count += 1
                g.left_hole_steps.append(steps[index]['step'])
                last_hole = index
            if steps[index]['left'] > steps[index]['left_set'] and last_hole == index - 1:
                g.black_hole_count += 1
                g.left_black_step_count += 1
                g.left_black_hole_steps.append(steps[index]['step'])
            index += 1
            continue

        index = 0
        last_hole = -1
        while index < len(steps):
            if steps[index]['right'] == right_counts[index] and steps[index]['right_set'] == right_counts[index]:
                pass
            if steps[index]['right_set'] < right_counts[index]:
                print(steps[index])
                g.hole_count += 1
                g.right_hole_step_count += 1
                g.right_hole_steps.append(steps[index]['step'])
                last_hole = index
            if steps[index]['right'] > steps[index]['right_set'] and last_hole == index - 1:
                print('black', steps[index])
                g.black_hole_count += 1
                g.right_black_step_count += 1
                g.right_black_hole_steps.append(steps[index]['step'])
            index += 1
            continue

        return g


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

import os
from multiprocessing import Pool
class HoleAnalyzer:
    def __init__(self, path, thread=1):
        self.paths: list = []
        self.thread = thread
        self.teams: Dict[str, Team] = {}
        self.games: List[Game] = []
        self.analyze(path)

    def find_file(self, path):
        if not os.path.isdir(path):
            self.paths.append(path)
            return
        objects = os.listdir(path)

        for obj in objects:
            p = os.path.join(path, obj)
            if os.path.isdir(p):
                self.find_file(p)
            else:
                if p.endswith('.rcl'):
                    self.paths.append(p)
                elif p.endswith('.rcl.gz'):
                    os.system(f'gzip -d {p}')
                    if os.path.exists(p[:-3]):
                        self.paths.append(p[:-3])
                elif p.endswith('log.tar.gz'):
                    if obj[:-11] + '.rcl' in objects:
                        continue
                    os.system(f'tar -xzvf {p} -C {path}')
                    if os.path.exists(p[:-11] + '.rcl'):
                        self.paths.append(p[:-11] + '.rcl')

    def analyze(self, path):
        self.find_file(path)
        pool = Pool(self.thread)
        pool_out = pool.map(Game.read_rcl, self.paths)
        for p in pool_out:
        # for p in self.paths:
        #     g = Game.read_rcl(p)
            self.games.append(p)

        for g in self.games:
            left_team = g.left_team
            right_team = g.right_team
            if left_team not in self.teams.keys():
                self.teams[left_team] = Team(left_team)
            if right_team not in self.teams.keys():
                self.teams[right_team] = Team(right_team)
            self.teams[left_team].game_count += 1
            if g.left_hole_step_count > 0:
                self.teams[left_team].game_with_hole += 1
            if g.left_black_step_count > 0:
                self.teams[left_team].game_with_black_hole += 1
            self.teams[left_team].step_count += g.step_count
            self.teams[left_team].hole_count += g.left_hole_step_count
            self.teams[left_team].black_hole_count += g.left_black_step_count
            if g.left_hole_step_count > 0:
                self.teams[left_team].hole_steps[g.rcl_path] = g.left_hole_steps
            if g.left_black_step_count > 0:
                self.teams[left_team].black_hole_steps[g.rcl_path] = g.left_black_hole_steps

            self.teams[right_team].game_count += 1
            if g.right_hole_step_count > 0:
                self.teams[right_team].game_with_hole += 1
            if g.right_black_step_count > 0:
                self.teams[right_team].game_with_black_hole += 1
            self.teams[right_team].step_count += g.step_count
            self.teams[right_team].hole_count += g.right_hole_step_count
            self.teams[right_team].black_hole_count += g.right_black_step_count
            if g.right_hole_step_count > 0:
                self.teams[right_team].hole_steps[g.rcl_path] = g.right_hole_steps
            if g.right_black_step_count > 0:
                self.teams[right_team].black_hole_steps[g.rcl_path] = g.right_black_hole_steps

    def __str__(self):
        r = f'''{"#" * 20}'''
        r += f'game count: {len(self.games)}\n'
        r += f'team count: {len(self.teams.keys())}\n'
        r += f'''{"#" * 20}'''
        for g in self.games:
            if g.hole_count > 0 or g.black_hole_count > 0:
                r += str(g)
        r += f'''{"#" * 20}\n'''
        for t, v in self.teams.items():
            # if v.hole_count > 0 or v.black_hole_count > 0:
                r += str(v)
        return r

    def print_table(self):
        headers = [
                    'team_name',
                    'game',
                    'game_hole',
                    'game_black_hole',
                    'step',
                    'hole',
                    'black_hole',
                    'all_hole'
        ]
        data = []
        for t, v in self.teams.items():
            data.append([])
            data[-1].append(v.team_name)
            data[-1].append(v.game_count)
            data[-1].append(v.game_with_hole)
            data[-1].append(v.game_with_black_hole)
            data[-1].append(v.step_count)
            data[-1].append(v.hole_count)
            data[-1].append(v.black_hole_count)
            data[-1].append(v.black_hole_count + v.hole_count)
        data.sort(key=lambda x: x[0], reverse=True)
        print(tabulate(data, headers=headers, tablefmt='orgtbl'))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # h = HoleAnalyzer('./sample_data', 1)
    h = HoleAnalyzer('./IranOpen2023/Starter-Junior/Log/SK/GsiKNvP_server2_CYRUS_4-vs-cyrus-girls_0.rcl', 1)
    # h = HoleAnalyzer('/home/nader/workspace/robo/SS2D-Docker-Tournament-Runner/log', 30)
    print(h)
    print(errors)
    h.print_table()
    # g = Game.read_rcl('sample_data/GGHv1WP_server1_Robo2D_1-vs-YuShan2023_4.rcl')
    # pri
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
