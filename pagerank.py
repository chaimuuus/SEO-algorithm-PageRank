import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000 ## prendre a chaque fois une valeur aleatoir de chaque noeud pour créer a sample de page rank


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


import random

DAMPING = 0.85
SAMPLES = 10000


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next.
    """
    num_pages = len(corpus)
    probabilities = {}

    links = corpus[page]
    if links:
        for p in corpus:
            probabilities[p] = (1 - damping_factor) / num_pages
        for link in links:
            probabilities[link] += damping_factor / len(links)
    else:
        # No outgoing links → equal probability to all pages
        for p in corpus:
            probabilities[p] = 1 / num_pages

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling n times.
    """
    pagerank = {page: 0 for page in corpus}
    pages = list(corpus.keys())

    # First sample: random choice
    current_page = random.choice(pages)
    pagerank[current_page] += 1

    for _ in range(1, n):
        probs = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(list(probs.keys()), weights=probs.values())[0]
        pagerank[current_page] += 1

    # Normalize counts to probabilities
    for page in pagerank:
        pagerank[page] /= n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively applying formula.
    """
    N = len(corpus)
    pagerank = {page: 1 / N for page in corpus}

    # Treat pages with no links as linking to all pages
    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = set(corpus.keys())

    while True:
        new_pagerank = {}
        for page in corpus:
            new_rank = (1 - damping_factor) / N
            for possible_page in corpus:
                if page in corpus[possible_page]:
                    new_rank += damping_factor * (pagerank[possible_page] / len(corpus[possible_page]))
            new_pagerank[page] = new_rank

        # Check for convergence
        diff = max(abs(new_pagerank[p] - pagerank[p]) for p in pagerank)
        pagerank = new_pagerank
        if diff < 0.001:
            break

    return pagerank



if __name__ == "__main__":
    main()
