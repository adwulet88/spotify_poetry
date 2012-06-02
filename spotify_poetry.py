# via spotify developer site
import spotimeta
import string
import time

# tree object
class Tree(object):
	def __init__(self):
		self.children = list()
		self.data = None
		self.parent = None

# Find the songs in aux2 that have input_string at the *beginning* of the song track
# Returns a pruned list of songs that satisfy this criterion
def isl_in_start_of_aux(input_string, aux2):
	N = len(aux2)
	pruned_list = list()
	for k in range(N):
		try:
			title = str(aux2[k]['name']).lower()
		except UnicodeEncodeError: # unfortunately could not figure out how to handle this error in time
			title = ""
		i_find = title.find(input_string)
		if(i_find == 0):
			pruned_list.append(aux2[k])
	return(pruned_list)	

# Find any song within aux_within that has the title input_string_temp
# Note that this returns only the first song that satisfies this criterion
# We could alternatively return a list of all the songs if we wanted to factor in the poet's preferences e.g., artist, genre, etc.
def is_song(input_string_temp, aux_within):
	for aw in aux_within:
		try:
			title = str(aw['name']).lower()
		except UnicodeEncodeError:
			title = ""
		if(input_string_temp == title):
			return(aw)
	return(None)

# Builds a "track title" tree
# Each node corresponds to a track with title matching a portion of the poem
# The descendants of each node sequentially step through the poem's words using track titles
# The root of the tree has no associated value
# isl_list is the list of words in sequential order corresponding to the poem
def build_tree(root, isl_list):
	if(len(isl_list)>0):
		
		# "check_beginning_block"
		# For each word in isl_list, sequentially append words to an input_string and search for tracks using spotimeta.
		# Each search result will be pruned keep only songs that have input_string at the *beginning* of the track title
		# Originally, this portion of the code only performed the search using the first word of isl_list (e.g. isl_list[0]); 
		# however, the results from the search do not necessarily give ALL songs with the first word corresponding to isl_list[0].
		# This resulted in lots of tracks missing on test cases.
		tmp = list()
		for i in range(len(isl_list)): 
			if(i == 0):
				input_string = isl_list[0]
			else:
				input_string = input_string + " " + isl_list[i]
			print(input_string)
			# time is used to avoid hitting API limit of 10 request per second
			time.sleep(.15)
			
			# couldn't figure out quite how to cache things, but i believe it should go here prior to calling search
			aux = spotimeta.search_track(input_string)
			
			aux2 = aux['result']
			# if we can't find anything with input_string, assume that input_string + something_else will also return no results 
			if(len(aux2)>0): 
				tmp.append(isl_in_start_of_aux(input_string, aux2))
			else:
				break
		
		if(len(tmp)>0):
			aux_within = reduce(lambda x,y: x+y, tmp)
		else: 
			aux_within = tmp
			
		current_songs = list()
		current_inputs = list()
		input_string_temp = isl_list[0]
		
		# "check_song_block"
		# For each word in isl_list, sequentially append words to input_string_temp and check for tracks that match exactly
		# to input_string_temp.  If there is a match, we will create a child node out of it using the song track and 
		# all words after the last word of the track.
		for s in range(len(isl_list)): # here, we may alternatively set the range to be range(min(5, len(isl_list))) to speed up
			if(s > 0):
				input_string_temp = input_string_temp + " " + isl_list[s]
			
			aux_song = is_song(input_string_temp, aux_within)
			print(input_string_temp)
			
			if(aux_song != None):
				current_songs.append(aux_song)
				if(s<(len(isl_list)-1)):
					# these inputs will be used to create a child node using all words subsequent to isl_list[s]
					current_inputs.append(isl_list[(s+1):(len(isl_list))])
				else:
					current_inputs.append(list())
		
		# "children block"
		if(len(current_songs) > 0):
			for k in range(len(current_songs)):
				new_node = Tree()
				new_node.data = current_songs[k]
				new_node.parent = root
				new_node.children.append(build_tree(new_node, current_inputs[k]))
				root.children.append(new_node)
	else:
		root.children = None

# Prints out the tree using a depth-first traversal.  Mostly for debugging.
def d_search(root):
	if(root != None):
		if(root.data != None):
			print(root.data['name'])
			print(root.data['href'])
		if(root.children != None):
			for child in root.children:
				d_search(child)

# Given a node, traverse up the tree to find it's parents.
# This will be used to backtrack through a depth-first search for the solution
def traverse_up(root):
	if(root.parent != None):
		print(root.data['name'] + ", " + root.data['href'])
		traverse_up(root.parent)

# Does a depth-first traversal of the tree and looks for a solution.
# Here, solution is defined as when the accumulation variable "count" matches the entire length of the poem.
# ALL possible solutions are printed out in *REVERSE* order with the corresponding URI's listed next to the track titles
def d_search2(root, count, total_n):
	if(root != None):
		if(root.data != None):
			#print(root.data['name'])
			#print(root.data['href'])
			num_words = len(str(root.data['name']).rsplit(" "))
			count = count + num_words
			if(count == total_n):
				print("\nSOLUTION")
				traverse_up(root)
				print("END SOLUTION\n")
		if(root.children != None):
			for child in root.children:
				d_search2(child, count, total_n)				

# "main" block
# input string
input_string = "time frozen whEn I live my Dream no one sleepS when i'm aWake"
#input_string = "friday friday friday friday on my mind friday i'm in love"
#input_string = "all alone in an empty house crying waiting hoping praying time will soon be over where the world comes to an end"

# convert to lower case for matching
isl = input_string.lower()
isl_list = isl.rsplit(" ")
total_n = len(isl_list)
root = Tree()
build_tree(root, isl_list)

# run the search
d_search2(root, 0, total_n)