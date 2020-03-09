import math
import matplotlib.pyplot as plt
import numpy as np


class Map2D:
    def __init__(self, width, length, verbose=False):
        self.x_size = width
        self.y_size = length
        self.walls = []
        self.add_wall(  (0, 10),  (10, 10)  )
        self.add_wall(  (0, 0),  (10, 0)  )
        self.add_wall(  (0, 0),  (0, 10)  )
        self.add_wall(  (10, 0),  (10, 10)  )
        self.verbose = verbose


    def add_wall(self, point1, point2):
        self.walls.append((point1, point2))

    def get_walls(self):
        return self.walls

    def check_collide(self, point1, point2):
        p1 = np.array(point1)
        p2 = np.array(point2)
        if self.verbose:
            print("Test collide between ")
            print(p1)
            print(p2)
        v = False
        if v:
            print("There are ", len(self.walls), "walls")
        for w in self.walls:
            w1 = np.array(w[0])
            w2 = np.array(w[1])
            if w1[1] == w2[1]:
                if v:
                    print("wall is parallel to OX")
                if w1[0] > w2[0]:
                    w1 = np.array(w[1])
                    w2 = np.array(w[0])
                if p1[1] == p2[1]: # 1
                    if v:
                        print("particle move is parallel to OX")
                    continue
                elif p1[0] == p2[0]: # 3
                    if v:
                        print("particle move is parallel to OY")
                    if p1[0] >= w1[0] and p1[0] <= w2[0]:
                        if (p1[1] >= w1[1] and p2[1] <= w1[1]) or (p1[1] <= w1[1] and p2[1] >= w1[1]):
                            return True
                        else:
                            continue
                    else:
                        continue
            elif w1[0] == w2[0]:
                if v:
                    print("Wall is parallel to OY")
                if w1[1] > w2[1]:
                    w1 = np.array(w[1])
                    w2 = np.array(w[0])
                if p1[0] == p2[0]:
                    if v:
                        print("particle move is parallel to OY")
                    continue
                elif p1[1] == p2[1]:
                    if v:
                        print("particle move is parallel to OX")
                    if p1[1] > w1[1] and p1[1] < w2[1]:
                        if p1[0] <= w1[0] and p2[0] >= w1[0] or p1[0] >= w1[0] and p2[0] <= w1[0]:
                            return True
                        else:
                            continue
                    else:
                        continue
        return False


        if self.verbose:
            print("Does not collide")
        return False



class Environment:

    def distance_loss(self, env_info : dict):
        x = env_info["finish_x"] - env_info["x"]
        y = env_info["finish_y"] - env_info["y"]
        if self.verbose:
            print("Distance between ", env_info["finish_x"], env_info["finish_y"], "and", env_info["x"], env_info["y"], "is", math.sqrt(x ** 2 + y ** 2))
        return math.sqrt(x ** 2 + y ** 2)

    def execute_move_action(self, env_info : dict, action : int):
        first_point = (env_info["x"], env_info["y"])
        new_env = env_info[action](env_info)
        second_point = (new_env["x"], new_env["y"])
        if self.verbose:
            print("Move from ", first_point, "to", second_point)
        if self.map.check_collide(first_point, second_point):
            if self.verbose:
                print("Collide, move stopped")
            return env_info
        else:
            if self.verbose:
                print("Does not collide, move completed")
            return new_env

    @staticmethod
    def get_default_environment_info():
        def up(env : dict):
            new_env = dict(env)
            new_env["y"] = env["y"] + 1
            return new_env
        def down(env : dict):
            new_env = dict(env)
            new_env["y"] = env["y"] - 1
            return new_env

        def right(env : dict):
            new_env = dict(env)
            new_env["x"] = env["x"] + 1
            return new_env
        def left(env : dict):
            new_env = dict(env)
            new_env["x"] = env["x"] - 1
            return new_env

        def stay(env : dict):
            return dict(env)


        info = {
            "start_x": 0,
            "start_y": 0,
            "finish_x": 0,
            "finish_y": 0,
            "x": 0,
            "y": 0,
            1: up,
            2: down,
            3: right,
            4: left,
            0: stay
        }
        return info

    def __init__(self, environment_info, env_map : Map2D, verbose=False):
        self.environment_info = environment_info
        self.map = env_map
        self.verbose = verbose

    def get_environment_info(self):
        return self.environment_info

    def get_start_position(self):
        return (self.environment_info["start_x"], self.environment_info["start_y"])

    def get_map(self):
        return self.map

    def count_loss_for_path(self, path, verbose=False):
        inst = Instance(self)
        inst.execute_actions(path)
        if verbose:
            print(inst.env_data["x"], inst.env_data["y"])
        return inst.get_loss()

class Instance:
    def __init__(self, environment : Environment, verbose=False):
        self.env_data = environment.get_environment_info()
        self.environment = environment
        self.verbose = verbose

        self.env_data["x"] = self.env_data["start_x"]
        self.env_data["y"] = self.env_data["start_y"]

        self.data = dict()

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data[key]

    def reset_position(self):
        self.env_data["x"] = self.env_data["start_x"]
        self.env_data["y"] = self.env_data["start_y"]


    def execute_actions(self, actions_vector):
        env_list = [dict(self.env_data)]
        if self.verbose:
            print("Execute actions: ", actions_vector)
            print("Start pos: ",self.env_data["x"], self.env_data["y"])
        for action in actions_vector:
            new_env_info = self.environment.execute_move_action(env_list[-1], action)
            env_list.append(new_env_info)
        self.env_data = env_list[-1]
        if self.verbose:
            print("Ended up in ", self.env_data["x"], self.env_data["y"])
        return env_list

    def get_loss(self):
        return self.environment.distance_loss(self.env_data)


def draw_map(map : Map2D, start_point, finish_point):
    for w in map.get_walls():
        point1 = w[0]
        point2 = w[1]
        plt.plot((point1[0], point2[0]),  (point1[1], point2[1]), "r-")
    plt.plot(start_point[0], start_point[1], "rx")
    plt.plot(finish_point[0], finish_point[1], "mh")


def plot_actions(actions_list, env : Environment):
    i = Instance(env)
    env_list = i.execute_actions(actions_list)
    x_list = []
    y_list = []
    for event in env_list:
        x_list.append(event["x"])
        y_list.append(event["y"])
    print([(x_list[i], y_list[i]) for i in range(len(x_list))])
    plt.plot(x_list, y_list, "b-")


