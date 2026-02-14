# first sketch of design to make concepts clear



class Engine:
    def __init__(self, seed, config):
        self.rng = np.random.default_rng(seed)
        self.tick = 0
        self.state = self.initialize_state(config)

    def step(self):
        next_state = self.compute_next_state(self.state)
        self.state = next_state
        self.tick += 1

    def run(self, steps):
        for _ in range(steps):
            self.step()