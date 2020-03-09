from environment import *
import random


class ActionGraph:

    class Node:
        def __init__(self, value, children_count):
            self.value = value
            self.children = [None for i in range(children_count)]
            self.visits = []

        def set_child(self, child_num, node):
            self.children[child_num] = node

        def get_children(self):
            return self.children

        def get_child(self, child_index):
            return self.children[child_index]

        def get_value(self):
            return self.value

        def set_value(self, value):
            self.value = value

        def reset_visits(self):
            self.visits = []

        def add_visit(self, value):
            self.visits.append(value)

        def get_visits_values(self):
            return self.visits

        def check_children(self):
            return [not(child is None) for child in self.children]

        def get_not_None_children(self):
            return [child for child in self.children if not(child is None)]

        def get_children_values(self, init_value):
            result_list = []
            for child in self.children:
                if child is None:
                    result_list.append(init_value)
                else:
                    result_list.append(child.value)
            return result_list



    def __init__(self, init_value=1, action_count=5):
        self.head = self.Node(init_value, action_count)
        self.init_value = init_value
        self.actions_count = 5


    def show(self):
        value_list = []
        next_list = []
        current_list = [self.head]
        size = 0
        while len(current_list) > 0:
            node = current_list.pop()
            size += 1
            value_list.append((node.get_value(), node.get_visits_values(), node.check_children()))
            next_list.extend(node.get_not_None_children())
            if len(current_list) < 1:
                current_list.extend(next_list)
                next_list = []
                print(value_list)
                value_list = []
        print("graph size", size)

    def map_all(self, func, arguments=None):
        queue = [self.head]
        while len(queue) > 0:
            node = queue.pop()
            node = func(node, arguments)
            queue.extend(node.get_not_None_children())

    def map_one(self, path, func, arguments=None):
        this_node = self.head
        for step in path:
            if this_node.get_child(step) is None:
                this_node.set_child(step, self.Node(self.init_value, self.actions_count))
            this_node = this_node.get_child(step)
        this_node = func(this_node, arguments)
        return this_node

    def get_node_value(self, path):
        this_node = self.head
        for step in path:
            if this_node.get_child(step) is None:
                this_node.set_child(step, self.Node(self.init_value, self.actions_count))
            this_node = this_node.get_child(step)
        return this_node.get_value()

    def get_children_values(self, path):
        this_node = self.head
        for step in path:
            if this_node.get_child(step) is None:
                this_node.set_child(step, self.Node(self.init_value, self.actions_count))
            this_node = this_node.get_child(step)
        return this_node.get_children_values(self.init_value)

    def reset_visits(self):
        queue = [self.head]

        while len(queue) > 0:
            node = queue.pop()
            node.reset_visits()
            queue.extend(node.get_not_None_children())



class AntColonySwarm:
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

    def start(self, instances_count : int, total_path_length : int, epochs : int, ant_action_count=5, evaporation_index=0, ant_q=1, verbose=False):
        self.particles = []
        for i in range(instances_count):
            p = Instance(self.environment)
            self.particles.append(p)
        self.graph = ActionGraph(action_count=ant_action_count)


        def update_pheromone(node, arguments=None,  verbose=False):
            old_value = node.get_value()
            node.set_value((1 - evaporation_index) * node.get_value() + np.sum(node.get_visits_values()))
            if verbose:
                print("Updated pheromone from", old_value, "to", node.get_value())

            return node

        def append_visit(node, arguments=None, verbose=False):
            node.add_visit(arguments[0])
            return node

        def get_best_path(verbose=False):
            if verbose:
                print("Show best found path in graph:")
            path = []
            for step in range(total_path_length):
                children_values = self.graph.get_children_values(path)
                if verbose:
                    print("Children values:", children_values)
                loss_values = [self.environment.count_loss_for_path(path + [child]) for child in range(ant_action_count)]
                loss_values_new = np.array(loss_values)
                loss_values_old = self.environment.count_loss_for_path(path)
                loss_values = loss_values_old - loss_values_new
                loss_values[loss_values < 0] = 0
                product_list = children_values * loss_values
                denominator = np.sum(product_list)
                if denominator <= 0:
                    probability = [(1 / ant_action_count, i) for i, item in enumerate(product_list)]
                else:
                    probability = [(item / denominator, i) for i, item in enumerate(product_list)]

                probability = np.array(sorted(probability, key=lambda item: item[0], reverse=True))
                if verbose:
                    print("sorted probabilities", probability)
                path.append(int(probability[0][1]))
            return path

        self.graph.reset_visits()

        history = []

        for e in range(epochs):
            for particle in self.particles:
                path = []
                for step in range(total_path_length):
                    children_values = self.graph.get_children_values(path)
                    if verbose:
                        print("path:", path)
                        print("Children values:", children_values)
                    loss_values = [self.environment.count_loss_for_path(path + [child]) for child in range(ant_action_count)]
                    loss_values_new = np.array(loss_values)
                    if verbose:
                        print("Loss values new are:", loss_values_new)
                    loss_values_old = self.environment.count_loss_for_path(path)
                    if verbose:
                        print("loss value old: ", loss_values_old)
                    loss_values = loss_values_old - loss_values_new
                    loss_values[loss_values < 0] = 0
                    if verbose:
                        print("Delta loss value:", loss_values)
                    product_list = children_values * loss_values
                    denominator = np.sum(product_list)

                    if denominator <= 0:
                        probability = [(1 / ant_action_count, i) for i, item in enumerate(product_list)]
                    else:
                        probability = [(item / denominator, i) for i, item in enumerate(product_list)]

                    probability = np.array(sorted(probability, key=lambda item: item[0], reverse=True))
                    if verbose:
                        print("sorted probabilities", probability)
                    cumulative = [np.sum(probability[i :, 0]) for i in range(len(probability))]
                    if verbose:
                        print("cumulative", cumulative)
                    cumulative_index = len(cumulative) - 1
                    rand_item = random.random()
                    while rand_item > cumulative[cumulative_index]:
                        cumulative_index -= 1
                    child_index = int(probability[cumulative_index][1])
                    path.append(child_index)
                    if verbose:
                        print("random item: ", rand_item)
                        print("Picked child", child_index)
                    self.graph.map_one(path, append_visit, arguments=(ant_q * loss_values[child_index],))
                    
            
            self.graph.map_all(update_pheromone)
            self.graph.reset_visits()

            history.append((get_best_path(), self.environment.count_loss_for_path(get_best_path())))


        return history





plt.figure("Ants path")

ants = AntColonySwarm()
history = ants.start(3, 13, 3, verbose=True)
plot_actions(history[-1][0], ants.environment)
plt.show()
print("history")
print(np.array(history))







