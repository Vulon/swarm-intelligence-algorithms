from Particle_swarm import *
from environment import *

def test_Particle_Swarm():
    instances = 16
    actions = 37
    epochs = 20
    omega = 0.5
    phi_p = 0.5
    phi_g = 0.5
    p = ParticleSwarm()
    actions_list, value = p.start(instances, actions, epochs, omega, phi_p, phi_g, None, verbose=False)
    print("Value", value)
    print("Actions: ", actions_list)
    plt.figure("Actions path")
    draw_map(p.env_map, p.start_point, p.finish_point)
    plot_actions(actions_list, p.environment)
    plt.show()

