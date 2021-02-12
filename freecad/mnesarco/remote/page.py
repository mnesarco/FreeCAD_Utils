
class Page:

    def title(self):
        return "Page"

    def sections(self):
        return []

    def stylesheet(self):
        return "css/default.css"

    def data(self):
        return {
            'title': self.title(),
            'stylesheet': self.stylesheet(),
            'sections': [s.data() for s in self.sections()]
        }

class Section:

    def __init__(self, title, actions):
        self.title = title
        self.actions = actions
    
    def data(self):
        return {
            'title': self.title,
            'actions': [s.data() for s in self.actions]
        }

class Action:
    
    def __init__(self, title, icon, action):
        self.title = title
        self.icon = icon
        self.action = action

    def data(self):
        return self.__dict__