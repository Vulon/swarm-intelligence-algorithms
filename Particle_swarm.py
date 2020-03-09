from environment import *
import random
import numpy as np



def random_vector(size, max_value):
    return np.array([random.random() * max_value for i in range(size)])

class ParticleSwarm:
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

    def start(self, instance_count : int, particle_state_vector_size : int, epochs : int, omega_constant : float, phi_p : float, phi_g : float, particle_styles : list, base_movement_actions_size = 5, verbose=False):
        plt.figure("Particle Swarm")
        if particle_styles is None:
            particle_styles = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(instance_count)]

        from math import sqrt
        subplots_x = int(sqrt(epochs))
        subplots_y = int(epochs / subplots_x) + int(epochs % subplots_x != 0)

        self.particles = []
        for i in range(instance_count):
            p = Instance(self.environment)
            self.particles.append(p)

        global_minimum = None

        for particle in self.particles:
            r = random_vector(particle_state_vector_size, base_movement_actions_size)
            particle.set_data("actions_vector", r)
            particle.execute_actions([int(value) for value in r])
            if global_minimum is None or global_minimum[1] > particle.get_loss():
                global_minimum = (np.array([int(value) for value in r]), particle.get_loss())
            particle.set_data("speed", random_vector(particle_state_vector_size, 1))
            particle.set_data("best_vector", np.array([int(value) for value in r]))
            particle.set_data("best_loss", particle.get_loss())

        if verbose:
            print("Swarm initialized!!!")
        for e in range(epochs):
            if verbose:
                print("Epoch ", e )
            if verbose:
                plt.subplot(subplots_x, subplots_y, e + 1)
                plt.title(str(e))
                plt.axis([-4, self.env_map.x_size, -4, self.env_map.y_size])
                draw_map(self.env_map, self.start_point, self.finish_point)


            for p_index, particle in enumerate(self.particles):
                particle.reset_position()
                rp = random_vector(particle_state_vector_size, base_movement_actions_size)
                rg = random_vector(particle_state_vector_size, base_movement_actions_size)
                new_speed = particle.get_data("speed") * omega_constant \
                            + rp * phi_p * (particle.get_data("best_vector") - particle.get_data("actions_vector")) \
                            + rg * phi_g * (global_minimum[0] - particle.get_data("actions_vector"))
                new_actions = particle.get_data("actions_vector") + new_speed
                new_actions[new_actions >= base_movement_actions_size] = base_movement_actions_size - 1
                new_actions[new_actions < 0] = 0
                new_actions = np.array( [int(value) for value in new_actions] )
                env_list = particle.execute_actions(new_actions)
                if verbose:
                    print("Particle new actions: ", new_actions)
                    print("Particle loss", particle.get_loss())
                if particle.get_loss() < global_minimum[1]:

                    global_minimum = (new_actions, particle.get_loss(), particle.env_data["x"], particle.env_data["y"])
                if particle.get_loss() < particle.get_data("best_loss"):
                    particle.set_data("best_loss", particle.get_loss())
                    particle.set_data("best_vector", new_actions)
                particle.set_data("actions_vector", new_actions)
                x_list = []
                y_list = []
                for env_info in env_list:
                    x_list.append(env_info["x"] + p_index * 0.001)
                    y_list.append(env_info["y"] + p_index * 0.001)
                if verbose:
                    plt.plot(x_list, y_list, particle_styles[p_index])


        if verbose:
            dictionary = {
                0: "0",
                1: "up",
                2: "down",
                3: "right",
                4: "left"
            }
            translated = [dictionary[a] for a in global_minimum[0]]
            print("Translated actions: ", translated)
            print("Global minimum", global_minimum)
            plt.show()
        return global_minimum[0],  global_minimum[1]






