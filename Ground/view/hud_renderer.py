__author__ = 'will'



class HudRenderer():
    def __init__(self,receiver):
        self.receiver = receiver
        self.height_lines = 15
        self.width_chars = 50

        self.clear_line = "-".join(["" for i in range(self.width_chars)]) + "\n"
        self.clear_screen = "".join([self.clear_line for i in range(self.height_lines)])
        #print self.clear_screen.replace("<br>",'\n')

    def get_screen(self):
        """Get text and return it"""
        return """<span font="Arial Black 20" foreground="white">{0}</span>""".format(self.clear_screen)
        if 'attitude' in self.receiver.data:
            return """<span font="Arial Black 20" foreground="white"> Attitude:{0}</span>""".format(self.receiver.data['attitude'])
        else:
            return '---'