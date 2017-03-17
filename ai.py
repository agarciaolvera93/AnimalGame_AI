
import json
from pprint import pprint
import copy


#These are functions that will handle the database reading and updating

def readJSON(file) : # source: http://stackoverflow.com/questions/2835559/parsing-values-from-a-json-file-in-python
	with open(file) as data_file:    
	    data = json.load(data_file)
	return data

def makeJSON(data, file) : #sources: http://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file-in-python , http://stackoverflow.com/questions/2967194/open-in-python-does-not-create-a-file-if-it-doesnt-exist
	with open(file, 'w') as outfile:
	    json.dump(data, outfile, indent = 4)

# Function for finding and linking the two main objects (questions and animals)

def findInArray(object,key,value):
	for i in range(len(object)):
			if object[i][key] == value:
				return object[i]
				

def removeQuestion(object, id):
	for x in range(len(object)):
		if object[x]["id"] == id:
			object.remove(object[x])
			return #its necessary otherwise will throw error, important

def removeAnimals(object, questionId, answer):
	for x in range(len(object)):
		for y in range(len(object[x]["answers"])):
			if (object[x]["answers"][y]["id"] == questionId) and (object[x]["answers"][y]["answer"] == answer):
				object.remove(object[x])
				return removeAnimals(object, questionId, answer) #recursive to avoid problem
	return object			

def resetCutRatio(graph):
	for x in range(len(graph)):
		graph[x]["cutRatio"] = {"yes":0,"total":0}

#This is the variable I created to the algorithm step evaluation, should be in the interval (0,1)
desiredValue = .5

def defineGraphDistances(graph, animals):

	#always reset the cut ratio for each step
	resetCutRatio(graph)

	#we define the cut ratio "yes" and "total" first
	for x in range(len(animals)):
			for y in range(len(animals[x]["answers"])):
				if animals[x]["answers"][y]["answer"] == True:
					#Found answer equals to true, update cutRatio counter
					graph[animals[x]["answers"][y]["id"]]["cutRatio"]["yes"]+=1
				graph[animals[x]["answers"][y]["id"]]["cutRatio"]["total"]+=1
	
	#we define the distance
	for i in range(len(graph)):
		if float(graph[i]["cutRatio"]["total"]) != 0:
			graph[i]["cutRatio"]["ratio"] = float(graph[i]["cutRatio"]["yes"])/ float(graph[i]["cutRatio"]["total"])
		else:
			graph[i]["cutRatio"]["ratio"] = 0	
		graph[i]["cutRatio"]["distance"] = abs(desiredValue-graph[i]["cutRatio"]["ratio"])

#this variable records the user history
userHistory = []
def addCurrentAnswer(qId, answer):
	userHistory.append({"id":qId,"answer":answer})

#compares if all answers are correct
def compareAnswers(animalName, animalDatabase, questionDatabase):
	for x in range(len(animalDatabase)):
		if animalDatabase[x]["name"].lower() == animalName.lower():
			print "Our database contains the animal " + animalDatabase[x]["name"] +", but with different answers:"
			currentAnimal = animalDatabase[x]
			for i in range(len(userHistory)):
				questionId = userHistory[i]["id"]
				for z in range(len(currentAnimal["answers"])):
					if currentAnimal["answers"][z]["id"] == questionId:
						if currentAnimal["answers"][z]["answer"] != userHistory[i]["answer"]:
							currentQuestion = findInArray(questionDatabase,"id", questionId)
							print currentQuestion["question"]
							print "you answered "+ str(userHistory[i]["answer"]) +". The database says "+ str(currentAnimal["answers"][z]["answer"])
							print "Is the database right?"
							keep = True if (list(raw_input())[0] == "y") else False
							if not keep:
								currentAnimal["answers"][z]["answer"] = not currentAnimal["answers"][z]["answer"]	
			print "Updating database..."
			makeJSON({"animals":animalDatabase}, "animals.json")	
			print "Database updated"
			return "found"		
	return "new"						
	#print questionDatabase								





#This function will read the database files and start the game
def init():
	#database reading
	animalsJSON = readJSON("animals.json") #both for writing at the end of algorithm
	questionsJSON = readJSON("questions.json")

	animals = readJSON("animals.json")["animals"]
	questions = readJSON("questions.json")["questions"]

	#we start by making our graph equal to the questions list
	graph = copy.deepcopy(questions)

	print('\n' * 3)
	print("========================================================================================================================")

	print "Welcome to 20 questions game! Answer the questions with (Y) Yes or (N) No and I will figure out what you're thinking of!"
	print('')

	#here the game begins: pick a question closest to .5 ratio	
	while len(animals) > 1:
		defineGraphDistances(graph, animals) #this shouldnt be outside the loop
		newlist = sorted(graph, key=lambda k: k['cutRatio']['distance']) 
		question = newlist[0]
		print(question["question"])
		answer = True if (list(raw_input())[0] == "y") else False
		addCurrentAnswer(question["id"], answer)
		removeAnimals(animals,newlist[0]["id"], not answer) #IMPORTANT: Opposite than answer, removing all items that are not true		
		removeQuestion(newlist,0)
	print('')	
	print "I KNOW WHAT IT IS: "+str(animals[0]["name"])
	correct = raw_input("AM I CORRECT? ")
        if correct == "y" :
        		#might update with previous unanswered questions
        		for x in range(len(userHistory)):
        			alreadyExists = False
        			for y in range(len(animals[0]["answers"])):
        				if userHistory[x]["id"] == animals[0]["answers"][y]["id"]:
        					animals[0]["answers"][y]["answer"] = userHistory[x]["answer"]
        					alreadyExists = True
        					break
        			if not alreadyExists:
        				print "Adding a new answer to the animal"		
        				animals[0]["answers"].append(userHistory[x])
        		findInArray(animalsJSON["animals"], "name", animals[0]["name"])["answers"] = animals[0]["answers"]
        		makeJSON(animalsJSON,"animals.json")

                	print("THANK YOU FOR PLAYING!")
                #this print line allows the profile to be printed if "y"
                #print str(animals[0]["answers"])
        elif correct == "n":
                newA = raw_input("WHAT IS THE ANIMAL YOU WERE THINKING OF? ")
                print ''

                #if theres no such animal in the database, add it
                if compareAnswers(newA, animalsJSON["animals"], questionsJSON["questions"]) == "new":

                	#create a newAnimal with deepcopy to separate pointers
                	newAnimal = copy.deepcopy(animals[0])
                	#set its name as the input from user
                	newAnimal["name"] = newA.capitalize()

                	#copy only the questions that were asked
                	newAnimal["answers"] = copy.deepcopy(userHistory)


                	#create a question to distinguish both animals
                	newQ = raw_input("PLEASE PROVIDE A QUESTION I CAN DISTINGUISH MY GUESS FROM WHAT YOU WERE THINKING OF: ")
                	newQuestionId = len(questionsJSON["questions"])
                	questionsJSON["questions"].append({"id":newQuestionId, "question":newQ})
                	#save the question in questions.json
                	makeJSON(questionsJSON, "questions.json")


                	#add answers to created question by both animals
                	#previous animal
                	previousAnimalName = str(animals[0]["name"])
                	previousAnimalMessage = "Answer for animal " + previousAnimalName + " "
                	previousAnimalAnswer = True if (list(raw_input(previousAnimalMessage))[0] == "y") else False
                	#update the previous item in the memory
                	findInArray(animalsJSON["animals"], "name", previousAnimalName)["answers"].append({"id":newQuestionId, "answer":previousAnimalAnswer})
                	
                	#new animal
                	currentAnimalName = newAnimal["name"]
                	currentAnimalMessage = "Answer for animal " + currentAnimalName + " "
                	currentAnimalAnswer = not previousAnimalAnswer
                	print "Answer for new animal is therefore: " + str(currentAnimalAnswer)
                	newAnimal["answers"].append({"id":newQuestionId, "answer":currentAnimalAnswer})
                    	
                	#append the new animal in the animals list
                	animalsJSON["animals"].append(newAnimal)
                	makeJSON(animalsJSON, "animals.json")


init()



