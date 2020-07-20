import string
import random
from difflib import get_close_matches

"""
Language processing for Project Gutenberg's Pride and Prejudice "
"""
#Creates a Trie used for the autocomplete method
class Trie:
  def __init__(self, val):
    self.val = val
    self.end_word = False
    self.children = {}

  def add_word(self, s):
    def helper(node, i):
      if i >= len(s):
        return
      if s[i] not in node.children:
        node.children[s[i]] = Trie(s[i])
        if i == len(s)-1:
          node.children[s[i]].end_word = True
          return
      helper(node.children[s[i]], i+1)
    helper(self, 0)

  def get_prefix(self, s, tree):
    nde = tree
    i=0
    while i < len(s):
      nde = nde.children[s[i]]
      i+=1
    return nde

  def getAllWords(self, s, t, lst):
    for k in t.children:
      child = t.children[k]
      news = s+child.val
      if child.end_word:
        lst.append(news)
      self.getAllWords(news,child, lst)

  def predict_word(self, s):
    all_words = []
    nde = self.get_prefix(s, self)
    if nde:
      self.getAllWords(s,nde,all_words)
    return all_words


#Class used for textual analysis
class Analysis:

  def __init__(self,filename):
    self.filename = filename
    with open(self.filename, 'r') as file:
      self.corpus = file.read().replace('\n', ' ')
    self.corpus = self.corpus.split(" ")

    #dirty_corpus  isn't made lower case and isn't cleaned for punctuation
    self.dirty_corpus = self.corpus

    self.corpus = [("".join((char for char in s if char not in string.punctuation))).lower() for s in self.corpus]

    with open("common.txt","r") as file:
      common_words= file.read().replace('\n', ' ')

    self.common_words = common_words.split(" ")[:100]
    self.common_words = set(i.lower() for i in self.common_words)

    self.unique_words = self.getUniqueWords()

    self.frequencies = self.ordered_words()

    self.word_trie = self.make_trie()

    self.chapter_lists = self.create_chapter_corpus()

    with open(self.filename, "r") as file:
      self.sentences = file.read().replace('\n', ' ').replace("Chapter", "").replace(string.digits,"")
    self.sentences.split()

  #corpus refers to a body of text in this case

  def getUniqueWords(self):
    unique_words = {}
    for word in self.corpus:
      if word not in unique_words:
        unique_words[word] = 1
      else:
        unique_words[word] += 1
    unique_words.pop('')
    unique_words.pop("chapter")
    return unique_words

  def ordered_words(self):
    frequencies = []
    for key in self.unique_words:
      frequencies.append([key,self.unique_words[key]])
    frequencies.sort(key=lambda x:-x[1])
    return frequencies

  def make_trie(self):
    t = Trie("#")
    for k in self.unique_words:
      t.add_word(k)
    return t

  def create_chapter_corpus(self):
    chapter_lists = []
    curr_list = []
    for i in self.dirty_corpus:
      if i == "Chapter":
        chapter_lists.append(curr_list)
        curr_list = []
        continue
      curr_list.append(i)
    chapter_lists.append(curr_list)

    #Remove the edge case of having an empty list created before first chapter
    chapter_lists.pop(0)
    return chapter_lists


  def getTotalNumberOfWords(self):
      """
      Method takes in a .txt file and returns the number of words in the file
      Note: index, author's notes, and introductions are not part of the book.
      Input: "The blue cat hopped over the blue dog"
      Output: 8
      """
      return len(self.corpus)

  def getTotalUniqueWords(self):
      """
      Method takes in a .txt file and returns the number of unique words in the text file
      Input: "The blue cat hopped over the blue dog"
      Output: 6
      """
      return len(self.unique_words)

  def get20MostFrequentWords(self):
      """
      Method takes in a .txt file and returns an array of words and the number of times they were used
      Note: each element in the array is another array of size 2, where the first element is a string and the second is an int
      Input: harrypotterprisonerofaazkaban.txt
      Output: [ [“Harry”, 526], [“owl”, 256], [“Hogwarts”, 135], … ]
      """
      return self.frequencies[:20]


  def get20MostInterestingFrequentWords(self):
      """
      Method filters the most common 100 English words and returns the 20 most frequently used words and the number of times they were used
      Note: use https://gist.github.com/deekayen/4148741 to find list of 1000 most commonly used English words
      Since the list gives us 1000 words, feel free to tune your algorithm to filter the most common 100, 200, or 300 words and see how it affects the outcomes.
      """

      count = 0
      i = -1
      words =[]
      while count < 20:
        i+=1
        if self.frequencies[i][0] in self.common_words:
          continue
        words.append(self.frequencies[i])
        count+=1
      return words

  def get20LeastFrequentWords(self):
    """
    Method returns the 20 LEAST frequently used words and the number of times they were used.
    """
    return self.frequencies[-20:]
  #extra textual analysis

  def getFrequencyOfWord(self, findword):
      """
      Method that takes in a word and returns an array of the number of times the word was used in each chapter
      Note: Size of the array should be equal to the number of the chapters in the book
      Input: voldemort, harrypottersorcerersstone
      Output: [1, 0, 0, 2, 0, 0, …. , 10, 12, 20, 34, 2]
      """
      dct = {}
      curr = 0
      curr_counts = {}
      for word in self.corpus:
        if word == "chapter":
          dct[curr] = curr_counts
          curr_counts = {}
          curr+=1
          continue
        if word not in curr_counts:
          curr_counts[word] = 1
        else:
          curr_counts[word] += 1
      dct[curr] = curr_counts
      lst = []
      for i in range(len(dct)):
        if findword not in dct[i]:
          lst.append(0)
        else:
          lst.append(dct[i][findword])
      return lst

  def getChapterQuoteAppears(self,quote):
      """
      Method that takes in a quote as a string and returns a number denoting the chapter of the book. If the quote cannot be found in the book, method returns -1
      Input: "Harry yer a wizard"
      Output: 4
      """
      chapter_strings = []
      for i in range(len(self.chapter_lists)):
        chapter_strings.append(" ".join(self.chapter_lists[i]))

      j = 1
      for chapter in chapter_strings:
        if chapter.find(quote) != -1:
          return j
        j+=1
      return -1



  def generateSentence(self, start = "the", length = 15):
      """
      Method to generate a random sentence in the author's style of writing
      Note: https://docs.google.com/document/d/11jfZCa_iHiwZjF26R7MfEi5HiIUTNO8hvV23ubdSkTs/edit helpful
      """
      bigrams = {}
      for i in range(len(self.corpus)-1):
        curr = self.corpus[i]
        nxt = self.corpus[i+1]
        if curr not in bigrams:
          bigrams[curr] = {}
        if nxt not in bigrams[curr]:
          bigrams[curr][nxt] = 0
        bigrams[curr][nxt] += 1
      curr = start
      sent = start
      i = 1
      while i < length:
        lst = [[k,bigrams[curr][k]] for k in bigrams[curr]]
        curr = random.choice(lst)[0]
        sent += " "
        sent += curr
        i+=1
      return sent

  def getAutocompleteSentence(self, startOfSentence):
      """
      Method takes in a string and returns a list of strings that start with the input.
      Note: use a trie to find the avaliable words. Hint: https://medium.com/@dookpham/predictive-text-autocomplete-using-a-trie-prefix-tree-data-structure-in-javascript-part-1-6ff7fa83c74b
      """
      #Get the end of the sentence and try to complete that
      split = startOfSentence.split(" ")[-1]
      return self.word_trie.predict_word(split)




  def findClosestMatchingQuote(self, quote, threshold=.9):
      """
      Method that takes in a quote and returns the chapter this quote is found in.
      Note: the method could take in a misquoted quote, but still be able to find it
      Input: "Yer a wizard, Harry!"
      Output: "Harry - yer a wizard"
      """
      quotelen = len(quote.split(" "))
      chaptersubstrings = []
      lst_of_substrings = []
      for chapter in self.chapter_lists:
        for i in range(len(chapter)-quotelen):
          #Make a substring for every substring of size quotelen
          #Turn the sub array ito a string
          lst_of_substrings.append(" ".join(chapter[i:i+quotelen]))
        chaptersubstrings.append(lst_of_substrings)
        lst_of_substrings= []

      def helper(threshold):
        if threshold < 0:
          return "",-1
        print("Threshold is", threshold)
        best = []
        for i in range(len(self.chapter_lists)):
          good = get_close_matches(quote,chaptersubstrings[i], n =3, cutoff=threshold)
          if good:
            #add the best match to a list
            best.append(good[0])
        #Compare the best of all the chapters together and pick the best one
        final_match = get_close_matches(quote, best, n = 1, cutoff= threshold)
        if not final_match:
          return helper(threshold-.1)
        final_match = final_match[0]
        final_idx = best.index(final_match)+1
        return final_match, final_idx
      return helper(threshold)


#Test Cases
pap_analysis = Analysis("1342.txt")
print(pap_analysis.getTotalNumberOfWords())
print(pap_analysis.getTotalUniqueWords())
print(pap_analysis.get20MostFrequentWords())
print(pap_analysis.get20MostInterestingFrequentWords())
print(pap_analysis.get20LeastFrequentWords())
print(pap_analysis.getFrequencyOfWord("love"))
print(pap_analysis.generateSentence("the"))

print(pap_analysis.getChapterQuoteAppears("When they were gone, Elizabeth, as if"))

print(pap_analysis.getAutocompleteSentence("the col"))

print(pap_analysis.findClosestMatchingQuote("his ws speaki jestingli"))
