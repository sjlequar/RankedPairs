import boto3
from boto3.dynamodb.conditions import Key
"""
RankedPairsDB

This module contains the interface for the database. 
"""

class VoteNotFound(Exception):
	"""
	Error raised if a vote isn't found in the database
	"""
	pass


def get_table(dynamodb, name="RankedPairsVotes"):
	"""
	Helper function, gets the table from a database resource. 
	dynamodb: databse object, uses localhost if none
	name:	  str, default RankedPairsVotes
	return:   dynamodb.Table
	"""
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', 
								  endpoint_url="http://localhost:8000")
	return dynamodb.Table(name)

def create_ballot(ballot, dynamodb=None):
	"""
	Helper function that adds an entry to store all elections on a ballot
	ballot:   str, ballot_id
	dynamodb: databse object, uses localhost if none
	return:   response
	"""
	table = get_table(dynamodb)
	response = table.put_item(
		Item={
			'ballot': ballot,
			'vote_id': "69", # This number is irrelevant, it's important that
							 # it doesn't end in a pound sign
			'elections': []
		}
	)
	return response

def add_election_to_ballot(ballot, election, dynamodb=None):
	table = get_table(dynamodb)
	response = table.update_item(
		Key={
			'ballot': ballot, 
			'vote_id': "69"
		}, 
		UpdateExpression="SET elections = list_append(elections, :e)", 
		ExpressionAttributeValues={
			':e': [election]
		},

			



def vote(ballot, election, voter_id, vote, time, dynamodb=None):
	"""
	Used to cast a vote, storing it in the database. 
	ballot:    str, ballot_id
	election:  str, election_id
	voter_id:  str, voter_id
	vote:	   str, vote, formatted as ##TODO
	timestamp: str, time of vote
	dynamodb:  databse object, default None, uses localhost if none
	"""
	table = get_table(dynamodb)
	response = table.put_item(
		Item={
			'ballot': ballot, 
			'vote_id': f"{election}#{voter_id}", 
			'vote': vote,
			'time': time
		}
	)
	return response


def get_individual_vote(ballot, election, voter_id, dynamodb=None):
	"""
	Used to retrieve an individual vote
	ballot:    str, ballot_id
	election:  str, election_id
	voter_id:  str, voter_id
	dynamodb:  databse object, default None, uses localhost if none
	return:    str
	"""
	table = get_table(dynamodb)
	response = table.get_item(
		Key={
			'ballot': ballot, 
			'vote_id': f"{election}#{voter_id}",
		}
	)
	if 'Item' not in response:
		raise VoteNotFound()
	else:
		return response['Item']['vote']


def get_election_votes(ballot, election, dynamodb=None):
	"""
	Used to retrieve a list of all votes in an election, anonimized
	ballot:   str, ballot_id
	election: str, election_id
	dynamodb: databse object, default None, uses localhost if none
	return:   [str]
	"""	
	table = get_table(dynamodb)
	response = table.query(
		KeyConditionExpression = 
			Key("ballot").eq(ballot) &
			Key("vote_id").begins_with(f"{election}#"),
		Select="SPECIFIC_ATTRIBUTES",
		ProjectionExpression="vote"
		
	)
	return list(map(lambda x: x['vote'], response['Items']))



