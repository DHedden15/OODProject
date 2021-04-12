from algo import Algo
import pkg_resources
from symspellpy import SymSpell, Verbosity
import pickle

try:
	symspell = pickle.load(open('symspell.pkl','rb'))
except:
	symspell = SymSpell(max_dictionary_edit_distance=4, prefix_length=7)
	dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
	symspell.load_dictionary(dictionary_path, term_index=0, count_index=1)
	pickle.dump(symspell,open('symspell.pkl','wb'))
	
inp = input("Enter: ")

while inp != '':
	a = Algo(inp,symspell)
	print(a.out)
	inp = input("Enter: ")
