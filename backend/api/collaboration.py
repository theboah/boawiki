import redis
from models.article import Articles

class Collab:
    def __init__(self, article_id, users=[]):
        self.article_id = article_id
        self.users = users
        self.article = Articles.query(article_id).first()
        mouse_positions = {}
        text_edit_positions = {}
        text_select_positions = {}


#collab manager
class CollabManager():
    def __init__(self,env):
        self.redis_url = env.get_key('REDIS_URL')
        self.redis_client = redis.from_url(self.redis_url)


    #Load the article into memory
    def create_collab(self, article_id):
        return self.collab_repo.create_collab(article_id)

    def get_collab(self, user_id):
        return self.collab_repo.get_collab(user_id)

    def update_collab(self, user_id, collab_data):
        return self.collab_repo.update_collab(user_id, collab_data)

    def leave_collab(self, user_id):
        return self.collab_repo.leave_collab(user_id, user_id)
    
    def get_collab_users(self, collab_id):
        return self.collab_repo.get_collab_users(collab_id)