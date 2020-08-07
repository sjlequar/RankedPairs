import nose, random
import rp

def make_votes_from_cand_stren(candidates, strengths, num_votes, noise=3):
	votes = []
	nc = len(candidates)
	for _ in range(num_votes):
		vote = {}
		for candidate in candidates:
			vote[candidate] = max(min(strengths[candidate] + \
								  random.randint(-noise, noise), nc), 0)
		votes.append(vote)
	return votes

def make_candidates(num_candidates):
	candidates = list(range(1, num_candidates + 1))
	strengths = {}
	for candidate in candidates:
		strengths[candidate] = random.randint(1, num_candidates)
	return candidates, strengths

def make_random_candidates_votes(num_candidates, num_votes, noise=3):
	c, s = make_candidates(num_candidates)
	v = make_votes_from_cand_stren(c, s, num_votes, noise=noise)
	return c, v, s


NUMTESTS = 1000
FULLGRAPH = False

def helper_running(nc, nv, nt):
	for _ in range(nt):
		c, v, s = make_random_candidates_votes(nc, nv)
		w = rp.run(c, v, full_graph=FULLGRAPH)
		assert(len(w)!= 0 and w.issubset(c))

def test_running_small():
	NUMCAND = range(1, 6)
	NUMVOTES = range(1, 6)
	for nc in NUMCAND:
		for nv in NUMVOTES:
			helper_running(nc, nv, NUMTESTS)

def test_running_large():
	NUMCAND = [10, 20]
	NUMVOTES = [30, 50, 200]
	SCALED = int(NUMTESTS ** .5)
	for nc in NUMCAND:
		for nv in NUMVOTES:
			helper_running(nc, nv, SCALED)
			

def test_accuracy():
	NUMCAND = 10
	NUMVOTES = 100
	MARGIN = .75
	NOISE = 5
	SCALED = int(NUMTESTS / 10)
	for _ in range(SCALED):
		c, s = make_candidates(NUMCAND)
		win_stren = max(s.values())
		strongest = [c for c in s if s[c] == win_stren]
		winners = []
		for _ in range(SCALED):
			v = make_votes_from_cand_stren(c, s, NUMVOTES, noise=NOISE)
			winners.extend(rp.run(c, v, full_graph=FULLGRAPH))
		for candidate in strongest:
			win_odds = [winners.count(c)/SCALED for c in strongest]
			try:
				for i in win_odds:
					assert(i > MARGIN/(len(strongest) ** 2))
				assert(sum(win_odds) > MARGIN)
			except AssertionError:
				stren_list = sorted([(k, v) for k, v in s.items()], \
									key=lambda x: -x[1])
				print("strengths")
				print(stren_list[:5], "(some omitted)")
				print("win incidence")
				print([(i, round(winners.count(i)/SCALED, 5)) \
					   for (i, _) in stren_list[:5]])
				print("cause of error")
				print(f"{candidate} with {winners.count(candidate)/SCALED}")
				print(f"margin was {MARGIN/len(strongest)}")
				print()	
				raise AssertionError

def test_full_matches_fast():
	NUMCAND = 10
	NUMVOTES = 100
	SCALED = int(NUMTESTS / 10)
	for _ in range(SCALED):
		c, v, s = make_random_candidates_votes(NUMCAND, NUMVOTES)
		full = rp.run(c, v, True)
		fast = rp.run(c, v, False)
		try:
			assert(full == fast)
		except AssertionError:
			print(full, fast)

def test_tied():
	NUMCAND = 10
	NUMVOTES = 10
	for _ in range(NUMTESTS):
		c, v, s = make_random_candidates_votes(NUMCAND, NUMVOTES, noise=0)	
		win_stren = max(s.values())
		strongest = [c for c in s if s[c] == win_stren]
		assert(len(rp.run(c, v)) == len(strongest))

if __name__ == "__main__":
	nose.runmodule()
