"""
hw3.py
author: Emily Fountain

Modify this code to provide an interface for your Boolean search engine
To start the application:
   >python hw3.py
To terminate the application, use control-c
To use the application within a browser, use the url:
   http://127.0.0.1:5000/

Some test queries to exercise the dummy interface:
king of sweden
<next button>
prince
a of

"""

from flask import Flask, render_template, request
# from Flask_example_boolean_retrieval.utils import search, movie_data, movie_snippet
from utils import search, movie_data, movie_snippet, timer
import shelve, os, json, re, nltk
from timeit import default_timer as timer

shelf = {}

# Create an instance of the flask application within the appropriate namespace (__name__).
# By default, the application will be listening for requests on port 5000 and assuming the base
# directory for the resource is the directory where this module resides.
app = Flask(__name__)


# Welcome page
# Python "decorators" are used by flask to associate url routes to functions.
# A route is the path from the base directory (as it would appear in the url)
# This decorator ties the top level url "localhost:5000" to the query function, which
# renders the query_page.html template.
@app.route("/")
def query():
    """For top level route ("/"), simply present a query page."""
    return render_template('query_page.html')


# This takes the form data produced by submitting a query page request and returns a page displaying results (SERP).
@app.route("/results", methods=['POST'])
def results():
    """Generate a result set for a query and present the 10 results starting with <page_num>."""

    stemmer = nltk.stem.porter.PorterStemmer()

    page_num = int(request.form['page_num'])
    query = request.form['query']  # Get the raw user query
    query_terms = query.split(' ')
    for i, item in enumerate(query_terms):
        query_terms[i] = normalize(item, stemmer) # normalize the query, the same way it's normalized in the corpus

    # print(query)
    # print(query_terms)

    # Keep track of any stop words removed from the query to display later.
    # Stop words should be stored in persistent storage when building your index,
    # and loaded into your search engine application when the application is started.
    stopwords = ["i", "a", "about", "an", "are", "as", "at", "be", "by", "com", "for", "from", "how", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with", "the"]
    skipped = [e for e in query_terms if e in stopwords]
    # print("skipped",skipped)

    unknown_terms = [e for e in query_terms if e not in index and e not in stopwords]
    # print("unknown words",unknown_terms)

    # remove stopwords and unknown terms from the query so they're not used in the search
    for word in skipped:
        query_terms.remove(word)
    for word in unknown_terms:
        query_terms.remove(word)

    director_terms=[]
    director = request.form['director']
    if director != "":
        director_terms = director.split(' ')
        for i, item in enumerate(director_terms):
            director_terms[i] = normalize(item, stemmer)
        print(director_terms)
        d_skipped = [e for e in director_terms if e in stopwords]
        d_unknown = [e for e in director_terms if e not in directors and e not in stopwords]
        print(d_skipped,d_unknown)
        for word in d_skipped:
            director_terms.remove(word)
        for word in d_unknown:
            director_terms.remove(word)
        skipped.extend(d_skipped)
        unknown_terms.extend(d_unknown)

    starring_terms=[]
    starring = request.form['starring']
    if starring != "":
        starring_terms = starring.split(' ')
        for i, item in enumerate(starring_terms):
            starring_terms[i] = normalize(item, stemmer)
        s_skipped = [e for e in starring_terms if e in stopwords]
        s_unknown = [e for e in starring_terms if e not in stars and e not in stopwords]
        for word in s_skipped:
            starring_terms.remove(word)
        for word in s_unknown:
            starring_terms.remove(word)
        skipped.extend(s_skipped)
        unknown_terms.extend(s_unknown)

    location_terms=[]
    location = request.form['location']
    if location != "":
        location_terms = location.split(' ')
        for i, item in enumerate(location_terms):
            location_terms[i] = normalize(item, stemmer)
        l_skipped = [e for e in location_terms if e in stopwords]
        l_unknown = [e for e in location_terms if e not in locations and e not in stopwords]
        for word in l_skipped:
            location_terms.remove(word)
        for word in l_unknown:
            location_terms.remove(word)
        skipped.extend(l_skipped)
        unknown_terms.extend(l_unknown)
    # print(unknown_terms)
    # check to see if there are any remaining query terms (if they weren't all removed because they
    # were stopwords or unknown)
    if len(query_terms) > 0 and query_terms[0] != "":
        movie_ids = list(set(search(query_terms, index, director=director_terms, directors=directors, starring=starring_terms, stars=stars, location=location_terms, locations=locations)))  # Get a list of movie doc_ids that satisfy the query.
    else:
        movie_ids = []
    # render the results page
    num_hits = len(movie_ids)  # Save the number of hits to display later
    movie_ids = movie_ids[((page_num - 1) * 10):(page_num * 10)]  # Limit of 10 results per page
    # print("matched ids",movie_ids)
    # movie_results = list(map(dummy_movie_snippet, movie_ids))  # Get movie snippets: title, abstract, etc.
    movie_results = [movie_snippet(e, query_terms, shelf, director_terms, starring_terms, location_terms) for e in movie_ids]
    return render_template('results_page.html', orig_query=query, orig_dir=director, orig_star=starring, orig_loc=location,              movie_results=movie_results, srpn=page_num, len=len(movie_ids), skipped_words=skipped, unknown_terms=unknown_terms, total_hits=num_hits)


# Process requests for movie_data pages
# This decorator uses a parameter in the url to indicate the doc_id of the film to be displayed
@app.route('/movie_data/<film_id>')
def movie_doc(film_id):
    """Given the doc_id for a film, present the title and text (optionally structured fields as well)
    for the movie."""
    data = movie_data(film_id, shelf)  # Get all of the info for a single movie
    return render_template('doc_data_page.html', data=data)


# Applies all normalization procedures to a given word.
def normalize(word, stemmer):
    """
    Normalizes a word passed into it by making it lowercase, removing punctuation of all types,
    and stemming.
    """
    result = ""
    result = word.lower()
    result = re.sub(r'[.,!?\"\':;<>\[\]\{\}\-\(\)]', "", result)
    result = stemmer.stem(result)
    return result


# If this module is called in the main namespace, invoke app.run().
# This starts the local web service that will be listening for requests on port 5000.
if __name__ == "__main__":

    ### Insert your corpus name here (without the .json extension)
    corpus_name = "Emily_corpus"

    stopwords = ["i", "a", "about", "an", "are", "as", "at", "be", "by", "com", "for", "from", "how", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "with", "the"]

    stemmer = nltk.stem.porter.PorterStemmer()

    start = timer()
    # if there's no shelf already created, create it.
    if not os.path.isfile(corpus_name + ".db"):
        shelf = shelve.open(os.path.join(corpus_name), writeback=False)
        with open(os.path.join(corpus_name + ".json")) as f:
            corpus = json.load(f)
            for item in corpus:
                shelf[item] = corpus[item]
        shelf.close()
    shelf = shelve.open(os.path.join(corpus_name), writeback=False)

    # if there's no index already created, create it.
    if not os.path.isfile(corpus_name + "_index.db"):
        index = shelve.open(os.path.join(corpus_name + "_index"), writeback=True)
        with open(os.path.join(corpus_name + ".json")) as f:
            corpus = json.load(f)
            for item in corpus:
                indexable = corpus[item]["Title"].split()
                indexable.extend(corpus[item]["Text"].split())
                indexable = list(set(indexable))
                for word in indexable:
                    if word in stopwords:
                        pass
                    else:
                        word = normalize(word, stemmer)
                        if word in index:
                            if item not in index[word]:
                                index[word].append(item)
                        else:
                            index[word] = []
                            index[word].append(item)
        index.close()
    index = shelve.open(os.path.join(corpus_name + "_index"), writeback=False)

    if not os.path.isfile(corpus_name + "_directors.db"):
        directors = shelve.open(os.path.join(corpus_name + "_directors"), writeback=True)
        with open(os.path.join(corpus_name + ".json")) as f:
            corpus = json.load(f)
            for item in corpus:
                indexable = []
                for dir in corpus[item]["Director"]:
                    indexable.extend(dir.split())
                indexable = list(set(indexable))
                for word in indexable:
                    if word in stopwords:
                        pass
                    else:
                        word = normalize(word, stemmer)
                        if word in directors:
                            if item not in directors[word]:
                                directors[word].append(item)
                        else:
                            directors[word] = []
                            directors[word].append(item)
        directors.close()
    directors = shelve.open(os.path.join(corpus_name + "_directors"), writeback=False)

    if not os.path.isfile(corpus_name + "_stars.db"):
        stars = shelve.open(os.path.join(corpus_name + "_stars"), writeback=True)
        with open(os.path.join(corpus_name + ".json")) as f:
            corpus = json.load(f)
            for item in corpus:
                indexable = []
                for dir in corpus[item]["Starring"]:
                    indexable.extend(dir.split())
                indexable = list(set(indexable))
                for word in indexable:
                    if word in stopwords:
                        pass
                    else:
                        word = normalize(word, stemmer)
                        if word in stars:
                            if item not in stars[word]:
                                stars[word].append(item)
                        else:
                            stars[word] = []
                            stars[word].append(item)
        stars.close()
    stars = shelve.open(os.path.join(corpus_name + "_stars"), writeback=False)

    if not os.path.isfile(corpus_name + "_locations.db"):
        locations = shelve.open(os.path.join(corpus_name + "_locations"), writeback=True)
        with open(os.path.join(corpus_name + ".json")) as f:
            corpus = json.load(f)
            for item in corpus:
                indexable = []
                for dir in corpus[item]["Location"]:
                    indexable.extend(dir.split())
                indexable = list(set(indexable))
                for word in indexable:
                    if word in stopwords:
                        pass
                    else:
                        word = normalize(word, stemmer)
                        if word in locations:
                            if item not in locations[word]:
                                locations[word].append(item)
                        else:
                            locations[word] = []
                            locations[word].append(item)
        locations.close()
    locations = shelve.open(os.path.join(corpus_name + "_locations"), writeback=False)

    elapsed_time = timer() - start # in seconds
    # print(elapsed_time)

    app.run(debug=True) # run the app
    shelf.close()
    index.close()
    # While you are debugging, set app.debug to True, so that the server app will reload
    # the code whenever you make a change.  Set parameter to false (default) when you are
    # done debugging.
