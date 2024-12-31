import numpy as np
import matplotlib.pyplot as plt

def simulate_crash():
    house_edge = 0.08
    instant_crash_prob = 0.01
    
    r = np.random.random()
    
    if r < instant_crash_prob:
        return 1.00
    else:
        multiplier = (0.95 / (1 - house_edge)) / (r - instant_crash_prob + 0.02)
        return max(1.00, multiplier)

def simulate_betting_strategy(starting_balance=100, bet_amount=1, target_multiplier=2.00):
    balance = starting_balance
    num_games = 1000
    
    for _ in range(num_games):
        if balance < bet_amount:
            break
            
        crash_point = simulate_crash()
        balance -= bet_amount  # Place bet
        
        # If we successfully cashed out
        if crash_point >= target_multiplier:
            balance += bet_amount * target_multiplier
            
    return balance

def analyze_multiplier_distribution(num_games=10000):
    multipliers = []
    print("Simulating crash multipliers...")
    
    for i in range(num_games):
        multiplier = simulate_crash()
        multipliers.append(multiplier)
    
    # Create a new figure for multiplier distribution
    plt.figure(figsize=(12, 6))
    plt.hist(multipliers, bins=50, edgecolor='black')
    plt.title(f'Distribution of Crash Multipliers ({num_games:,} games)')
    plt.xlabel('Multiplier (x)')
    plt.ylabel('Frequency')
    
    # Calculate and display statistics
    avg_multiplier = np.mean(multipliers)
    median_multiplier = np.median(multipliers)
    std_dev = np.std(multipliers)
    
    stats_text = f'Statistics:\n' \
                 f'Average Multiplier: {avg_multiplier:.2f}x\n' \
                 f'Median Multiplier: {median_multiplier:.2f}x\n' \
                 f'Standard Deviation: {std_dev:.2f}\n' \
                 f'Instant Crashes: {(sum(1 for x in multipliers if x == 1.00) / num_games * 100):.1f}%'
    
    plt.text(0.95, 0.95, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.show()
    
    # Print percentile distribution
    print("\nMultiplier Percentile Distribution:")
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    for p in percentiles:
        value = np.percentile(multipliers, p)
        print(f"{p}th percentile: {value:.2f}x")

# Run multiple simulations
num_simulations = 100000
all_results = []

print("Running simulations...")
for i in range(num_simulations):
    if i % 10000 == 0:
        print(f"Completed {i:,} simulations...")
    final_balance = simulate_betting_strategy()
    all_results.append(final_balance)
print("Simulations complete!")

# Calculate statistics
average_final = np.mean(all_results)
median_final = np.median(all_results)
profitable_runs = (sum(1 for x in all_results if x > 100) / num_simulations) * 100
std_dev = np.std(all_results)

# Plot results
plt.figure(figsize=(12, 6))
plt.hist(all_results, bins=50, edgecolor='black')
plt.axvline(x=100, color='r', linestyle='--', label='Starting Balance')
plt.title(f'Distribution of Final Balances ({num_simulations:,} simulations)\nBetting $1 with 2x Target')
plt.xlabel('Final Balance ($)')
plt.ylabel('Frequency')

# Add statistics text box
stats_text = f'Statistics:\n' \
             f'Average Final Balance: ${average_final:.2f}\n' \
             f'Median Final Balance: ${median_final:.2f}\n' \
             f'Standard Deviation: ${std_dev:.2f}\n' \
             f'Profitable Runs: {profitable_runs:.1f}%'

plt.text(0.95, 0.95, stats_text,
         transform=plt.gca().transAxes,
         verticalalignment='top',
         horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.legend()
plt.show()

# Print detailed statistics
print(f"\nDetailed Statistics:")
print(f"Starting Balance: $100.00")
print(f"Average Final Balance: ${average_final:.2f}")
print(f"Median Final Balance: ${median_final:.2f}")
print(f"Standard Deviation: ${std_dev:.2f}")
print(f"Profitable Runs: {profitable_runs:.1f}%")
print(f"Best Result: ${max(all_results):.2f}")
print(f"Worst Result: ${min(all_results):.2f}")

# Additional percentile statistics
percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
print("\nPercentile Distribution:")
for p in percentiles:
    value = np.percentile(all_results, p)
    print(f"{p}th percentile: ${value:.2f}") 

# Add this at the bottom of the file to run the multiplier analysis
if __name__ == "__main__":
    analyze_multiplier_distribution(10000) 