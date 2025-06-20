import matplotlib.pyplot as plt

def draw_chromosome(ax, genes, label, y=0):
    n = len(genes)
    for i, gene in enumerate(genes):
        ax.add_patch(plt.Rectangle((i, y), 1, 1, fill=None, edgecolor='black'))
        ax.text(i+0.5, y+0.6, f'J{gene+1}', ha='center', va='center', fontsize=12)
    # Draw bold left and right borders
    ax.plot([0, 0], [y, y+1], color='black', lw=2)
    ax.plot([n, n], [y, y+1], color='black', lw=2)
    ax.text(-1.5, y+0.5, label, ha='right', va='center', fontsize=12, fontweight='bold')

fig, ax = plt.subplots(figsize=(11, 3))
# Example: first 12 genes for ft06
parent1 = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
parent2 = [5, 3, 2, 0, 4, 1, 5, 2, 3, 0, 1, 4]
child   = [0, 1, 2, 0, 4, 5, 5, 2, 3, 3, 1, 4]  # example PBX output

draw_chromosome(ax, parent1, "Parent 1", y=2)
draw_chromosome(ax, parent2, "Parent 2", y=1)
draw_chromosome(ax, child,   "Child",    y=0)

ax.set_xlim(-2, len(parent1))
ax.set_ylim(-0.7, 3.5)
ax.axis('off')
plt.title("Example of Position-Based Crossover\n(job-based permutation encoding, ft06 segment)")
plt.tight_layout()
plt.show()
