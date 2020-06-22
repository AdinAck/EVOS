import math
import digitalio

err = None

class Screen:
    def setEncoder(encoder, button):
        Screen.e = encoder
        Screen.cursorPosition = Screen.e.position
        Screen.last_cursorPosition = None
        Screen.cursor = 0

        Screen.button = button
        Screen.button.direction = digitalio.Direction.INPUT
        Screen.button.pull = digitalio.Pull.UP

        Screen.index = 0
        Screen.selecting = True
        Screen.last_button_value = 1

    def setDisplay(display):
        Screen.d = display

    def __init__(self):
        self.components = []
        self.selectable = []

    def add(self, component):
        self.components.append(component)
        if type(component) in [Button, SingleDigitNumberSelector]:
            self.selectable.append(component)

class Button:
    def __init__(self, screen, xpos, ypos, sizex, sizey, textSize, text):
        screen.add(self)
        self.xpos = xpos
        self.ypos = ypos
        self.sizex = sizex
        self.sizey = sizey
        self.textSize = textSize
        self.text = text
        self.wrapper = Wrapper(text)
        self.xBound = 10
        self.yBound = 10

    def draw(self):
        self.wrapper.val = self.text
        Screen.d.drawRect(self.xpos, self.ypos, self.sizex, self.sizey)
        Screen.d.drawStr(self.xpos, self.ypos+self.sizey-((self.sizey-self.textSize)//2), str(self.wrapper.val))


class Text:
    def __init__(self, screen, xpos, ypos, textSize, text):
        screen.add(self)
        self.xpos = xpos
        self.ypos = ypos
        self.textSize = textSize
        self.text = text
        self.wrapper = Wrapper(text)
        self.xBound = 10
        self.yBound = 10

    def draw(self):
        self.wrapper.val = self.text
        Screen.d.drawStr(self.xpos, self.ypos, str(self.wrapper.val))

class SingleDigitNumberSelector:
    def __init__(self, screen, xpos, ypos):
        screen.add(self)
        self.xpos = xpos
        self.ypos = ypos
        self.val = 0
        self.count1 = 0
        self.count2 = 0
        self.xBound = 20
        self.yBound = 35

    def draw(self):
        if Screen.focused == self:
            if not Screen.selecting:
                if Screen.cursor == 1:
                    self.val += 1
                    self.count1 = 5
                elif self.count1 == 0:
                    Screen.d.drawTriangle(self.xpos-8,self.ypos-10, self.xpos,self.ypos-17, self.xpos+7,self.ypos-10)
                if Screen.cursor == -1:
                    self.val -= 1
                    self.count2 = 5
                elif self.count2 == 0:
                    Screen.d.drawTriangle(self.xpos-6,self.ypos+11, self.xpos,self.ypos+17, self.xpos+6,self.ypos+11)
                if self.count1 != 0:
                    self.count1 -= 1
                if self.count2 != 0:
                    self.count2 -= 1

                if self.val == 10:
                    self.val = 0
                elif self.val == -1:
                    self.val = 9

        Screen.d.drawCenterHRect(self.xpos, self.ypos, 14, 17)
        Screen.d.drawStr(self.xpos-4, self.ypos+6, str(self.val))

class Dial:
    def __init__(self, screen, xpos, ypos, radius, positionCount, minAngle=0, maxAngle=0):
        screen.add(self)
        self.xpos = xpos
        self.ypos = ypos
        self.r = radius
        self.positionCount = positionCount
        self.position = -math.pi/2
        if minAngle != maxAngle:
            self.min = math.pi*(minAngle)/180 - math.pi/2
            self.max = math.pi*(maxAngle)/180 - math.pi/2
            self.dr = (self.max-self.min)/self.positionCount
        else:
            self.dr = 2*math.pi/self.positionCount

    def draw(self):
        if self.max == self.min:
            if Screen.cursor == 1:
                self.position += self.dr
            if Screen.cursor == -1:
                self.position -= self.dr
            for i in range(self.positionCount + self.positionCount % 2):
                Screen.d.drawPixel(int((self.r)*math.cos(i*self.dr-math.pi/2))+self.xpos, int((self.r)*math.sin(i*self.dr-math.pi/2))+self.ypos)
        else:
            if Screen.cursor == 1 and self.position+self.dr <= self.max:
                self.position += self.dr
            if Screen.cursor == -1 and self.position-self.dr >= self.min:
                self.position -= self.dr
            for i in range(self.positionCount + self.positionCount % 2):
                Screen.d.drawPixel(int((self.r)*math.cos(i*self.dr-math.pi/2-(self.max-self.min)/2))+self.xpos, int((self.r)*math.sin(i*self.dr-math.pi/2-(self.max-self.min)/2))+self.ypos)

        Screen.d.drawHCircle(self.xpos, self.ypos, self.r-4)
        Screen.d.drawLine(self.xpos, self.ypos, int((self.r-4)*math.cos(self.position))+self.xpos, int((self.r-4)*math.sin(self.position))+self.ypos)

class Wrapper:
    def __init__(self,variable=None):
        self.val = variable

def update():
    global err

    Screen.last_cursorPosition = Screen.cursorPosition
    Screen.cursorPosition = Screen.e.position
    if Screen.last_cursorPosition in [None, Screen.cursorPosition]:
        Screen.cursor = 0
    elif Screen.cursorPosition - Screen.last_cursorPosition > 0:
        Screen.cursor = 1
        if Screen.selecting:
            if Screen.index < len(Screen.current.selectable)-1:
                Screen.index += 1
            else:
                Screen.index = 0
    else:
        Screen.cursor = -1
        if Screen.selecting:
            if Screen.index > -len(Screen.current.selectable):
                Screen.index -= 1
            else:
                Screen.index = -1
    try:
        Screen.focused = Screen.current.selectable[Screen.index]
    except IndexError:
        Screen.selecting = False

    for component in Screen.current.components:
        component.draw()

    if Screen.last_button_value != Screen.button.value:
        if Screen.button.value == 0 and Screen.selecting:
            Screen.selecting = False
        elif Screen.button.value == 0 and not Screen.selecting:
            Screen.selecting = True
        Screen.last_button_value = Screen.button.value

    if Screen.selecting:
        Screen.d.drawCenterRect(Screen.focused.xpos,Screen.focused.ypos,Screen.focused.xBound,Screen.focused.yBound)