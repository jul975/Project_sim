import matplotlib.pyplot as plt
import numpy as np

# Parameters
s0 = 100
lam = 1.05
steps = 50
simulations = 5  # Number of random paths to show

if __name__ == "__main__":
        
    plt.figure(figsize=(10, 6))

    for i in range(simulations):
        s = [s0]
        for t in range(steps):
            
            xi_t = np.random.normal(0, 2) 
            
            
            next_s = s[-1] * lam + xi_t
            s.append(next_s)
        
        plt.plot(s, alpha=0.7, label=f"Path {i+1}")

    plt.title(f"Stochastic State Simulation: ")
    plt.xlabel("Time (t)")
    plt.ylabel("Value (S)")
    plt.grid(True, linestyle='--')
    plt.legend()
    plt.show()
