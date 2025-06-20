import matplotlib.pyplot as plt

def draw_chromosome(ax, genes, label, y=0, swap_idxs=None):
    n = len(genes)
    for i, gene in enumerate(genes):
        # Highlight swap positions
        facecolor = '#cde8ff' if swap_idxs and i in swap_idxs else None
        rect = plt.Rectangle((i, y), 1, 1, fill=facecolor is not None, facecolor=facecolor, edgecolor='black')
        ax.add_patch(rect)
        ax.text(i+0.5, y+0.6, f'J{gene+1}', ha='center', va='center', fontsize=12)
    # Bold vertical borders
    ax.plot([0, 0], [y, y+1], color='black', lw=2)
    ax.plot([n, n], [y, y+1], color='black', lw=2)
    ax.text(-1.5, y+0.5, label, ha='right', va='center', fontsize=12, fontweight='bold')
    # Draw swap arrow
    if swap_idxs:
        i, j = swap_idxs
        ax.annotate('', xy=(j+0.5, y+0.2), xytext=(i+0.5, y+0.8),
                    arrowprops=dict(arrowstyle="<->", color='red', lw=2, shrinkA=0, shrinkB=0))

fig, ax = plt.subplots(figsize=(10, 2.5))
parent = [0, 1, 2, 0, 4, 5, 0, 1, 2, 3, 4, 5]  # Example ft06 segment
swap_idxs = (2, 8)
mutant = parent.copy()
mutant[swap_idxs[0]], mutant[swap_idxs[1]] = mutant[swap_idxs[1]], mutant[swap_idxs[0]]

draw_chromosome(ax, parent, "Before swap", y=1, swap_idxs=swap_idxs)
draw_chromosome(ax, mutant, "After swap", y=0, swap_idxs=swap_idxs)

ax.set_xlim(-2, len(parent))
ax.set_ylim(-0.5, 2.5)
ax.axis('off')
plt.title("Example of Swap Mutation\n(job-based permutation encoding, ft06 segment)", pad=30)
plt.tight_layout()
plt.show()
