import time, os.path, pickle, logging
from  more_itertools import unique_everseen


'''
These are the support functions for caching lemma_samples (previously "data_samples") and nes_samples.
These files are critical for many analysis in SCKE.
I changed it to "lemma_samples" instead of "data_samples" because the latter is an ambiguous name!!!

Before June-21-2017, lemma_samples were called "data_samples", and stored in a pickle.
"Data_samples" contained a list of lists of lemmas from annotated BioDoct jsons
(i.e. the citations for the input/query papers).
E.g. [['lemma for doc 1'], ['lemma for doc 2'], .., ['lemma for doc n']]

But these did not reference the pmcid for the citing document.... and that's important to have!
So I've changed the code to instead be:
[['1234', 'lemma for doc 1'], ['45678', 'lemma for doc 2'], .., ['09876', 'lemma for doc n']]
where the pmcid is in the first position of every lemma list

Ditto for nes_samples :)

'''

logging.basicConfig(filename='.app.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


#Revamped lemma_samples (data_samples) caching function!!!
#Old method: save a pickled list of lists for each query
#New method: saves a pickled list of list for one PMID.
#New method: FIRST thing in every list is the pmcid of the citation
def print_lemma_nes_samples(user_input, biodoc_data):
	t1 = time.time()
	logging.info("printing lemma samples & nes samples ... ")

	prefix = '/home/hclent/data/pmcids/' + str(user_input[0:3])  # folder for first 3 digits of pmcid
	suffix = prefix + '/' + str(user_input[3:6])  # folder for second 3 digits of pmcid nested in prefix

	#Step 1: does this file already exist? if so, pass
	try:
		#to open the file!!
		lemma_completeName = os.path.join(suffix, ('lemma_samples_' + (str(user_input)) + '.pickle'))
		with open(lemma_completeName, 'rb') as f:
			pickle.load(f)
		logging.info("lemmma_samples for " + user_input + " already exists! Don't re-make" )

		nes_completeName = os.path.join(suffix, ('nes_' + (str(user_input)) + '.pickle'))
		with open(nes_completeName, 'rb') as f:
			pickle.load(f)
		logging.info("nes_samples for " + user_input + " already exists! Don't re-make")
		pass

	#Step 2: The file doesn't exist? So make it!
	except Exception as e:
		logging.info("the file doesn't exist! Make it!")

		try:
			os.makedirs(prefix)  # creates folder named after first 3 digits of pmcid
		except OSError:
			if os.path.isdir(prefix):
				pass
			else:
				raise

		try:
			os.makedirs(suffix)  # creates folder named after second 3 digits of pmicd
		except OSError:
			if os.path.isdir(suffix):
				pass
			else:
				raise

		#biodocdata to lemma_samples ("data_samples")
		lemma_samples = []
		nes_samples = []

		# going to add the pmcid to the first place in every lemma row, to attach the id before its sent off to a pickle :')
		for bd_dict in biodoc_data:
			pmcid = bd_dict["pmcid"]
			lemmas = bd_dict["lemmas"]
			#add the id to the first position in the list so that we can be sure what the text refers to.
			lemmas.insert(0, pmcid) #yucky and not functional blegh :/
			lemma_samples.append(lemmas)

			nes = bd_dict["nes"]
			nes.insert(0, pmcid)
			nes_samples.append(nes)

		lemma_completeName = os.path.join(suffix, ('lemma_samples_' + (str(user_input)) + '.pickle'))
		logging.info(lemma_completeName)
		with open(lemma_completeName, "wb") as lcn:
			pickle.dump(lemma_samples, lcn)
		logging.info("lemma_samples dumped to pickle")

		nes_completeName = os.path.join(suffix, ('nes_' + (str(user_input)) + '.pickle'))
		logging.info(nes_completeName)
		with open(nes_completeName) as ncn:
			pickle.dump(nes_samples, ncn)
		logging.info("lemma_samples dumped to pickle")

	logging.info("Execute print_lemma_nes_samples: done in %0.3fs." % (time.time() - t1))


# biodoc_data = do_multi_preprocessing("18269575")
# print_lemma_nes_samples("18269575", biodoc_data)

'''
This function concatenates previous lemma_samples and nes_samples for queries longer than 1 input Paper.
We want to produce another pickle with just the unique papers for this query using
Thus we will output the lemma_samples and nes_samples (with no repeats!!!)
It will be saved in the file corresponding with the first paper in the query
E.g. for query "18952863+18269575", the samples are saved in the data/pmcids/189/528/ dir
'''
def concat_lemma_nes_samples(query):
	t1 = time.time()
	pmid_list = query.split('+')  # list of string pmids

	all_lemma_samples = []
	all_nes_samples = []

	#only need to concatenate datasamples if the query is more than 1 pubmed ID long
	if len(pmid_list) > 1:
		#does the file already exist?
		try:
			#check for the file
			#store these in the dir named for the first item in query
			first_pmid = pmid_list[0]
			query_lemma_completeName = '/home/hclent/data/pmcids/' + str(first_pmid[0:3]) + '/' + str(first_pmid[3:6]) + 'lemma_samples_' + str(query) + ".pickle"
			query_nes_completeName = '/home/hclent/data/pmcids/' + str(first_pmid[0:3]) + '/' + str(first_pmid[3:6]) + 'nes_' + str(query) + ".pickle"

			# efficient way to open a pickle is via "with" because it closes after the statement ends
            # even if an exception occurs!
			with open(query_lemma_completeName, "rb") as qlemma:
				pickle.load(qlemma)
			logging.info("query_lemmma_samples for " + query + " already exists! Don't re-make")
			with open(query_nes_completeName, "rb") as qnes:
				pickle.load(qnes)
			logging.info("query_nes_samples for " + query + " already exists! Don't re-make")

		#no file! make one!
		except Exception as e:
			logging.info(e)

			for pmid in pmid_list:
				lemma_file = '/home/hclent/data/pmcids/' + str(pmid[0:3])  + '/' + str(pmid[3:6]) + '/' +'lemma_samples_' + (str(pmid)) + '.pickle'
				with open(lemma_file, 'rb') as f:
					lemma_list = pickle.load(f)
				for ls in lemma_list:
					all_lemma_samples.append(ls)

				nes_file = '/home/hclent/data/pmcids/' + str(pmid[0:3])  + '/' + str(pmid[3:6]) + '/' +'nes_' + (str(pmid)) + '.pickle'
				with open(nes_file, 'rb') as f:
					nes_list = pickle.load(f)
				for ns in nes_list:
					all_nes_samples.append(ns)



			### Now to get the UNIQUE stuff only!
			#now get all_lemma_samples and all_nes_samples to ONLY contain UNIQUE stuff. no duplicates

			## problem: list and dict are unhashable. can't use set() or unique_everseen()
			##

			print(len(all_lemma_samples))
			lemma_samples_set = [list(x) for x in set(tuple(x) for x in all_lemma_samples)]
			lemma_samples = [ds for ds in lemma_samples_set]
			print(len(lemma_samples))
			# print(lemma_samples[0])



			print(len(all_nes_samples))
			#nes_set = [list(n) for n in set((n[0]) for n in all_nes_samples)] #n in all_nes_samples is a list of dictionaries


			#nes_samples = [ns for ns in nes_set]
			#print(len(nes_samples))
			#print(nes_samples[0])





	#don't need to create a new file if its like... just 1 pmcid
	else:
		logging.info("its just one input paper. Don't need to concatenate any lemmas or nes")
		pass
	logging.info("Execute concat_lemma_nes_samples: done in %0.3fs." % (time.time() - t1))



concat_lemma_nes_samples('18952863+18269575')