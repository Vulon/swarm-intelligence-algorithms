from environment import *
import numpy as np
import random

class Bee:
    def __init__(self, value_vector, age_limit):
        self.value_vector = value_vector
        self.age_limit = age_limit
        self.age = 0
        self.loss = None

    def increase_age(self):
        self.age += 1

    def is_abandoned(self):
        return self.age >= self.age_limit

    def set_value_vector(self, value_vector):
        self.valu = value_vector
        self.age = 0

    def set_loss(self, loss):
        self.loss = loss
    def get_loss(self):
        return self.loss

    def get_value_vector(self):
        return self.value_vector


def intfy(vector):
    return [int(value) for value in vector]

class BeeSwarm:
    def __init__(self):
        env_map = Map2D(10, 10)
        env_map.add_wall((1, 9), (3, 9))
        env_map.add_wall((5, 9), (6, 9))
        env_map.add_wall((8, 9), (8, 8))
        env_map.add_wall((9, 8), (9, 4))
        env_map.add_wall((3, 7), (3, 6))
        env_map.add_wall((8, 7), (8, 6))
        env_map.add_wall((4, 7), (7, 7))
        env_map.add_wall((4, 7), (4, 6))
        env_map.add_wall((4, 6), (4, 5))
        env_map.add_wall((7, 6), (7, 5))
        env_map.add_wall((6, 5), (6, 4))
        env_map.add_wall((0, 4), (2, 4))
        env_map.add_wall((6, 4), (8, 4))
        env_map.add_wall((5, 4), (5, 3))
        env_map.add_wall((3, 5), (3, 1))
        env_map.add_wall((2, 3), (2, 2))
        env_map.add_wall((4, 2), (6, 2))
        env_map.add_wall((8, 2), (8, 1))
        self.env_map = env_map
        env_info = Environment.get_default_environment_info()
        self.start_point = (1.5, 7.5)
        env_info["start_x"] = self.start_point[0]
        env_info["start_y"] = self.start_point[1]
        self.finish_point = (8.5, 1.5)
        env_info["finish_x"] = self.finish_point[0]
        env_info["finish_y"] = self.finish_point[1]

        self.environment = Environment(env_info, env_map)
        self.particles = []
        draw_map(env_map, self.start_point, self.finish_point)

    def start(self, employed_bees_count : int, onlooker_bees_count : int, max_bees_count : int, steps_count, epochs : int, bee_actions_amount=5, food_age_limit=5, verbose = False):

        def generate_random_source():
            return np.random.rand(steps_count) * bee_actions_amount



        def get_neighbour(x_vector : np.ndarray):
            result = x_vector + np.random.rand(steps_count) * (x_vector - generate_random_source())
            for i in range(len(result)):
                result[i] = max(0, result[i])
                result[i] = min(result[i], bee_actions_amount - 1)
            return result

        employed_bees = [Bee(generate_random_source(), food_age_limit) for i in range(employed_bees_count)]
        for bee in employed_bees:
            bee.set_loss(self.environment.count_loss_for_path(intfy(bee.get_value_vector())))

        global_minimum = (employed_bees[0].get_value_vector(), employed_bees[0].get_loss())
        for epoch in range(epochs):
            print("Epoch", epoch, " / ", epochs)
            #Employed bees phase:


            #abandon old
            for bee in employed_bees:
                if bee.is_abandoned():
                    if verbose:
                        print("Abandoned ", bee.get_value_vector())
                    bee.set_value_vector(generate_random_source())
                    bee.set_loss(self.environment.count_loss_for_path(intfy(bee.get_value_vector())))
                    if verbose:
                        print("New source", bee.get_value_vector())


            #Find new neighbour
            for bee in employed_bees:
                if bee.get_loss() is None:
                    bee.set_loss(self.environment.count_loss_for_path(intfy(bee.get_value_vector())))
                new_vector = get_neighbour(bee.get_value_vector())
                new_loss = self.environment.count_loss_for_path(intfy(new_vector))
                if new_loss < bee.get_loss():
                    if verbose:
                        print("Old loss", bee.get_loss(), "new loss", new_loss)
                    bee.set_value_vector(new_vector)
                    bee.set_loss(new_loss)
                else:
                    bee.increase_age()
                    if verbose:
                        print("bee loss", bee.get_loss())
                if bee.get_loss() < global_minimum[1]:
                    global_minimum = (bee.get_value_vector(), bee.get_loss())

            #Onlooker bees phase

            loss_sum = 0
            for bee in employed_bees:
                loss_sum += bee.get_loss()
            if verbose:
                print("Total loss", loss_sum)
            probabilities = [(bee.get_loss() / loss_sum, bee.get_value_vector()) for bee in employed_bees]
            probabilities = np.array(sorted(probabilities, key=lambda tup : tup[0], reverse=True))
            if verbose:
                print("Sorted probabilities", probabilities[:, 0])
            cumulative = [np.sum(probabilities[i:, 0]) for i in range(len(probabilities))]
            if verbose:
                print("Cumulative", cumulative)

            cumulative_index = len(cumulative) - 1

            for onlooker_index in range(onlooker_bees_count):
                rand_item = random.random()
                while rand_item > cumulative[cumulative_index]:
                    cumulative_index -= 1
                if verbose:
                    print("Cumulative index", cumulative_index)
                if verbose:
                    print("Onlooker", onlooker_index)
                    print("random item: ", rand_item)
                bee = Bee(get_neighbour(probabilities[cumulative_index][1]), food_age_limit)
                bee.set_loss(self.environment.count_loss_for_path(intfy(bee.get_value_vector())))
                if verbose:
                    print("New added bee", bee.get_loss())
                if global_minimum[1] > bee.get_loss():
                    global_minimum = (bee.get_value_vector(), bee.get_loss())
                employed_bees.append(bee)

            #Shrink bees count

            employed_bees = sorted(employed_bees, key=lambda bee: bee.get_loss())
            if len(employed_bees) > max_bees_count:
                employed_bees = employed_bees[:max_bees_count]

        return global_minimum

# 
# cases = []
# total = len([employed_bees for employed_bees in range(100, 400, 50)]) * len([employed_bees for employed_bees in range(10, 100, 10)]) * len([employed_bees for employed_bees in range(5, 50, 5)])
# count = 0
# for employed_bees in range(100, 400, 50):
#     for onlooker_bees in range(10, 100, 10):
#         for epochs in range(5, 50, 5):
#             ABC = BeeSwarm()
#             minimum = ABC.start(employed_bees, onlooker_bees, employed_bees * 2, 13, epochs)
#             cases.append((employed_bees, onlooker_bees, epochs, minimum[1]))
#             print(count, " / ", total, cases[-1])
#             count += 1
# 
# 
# cases = np.array(sorted(cases, key= lambda case: case[3]))
# print(cases)
# print("Best 10", cases[:10])
plt.figure("BeeSwarm")
ABC = BeeSwarm()
value = ABC.start(400, 450, 400, 26, 50)
print(value[1])
print(intfy(value[0]))
plot_actions(intfy(value[0]), ABC.environment)
print(ABC.environment.count_loss_for_path(intfy(value[0]), verbose=True))
plt.show()
# (150, 10, 15, 2.23606797749979)
# (100, 50, 25, 2.23606797749979)