import boto3

def create_election_table(dynamodb=None):
    """
    Creates a table storing all ballots
    """
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName='RankedPairsVotes',
        KeySchema=[
            {
                'AttributeName': 'ballot',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'vote_id', # Position + VoterID
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ballot',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'vote_id',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return table

def create_user_table(dynamodb=None):
    """
    Creates a table storing all Users
    """
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName='RankedPairsVotes',
        KeySchema=[
            {
                'AttributeName': 'ballot',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'vote_id', # Position + VoterID
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ballot',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'vote_id',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return table

	

if __name__ == '__main__':
    election_table = create_election_table()
    print("Table status:", election_table.table_status)
