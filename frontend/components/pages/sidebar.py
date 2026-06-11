from nicegui import ui
from models.article import Articles
from models.folder import Folders
from models.user import UserAccount

#https://nicegui.io/documentation/expansion

#Takes a list of pages and creates a sidebar with links to those pages
def sidebar(links):
    with ui.left_drawer(fixed=False, top_corner=True, bottom_corner=True,bordered=True) as drawer:
        dark = ui.dark_mode()
        ui.switch('Dark mode').bind_value(dark)
        _get_links_for_user(user_id)
    return drawer

def _get_links_for_user(user_id: int) -> list:
    #get links for user from database
    folders = []
    articles = []
    folders += Folders.query.filter_by(owner_id=user_id).all()
    folders += Folders.query.filter_by(permitted_usernames.contains(str(user_id))).all()
    articles += Articles.query.filter_by(author_id=user_id).all()
    articles += Articles.query.filter_by(permitted_usernames.contains(str(user_id))).all()
    
    
    for folder in folders:
        if folder.parent_id is None:
            ui.expansion(folder.name, icon=folder.icon).classes('w-full')
        else:
            parentFolder = Folders.query.filter_by(id=folder.parent_id).first()
            ui.expansion(folder.name, icon=folder.icon,group=parentFolder).classes('w-full')
            
    for article in articles:
        ui.button(article.title, on_click=lambda a=article: ui.open('/article/' + str(a.title)), flat=True).classes('w-full text-left')
    