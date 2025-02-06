import matplotlib.pyplot as plt


write2file = True

# Activate the XKCD sketch style
plt.xkcd()

fig, ax = plt.subplots(figsize=(8, 4))

# Set axis limits: lead time from 1 to 5, skill from 0 to 1
ax.set_xlim(1, 10)
ax.set_ylim(0, 1)

# Label the axes
ax.set_xlabel("Lead time (days)")
ax.set_ylabel("Forecast skill")

# Choose some sensible ticks
ax.set_xticks(range(1, 11))           # 1, 2, 3, 4, 5
#ax.set_yticks([i / 10 for i in range(11)])  # 0, 0.1, 0.2, ... 1.0
ax.set_yticks([0.0,0.2,0.4,0.6,0.8,1.0])
# Draw a straight arrow from (1, 0.7) to (5, 0)
ax.annotate(
    '',
    xy=(6, 0),         # arrow head
    xytext=(1, 0.7),   # arrow tail
    arrowprops=dict(
        arrowstyle="->, head_length=0.75, head_width=0.75",
        lw=4,
        color='tab:blue'
    )
)

"""
ax.annotate(
    '',
    xy=(9, 0),         # arrow head
    xytext=(1, 0.9),   # arrow tail 
    arrowprops=dict(
	arrowstyle="->, head_length=0.75, head_width=0.75",
	lw=4,
	color='tab:red'
    )
)
"""

x_arrow_label = 3.2
y_arrow_label = 0.3
ax.text(
    x_arrow_label, 
    y_arrow_label, 
    'grid-scale', 
    color='tab:blue', 
    fontsize=20, 
    ha='right'   # center-aligned horizontally
    # You could also set va='center' if you want to center vertically
)

"""
x_arrow_label = 4
y_arrow_label = 0.61
ax.text(
    x_arrow_label,
    y_arrow_label,
    'spatially-aggregated',
    color='tab:red',
    fontsize=20,
    ha='left'   # center-aligned horizontally                                                                                                                  
    # You could also set va='center' if you want to center vertically                                                                                           
)
"""
#ax.set_title("Prediction Skill vs. Lead Time")

plt.tight_layout()

if write2file: plt.savefig('/nird/home/edu061/cf-forsikring/fig/paper/presentation_figure.pdf')
plt.show()
