from tecton import Entity

user = Entity(
    name='user_entity',
    join_keys=['USER_ID'],
    description='The customer user id',
    owner='nlee@tecton.ai',
    tags={'release': 'production'}
)

chat_id = Entity(
    name='chat_id',
    join_keys=['CHAT_MESSAGE_ID'],
    description='A unique chat identifier',
    owner='nlee@tecton.ai',
    tags={'release': 'production'}
)