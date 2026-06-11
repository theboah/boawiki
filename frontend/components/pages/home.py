from nicegui import ui
from frontend.components.pages.sidebar import sidebar
from components.pages.article import article

@ui.page('/')
def home():
    ui.page_title('Home')
    bar = sidebar([])
    with ui.header(elevated=True).style('background-color: #3874c8').classes("grid grid-cols-24 gap-4"):
        ui.button(on_click=lambda: bar.toggle(),icon='menu').classes("col-span-1 col-start-1")
        ui.label('BoA Wiki').style('color: white').classes("col-span-1 col-start-12")
    ui.separator()
    
    ui.sub_pages({'/': homepage, '/other': article},data={'name':'example', 'authtoken':'token'})
    
def homepage():
    ui.label('This is the homepage')
    ui.link('Go to other page', '/other')
