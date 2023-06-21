import os
from multiprocessing import Pool
from typing import Dict, List
from src.Game import Game
from tabulate import tabulate

from src.Team import Team

import json


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
            if not g:
                continue
            left_team = g.left_team
            right_team = g.right_team
            if left_team not in self.teams.keys():
                self.teams[left_team] = Team(left_team)
            if right_team not in self.teams.keys():
                self.teams[right_team] = Team(right_team)
            self.teams[left_team].game_count += 1
            self.teams[left_team].games.append(g.rcl_path)
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
            self.teams[right_team].games.append(g.rcl_path)
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
            if not g:
                continue
            if g.hole_count > 0 or g.black_hole_count > 0:
                r += str(g)
        r += f'''{"#" * 20}\n'''
        for t, v in self.teams.items():
            # if v.hole_count > 0 or v.black_hole_count > 0:
            r += str(v)
        return r

    def print_table(self):
        if 'WLF' in self.teams.keys():
            del self.teams['WLF']
        headers = [
            'team_name',
            'game',
            'games_w_holes',
            'games_w_black_holes',
            # 'step',
            'hole',
            'black_hole',
            'all_hole',
            'avg_hole',
            'avg_black_hole'
        ]
        data = []
        for t, v in self.teams.items():
            data.append([])
            data[-1].append(v.team_name)
            data[-1].append(v.game_count)
            data[-1].append(v.game_with_hole)
            data[-1].append(v.game_with_black_hole)
            # data[-1].append(v.step_count)
            data[-1].append(v.hole_count)
            data[-1].append(v.black_hole_count)
            data[-1].append(v.black_hole_count + v.hole_count)
            data[-1].append(round(v.hole_count / v.game_count, 2))
            data[-1].append(round(v.black_hole_count / v.game_count, 2))
        data.sort(key=lambda x: str(x[0]).lower())
        data.append([
            'Total',
            sum(v.game_count for v in self.teams.values()),
            sum(v.game_with_hole for v in self.teams.values()),
            sum(v.game_with_black_hole for v in self.teams.values()),
            # sum(v.step_count for v in self.teams.values()),
            sum(v.hole_count for v in self.teams.values()),
            sum(v.black_hole_count for v in self.teams.values()),
            sum(v.black_hole_count + v.hole_count for v in self.teams.values()),
            round(sum(v.hole_count for v in self.teams.values()) /
                  sum(v.game_count for v in self.teams.values()), 2),
            round(sum(v.black_hole_count for v in self.teams.values()) /
                  sum(v.game_count for v in self.teams.values()), 2),
        ])
        print(tabulate(data, headers=headers, tablefmt='pretty', colalign=('center',)))

    def to_json(self):
        if 'WLF' in self.teams.keys():
            del self.teams['WLF']
        data = []
        for t, v in self.teams.items():
            data.append({
                'team_name': v.team_name,
                'games': v.game_count,
                'games_w_holes': v.game_with_hole,
                'games_w_black_holes': v.game_with_black_hole,
                # 'step': v.step_count,
                'hole': v.hole_count,
                'black_hole': v.black_hole_count,
                'all_hole': v.black_hole_count + v.hole_count,
                'avg_hole': round(v.hole_count / v.game_count, 2),
                'avg_black_hole': round(v.black_hole_count / v.game_count, 2),
            })
        data.sort(key=lambda x: str(x['team_name']).lower())
        data = {
            'teams': data,
            'total': {
                'games': sum(v.game_count for v in self.teams.values()),
                'games_w_holes': sum(v.game_with_hole for v in self.teams.values()),
                'games_w_black_holes': sum(v.game_with_black_hole for v in self.teams.values()),
                # 'step': sum(v.step_count for v in self.teams.values()),
                'hole': sum(v.hole_count for v in self.teams.values()),
                'black_hole': sum(v.black_hole_count for v in self.teams.values()),
                'all_hole': sum(v.black_hole_count + v.hole_count for v in self.teams.values()),
                'avg_hole': round(sum(v.hole_count for v in self.teams.values()) / sum(v.game_count for v in self.teams.values()), 2),
                'avg_black_hole': round(sum(v.black_hole_count for v in self.teams.values()) / sum(v.game_count for v in self.teams.values()), 2),
            }
        }
        return data

    def to_csv(self):
        headers = [
            'team_name',
            'games (G)',
            'games_w_holes(GH)',
            'games_w_black_holes(GBH)',
            # 'steps_taken()',
            'total_holes(TH)',
            'total_black_holes(TBH)',
            'all_hole(H+BH)',
            'avg_hole(H/PG)',
            'avg_black_holes(BH/PG)'
        ]
        data = []
        if len(self.teams) == 0:
            print("No Team found. exiting...")
            exit()
        for t, v in self.teams.items():
            data.append([])
            data[-1].append(v.team_name)
            data[-1].append(v.game_count)
            data[-1].append(v.game_with_hole)
            data[-1].append(v.game_with_black_hole)
            # data[-1].append(v.step_count)
            data[-1].append(v.hole_count)
            data[-1].append(v.black_hole_count)
            data[-1].append(v.black_hole_count + v.hole_count)
            data[-1].append(round(v.hole_count / v.game_count, 2))
            data[-1].append(round(v.black_hole_count / v.game_count, 2))
        data.sort(key=lambda x: str(x[0]).lower())
        data.append([
            'Total',
            sum(v.game_count for v in self.teams.values()),
            sum(v.game_with_hole for v in self.teams.values()),
            sum(v.game_with_black_hole for v in self.teams.values()),
            sum(v.step_count for v in self.teams.values()),
            sum(v.hole_count for v in self.teams.values()),
            sum(v.black_hole_count for v in self.teams.values()),
            sum(v.black_hole_count + v.hole_count for v in self.teams.values()),
            round(sum(v.hole_count for v in self.teams.values()) /
                  sum(v.game_count for v in self.teams.values()), 2),
            round(sum(v.black_hole_count for v in self.teams.values()) /
                  sum(v.game_count for v in self.teams.values()), 2),
        ])
        return data, headers

    def output_csv(self, file_name=''):
        data, headers = self.to_csv()
        if len(file_name) > 0:
            res = ','.join(headers) + '\n'
            for d in data:
                res += ','.join(map(str, d))
                res += '\n'
            f = open(file_name, 'w')
            f.write(res)
            f.close()
        else:
            print(','.join(headers))
            for d in data:
                print(','.join(map(str, d)))
        # print(tabulate(data, headers=headers, tablefmt='orgtbl'))

    def output_json(self, file_name=''):
        data = self.to_json()
        if len(file_name) > 0:
            f = open(file_name, 'w')
            f.write(json.dumps(data, indent=4))
            f.close()
        else:
            print(json.dumps(data, indent=4))
