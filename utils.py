"""
utils.py
author: Emily Fountain

Modify this file to include functions that implement Boolean search, snippet generation, and doc_data presentation.
"""
import functools
import time
import json, re, nltk


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


def intersect(list1, list2):
    """
    Does a list intersect over the two lists passed in and returns the
    items it has in common. Only words for lists of integers.
    """
    answer = []
    list1.sort()
    list2.sort()
    while len(list1) is not 0 and len(list2) is not 0:
        if list1[0] == list2[0]:
            answer.append(list1[0])
            list1.pop(0)
            list2.pop(0)
        elif list1[0] < list2[0]:
            list1.pop(0)
        else:
            list2.pop(0)
    return answer


def search(query, index, director, directors, starring, stars, location, locations): #, location=None, starring=None
    """Return a list of movie ids that match the query."""
    possible_ids = []
    # print("searching",query)

    ## make a list of lists (possible_ids). Each list in the list represents a word in the query.
    ## Doing an intersection over these lists will give you the result of the boolean query.
    for word in query:
        possible_ids.append(index[word])
    if director:
        for word in director:
            possible_ids.append(directors[word])
    if location:
        for word in location:
            possible_ids.append(index[word])
    if starring:
        for word in starring:
            possible_ids.append(index[word])

    total_length = len(query) + len(director) + len(starring) + len(location)

    if total_length == 1:
        return possible_ids[0]
    elif total_length == 2:
        return intersect(possible_ids[0], possible_ids[1])
    else:
        answer = intersect(possible_ids[0], possible_ids[1])
        for i in range(2,total_length):
            answer = intersect(answer, possible_ids[i])
    return answer


def movie_data(doc_id, shelf):
    """
    Return data fields for a movie.
    Your code should use the doc_id as the key to access the shelf entry for the movie doc_data.
    You can decide which fields to display, but include at least title and text.
    """

    movie_object = shelf[doc_id]
    return movie_object

def not_less_than_zero(number):
    """
    Helper function that returns numbers between 0 and the number.
    """
    if number > 0:
        return number
    return 1

def not_greater_than(number, cap):
    """
    Helper function that returns numbers between the number the the cap.
    """
    if number < cap:
        return number
    return cap

def movie_snippet(doc_id, query_terms, shelf, director_terms, starring_terms, location_terms):
    """
    Return a snippet for the results page.
    Needs to include a title and a short description.
    Your snippet does not have to include any query terms, but you may want to think about implementing
    that feature. Consider the effect of normalization of index terms (e.g., stemming), which will affect
    the ease of matching query terms to words in the text.
    """
    stemmer = nltk.stem.porter.PorterStemmer()


    id = str(doc_id)
    title = shelf[id]["Title"]
    full_text = shelf[id]["Text"]
    director = shelf[id]["Director"]
    starring = shelf[id]["Starring"]
    location = shelf[id]["Location"]
    # get the first 3 sentences of the text
    text = re.search(r'([^\.]+\.){2,3}', shelf[id]["Text"]).group(0)
    concordance = ""
    text_split = full_text.split()
    text_length = len(text_split)
    # search over text and title in order to find places where the search terms appear in the text
    for t in title.split():
        if normalize(t, stemmer) in query_terms:
            concordance += ("TITLE" + ": " + title) + ", "
    for dir in director:
        for t in dir.split():
            if normalize(t, stemmer) in director_terms:
                concordance += ("DIRECTOR" + ": " + str(dir)) + ", "
    for star in starring:
        for t in star.split():
            if normalize(t, stemmer) in starring_terms:
                concordance += ("STARRING" + ": " + str(star)) + ", "
    for loc in location_terms:
        for t in loc.split():
            if normalize(t, stemmer) in location_terms:
                concordance += ("LOCATION" + ": " + str(loc)) + ", "
    for i,t in enumerate(text_split):
        if normalize(t, stemmer) in query_terms:
            concordance += (t.upper() + ": ..." + ' '.join(text_split[not_less_than_zero(i-10):i]) + " " + ' '.join(text_split[not_greater_than(i, text_length):not_greater_than(i+9, text_length)]) + "... ")

    # concordance += "<br>"
    return doc_id, title, text, concordance


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_t = time.perf_counter()
        f_value = func(*args, **kwargs)
        elapsed_t = time.perf_counter() - start_t
        mins = elapsed_t//60
        print(f'Elapsed time: {mins} minutes, {elapsed_t - mins * 60:0.2f} seconds')
        return f_value
    return wrapper_timer
