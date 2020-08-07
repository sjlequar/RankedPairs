"""
Ranked Pairs

This module can run the Ranked Pairs election method given a set of votes
represented as preferences.

The method is taken from the Wikipedia article on Ranked Pairs

Written by Simon Lequar, Dabney '22
"""

from networkx import DiGraph
from networkx.algorithms.cycles import find_cycle
from networkx.exception import NetworkXNoCycle as no_cycle

def clean_votes(candidates, votes):
	"""
	params:
	 - candidates (list 'a): The list of candidates
	 - votes (list (dict {'a : Ord 'b})): The list of votes, which are
	   candidates mapped to a preference
	returns:
	 - cleaned votes (list (dict {'a : Ord 'b}))

	Cleans votes by adding a 0 for each non-present candidate, which means
	votes should be in high-preference, high rank order (1-10 worst-best)
	"""
	for vote in votes:
		for candidate in candidates:
			if candidate not in vote:
				vote[candidate] = 0
	return votes

def _pair_ranker(pairs, comp):
	"""
	helper function for _gen_pairs(), sorts a list of pairs based on some
	comparison
	notably, it doesn't include any ties, since this would be an irrelevant
	edge in the graph later. (if comp[(1, 3)] == comp[(3, 1)], which means
	there is no preference between 1 and 3, then neither (1, 3) nor (3, 1)
	will be in the list of pairs returned)
	"""
	ranked_pairs = [p for p in pairs if comp[p] > comp[p[::-1]]]
	ranked_pairs.sort(reverse=True, key=(lambda x: (comp[x], -comp[x[::-1]])))
	return ranked_pairs

def _gen_pairs(candidates, votes):
	"""
	Helper function for run(), used to generate the ordered pairs of
	candidates. The returned pairs are already in strength order
	"""
	# We need to compare each pair (Ranked Pairs, duh) of candidates
	pairs = [(i, j) for i in candidates for j in candidates if i != j]
	votes = clean_votes(candidates, votes)

	# This calculates the strength of each pairwise election
	comp = {}
	for i, j in pairs:
		temp = 0
		for vote in votes:
			if vote[i] > vote[j]:
				temp += 1
		comp[(i, j)] = temp

	# This helper function can be changed for different tiebreakers
	return _pair_ranker(pairs, comp)

def _graph(candidates, pairs):
	"""
	helper function for run(), evaluates winner of pairs given ordered pairs
	slower than _faster_comp(), produces same results
	"""
	# This is the standard graph based way to do ranked pairs
	g = DiGraph()
	g.add_nodes_from(candidates)

	# The strongest victories are added in order, unless there is a cycle,
	# in which case they are skipped
	edges = set()
	for (i, j) in pairs:
		if (j, i) not in edges:
			g.add_edge(i, j)
			# if a cycle exists, the edge is removed, otherwise continue
			try:
				find_cycle(g)
				g.remove_edge(i, j)
			except no_cycle:
				pass
			edges.add((i, j))

	# We then find the source of the graph, which is the winner
	winners = set()
	for c in candidates:
		try:
			next(g.in_edges(c).__iter__())[0]
		except StopIteration:
			winners.add(c)

	return winners

def _faster_comp(candidates, pairs):
	"""
	helper function for run(), evaluates winner of pairs, but faster (by
	about two orders of magnitude) than _graph()
	"""
	# This tentatively works, it failed a test once (and only once), and I
	# reran two orders of magnitudes more random tests and it passed them all
	# This works by tracking all nodes that have an edge pointing into them
	# and not checking any edge coming out of that node (as it wouldn't be a
	# source on the graph in that case).
	edges = set()
	children = set()
	for (i, j) in pairs:
		if i not in children and (j, i) not in edges:
			children.add(j)
			edges.add((i, j))
	winners = set()
	for c in candidates:
		if c not in children:
			winners.add(c)
	return winners

def run(candidates, votes, full_graph=False):
	"""
	params:
	 - candidates (list 'a): The list of candidates
	 - votes (list (dict {'a : Ord 'b})): The list of votes, which are
	   candidates mapped to a preference
	 - full_graph (bool, default False): whether to use the full graph to
	   check the winner, faster method currently works, so isn't necessary
	returns:
	 - winners (set 'a): This is a set of all winners (more than 1 iff tied)

	Runs RP on a list of candidates and a list of dictionaries of votes

	Repeated candidates are not allowed, repeated votes are allowed

	Votes are in high-preference, high rank (ie 1-10, 1 worst, 10 best), and
	all ranks are positive

	Conditions of typical use:
		number of candidates small (~10 for original application)
		number of votes can be any size

	Linear in number of votes, O(N^2) in number of candidates
	"""
	# Some light error checking, may be expanded
	if len(candidates) == 0:
		raise ValueError("No candidates")
	if len(votes) == 0:
		raise ValueError("No votes")
	if len(candidates) != len(set(candidates)):
		raise ValueError("Repeated Candidates")

	pairs = _gen_pairs(candidates, votes)
	winners = None
	if full_graph:
		winners = _graph(candidates, pairs)
	else:
		winners = _faster_comp(candidates, pairs)

	return winners

def full_order(candidates, votes, full_graph=False):
	"""
	params:
	 - candidates (list 'a): The list of candidates
	 - votes (list (dict {'a : Ord 'b})): The list of votes, which are
	   candidates mapped to a preference
	 - full_graph (bool, default False): whether to use the full graph to
	   check the winner, faster method currently works, so isn't necessary
	returns:
	 - ordered results (list (set 'a)): A list representing the finish order

	Runs RP on a list of candidates and a list of dictionaries of votes, but
	returns the result for each candidate, as opposed to run(), which only
	returns first place.

	A return of [{2}, {1, 3}, {4}] would represent 2 in first, 1 and 3 tied
	for second, and 4 in third place.

	See documentation of run() for more details
	"""
	candidates = set(candidates)
	order = []
	while(len(candidates) > 0):
		winner = run(candidates, votes, full_graph=full_graph)
		order.append(winner)
		candidates -= winner
	return order
