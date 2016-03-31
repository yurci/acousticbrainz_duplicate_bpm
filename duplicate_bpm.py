
import json
import os, sys
import pandas as pd #http://pandas.pydata.org/

inputDir='ab-duplicates1000-2016-03-02/'
fileCount = 0
fname_MBID = ""
fname_List = [] # List of file names
path_Array = [] # List of full paths of the duplicates of a given song
ultimate_Bpm = [[0],[0],[0],[0],[0],[0]] # MBID, #1 Most Used Key, Rate of 1st, #2 Most Used Key, Rate of 2nd,Total # Duplicates



def json_Read(path_Array):
	song_Bpm = "" 
	bpm_Array = [[],[]]
	

	for n in path_Array: # For each duplicate

		fDict = json.load(open((str(n)))) #Read the data

		song_Bpm = round(fDict['rhythm']['bpm']) # Take the bpm

		#---- Filll the bpm_Array with duplicates bpm values(First Column) and if there is same bpm value exists rise the count (Second Cloumn) ----#

		#If bpm value is already in the list
		try:
			index = bpm_Array[0].index(song_Bpm) # Check if the current bpm value is already in the bpm_Array
			bpm_Array[1][index] = bpm_Array[1][index]+1 # If yes rise the count

		# If bpm value is not in the bpm_Array add it
		except:
			bpm_Array[0].append(song_Bpm) # Add bpm value to the bpm_Array
			index = bpm_Array[0].index(song_Bpm) # Detect the index  
			bpm_Array[1].append(1)	# Rise the count column

	
	#---- Calculate Percentages -----#
	total_Songs = sum(bpm_Array[1]) #Total Number of songs
	most_Bpm_Index = bpm_Array[1].index(max(bpm_Array[1])) # Index of Most Used Bpm
	rate = float(bpm_Array[1][most_Bpm_Index])/total_Songs*100 # Percentage of the most used bpm 


	#----- Fill a global array in order to write it as csv output ------#

	#First the Most Used Bpm
	ultimate_Bpm[0].append(fname_MBID) # First column of the ultmate_Bpm will be our MBID which is same for all instances in the current path_Array
	ultimate_Bpm[1].append(bpm_Array[0][most_Bpm_Index]) # Second column will be the value of most used bpm
	ultimate_Bpm[2].append(rate)                         # Third column will be the percentage of the most used bpm

	#Second most used Bpm

	#To do it so remove the previous maximum
	bpm_Array[0].remove(bpm_Array[0][most_Bpm_Index]) # Remove the Max bpm value from the array
	bpm_Array[1].remove(bpm_Array[1][most_Bpm_Index]) # Remove the Max bpm Count from the array


	try:
		most_Bpm_Index = bpm_Array[1].index(max(bpm_Array[1])) # Index of Second Most Used Key
		rate = float(bpm_Array[1][most_Bpm_Index])/total_Songs*100 # Rate of the Second 

		ultimate_Bpm[3].append(bpm_Array[0][most_Bpm_Index]) # Add second most used bpm to the fourth column
		ultimate_Bpm[4].append(rate)						 # Add the percentage to the fifth column

	# If there is no second bpm (Where every duplicate has same value)
	except:
		ultimate_Bpm[3].append("Nan") # No second exist
		ultimate_Bpm[4].append("Nan") # No second exist


	ultimate_Bpm[5].append(total_Songs)	# Last column will be the total number of songs


	#---- Check if the First most used bpm and Second most used bpm are close (in +2,- 2 range)?  -----#
	i=0 #Counter

	for bpm in ultimate_Bpm[1] : # For every most used bpm value

		if ultimate_Bpm[3][i]=="Nan": # If no second exist pass
			pass

		# If first and second most used bpms are in range of difference by -2 or +2 merge them
		elif ((ultimate_Bpm[3][i]-1 == bpm) or (ultimate_Bpm[3][i]-2 == bpm) or (ultimate_Bpm[3][i]+1 == bpm) or (ultimate_Bpm[3][i]+2==bpm)) :

			ultimate_Bpm[2][i]=ultimate_Bpm[2][i]+ultimate_Bpm[4][i] # Merge their percentages
			ultimate_Bpm[4][i] = "Nan"								 # Right now we don't have any second left
			ultimate_Bpm[3][i] = "Nan"								 # Assign Nan to the second's values
		i=i+1




	print (fname_MBID) + ' Processed!'
	#	print n
	

def file_trav(inputDir):
	#Traverse over given directory and detect json files inside
	for path,dname,fnames in os.walk(inputDir):
		for fname in fnames:


			if '.json' in fname.lower():

				global fileCount, path_Array
				fileCount += 1
				global fname_MBID

				fname_MBID = fname[0:36] #first 36 characters of fname, without duplicate number
				fname_List.append(fname_MBID)

				#--------- Detection of Duplicates From Same Song Only ----------# 

				if (len(path_Array) >= 3 and (fname_List [-1] == fname_List[-2])): # Check if the New File added to the fname_List has same MBID

					path_Array.append(str(path) + "/" + str(fname)) # Adds the duplicate with same MBID to the path array


				elif (len(path_Array) >= 3 and (fname_List [-1] != fname_List [-2])): # If the new File is not with same MBID path_Array is full with All the duplicates for particular song
					#Send path_Array to the json_Read
					json_Read(path_Array)

					#Reset path_Array and assign the first duplicate on cue to the path_Array
					path_Array = []
					path_Array.append(str(path) + "/" + str(fname))

				elif (len(path_Array) <= 2):    # First two duplicates added to path_Array here
					path_Array.append(str(path) + "/" + str(fname))
					#print path_Array #two and three elements

file_trav(inputDir) # Main Function

df = pd.DataFrame() #Define a dataframe in order to write arrays as csv 

# Fill the data frame
df['MBID'] = ultimate_Bpm[0]
df['#1 Most Used Bpm'] = ultimate_Bpm[1]
df['Percentage of 1st'] = ultimate_Bpm[2]
df['#2 Most Used Bpm'] = ultimate_Bpm[3]
df['Percentage of 2nd'] = ultimate_Bpm[4]
df['Total # Duplicates'] = ultimate_Bpm[5]

df = df.ix[1:] # Delete the First Row as they were 0's

df.to_csv('Bpm.csv')

print str(fileCount) + " -->  File Count"