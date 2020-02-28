# PA6, CS124, Stanford, Winter 2019
# v.1.0.3
# Original Python code by Ignacio Cases (@cases)
######################################################################
import movielens

import numpy as np
import re
from collections import Counter


# noinspection PyMethodMayBeStatic
class Chatbot:
	"""Simple class to implement the chatbot for PA 6."""

	def __init__(self, creative=False):
		# The chatbot's default name is `moviebot`. Give your chatbot a new name.
		self.name = 'moviebot'

		self.creative = creative

		# This matrix has the following shape: num_movies x num_users
		# The values stored in each row i and column j is the rating for
		# movie i by user j
		self.titles, ratings = movielens.ratings()
		self.sentiment = movielens.sentiment()
		self.articles = ["the", "a", "an", "The", "A", "An"]
		self.movieToYear = {} # movie title -> year
		self.recommends = {} # score -> movie index   (only k entries)
		self.userSentiment = {} # movie index -> sentiment
		self.count = 0 # keep track of number of movies user has given

		#############################################################################
		# TODO: Binarize the movie ratings matrix.                                  #
		#############################################################################

		# Binarize the movie ratings before storing the binarized matrix.
		# print(ratings[0])
		self.ratings = self.binarize(ratings, threshold=2.5)
		# print(self.ratings[0])

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################

	#############################################################################
	# 1. WARM UP REPL                                                           #
	#############################################################################

	def greeting(self):
		"""Return a message that the chatbot uses to greet the user."""
		#############################################################################
		# TODO: Write a short greeting message                                      #
		#############################################################################

		greeting_message =  "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen. I need 5 preferences recommendations"

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return greeting_message

	def goodbye(self):
		"""Return a message that the chatbot uses to bid farewell to the user."""
		#############################################################################
		# TODO: Write a short farewell message                                      #
		#############################################################################

		goodbye_message = "Thank you for hanging out with me! Stay in touch! Goodbye!"

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return goodbye_message

	###############################################################################
	# 2. Modules 2 and 3: extraction and transformation                           #
	###############################################################################

	def process(self, line):
		"""Process a line of input from the REPL and generate a response.

		This is the method that is called by the REPL loop directly with user input.

		You should delegate most of the work of processing the user's input to
		the helper functions you write later in this class.

		Takes the input string from the REPL and call delegated functions that
		  1) extract the relevant information, and
		  2) transform the information into a response to the user.

		Example:
		  resp = chatbot.process('I loved "The Notebook" so much!!')
		  print(resp) // prints 'So you loved "The Notebook", huh?'

		:param line: a user-supplied line of text
		:returns: a string containing the chatbot's response to the user input
		"""
		#############################################################################
		# TODO: Implement the extraction and transformation in this method,         #
		# possibly calling other functions. Although modular code is not graded,    #
		# it is highly recommended.                                                 #
		#############################################################################
		if self.creative:
			response = "I processed {} in creative mode!!".format(line)


		else:
			#STARTER SECTION

			response = "I processed {} in starter mode!!".format(line) #Inserts line for {}


			extracted_movies = self.extract_titles(line)
			if len(extracted_movies) == 0:
				response = "Sorry, I don't understand. Tell me about a movie that you have seen."
				return response

			if len(extracted_movies) > 1:
				response = "Please tell me about one movie at a time. Go ahead."
				return response

			sentiment_val = self.extract_sentiment(line)
			extracted_movie = extracted_movies[0]

			found_movies = []
			for m in extracted_movies:
				title = self.buildUserDict(m)
				found_movies.extend(self.find_movies_by_title(title))

			for m in found_movies:
				self.userSentiment[m] = sentiment_val

			if len(found_movies) == 0:
				response = "I'm sorry, I haven't heard about that movie before. Please give me another movie."
				return

			sentiment = self.extract_sentiment(line)
			if sentiment == 0:
				return "Hmmm, I couldn't tell if you liked \"" + extracted_movie + "\". Can you tell me more about " + extracted_movie + "?"
			elif sentiment == 1:
				response = "Nice, I'm glad you liked \"" + extracted_movie + "\"! It sounds like an awesome movie! " + "I'll definitely check it out some time."
			elif sentiment == -1:
				response = "Ugh, I'm sorry you didn't like \"" + extracted_movie + "\". It sounds like a terrible movie! " + "I'll make sure to avoid that one, for sure."


			self.count += 1
			self.movieToYear = {}

			print("extracted movies: ", extracted_movies)
			print("found movies: ",found_movies)
			print("sentiment: ", sentiment_val)

			response += " Thanks for sharing that with me! Please give me another movie."

			if self.count == 6:
				user_matrix = self.createUserMatrix()
				recommendations = self.recommend(user_matrix, self.ratings, 5, creative=False)
				print(response)
				response = "That's enough for me to make a recommendation. I suggest you watch " + self.titles[recommendations[0]][0] + ". Would you like to hear another recommendation? (Or enter :quit if you're done.)"
				print("recommendations", recommendations)
				self.count = 0

			



			# user_matrix = np.zeros((self.ratings.shape[0], 1))
			# print(user_matrix)
			# print(user_matrix.shape)

			'''
			TESTING RECOMMEND
			+1 : 8514, 7953, 6979, 7890

			I like "Wonder Woman (2009)"
			I like "The Dark Knight Rises (2012)"
			I like "The Incredible Hulk (2008)"
			I like "The Avengers (2012)"

			-1: 7369, 8726
			I don't like "Saw VI (2009)"
			I don't like "Dumb and Dumber To (2014)"
			'''

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return response

	@staticmethod
	def preprocess(text):
		"""Do any general-purpose pre-processing before extracting information from a line of text.

		Given an input line of text, this method should do any general pre-processing and return the
		pre-processed string. The outputs of this method will be used as inputs (instead of the original
		raw text) for the extract_titles, extract_sentiment, and extract_sentiment_for_movies methods.

		Note that this method is intentially made static, as you shouldn't need to use any
		attributes of Chatbot in this method.

		:param text: a user-supplied line of text
		:returns: the same text, pre-processed
		"""
		#############################################################################
		# TODO: Preprocess the text into a desired format.                          #
		# NOTE: This method is completely OPTIONAL. If it is not helpful to your    #
		# implementation to do any generic preprocessing, feel free to leave this   #
		# method unmodified.                                                        #
		#############################################################################

		# Split sentence by word and convert to list
		# Lowercase all letters/words
		# normed_line = ""
		# for word in text.split():
		# 	word = word.lower()
		# 	normed_line += word + " "
		# return normed_line.strip()
		return text



		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################

		return text

	def extract_titles(self, preprocessed_input):
		"""Extract potential movie titles from a line of pre-processed text.

		Given an input text which has been pre-processed with preprocess(),
		this method should return a list of movie titles that are potentially in the text.

		- If there are no movie titles in the text, return an empty list.
		- If there is exactly one movie title in the text, return a list
		containing just that one movie title.
		- If there are multiple movie titles in the text, return a list
		of all movie titles you've extracted from the text.

		Example:
		  potential_titles = chatbot.extract_titles(chatbot.preprocess('I liked "The Notebook" a lot.'))
		  print(potential_titles) // prints ["The Notebook"]

		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: list of movie titles that are potentially in the text
		"""
		patterns = [
			# '"([\w ]+\'\w?)"' ,
			# '"([\w ]+)"' ,
			# '"([\w]+[\'][\w]+)"'
			'"([^"]*)"'
		]

		pattern = '"([^"]*)"'

		matches = re.findall(pattern, preprocessed_input)
		for m in matches:
			self.buildUserDict(m)
		return matches


	#Takes a found movie given by user and adds to movie->year dict.
	#If year is not given, year = -1
	def buildUserDict(self, input_movie):
		year = self.checkYearHelper(input_movie)
		if year != None:
			input_movie = input_movie.replace(year, '')  #remove year
			input_movie = input_movie.strip()
		input_movie = self.fixedTitles(input_movie)  #Rearranges first article word
		if year != None:
			self.movieToYear[input_movie] = year
		else:
			self.movieToYear[input_movie] = -1
		return input_movie


	#Checks if a year is given by user. Returns year
	def checkYearHelper(self, input_movie):
		year = None
		p = '(\([0-9]{4}\))'
		c = re.search(p, input_movie)
		if c != None:
			year = c.group(1)
		return year

	# Removes first article word in titles in database
	def fixedTitles(self, title):
		words = title.split(' ', 1)
		if words[0] in self.articles:
			title = words[1] + ", " + words[0]
		return title


	def find_movies_by_title(self, title):
		""" Given a movie title, return a list of indices of matching movies.

		- If no movies are found that match the given title, return an empty list.
		- If multiple movies are found that match the given title, return a list
		containing all of the indices of these matching movies.
		- If exactly one movie is found that matches the given title, return a list
		that contains the index of that matching movie.

		Example:
		  ids = chatbot.find_movies_by_title('Titanic')
		  print(ids) // prints [1359, 1953]

		:param title: a string containing a movie title
		:returns: a list of indices of matching movies
		"""
		movies = []
		for i,t in enumerate(self.titles):
			t_title = t[0]
			t_year = self.checkYearHelper(t_title)
			if t_year != None:
				t_title = t_title.replace(t_year, '')  #remove year
				t_title = t_title.strip()
			new_t = self.fixedTitles(t_title)
			if title == new_t:
				if self.movieToYear[title] == t_year:
					movies.append(i)
				elif self.movieToYear[title] == -1:
					movies.append(i)
		return movies




	def removeTitleHelper(self, input_text):
		patterns = '(".*")'
		input_text = re.sub(patterns, '', input_text)
		return input_text

	def removePunctuationHelper(self, input_text):
		patterns = '([\.,!\?;])'
		input_text = re.sub(patterns, '', input_text)
		return input_text

	def extract_sentiment(self, preprocessed_input):
		"""Extract a sentiment rating from a line of pre-processed text.
		You should return -1 if the sentiment of the text is negative, 0 if the
		sentiment of the text is neutral (no sentiment detected), or +1 if the
		sentiment of the text is positive.
		As an optional creative extension, return -2 if the sentiment of the text
		is super negative and +2 if the sentiment of the text is super positive.
		Example:
		  sentiment = chatbot.extract_sentiment(chatbot.preprocess('I liked "The Titanic"'))
		  print(sentiment) // prints 1
		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: a numerical value for the sentiment of the text
		"""
		negationFlag = False
		posCount = 0
		negCount = 0

		# remove titles from input
		input_text = self.removeTitleHelper(preprocessed_input)
		input_text = self.removePunctuationHelper(input_text)

		# count pos and neg words in the input
		input_list = input_text.split()
		for word in input_list:
			value = self.checkLexicon(word)
			if value == 'pos':
				posCount += 1
			elif value == 'neg':
				negCount += 1
			"""print("word", word)
			print("pos count: ", posCount)
			print("neg count: ", negCount)
			print()
		print("===")"""
		
		# modify pos and neg counts depending on negation words
		negated_list = self.checkNegation(input_text)
		for negated_word in negated_list:
			value = self.checkLexicon(negated_word)
			# print("negated word: ", negated_word)
			# print("value: ", value)
			if value == 'pos':
				posCount -= 1
				negCount += 1
			elif value == 'neg':
				negCount -= 1
				posCount += 1
			# print("pos count: ", posCount)
			# print("neg count: ", negCount)

		# print("final pos count: ", posCount)
		# print("final neg count: ", negCount)
		if posCount > negCount:
			return 1
		elif negCount > posCount:
			return -1
		else:
			return 0

	def checkNegation(self, input_text):
		""" 
		Returns a list of words that would be negated and whose sentiments should
		be reversed.
		"""
		patterns = [
			'n\'t (.*) ',
			'n\'t really (.*) ',
			'not (.*) ',
			'not really (.*) ',
			'never (.*) '
		]

		to_negate = []
		for p in patterns:
			matches = re.findall(p, input_text)
			for match in matches:
				print(match)
				to_negate.append(match)

		return to_negate


	def checkLexicon(self, word):
		""" 
		Checks if the sentiment lexicon contains the word (or other forms of the word, i.e. singular,
		present tense, etc.) and 
		- returns 'pos' for positive words
		- returns 'neg' for negative words
		- returns 'none' for words not in the sentiment lexicon
		"""
		forms = []
		value = 'none'
		forms.append(word)

		# check last letter
		if word[-1:] == "s" or word[-1:] == "d":
			forms.append(word[0:len(word)-1]) # likes -> like, liked -> like

		# check last 2 letters
		if word[-2:] == "ed":
			forms.append(word[0:len(word)-2]) # enjoyed -> enjoy

		# check last 3 letters
		if word[-3:] == "ing":
			forms.append(word[0:len(word)-3]) # enjoying -> enjoy

		forms.append(word + "s") # like -> likes
		forms.append(word + "d") # like -> liked
		forms.append(word + "ed") # enjoy -> enjoyed

		for form in forms:
			if form in self.sentiment:
				value = self.sentiment[form]

		return value

	def extract_sentiment_for_movies(self, preprocessed_input):
		"""Creative Feature: Extracts the sentiments from a line of pre-processed text
		that may contain multiple movies. Note that the sentiments toward
		the movies may be different.

		You should use the same sentiment values as extract_sentiment, described above.
		Hint: feel free to call previously defined functions to implement this.

		Example:
		  sentiments = chatbot.extract_sentiment_for_text(
						   chatbot.preprocess('I liked both "Titanic (1997)" and "Ex Machina".'))
		  print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

		:param preprocessed_input: a user-supplied line of text that has been pre-processed with preprocess()
		:returns: a list of tuples, where the first item in the tuple is a movie title,
		  and the second is the sentiment in the text toward that movie
		"""
		pass

	def find_movies_closest_to_title(self, title, max_distance=3):
		"""Creative Feature: Given a potentially misspelled movie title,
		return a list of the movies in the dataset whose titles have the least edit distance
		from the provided title, and with edit distance at most max_distance.

		- If no movies have titles within max_distance of the provided title, return an empty list.
		- Otherwise, if there's a movie closer in edit distance to the given title
		  than all other movies, return a 1-element list containing its index.
		- If there is a tie for closest movie, return a list with the indices of all movies
		  tying for minimum edit distance to the given movie.

		Example:
		  chatbot.find_movies_closest_to_title("Sleeping Beaty") # should return [1656]

		:param title: a potentially misspelled title
		:param max_distance: the maximum edit distance to search for
		:returns: a list of movie indices with titles closest to the given title and within edit distance max_distance
		"""

		pass

	def disambiguate(self, clarification, candidates):
		"""Creative Feature: Given a list of movies that the user could be talking about
		(represented as indices), and a string given by the user as clarification
		(eg. in response to your bot saying "Which movie did you mean: Titanic (1953)
		or Titanic (1997)?"), use the clarification to narrow down the list and return
		a smaller list of candidates (hopefully just 1!)

		- If the clarification uniquely identifies one of the movies, this should return a 1-element
		list with the index of that movie.
		- If it's unclear which movie the user means by the clarification, it should return a list
		with the indices it could be referring to (to continue the disambiguation dialogue).

		Example:
		  chatbot.disambiguate("1997", [1359, 2716]) should return [1359]

		:param clarification: user input intended to disambiguate between the given movies
		:param candidates: a list of movie indices
		:returns: a list of indices corresponding to the movies identified by the clarification
		"""
		pass

	#############################################################################
	# 3. Movie Recommendation helper functions                                  #
	#############################################################################

	@staticmethod
	def binarize(ratings, threshold=2.5):
		"""Return a binarized version of the given matrix.

		To binarize a matrix, replace all entries above the threshold with 1.
		and replace all entries at or below the threshold with a -1.

		Entries whose values are 0 represent null values and should remain at 0.

		Note that this method is intentionally made static, as you shouldn't use any
		attributes of Chatbot like self.ratings in this method.

		:param ratings: a (num_movies x num_users) matrix of user ratings, from 0.5 to 5.0
		:param threshold: Numerical rating above which ratings are considered positive

		:returns: a binarized version of the movie-rating matrix
		"""
		#############################################################################
		# TODO: Binarize the supplied ratings matrix. Do not use the self.ratings   #
		# matrix directly in this function.                                         #
		#############################################################################

		# The starter code returns a new matrix shaped like ratings but full of zeros.
		# binarized_ratings = np.zeros_like(ratings)
		binarized_ratings = ratings
		binarized_ratings[binarized_ratings == 0] = 10
		binarized_ratings[binarized_ratings < 3.0] = -1
		binarized_ratings[binarized_ratings == 10] = 0
		binarized_ratings[binarized_ratings >= 3.0] = 1
		

		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return binarized_ratings

	def similarity(self, u, v):
		"""Calculate the cosine similarity between two vectors.

		You may assume that the two arguments have the same shape.

		:param u: one vector, as a 1D numpy array
		:param v: another vector, as a 1D numpy array

		:returns: the cosine similarity between the two vectors
		"""
		#############################################################################
		# TODO: Compute cosine similarity between the two vectors.
		#############################################################################
		sim = 0
		# if np.linalg.norm(u) * np.linalg.norm(v) != 0:
		# 	sim == np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
		if np.linalg.norm(u) != 0 and np.linalg.norm(v) != 0:
			sim = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return sim



	# Creates and returns sparse vector of user sentiments to given movies
	def createUserMatrix(self):
		user_matrix = np.zeros((self.ratings.shape[0], 1))
		for key, value in self.userSentiment.items():
			user_matrix[key] = value
		return user_matrix


	def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
		"""Generate a list of indices of movies to recommend using collaborative filtering.

		You should return a collection of `k` indices of movies recommendations.

		As a precondition, user_ratings and ratings_matrix are both binarized.

		Remember to exclude movies the user has already rated!

		Please do not use self.ratings directly in this method.

		:param user_ratings: a binarized 1D numpy array of the user's movie ratings
		:param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
		  `ratings_matrix[i, j]` is the rating for movie i by user j
		:param k: the number of recommendations to generate
		:param creative: whether the chatbot is in creative mode

		:returns: a list of k movie indices corresponding to movies in ratings_matrix,
		  in descending order of recommendation
		"""

		#######################################################################################
		# TODO: Implement a recommendation function that takes a vector user_ratings          #
		# and matrix ratings_matrix and outputs a list of movies recommended by the chatbot.  #
		# Do not use the self.ratings matrix directly in this function.                       #
		#                                                                                     #
		# For starter mode, you should use item-item collaborative filtering                  #
		# with cosine similarity, no mean-centering, and no normalization of scores.          #
		#######################################################################################

		# Populate this list with k movie indices to recommend to the user.
		recommendations = []
		rec = {} # movie index -> scores
		user_pref = {}
		for index, row in enumerate(user_ratings):
			if user_ratings[index] != 0:
				user_pref[index] = user_ratings[index]

		for index, row in enumerate(ratings_matrix):
			if index not in user_pref:
				score = 0
				for key,value in user_pref.items():
					sim = self.similarity(ratings_matrix[key], row)
					score += (sim * value)
				rec[index] = score
		recommendations = sorted(rec, key=rec.get, reverse=True)[:k]




		# Ask for 5 movies -> fill in sentiment for those indexes in sparse user/movie vector
		# Cosine sim each missing movie with rows of 5 movies that user gave input on
		# Compute given user rating * sim = score for each given movie
		# Store in dict score -> index of movie  ----> Keep highest k scores


		#############################################################################
		#                             END OF YOUR CODE                              #
		#############################################################################
		return recommendations

	#############################################################################
	# 4. Debug info                                                             #
	#############################################################################

	def debug(self, line):
		"""Return debug information as a string for the line string from the REPL"""
		# Pass the debug information that you may think is important for your
		# evaluators
		debug_info = 'debug info'
		return debug_info

	#############################################################################
	# 5. Write a description for your chatbot here!                             #
	#############################################################################
	def intro(self):
		"""Return a string to use as your chatbot's description for the user.

		Consider adding to this description any information about what your chatbot
		can do and how the user can interact with it.
		"""
		return """
		Your task is to implement the chatbot as detailed in the PA6 instructions.
		Remember: in the starter mode, movie names will come in quotation marks and
		expressions of sentiment will be simple!
		Write here the description for your own chatbot!
		"""


if __name__ == '__main__':
	print('To run your chatbot in an interactive loop from the command line, run:')
	print('    python3 repl.py')
