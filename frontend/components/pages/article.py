from nicegui import ui

def article(name, authtoken):
    #functions to get name etc
    ui.label('ARTICLE HEADER')
    ui.label('This is the article page for ' + name)
    ui.link('Go home', '/')
    
#Context Menu
#https://nicegui.io/documentation/context_menu