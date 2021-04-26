# Importing the matplotlb.pyplot
import matplotlib.pyplot as plt
import os


def draw_gantt_plot(data:dict):
	# Declaring a figure "gnt"
	fig, gnt = plt.subplots()
	cell_height = 10
	# Setting Y-axis limits
	gnt.set_ylim(0, len(data)*cell_height + cell_height)
	length = 0
	for i in range(1, len(data) + 1):
		if data[i][-1][1] + data[i][-1][0] > length:
			length = data[i][-1][1] + data[i][-1][0]
	length = int(length)
	# Setting X-axis limits
	gnt.set_xlim(0, length)

	# Setting labels for x-axis and y-axis
	gnt.set_xlabel('seconds since start')
	gnt.set_ylabel('Processor')

	# Setting ticks on y-axis
	yticks = [i*cell_height for i in range(1, len(data) + 1)]
	yticks_labels = [str(i) for i in range(1, len(data) + 1)]
	gnt.set_yticks(yticks)
	gnt.set_yticklabels(yticks_labels)
	# Setting ticks on x-axis
	alist = []
	blist = []
	for i in range(length):
		if i % 5 == 0:
			blist.append(str(i))
		else:
			blist.append('')
		alist.append(i)

	gnt.set_xticks(alist)
	# Labelling tickes of y-axis
	gnt.set_xticklabels(blist)

	# Setting graph attribute
	gnt.grid(True)

	for i in range(1, len(data) + 1):
		# Declaring a bar in schedule
		gnt.broken_barh(data[i], (10*i, 10), facecolors=('tab:orange'))

	# # Declaring multiple bars in at same level and same width
	# gnt.broken_barh([(110, 10), (150, 10)], (10, 9),
	# 				facecolors='tab:blue')
	#
	# gnt.broken_barh([(10, 50), (100, 20), (130, 10)], (20, 9),
	# 				facecolors=('tab:red'))
	#plt.savefig("gantt1.png")
	max = 0
	with os.scandir('.') as entries:
		for entry in entries:
			if entry.name.startswith("gantt") and entry.name.endswith(".png"):
				number = int(entry.name[5:-4])
				if number > max:
					max = number
	filename = f"gantt{max+1}.png"
	plt.savefig(filename)
	return filename