"""
Calculates each node's coreness value, as described by Stephen Borgatti
"""

__author__ = """Alex Levenson (alex@isnontinvain.com)"""

#	(C) Reya Group: http://www.reyagroup.com
#	Alex Levenson (alex@isnotinvain.com)
#	BSD license.

__all__ = ["triadic_census"]

from scipy import optimize
from scipy.stats.stats import pearsonr
import numpy
import networkx as nx

def core_correlation(A,C):
	"""
	returns the pearson correlation between A and
	the ideal coreness matrix created from C
	
	A: ajacency matrix (valued or unvalued)
	C: 1D matrix representing the coreness of each node
	"""
	cMat = numpy.matrix(C)
	Cij = numpy.multiply(cMat,cMat.transpose())
	return pearsonr(A.flat,Cij.flat)
	
def _core_fitness(C,*args):
	"""
	converts coreCorrelation(A,C) to something useable
	with scipy.optimize (which aims to MINIMIZE a function)
	Need to express highest positive correlation as function
	to be minimized
	"""
	return core_correlation(args[0],C)[0] * -1.0

def coreness(G,return_correlation=False):
	"""
	Calculates each node's coreness value, as described by Stephen Borgatti
	
	Coreness describes to what degree a node is a member of the graph's core
	Parameters
	----------
	G : graph
		A networkx graph
	
	return_correlation : whether to return the final correlation to the ideal core / periphery structure
	Returns
	-------
	census : dictionary
			 Dictionary with nodes as keys and coreness as values
			 *if return_correlation is set, then returns a tuple (dict with nodes as keys and coreness as values,correlation)* 
	Refrences
	---------	
	.. [1] Models of Core/Periphery Structures
	   Stephen P. Borgatti, Boston College
	   http://dx.doi.org/10.1016/S0378-8733(99)00019-2
	"""

    A = nx.to_numpy_matrix(G)
	
	# need a starting point for the optimizer, for now using a random starting point.
	initialC = numpy.random.rand(len(A)) # can we do better? Is it important? Maybe use constraint or centrality? 
	
	# run a bfgs optimizers that optimizes correlation between calculated coreness scores and the ideal model
	best = optimize.fmin_l_bfgs_b(_core_fitness, initialC,args=(A,None),approx_grad=True,bounds=[(0.0,1.0) for i in xrange(len(A))])	
	
	part = {}
	for node in G:
		part[node] = best[0][G.nodes().index(node)]
	
	# return correlation to ideal if return_correlation is set
	if return_correlation: 
		return part,best[1] * -1.0
	return part