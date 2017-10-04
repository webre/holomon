# Finn Weber
# jfweber
# 35 hours

import pygame, string, copy, random, sys, os, eztext
# EZTEXT is not my code or work. It was found at http://www.pygame.org/project-EzText-920-.html
# most formulas are from bulbapedia/the Pokemon series games by Nintendo

class Config:
    # Config class holds setup functions and info about the system
    slash = '\\' if os.name == 'nt' else '/'
    imagePath = os.getcwd() + slash + 'images' + slash
    blockItemPath = imagePath + 'blockitems' + slash
    blockPath = imagePath + 'blocks' + slash
    holomonPath = imagePath + 'holomon' + slash
    personPath = imagePath + 'persons' + slash
    datPath = os.getcwd() + slash + 'dat' + slash
    savePath = os.getcwd() + slash + 'save' + slash

    @staticmethod
    def gameSetup():
        # looks for all input files to populate the game's class variable lists
        Config.loadAllBlocks()
        Config.loadAllBlockItems()
        Config.loadAllTypeMatchups()
        Config.loadAllMoves()
        Config.loadAllHolomon()
        Config.loadAllPersons()
        Config.loadAllAreaMaps()
        Config.loadAllItems()
        Config.loadExitLinks()

    @staticmethod
    def loadAllBlocks():
        Game.allBlocks = dict()
        blocks = open(Config.datPath + 'blockimages.dat', 'rU')

        for line in blocks:
            words = line.split()
            # name/key of block, then image name
            Game.allBlocks[words[0]] = Block(Config.blockPath + words[1])

        blocks.close()
        tallgrasses = open(Config.datPath + 'tallgrasses.dat', 'rU')
        
        for line in tallgrasses:
            words = line.split()
            name = words[0]
            occurrences = []

            for index in xrange(1, len(words) - 1, 2):
                # first term is holomon name, second is % occurrence
                occurrences.append((words[index], float(words[index + 1])))

            # average level in this tall grass
            occurrences.append(int(words[-1]))
            Game.allBlocks[name] = TallGrass(occurrences)

        tallgrasses.close()

    @staticmethod
    def loadAllBlockItems():
        Game.allBlockItems = dict()

        # load name and image of all block items
        blockItems = open(Config.datPath + 'blockitemimages.dat', 'rU')
        for line in blockItems:
            words = line.split()
            Game.allBlockItems[words[0]] = BlockItem(Config.blockItemPath + \
                                          words[1])

        blockItems.close()

        # load defined signs
        signs = open(Config.datPath + 'signtext.dat', 'rU')
        for line in signs:
            words = line.split()
            Game.allBlockItems[words[0]] = Sign(' '.join(words[1:]))

        signs.close()

        Game.allBlockItems['pc'] = PC()
        Game.allBlockItems['counter'] = Counter()
    
    @staticmethod
    def loadAllTypeMatchups():
        Game.allTypeMatchups = dict()
        data = open(Config.datPath + 'matchups.dat', 'rU')
        text = data.readlines()

        # loads super effective and ineffective for each defined type
        for index in xrange(0, len(text) - 1, 2):
            first = text[index].strip().split()
            second = text[index + 1].strip().split()
            Game.allTypeMatchups[first[0]] = dict()
            matchups = Game.allTypeMatchups[first[0]]
            matchups['double'] = set(first[2:])
            matchups['half'] = set(second[2:])
    
    @staticmethod
    def loadAllMoves():
        Game.allMoves = dict()

        moves = open(Config.datPath + 'moves.dat', 'rU')
        moveList = moves.readlines()
        moves.close()

        # 8 lines between input blocks including space line
        for line in xrange(0, len(moveList), 8):
            Config.loadMove(moveList, line)

        Game.allMoves['default'] = Move('Struggle', 'Used when out of PP',
                                        10, 85, 'NORMAL', 'physical', 9999)
    
    @staticmethod
    def loadMove(moveList, line):
        # parse each line to get move statistic
        name = moveList[line].strip().split()[1]
        description = ' '.join(moveList[line + 1].strip().split()[1:])
        power = int(moveList[line + 2].strip().split()[1])
        accuracy = int(moveList[line + 3].strip().split()[1])
        holoType = moveList[line + 4].strip().split()[1]
        moveType = moveList[line + 5].strip().split()[1]
        PP = int(moveList[line + 6].strip().split()[1])

        move = Move(name, description, power, accuracy, holoType, moveType, PP)
        Game.allMoves[name] = move

    @staticmethod
    def loadAllHolomon():
        Game.allHolomon = dict()
        
        holomon = open(Config.datPath + 'holomon.dat', 'rU')
        holomonList = holomon.readlines()
        holomon.close()

        # 8 lines between input blocks including space line
        for line in xrange(0, len(holomonList), 8):
            Config.loadHolomon(holomonList, line)

    @staticmethod
    def loadHolomon(holomonList, line):
        # parse input to load image and other holomon data
        imageName = Config.holomonPath + holomonList[line].strip().split()[1]
        name = holomonList[line + 1].strip().split()[1]
        description = ' '.join(holomonList[line + 2].strip().split()[1:])
        holoType = holomonList[line + 3].strip().split()[1]
        moveset = Config.getMoveset(holomonList[line + 4].strip().split()[1:])
        baseStats = \
            Config.getBaseStats(holomonList[line + 5].strip().split()[1:])
        catchRate = int(holomonList[line + 6].strip().split()[1])

        holomon = Holomon(imageName, name, description, holoType, moveset, baseStats, catchRate)
        Game.allHolomon[name] = holomon

    @staticmethod
    def getMoveset(movesetList):
        # adds each move to the moveset dict keyed by name
        moveset = dict()
        for word in movesetList:
            moveID = word.strip(string.digits)
            level = int(word.strip(string.letters))
            moveset[level] = Game.allMoves[moveID].generate()
        return moveset

    @staticmethod
    def getBaseStats(baseStatsList):
        # gets holomon base stats as defined in file
        baseStats = dict()
        for word in baseStatsList:
            statName = word.strip(string.digits)
            value = int(word.strip(string.letters))
            baseStats[statName] = value
        return baseStats

    @staticmethod
    def loadAllPersons():
        Game.allPersons = dict()
        Game.allPersons['engineer'] = Engineer()
        Game.allPersons['shopowner'] = Shopowner()

        persons = open(Config.datPath + 'persons.dat', 'rU')
        personList = persons.readlines()
        persons.close()

        # load defined characters from file
        for line in xrange(0, len(personList), 4): # 5 lines in each trainer description (inc \n)
            Config.loadPerson(personList, line)

        trainers = open(Config.datPath + 'trainers.dat', 'rU')
        trainerList = trainers.readlines()
        trainers.close()

        # load defined trainers from file
        for line in xrange(0, len(trainerList), 6): # 7 lines in each trainer description (inc \n)
            Config.loadTrainer(trainerList, line)

    @staticmethod
    def loadPerson(personList, line):
        # get person info and add object to list
        name = personList[line].strip().split()[1]
        text = ' '.join(personList[line + 1].strip().split()[1:])
        direction = personList[line + 2].strip().split()[1]

        person = Person(name, text, direction)
        Game.allPersons[name] = person

    @staticmethod
    def loadTrainer(trainerList, line):
        # get trainer info and add object to list, add party as well
        name = trainerList[line].strip().split()[1]
        text = ' '.join(trainerList[line + 1].strip().split()[1:])
        loseText = ' '.join(trainerList[line + 2].strip().split()[1:])
        direction = trainerList[line + 3].strip().split()[1]

        party = []
        for holomonID in trainerList[line + 4].strip().split()[1:]:
            holomonName = holomonID.strip(string.digits)
            level = int(holomonID.strip(string.letters))
            party.append(Game.allHolomon[holomonName].generate(level))

        trainer = Trainer(name, text, loseText, direction, party)
        Game.allPersons[name] = trainer

    @staticmethod
    def loadAllAreaMaps():
        Game.allAreaMaps = dict()
        maps = open(Config.datPath + 'areamaps.dat', 'rU')
        mapsList = maps.readlines()
        maps.close()

        line = 0
        while line < len(mapsList):
            name = mapsList[line].split()[1]
            fullMap = []

            line += 1
            while line < len(mapsList) and mapsList[line] != '\n':
                # create the mapRow of block names to be parsed in areamap init
                fullMapRow = []
                for word in mapsList[line].split():
                    if '_' in word:
                        # there is an exit or object on the block
                        fullMapRow.append(word.split('_'))
                    else:
                        # nothing on the block
                        fullMapRow.append(word)
                fullMap.append(fullMapRow)
                line += 1
            Game.allAreaMaps[name] = AreaMap(fullMap, name)
            line += 1

    @staticmethod
    def loadAllItems():
        Game.allItems = dict()
        items = open(Config.datPath + 'items.dat', 'rU')

        # load items and info
        for line in items:
            itemList = line.split()
            name = itemList[0]
            amount = float(itemList[1])
            revive = itemList[2] == 'True'
            cost = int(itemList[3])
            Game.allItems[name] = Item(name, amount, revive, cost)
        items.close()

        # load cards and info
        cards = open(Config.datPath + 'cards.dat', 'rU')
        for line in cards:
            cardList = line.split()
            name = cardList[0]
            multiplier = float(cardList[1])
            cost = int(cardList[2])
            Game.allItems[name] = Card(name, multiplier, cost)
        cards.close()

    @staticmethod
    def loadExitLinks():
        # create dict of links between map exits to be used in game
        Game.exitLinks = dict()
        exits = open(Config.datPath + 'exitlinks.dat', 'rU')

        for line in exits:
            words = line.split()
            exit = words[1]
            info = []

            for index in xrange(3, len(words), 2):
                info.append(words[index])

            Game.exitLinks[exit] = info

        exits.close()

class Menu:
    @staticmethod
    def textBox(game, name, text):
        # main open-ended textBox function, blocks until enter pressed
        textBoxOpen = True
        Menu.drawTextBox(game, name, text)
        while textBoxOpen:            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.exit()

                if event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key)
                    if key == 'return':
                        textBoxOpen = False
            game.clock.tick(Game.fps)
    
    @staticmethod
    def drawTextBox(game, name, text):
        # back end draws textBox
        game.screen.fill(Game.white, [0, Game.height * \
                                     (1 - Game.textBoxRatio), Game.width, 
                                     Game.height * Game.textBoxRatio])
        if name != None:
            text = name + ': ' + text
        # get text list
        textList = text.split()
        
        # put all that will fit on first line into dispString
        Menu.placeText(game, textList)
        pygame.display.flip()

    @staticmethod
    def placeText(game, textList):
        # displays the string on two lines if neccessary
        dispString = ''
        while len(textList) > 0 and Game.font.size(dispString + \
                textList[0])[0] < .9 * Game.width:
            dispString += textList.pop(0) + ' '
        if len(textList) > 0:
            dispStringBelow = ' '.join(textList) # rest goes on next line
            yPosUp = Game.height * (1 - .5 * Game.textBoxRatio) - \
                Game.font.size(dispString)[1]
            yPosDown = yPosUp + Game.font.size(dispString)[1]
            surface = Game.font.render(dispString, True, Game.black)
            surfaceDown = Game.font.render(dispStringBelow, True, Game.black)
            game.screen.blit(surface, [Game.width * .05, yPosUp])
            game.screen.blit(surfaceDown, [Game.width * .05, yPosDown])
        else:
            yPos = Game.height * (1 - .5 * Game.textBoxRatio) - .5 * \
                                  Game.font.size(dispString)[1]
            surface = Game.font.render(dispString, True, Game.black)
            game.screen.blit(surface, [Game.width * .05, yPos])

    @staticmethod
    def popupMenu(game, choicesInput, backButton = False):
        # choices are strings, returns INDEX of string user clicks
        # 'back' returned for back button press
        choices = copy.deepcopy(choicesInput)
        game.screen.fill(Game.white)
        height = Game.font.size('word')[1]
        xStart = height
        yStart = height
        yPos = yStart

        if backButton:
            choices.append('Back')

        for choice in choices:
            surface = Game.font.render(choice, True, Game.black)
            game.screen.blit(surface, [xStart, yPos])
            yPos += height

        pygame.display.flip()
        return Menu.inputPopupMenu(game, choices, backButton, xStart, yStart)

    @staticmethod
    def inputPopupMenu(game, choices, backButton, xStart, yStart):
        # gets input for popup menu and returns 'back' for back button
        height = Game.font.size('word')[1]
        menuOpen = True
        while menuOpen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    xClick, yClick = event.pos
                    if yClick >= yStart and yClick < yStart + len(choices) * \
                                                              height:
                        selection = int(yClick - yStart) / int(height)
                        selection = int(selection)
                        if xClick >= xStart and xClick <= xStart + \
                                Game.font.size(choices[selection])[0]:
                            if backButton and selection == len(choices) - 1:
                                selection = 'back'
                            menuOpen = False
            game.clock.tick(Game.fps)
        return selection

    @staticmethod
    def bottomMenu(game, choicesInput, backButton = False):
        # same as above but only 4 choices, returns 'back' for back button
        choices = copy.deepcopy(choicesInput)
        length = len(choices)
        if length < 4:
            choices.extend(['-'] * (4 - length))

        backRect = Menu.drawBoxes(game, backButton)
        Menu.drawWords(game, choices, backRect, backButton)
        selection = Menu.getInput(game, backRect, backButton, length)
        
        return selection

    @staticmethod
    def drawBoxes(game, backButton):
        # draws outlines of 4 boxes at bottom
        x = 0
        y = int(Game.height * (1 - Game.textBoxRatio))
        width = Game.width
        height = int(Game.height * Game.textBoxRatio)
        rectangle = pygame.Rect(x, y, width, height)
        game.screen.fill(Game.white, rectangle)

        pygame.draw.line(game.screen, Game.black, [0, y + height / 2],
                                                  [width, y + height / 2])
        pygame.draw.line(game.screen, Game.black, [width / 2, y],
                                                  [width / 2, Game.height])

        if backButton:
            backSize = Game.font.size('Back')
            backRect = pygame.Rect((width - backSize[0]) / 2, Game.height - \
                                    backSize[1], backSize[0], backSize[1])
            backRect.center = rectangle.center
            pygame.draw.rect(game.screen, Game.white, backRect)
            pygame.draw.rect(game.screen, Game.black, backRect, 1)

        if backButton:
            return backRect

    @staticmethod
    def drawWords(game, choices, backRect, backButton):
        # places words in the 4 boxes and back button if present
        words = [[choices[0], choices[1]], [choices[2], choices[3]]]
        width = Game.width
        height = int(Game.height * Game.textBoxRatio)
        y = int(Game.height * (1 - Game.textBoxRatio))
        center = [width / 4, y + height / 4]

        for row in words:
            for word in row:
                size = Game.font.size(word)
                surface = Game.font.render(word, True, Game.black)
                game.screen.blit(surface, [center[0] - size[0] / 2,
                                           center[1] - size[1] / 2])
                pygame.display.flip()
                center[0] += width / 2
            center[1] += height / 2
            center[0] = width / 4

        if backButton:
            surface = Game.font.render('Back', True, Game.black)
            game.screen.blit(surface, [backRect[0], backRect[1]])

        pygame.display.flip()

    @staticmethod
    def getInput(game, backRect, backButton, length):
        # get click from user, returns 'back' for back
        width = Game.width
        height = int(Game.height * Game.textBoxRatio)
        y = int(Game.height * (1 - Game.textBoxRatio))
        menuOpen = True
        while menuOpen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    xClick, yClick = event.pos
                    if yClick >= y:
                        if backButton and Menu.withinBox(xClick, yClick,
                                                         backRect):
                            selection = 'back'
                        else:
                            selection = (xClick / (width / 2)) % 2 + \
                                        ((yClick - y) / (height / 2)) * 2                        
                        if selection < length or selection == 'back':
                            menuOpen = False
            game.clock.tick(Game.fps)
        return selection

    @staticmethod
    def withinBox(x, y, rectangle):
        # checks if bounds are within the given rectangle
        if y >= rectangle[1] and y <= rectangle[1] + rectangle[3] and \
                x >= rectangle[0] and x <= rectangle[0] + rectangle[2]:
            return True
        else:
            return False

class Game:
    blockSize = 24
    width = blockSize * 30
    height = blockSize * 20
    textBoxRatio = .3 # amount of vertical space textbox gets on screen
    font = None
    smallFont = None
    fps = 120
    wildProbability = .04 # probability of encounter in general for each block
    startLocation = ('Bedroom', 2, 2) # default start

    allBlocks = None
    allBlockItems = None
    allTypeMatchups = None
    allHolomon = None
    allMoves = None
    allPersons = None
    allAreaMaps = None
    exitLinks = None

    white = (255, 255, 255)
    black = (0, 0, 0)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    red = (255, 0, 0)
    paleBlue = (188, 222, 245)
    paleGreen = (140, 237, 140)
    cyan = (0, 255, 255)

    def __init__(self):
        # create screen, clock, and fonts; setup game with Config
        pygame.init()
        Game.font = pygame.font.SysFont('Helvetica', 20)
        Game.smallFont = pygame.font.SysFont('Helvetica', 14)

        self.size = (Game.width, Game.height)
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption('Holomon')

        self.clock = pygame.time.Clock()
        self.currentMap = None
        Config.gameSetup()

    def exit(self):
        # controlled exit of game
        pygame.quit()
        sys.exit()

    def mainMenu(self):
        choices = ['Holomon', 'New Game']
        # checks if a save file is present, bases options on this
        if os.path.isfile(Config.savePath + 'player.sav') and \
                os.path.isfile(Config.savePath + 'holomon.sav'):
            choices.append('Continue')
        choices.append('Quit')
        choice = Menu.popupMenu(self, choices, backButton = False)
        string = choices[choice]
        while string != 'Quit':
            if string == 'New Game':
                name = self.inputName()
                self.player = Player()
                self.player.name = name
                self.play()
                choices = ['Holomon', 'New Game', 'Continue', 'Quit']
            elif string == 'Continue':
                self.player = Player()
                self.player.load()
                self.play()
            choice = Menu.popupMenu(self, choices, backButton = False)
            string = choices[choice]
        self.exit()

    def inputName(self):
        # use eztext to get name (see citation at top)
        inputObj = eztext.Input(maxlength = 10, color = Game.black, \
                                prompt = 'Name: ', font = Game.font)
        inputObj.set_pos(10, 10)
        inputting = True
        while inputting:
            self.clock.tick(Game.fps)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.exit()
                if event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key)
                    if key == 'return':
                        inputting = False

            self.screen.fill(Game.white)
            inputObj.update(events)
            inputObj.draw(self.screen)
            pygame.display.flip()

        return inputObj.value

    def play(self):
        self.player.game = self
        self.redrawMap()

        # main game runtime loop
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                # handle movement and popup menu call
                if event.type == pygame.KEYDOWN:
                    key = pygame.key.name(event.key)
                      
                    if key == 'w': self.player.go('up')
                    elif key == 's': self.player.go('down')
                    elif key == 'a': self.player.go('left')
                    elif key == 'd': self.player.go('right')
                    elif key == 'escape': self.pauseMenu()
                    elif key == 'e': self.player.interact()

            # limits display to certain fps for performance reasons
            self.clock.tick(Game.fps)

    def redrawMap(self):
        self.screen.fill(Game.black) # clears board, like canvas.delete(ALL)
        self.player.areaMap.draw(self.screen)
        
        # flips buffers to show updated screen
        pygame.display.flip()

    def pauseMenu(self):
        # pause menu display and input handling
        choices = ['Holomon', 'Items', 'HoloCards', self.player.name, 'Save', 
                   'Quit']
        choice = Menu.popupMenu(self, choices, backButton = True)
        while choice != 'back':
            string = choices[choice]
            if string == 'Holomon':
                self.menuHolomon()
            elif string == 'Items':
                self.menuItems()
            elif string == 'HoloCards':
                self.menuCards()
            elif string == self.player.name:
                self.menuPlayer()
            elif string == 'Save':
                self.player.save()
                Menu.textBox(self, None, 'Game saved!')
                break
            elif string == 'Quit':
                self.running = False
                break

            if self.running:
                choice = Menu.popupMenu(self, choices, backButton = True)
        self.redrawMap()

    def menuHolomon(self):
        # choose a holomon to perform action on
        holomonList = [holomon.info() for holomon in self.player.party]
        choice = Menu.popupMenu(self, holomonList, backButton = True)

        while choice != 'back':
            self.holomonOptions(self.player.party[choice])
            # regenerates list in case item was used to change info
            holomonList = [holomon.info() for holomon in self.player.party]
            choice = Menu.popupMenu(self, holomonList, backButton = True)

        self.redrawMap()

    def holomonOptions(self, holomon):
        # displays different actions you can perform on a holomon in party
        choices = ['Summary', 'Move Summary', 'Switch', 'Use Item']
        choice = Menu.popupMenu(self, choices, backButton = True)

        while choice != 'back':
            string = choices[choice]
            if string == 'Summary':
                self.holomonSummary(holomon)
            elif string == 'Move Summary':
                self.moveSummary(holomon)
            elif string == 'Switch':
                self.switchHolomon(holomon)
                break
            elif string == 'Use Item':
                self.useItem(holomon)
                break
            
            choice = Menu.popupMenu(self, choices, backButton = True)

    def holomonSummary(self, holomon):
        strings = [
            holomon.name,
            holomon.description,
            'Level %d' % (holomon.level),
            'HP %d/%d' % (holomon.currentHP, holomon.getStat('hp')),
            'XP %d/%d' % (holomon.XP, holomon.XPForNextLevel()),
            '',
            'Moves: ' + \
            ', '.join([move.name for move in holomon.moves]),
            '',
            'Stats:',
            '    HP: %s' % (holomon.getStat('hp')),
            '    Attack: %s' % (holomon.getStat('attack')),
            '    Defense: %s' % (holomon.getStat('defense')),
            '    Special Attack: %s' % (holomon.getStat('specialattack')),
            '    Special Defense: %s' % (holomon.getStat('specialdefense')),
            '    Speed: %s' % (holomon.getStat('speed')),
            '']
        # displays summary of holomon
        choice = Menu.popupMenu(self, strings, backButton = True)
        while choice != 'back':
            choice = Menu.popupMenu(self, strings, backButton = True)

    def moveSummary(self, holomon):
        # displays various information about chosen move
        moveStrings = [move.info() for move in holomon.moves]

        choice = Menu.popupMenu(self, moveStrings, backButton = True)
        while choice != 'back':
            move = holomon.moves[choice]
            self.infoOnMove(move)
            choice = Menu.popupMenu(self, moveStrings, backButton = True)

    def infoOnMove(self, move):
        # prints move info
        info = [move.name,
                move.description,
                'Power: %d' % (move.power),
                'Accuracy: %d' % (move.accuracy),
                'Type: %s/%s' % (move.holoType, move.moveType),
                'PP: %d/%d' % (move.currentPP, move.PP)]

        choice = Menu.popupMenu(self, info, backButton = True)
        while choice != 'back':
            choice = Menu.popupMenu(self, info, backButton = True)

    def switchHolomon(self, holomon):
        # switches holomon in-menu
        index = 0
        for index in xrange(len(self.player.party)):
            if self.player.party[index] == holomon:
                break

        choices = [holomon.info() for holomon in self.player.party]
        choice = Menu.popupMenu(self, choices, backButton = True)
        
        if choice != 'back':
            # tuple swap
            self.player.party[index], self.player.party[choice] = \
            self.player.party[choice], self.player.party[index]

    def useItem(self, holomon):
        # display items sorted by cost to use on this holomon
        items = self.player.items.values()
        items = sorted(items, key = lambda item: item.cost)
        itemNames = [item.info() for item in items]

        choice = Menu.popupMenu(self, itemNames, backButton = True)

        if choice != 'back':
            items[choice].use(self.player, holomon)

    def menuItems(self):
        # display items sorted by cost to use on some holomon
        items = self.player.items.values()
        items = sorted(items, key = lambda item: item.cost)
        itemNames = [item.info() for item in items]

        choice = Menu.popupMenu(self, itemNames, backButton = True)

        while choice != 'back':
            self.useOnWhich(items[choice])
            items = self.player.items.values()
            items = sorted(items, key = lambda item: item.cost)
            itemNames = [item.info() for item in items]
            choice = Menu.popupMenu(self, itemNames, backButton = True)

    def useOnWhich(self, item):
        # choose holomon to use this item on
        choices = [holomon.info() for holomon in self.player.party]
        choice = Menu.popupMenu(self, choices, backButton = True)
        
        if choice != 'back':
            item.use(self.player, self.player.party[choice])
            Menu.textBox(self, None, 'Used the %s on %s!' % (item.name, self.player.party[choice].name))

    def release(self, holomon):
        # release holomon to the wild (only called from PC)
        choices = ['This will permanently release %s.' % (holomon.name), 'Continue']
        choice = Menu.popupMenu(self, choices, backButton = True)

        if choice != 'back' and choices[choice] == 'Continue':
            for index in xrange(len(self.player.party)):
                if self.player.party[index] == holomon:
                    break
            name = self.player.party.pop(index).name
            Menu.textBox(self, None, '%s released!' % (holomon.name))

    def menuCards(self):
        # view all cards in inventory
        cards = self.player.cards.values()
        cards = sorted(cards, key = lambda card: card.cost)
        cardNames = [card.info() for card in cards]

        choice = Menu.popupMenu(self, cardNames, backButton = True)
        while choice != 'back':
            choice = Menu.popupMenu(self, cardNames, backButton = True)

    def menuPlayer(self):
        # view all player data
        partyLen = len(self.player.party)
        PCLen = len(self.player.PCList)
        choices = ['Name: %s' % (self.player.name),
                   'Money: $%d' % (self.player.money),
                   '',
                   'Holomon',
                   '    In Party: %d' % (partyLen),
                   '    In PC: %d' % (PCLen),
                   '    Total: %d' % (partyLen + PCLen),
                   '']

        choice = Menu.popupMenu(self, choices, backButton = True)
        while choice != 'back':
            choice = Menu.popupMenu(self, choices, backButton = True)

    @staticmethod
    def getBlock(block, blockItem = None, person = None, exit = None):
        # produces the desired block for the user without shallow copies
        blockObj = Game.allBlocks[block].copy()

        # adds whatever addon the block has
        if blockItem != None:
            index = blockItem
            blockObj.blockItem = Game.allBlockItems[index].copy()
        elif person != None:
            index = person
            blockObj.person = Game.allPersons[index].copy()
        elif exit != None:
            index = exit.strip(string.letters)
            blockObj.exit = index
        
        return blockObj    

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'Player'
        self.images = dict()
        self.images['down'] = pygame.image.load(Config.personPath + \
                                                'playerdown.png')
        self.images['up'] = pygame.image.load(Config.personPath + \
                                              'playerup.png')
        self.images['left'] = pygame.image.load(Config.personPath + \
                                                'playerleft.png')
        self.images['right'] = pygame.image.load(Config.personPath + \
                                                 'playerright.png')
        self.direction = 'down'
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        
        # set position of default start location
        self.row = Game.startLocation[1]
        self.col = Game.startLocation[2]        
        self.rect.bottom = self.row * Game.blockSize + Game.blockSize
        self.rect.left = self.col * Game.blockSize
        # give the player a map, start with default
        self.areaMap = Game.allAreaMaps[Game.startLocation[0]]
        self.areaMap.grid[self.row][self.col].person = self

        self.beatenTrainers = set()
        self.party = [Game.allHolomon['Bonchar'].generate(5)] # starter
        self.PCList = [] # all holomon that are stored in pc
        self.items = {} # all items have quantity, pop if 0
        self.cards = {}
        self.money = 0

    def load(self):
        # parse data from save file and create player based on it
        data = open(Config.savePath + 'player.sav', 'rU')
        text = data.readlines()
        self.areaMap.grid[self.row][self.col].person = None # remove original
        self.name = text[0].strip().split()[1]
        self.direction = text[1].strip().split()[1]
        self.image = self.images[self.direction]
        self.row = int(text[2].strip().split()[1])
        self.col = int(text[3].strip().split()[1])
        self.areaMap = Game.allAreaMaps[text[4].strip().split()[1]]
        self.beatenTrainers = set(text[5].strip().split()[1:])
        self.items = {}
        self.cards = {}

        # load cards and items
        for word in text[6].strip().split()[1:]:
            name = word.strip(string.digits)
            item = Game.allItems[name].copy()
            item.quantity = int(word.strip(string.letters))
            self.items[name] = item
        for word in text[7].strip().split()[1:]:
            name = word.strip(string.digits)
            card = Game.allItems[name].copy()
            card.quantity = int(word.strip(string.letters))
            self.cards[name] = card

        self.money = int(text[8].strip().split()[1])
        self.rect.bottom = self.row * Game.blockSize + Game.blockSize
        self.rect.left = self.col * Game.blockSize
        self.areaMap.grid[self.row][self.col].person = self
        self.loadHolomon()

    def loadHolomon(self):
        # parse holomon in party and pc from file and add to player data
        data = open(Config.savePath + 'holomon.sav', 'rU')
        text = data.readlines()
        line = 0
        party = []
        PCList = []
        endParty = False
        while line < len(text):
            name = text[line].strip()
            level = int(text[line + 1].strip().split()[1])
            holomon = Game.allHolomon[name].generate(level)
            holomon.currentHP = int(text[line + 2].strip().split()[1])
            holomon.XP = int(text[line + 3].strip().split()[1])
            holomon.moves = []

            # get moves
            for word in text[line + 4].strip().split()[1:]:
                move = Game.allMoves[word.strip(string.digits)].generate()
                move.currentPP = int(word.strip(string.letters))
                holomon.moves.append(move)

            holomon.IVs = {word.strip(string.digits): \
                int(word.strip(string.letters)) for word in \
                text[line + 5].strip().split()[1:]}
            if not endParty:
                party.append(holomon)
            else:
                PCList.append(holomon)
            line += 7
            if line != 0 and text[line - 1].strip() == 'ENDPARTY':
                endParty = True

        self.party = party
        self.PCList = PCList

    def save(self):
        # write to save file
        data = open(Config.savePath + 'player.sav', 'w')
        data.write('name %s\n' % (self.name))
        data.write('direction %s\n' % (self.direction))
        data.write('row %s\n' % (self.row))
        data.write('col %s\n' % (self.col))
        data.write('areaMap %s\n' % (self.areaMap.name))
        data.write('beatenTrainers %s\n' % (' '.join(self.beatenTrainers)))
        data.write('items %s\n' % (' '.join(['%s%d' % \
            (item, self.items[item].quantity) for item in self.items])))
        data.write('cards %s\n' % (' '.join(['%s%d' % \
            (card, self.cards[card].quantity) for card in self.cards])))
        data.write('money %d\n' % (self.money))
        self.saveHolomon()

    def saveHolomon(self):
        # save holomon to file
        data = open(Config.savePath + 'holomon.sav', 'w')
        index = 0
        for holomon in self.party + self.PCList:
            data.write('%s\n' % (holomon.name))
            data.write('Level %d\n' % (holomon.level))
            data.write('HP %d\n' % (holomon.currentHP))
            data.write('XP %d\n' % (holomon.XP))
            data.write('Moves %s\n' % (' '.join(['%s%d' % \
                (move.name, move.currentPP) for move in holomon.moves])))
            data.write('IVs %s\n' % (' '.join(['%s%d' % \
                (stat, holomon.IVs[stat]) for stat in holomon.IVs])))
            index += 1
            if index == len(self.party):
                data.write('ENDPARTY\n')
            else:
                data.write('\n')

    def go(self, direction):
        # handles all movement based on move direction
        self.direction = direction
        self.image = self.images[self.direction]
        self.removeFromGrid()
        if self.canMove(direction) == True:
            if direction == 'up': self.row -= 1
            elif direction == 'down': self.row += 1
            elif direction == 'left': self.col -= 1
            elif direction == 'right': self.col += 1
        elif self.areaMap.grid[self.row][self.col].exit != None:
            exit = self.areaMap.grid[self.row][self.col].exit
            entrance = Game.exitLinks[exit][1]
            enterDir = Game.exitLinks[entrance][2]
            # confirm correct exit direction is same as player direction
            if set([enterDir, direction]) == set(['left', 'right']) or \
               set([enterDir, direction]) == set(['up', 'down']):
                self.changeMap(direction)
        self.rect.bottom = self.row * Game.blockSize + Game.blockSize
        self.rect.left = self.col * Game.blockSize
        self.addToGrid()
        self.game.redrawMap()
        self.checkPosition()
        self.game.redrawMap()
    
    def canMove(self, direction):
        row = self.row
        col = self.col
        grid = self.areaMap.grid

        # checks if indicated block is valid and unoccupied
        if direction == 'up':
            if row <= 0 or grid[row - 1][col].person != None or \
                           grid[row - 1][col].blockItem != None:
                return False
        elif direction == 'down':
            if row >= len(grid) - 1 or grid[row + 1][col].person != None or \
                                       grid[row + 1][col].blockItem != None:
                return False
        elif direction == 'left':
            if col <= 0 or grid[row][col - 1].person != None or \
                           grid[row][col - 1].blockItem != None:
                return False
        elif direction == 'right':
            if col >= len(grid[row]) - 1 or \
                    grid[row][col + 1].person != None or \
                    grid[row][col + 1].blockItem != None:
                return False

        # can move there if tests passed
        return True

    def changeMap(self, direction):
        # switches map after using an exit
        block = self.areaMap.grid[self.row][self.col]
        exit = block.exit
        exitLink = Game.exitLinks[exit]
        newAreaMap = Game.allAreaMaps[exitLink[0]].copy() # [0] is the new map

        for row in xrange(len(newAreaMap.grid)):
            for col in xrange(len(newAreaMap.grid[row])):
                # exitLink[1] is entrance number
                if newAreaMap.grid[row][col].exit == exitLink[1]:
                    self.row = row
                    self.col = col
                    break

        self.areaMap = newAreaMap
        self.direction = exitLink[2]

    def removeFromGrid(self):
        # simple function to remove from grid before moving
        self.areaMap.grid[self.row][self.col].person = None

    def addToGrid(self):
        # simple function to add back to grid after moving
        self.areaMap.grid[self.row][self.col].person = self

    def checkPosition(self):
        # checks for sightlines etc and responds to player if trainer/wild found
        self.areaMap.grid[self.row][self.col].respondToStep(self)
        self.checkRow()
        self.checkCol()
        
    def checkRow(self):
        playerPassed = False

        # goes through every column in row to respond if sightline isn't broken
        for col in xrange(len(self.areaMap.grid[self.row])):
            block = self.areaMap.grid[self.row][col]
            if block.person == self:
                playerPassed = True

            facingPlayer = 'left' if playerPassed else 'right'

            # respond to player
            if isinstance(block.person, Trainer) and \
                    block.person.direction == facingPlayer and \
                    block.person.name not in self.beatenTrainers:
                if self.sightlineFromHere(self.row, col):
                    block.person.respondToInteract(self)

    def checkCol(self):
        playerPassed = False

        # goes through every row in column to respond if sightline isn't broken
        for row in xrange(len(self.areaMap.grid)):
            block = self.areaMap.grid[row][self.col]
            if block.person == self:
                playerPassed = True

            facingPlayer = 'up' if playerPassed else 'down'

            # respond to player
            if isinstance(block.person, Trainer) and \
                    block.person.direction == facingPlayer and \
                    block.person.name not in self.beatenTrainers:
                if self.sightlineFromHere(row, self.col):
                    block.person.respondToInteract(self)

    def sightlineFromHere(self, row, col):
        # check sightline, helper for checkPosition(), finds obstructions
        if row == self.row and col < self.col:
            for col in xrange(col + 1, self.col):
                block = self.areaMap.grid[row][col]
                if block.person != None or block.blockItem != None:
                    return False
        elif row == self.row and col > self.col:
            for col in xrange(self.col + 1, col):
                block = self.areaMap.grid[row][col]
                if block.person != None or block.blockItem != None:
                    return False
        elif col == self.col and row < self.row:
            for row in xrange(row + 1, self.row):
                block = self.areaMap.grid[row][col]
                if block.person != None or block.blockItem != None:
                    return False
        elif col == self.col and row > self.row:
            for row in xrange(self.row + 1, row):
                block = self.areaMap.grid[row][col]
                if block.person != None or block.blockItem != None:
                    return False

        return True

    def interact(self):
        row = self.row
        col = self.col
        grid = self.areaMap.grid
        direction = self.direction

        # interacts with adjacent object (what you're looking at)
        if direction == 'up' and row > 0:
            grid[row - 1][col].respondToInteract(self)
        elif direction == 'down' and row < len(grid) - 1:
            grid[row + 1][col].respondToInteract(self)
        elif direction == 'left' and col > 0:
            grid[row][col - 1].respondToInteract(self)
        elif direction == 'right' and col < len(grid[row]) - 1:
            grid[row][col + 1].respondToInteract(self)

class AreaMap:
    def __init__(self, mapInput = None, name = ''):
        # get input from Config and parse to form this areaMap
        self.name = name
        if mapInput == None:
            self.grid = None
        else:
            self.grid = []

            for row in xrange(len(mapInput)):
                gridLine = []

                for col in xrange(len(mapInput[row])):
                    block = mapInput[row][col]
                    result = self.processBlockInput(block)
                    # setting bottom of rect so add extra block below row
                    result.rect.left = self.startX(len(mapInput[row])) + \
                        col * Game.blockSize
                    result.rect.bottom = self.startY(len(mapInput)) + \
                        row * Game.blockSize + Game.blockSize

                    gridLine.append(result)
                
                self.grid.append(gridLine)

    def processBlockInput(self, block):
        # parses single block input
        if type(block) == str: # empty
            blockType = block
            result = Game.getBlock(blockType)
        else:
            blockType = block[0]
            onBlock = block[1]
            
            if onBlock.strip(string.digits) == 'exit': # is a map exit
                result = Game.getBlock(blockType, exit = onBlock)
            elif onBlock in Game.allPersons:
                result = Game.getBlock(blockType, person = onBlock)
            elif onBlock in Game.allBlockItems:
                result = Game.getBlock(blockType, blockItem = onBlock)

        return result

    def draw(self, screen):
        # simple draw self function draws every block
        for row in self.grid:
            for block in row:
                block.draw(screen)

    def copy(self):
        # makes a deep copy of areamap and returns it 
        newGrid = []

        for row in xrange(len(self.grid)):
            gridLine = []

            for col in xrange(len(self.grid[row])):
                block = self.grid[row][col]
                result = block.copy()
                # setting bottom of rect so add extra block below row
                result.rect.left = self.startX(len(self.grid[0])) + \
                    col * Game.blockSize
                result.rect.bottom = self.startY(len(self.grid)) + \
                    row * Game.blockSize + Game.blockSize

                gridLine.append(result)
            newGrid.append(gridLine)

        newMap = AreaMap(name = self.name)
        newMap.grid = newGrid
        return newMap

    def startX(self, numBlocksWidth):
        # calculates start from number of blocks
        displayWidth = Game.blockSize * numBlocksWidth
        windowWidth = Game.width
        return (windowWidth - displayWidth) / 2.0

    def startY(self, numBlocksHeight):
        # calculates start from number of blocks
        displayHeight = Game.blockSize * numBlocksHeight
        windowHeight = Game.height
        return (windowHeight - displayHeight) / 2.0

class Block(pygame.sprite.Sprite):
    def __init__(self, imageName):
        # blocks are empty by default
        pygame.sprite.Sprite.__init__(self)
        self.person = None
        self.blockItem = None
        self.exit = None

        self.imageName = imageName
        self.image = pygame.image.load(imageName)
        self.rect = self.image.get_rect()

    def draw(self, screen):
        # draw block and directly draw anything on it
        screen.blit(self.image, self.rect)
        if self.blockItem != None:
            self.blockItem.rect.left = self.rect.left
            self.blockItem.rect.bottom = self.rect.bottom
            screen.blit(self.blockItem.image, self.blockItem.rect)
        elif self.person != None:
            self.person.rect.left = self.rect.left
            self.person.rect.bottom = self.rect.bottom
            screen.blit(self.person.image, self.person.rect)

    def respondToStep(self, player):
        # only tallgrass responds to step
        pass

    def respondToInteract(self, player):
        # decide if player or blockitem or none or person, have them respond
        if self.blockItem != None:
            self.blockItem.respondToInteract(player)
        elif self.person != None:
            self.person.respondToInteract(player)

    def copy(self):
        # return deep copy of block and item on it
        newBlock = Block(self.imageName)
        
        if self.blockItem != None:
            newBlock.blockItem = self.blockItem.copy()
        elif self.person != None:
            newBlock.person = self.person.copy()
        elif self.exit != None:
            newBlock.exit = self.exit

        return newBlock

class TallGrass(Block):
    def __init__(self, occurrences):
        # occurrences is dict of {holomon name: percentage} pairs
        Block.__init__(self, Config.blockPath + 'tallgrass.png')
        self.occurrences = occurrences

    def respondToStep(self, player):
        # use rand and Game.wildProbability, then use occurrences and do battle
        if random.random() < Game.wildProbability:
            choice = random.random()
            index = 0
            total = self.occurrences[index][1]
            while total <= choice and index < len(self.occurrences) - 2:
                index += 1
                total += self.occurrences[index][1]
            wildName = self.occurrences[index][0]
            wildLevel = self.occurrences[-1] + random.randint(-1, 1)
            holomon = Game.allHolomon[wildName].generate(wildLevel)
            holomon.respondToInteract(player)

    def copy(self):
        # deep copy of block is returned
        newTallGrass = TallGrass(copy.deepcopy(self.occurrences))
        
        if self.blockItem != None:
            newTallGrass.blockItem = self.blockItem.copy()
        elif self.person != None:
            newTallGrass.person = self.person.copy()
        elif self.exit != None:
            newTallGrass.exit = self.exit

        return newTallGrass

class BlockItem(pygame.sprite.Sprite):
    def __init__(self, imageName):
        # by default, block items just block movement
        pygame.sprite.Sprite.__init__(self)
        self.imageName = imageName
        self.image = pygame.image.load(imageName)
        self.rect = self.image.get_rect()

    def respondToInteract(self, player):
        pass

    def copy(self):
        return BlockItem(self.imageName)

class PC(BlockItem):
    # allows player to store holomon
    def __init__(self):
        BlockItem.__init__(self, Config.blockItemPath + 'pc.png')

    def respondToInteract(self, player):
        # start pc interface
        Menu.textBox(player.game, None, '%s booted up the PC.' % (player.name))
        choices = ['Deposit', 'Withdraw']
        choice = Menu.popupMenu(player.game, choices, backButton = True)
        while choice != 'back':
            string = choices[choice]
            if string == 'Deposit':
                if len(player.party) < 2:
                    Menu.textBox(player.game, None, 'Can\'t deposit your last Holomon!')
                elif len(player.PCList) >= 17 ** 2:
                    Menu.textBox(player.game, None, 'Not enough room in PC!')
                else:
                    self.deposit(player)
            elif string == 'Withdraw':
                if len(player.party) >= 6:
                    Menu.textBox(player.game, None, 'Party full!')
                elif len(player.PCList) < 1:
                    Menu.textBox(player.game, None, 'PC empty!')
                else:
                    self.withdraw(player)
            choice = Menu.popupMenu(player.game, choices, backButton = True)

        player.game.redrawMap()

    def deposit(self, player):
        # deposit menu for pc
        infos = [holomon.info() for holomon in player.party]
        choice = Menu.popupMenu(player.game, infos, backButton = 'True')

        if choice != 'back':
            holomon = player.party.pop(choice)
            holomon.heal()
            player.PCList.append(holomon)
            Menu.textBox(player.game, None, '%s deposited in PC!' % (holomon.name))

    def withdraw(self, player):
        # withdraw menu for pc
        boxes = self.initBoxes(player.PCList)
        boxNames = ['Box %d' % (index + 1) for index in xrange(len(boxes))]
        choice = Menu.popupMenu(player.game, boxNames, backButton = True)
        if choice != 'back':
            self.whichWithdraw(player, boxes, choice)

    def whichWithdraw(self, player, boxes, boxIndex):
        # choose which holomon to withdraw
        boxesStrings = [[holomon.info() for holomon in box] for box in boxes]
        thisBoxStrings = boxesStrings[boxIndex]
        choice = Menu.popupMenu(player.game, thisBoxStrings, backButton = True)

        if choice != 'back':
            holomonIndex = boxIndex * 17 + choice
            holomon = player.PCList.pop(holomonIndex)
            player.party.append(holomon)
            Menu.textBox(player.game, None, '%s added to party!' % (holomon.name))

    def initBoxes(self, PCList):
        # create 2D list representing list of boxes of holomon
        boxes = [[]]
        listCopy = [holomon.copy() for holomon in PCList]
        index = 0
        while len(listCopy) > 0:
            if len(boxes[index]) >= 17:
                boxes.append([])
                index += 1
            boxes[index].append(listCopy.pop(0))
        return boxes

    def copy(self):
        return PC()

class Counter(BlockItem):
    def __init__(self):
        BlockItem.__init__(self, Config.blockItemPath + 'counter.png')

    def respondToInteract(self, player):
        # look behind counter and have person there respond
        grid = player.areaMap.grid
        if player.direction == 'up' and player.row > 1:
            grid[player.row - 2][player.col].respondToInteract(player)
        elif player.direction == 'down' and player.row < len(grid) - 2:
            grid[player.row + 2][player.col].respondToInteract(player)
        elif player.direction == 'left' and player.col > 1:
            grid[player.row][player.col - 2].respondToInteract(player)
        elif player.direction == 'right' and player.col < len(grid[0]) - 2:
            grid[player.row][player.col + 2].respondToInteract(player)

    def copy(self):
        return Counter()

class Sign(BlockItem):
    # displays text when player interacts
    def __init__(self, text):
        BlockItem.__init__(self, Config.blockItemPath + 'sign.png')
        self.text = text

    def respondToInteract(self, player):
        # prints textbox
        Menu.textBox(player.game, None, self.text)
        player.game.redrawMap()

    def copy(self):
        return Sign(self.text)

class Person(pygame.sprite.Sprite):
    def __init__(self, name, text, direction = 'down'):
        # person is just a character that speaks to the player
        pygame.sprite.Sprite.__init__(self)
        path = Config.personPath
        self.images = dict()
        self.images['down'] = pygame.image.load(path + 'persondown.png')
        self.images['up'] = pygame.image.load(path + 'personup.png')
        self.images['left'] = pygame.image.load(path + 'personleft.png')
        self.images['right'] = pygame.image.load(path + 'personright.png')
        self.direction = direction
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()
        self.name = name
        self.text = text

    def respondToInteract(self, player):
        # just tell player text
        Menu.textBox(player.game, self.name, self.text)
        player.game.redrawMap()

    def copy(self):
        return Person(self.name, self.text, self.direction)

class Trainer(Person):
    def __init__(self, name, text, loseText, direction, party):
        # party is list of trainer's 6 holomon
        Person.__init__(self, name, text, direction = 'down')
        path = Config.personPath
        self.party = party
        self.loseText = loseText
        self.images = dict()
        self.images['down'] = pygame.image.load(path + 'trainerdown.png')
        self.images['up'] = pygame.image.load(path + 'trainerup.png')
        self.images['left'] = pygame.image.load(path + 'trainerleft.png')
        self.images['right'] = pygame.image.load(path + 'trainerright.png')
        self.direction = direction
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()

    def respondToInteract(self, player):
        # setup battle if not already beaten
        if self.name not in player.beatenTrainers:
            Menu.textBox(player.game, self.name, self.text)
            battle = Battle(player, trainer = self)
            battle.startBattle()
            if battle.canFight(player.party):                
                player.game.redrawMap()
                Menu.textBox(player.game, self.name, self.loseText)
                player.beatenTrainers.add(self.name)
                player.money += self.calculateMoney()
                player.game.redrawMap()
            else:
                Menu.textBox(player.game, None, 
                             '%s is out of usable Holomon. %s whited out!' % \
                             (player.name, player.name))
                player.game.running = False
        else:
            Menu.textBox(player.game, self.name, self.loseText)
            player.game.redrawMap()

    def copy(self):
        # deepcopy trainer
        newParty = []
        for holomon in self.party:
            newParty.append(holomon.copy())
        return Trainer(self.name, self.text, self.loseText, self.direction,
                       newParty)

    def calculateMoney(self):
        # calculate reward money
        base = 50
        money = base * self.party[-1].level
        return money

class Engineer(Person):
    def __init__(self, direction = 'down'):
        # engineer heals all party members
        Person.__init__(self, 'Engineer', 'Let me heal your Holomon for you.',
                        direction)
        path = Config.personPath
        self.images = dict()
        self.images['down'] = pygame.image.load(path + 'engineerdown.png')
        self.images['up'] = pygame.image.load(path + 'engineerup.png')
        self.images['left'] = pygame.image.load(path + 'engineerleft.png')
        self.images['right'] = pygame.image.load(path + 'engineerright.png')
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()

    def respondToInteract(self, player):
        # heals all party holomon
        Menu.textBox(player.game, self.name, self.text)
        for holomon in player.party:
            holomon.heal()
        Menu.textBox(player.game, self.name,
                     'All Holomon restored to full health!')
        player.game.redrawMap()

    def copy(self):
        return Engineer(self.direction)

class Shopowner(Person):
    def __init__(self, direction = 'down'):
        # allows purchase of items
        Person.__init__(self, 'Shopowner', 
                        'Welcome! What would you like to buy?', direction)
        path = Config.personPath
        self.images = dict()
        self.images['down'] = pygame.image.load(path + 'shopownerdown.png')
        self.images['up'] = pygame.image.load(path + 'shopownerup.png')
        self.images['left'] = pygame.image.load(path + 'shopownerleft.png')
        self.images['right'] = pygame.image.load(path + 'shopownerright.png')
        self.image = self.images[self.direction]
        self.rect = self.image.get_rect()

    def respondToInteract(self, player):
        # sort items by cost and display items with player quantity and cost
        Menu.textBox(player.game, self.name, self.text)
        itemList = [Game.allItems[key].copy() for key in Game.allItems]
        itemList = sorted(itemList, key = lambda item: item.cost) # lambda item: 
        buyList = [item.display(player) for item in itemList]
        choice = Menu.popupMenu(player.game, buyList, backButton = True)

        self.buyMenu(player, itemList, buyList, choice)

        player.game.redrawMap()

    def buyMenu(self, player, itemList, buyList, choice):
        # main loop for buy menu
        while choice != 'back':
            item = itemList[choice]
            if item.cost > player.money:
                Menu.textBox(player.game, None, 
                    'You don\'t have enough money to buy that.')
            else:
                Menu.textBox(player.game, None, 'Purchased the %s!' % \
                                                 (item.name))
                if not isinstance(item, Card):
                    if item.name in player.items:
                        player.items[item.name].quantity += 1
                    else: player.items[item.name] = item.copy()
                else:
                    if item.name in player.cards:
                        player.cards[item.name].quantity += 1
                    else: player.cards[item.name] = item.copy()

                player.money -= item.cost
                buyList = [item.display(player) for item in itemList]
            choice = Menu.popupMenu(player.game, buyList, backButton = True)

    def copy(self):
        return Shopowner(self.direction)

class Holomon(pygame.sprite.Sprite):
    def __init__(self, imageName, name, description, holoType, moveset, 
                 baseStats, catchRate):
        # base stats (and catchRate) scale from 0 to 255
        # IVs randomly from 0 to 31, stats scale by level (individual values)
        pygame.sprite.Sprite.__init__(self)
        self.imageName = imageName
        self.image = pygame.image.load(imageName)
        self.rect = self.image.get_rect()

        self.name = name
        self.level = 1
        self.XP = 0 # XP to next level
        self.moves = []
        self.description = description
        self.holoType = holoType
        self.moveset = moveset
        self.baseStats = baseStats
        self.catchRate = catchRate
        self.IVs = self.randomIVs()
        self.currentHP = self.getStat('hp')

    def draw(self, screen):
        # self draw function
        screen.blit(self.image, self.rect)

    def generate(self, level):
        # like copy but with new IVs and moves; for wild or trainer
        newHolomon = self.copy()
        newHolomon.IVs = newHolomon.randomIVs()
        newHolomon.level = level
        newHolomon.XP = 0
        newHolomon.currentHP = newHolomon.getStat('hp')

        # get 4 random moves from moveset < level, full currentPP
        validMoves = []
        for move in self.moveset:
            if move <= newHolomon.level:
                validMoves.append(self.moveset[move].generate())

        if len(validMoves) < 4:
            newHolomon.moves = validMoves
        else:
            newHolomon.moves = random.sample(validMoves, 4)
        
        return newHolomon

    def copy(self):
        # same IVs, for loading from save
        newHolomon = Holomon(self.imageName, self.name, self.description, self.holoType, self.moveset, self.baseStats, self.catchRate)
        newHolomon.IVs = copy.deepcopy(self.IVs)
        newHolomon.level = self.level
        newHolomon.XP = self.XP
        newHolomon.moves = [move.copy() for move in self.moves] # keeps same currentPP
        newHolomon.currentHP = self.currentHP
        return newHolomon

    def heal(self):
        # heal HP and PP
        self.currentHP = self.getStat('hp')
        for move in self.moves:
            move.currentPP = move.PP

    def randomIVs(self):
        # set random IVs and return
        IVs = dict()
        for key in self.baseStats:
            IVs[key] = random.randint(0, 31)
        return IVs

    def getStat(self, statName):
        # returns dict of attack, defense, etc, based on base stats and ivs
        base = self.baseStats[statName]
        iv = self.IVs[statName]

        # pokemon stat formulas from bulbapedia.bulbagarden.net/wiki/Stats
        if statName == 'hp':
            finalStat = int((iv + 2 * base + 100) * self.level / 100.0 + 10)
        else:
            finalStat = int((iv + 2 * base) * self.level / 100.0 + 5)

        return finalStat

    def getAllStats(self):
        # returns modified stats (with IVs)
        allStats = dict()
        for key in self.baseStats:
            allStats[key] = self.getStat(key)
        return allStats

    def info(self):
        # in-battle display
        string = '%s - Lv%d - %d/%d HP' % (self.name, self.level, self.currentHP, self.getStat('hp'))
        return string

    def updateXP(self, battle, holomon, wild = False):
        # updates XP and checks for level up etc
        if self.level < 100:
            self.XP += holomon.calculateXPReward() * (1 if wild else 1.5)
            self.XP = int(self.XP)
            battle.drawBackground()
            self.updateLevel(battle)

    def updateLevel(self, battle):
        # check xp, level up, check new moves and evolutions
        HPDifference = self.getStat('hp') - self.currentHP
        while self.XP >= self.XPForNextLevel() and self.level < 100:
            self.XP -= self.XPForNextLevel()
            self.level += 1
            self.currentHP = self.getStat('hp') - HPDifference
            battle.drawBackground()
            Menu.textBox(battle.player.game, None, 'Leveled up!')
            if self.level in self.moveset:
                self.checkNewMove(self.moveset[self.level], battle)
        self.currentHP = self.getStat('hp') - HPDifference

    def checkNewMove(self, move, battle):
        # check if can learn new move, menus drawn for this if so
        if len(self.moves) < 4:
            self.moves.append(move.generate())
            Menu.textBox(game, None, '%s learned %s!' % (self.name, move.name))
            battle.drawBackground()
        else:
            Menu.textBox(battle.player.game, None, 
                '%s can learn %s. Which move to overwrite?' % \
                (self.name, move.name))
            
            moveNames = [move.info() for move in self.moves]
            choice = Menu.bottomMenu(battle.player.game, moveNames, 
                                     backButton = True)
            
            if choice != 'back':
                self.moves[choice] = move.generate()
                battle.drawBackground()
                Menu.textBox(battle.player.game, None, '%s learned %s!' % \
                            (self.name, move.name))
                battle.drawBackground()
            else:
                battle.drawBackground()
                Menu.textBox(battle.player.game, None, \
                    '%s didn\'t learn %s.' % (self.name, move.name))
                battle.drawBackground()

    def calculateXPReward(self):
        # calculate xp reward if this pokemon fainted
        n = self.level
        baseXP = 5 + self.level * 2
        reward = n * baseXP
        return int(reward)

    def XPForNextLevel(self):
        # calculate amount needed for next level from this level
        n = self.level
        neededXP = ((n + 1) ** 3 - n ** 3) * 6.0 / 5.0
        return int(neededXP)

    def respondToInteract(self, player):
        # fight wild pokemon with respondToInteract
        Menu.textBox(player.game, None, 'A wild %s appeared!' % (self.name))
        battle = Battle(player, wild = self)
        battle.startBattle()
        if not battle.canFight(player.party):
            Menu.textBox(player.game, None, 
                '%s is out of usable Holomon. %s whited out!' % \
                (player.name, player.name))
            player.game.running = False
        player.game.redrawMap()

class Move:
    def __init__(self, name, description, power, accuracy, holoType, moveType, 
                 PP):
        # stores info on this move
        self.name = name
        self.description = description
        self.power = power
        self.accuracy = accuracy
        self.holoType = holoType
        self.moveType = moveType
        self.PP = PP
        self.currentPP = self.PP

    def copy(self):
        # current PP copy
        newMove = Move(self.name, self.description, self.power, self.accuracy, 
                       self.holoType, self.moveType, self.PP)
        newMove.currentPP = self.currentPP
        return newMove

    def generate(self):
        # full PP copy
        newMove = Move(self.name, self.description, self.power, self.accuracy,
                       self.holoType, self.moveType, self.PP)
        return newMove

    def info(self):
        # in-battle display
        string = '%s - %d/%d PP' % (self.name, self.currentPP, self.PP)
        return string

class Item:
    def __init__(self, name, healAmount, canRevive, cost):
        # heal amount is fraction for revive
        self.name = name
        self.healAmount = healAmount
        self.canRevive = canRevive
        self.quantity = 1
        self.cost = cost

    def use(self, player, holomon):
        # use revive type item or heal item
        self.decrementItem(player.items)
        if self.canRevive and holomon.currentHP == 0:
            holomon.currentHP += int(holomon.getStat('hp') * self.healAmount)
        elif not self.canRevive and not holomon.currentHP == 0:
            holomon.currentHP += int(self.healAmount)
            if holomon.currentHP > holomon.getStat('hp'):
                holomon.currentHP = holomon.getStat('hp')

    def info(self):
        # for selecting which to use
        return '%s x%d' % (self.name, self.quantity)

    def display(self, player):
        # for shop display
        if self.name not in player.items:
            quantityDisp = 0
        else:
            quantityDisp = player.items[self.name].quantity

        return '%s (%d) - $%s' % (self.name, quantityDisp, self.cost)

    def copy(self):
        newItem = Item(self.name, self.healAmount, self.canRevive, self.cost)
        # quantity is 1
        return newItem

    def decrementItem(self, itemDict):
        # pops from dict if out of item
        self.quantity -= 1
        if self.quantity < 1:
            del itemDict[self.name]

class Card(Item):
    def __init__(self, name, multiplier, cost):
        # multiplier multiplies by catchrate
        self.name = name
        self.multiplier = multiplier
        self.quantity = 1
        self.cost = cost

    def use(self, player, holomon): # returns true or false if caught or not
        self.decrementItem(player.cards)
        if self.multiplier == -1: # quantum computing card (masterball)
            return True
        modCatchRate = (3 * holomon.getStat('hp') - 2 * holomon.currentHP) * \
            holomon.catchRate * self.multiplier / (3.0 * holomon.getStat('hp'))
        probability = modCatchRate / 255.0
        
        if random.random() <= probability:
            return True
        else:
            return False

    def display(self, player):
        # for shop menu
        if self.name not in player.cards:
            quantityDisp = 0
        else:
            quantityDisp = player.cards[self.name].quantity

        return '%s (%d) - $%s' % (self.name, quantityDisp, self.cost)

    def copy(self):
        newCard = Card(self.name, self.multiplier, self.cost)
        # quantity is 1
        return newCard

class Battle:
    def __init__(self, player, trainer = None, wild = None):
        # handles all types of battles
        self.player = player
        self.trainer = trainer
        self.wild = wild
        self.battleType = 'trainer' if trainer != None else 'wild'
        self.friendlyTeam = player.party

        if self.battleType == 'trainer':
            self.enemyTeam = trainer.party
        else:
            self.enemyTeam = [wild]

        self.escapes = 1

    def startBattle(self):
        # true if player wins, false otherwise
        self.friendlyOut = self.friendlyTeam[0]
        self.enemyOut = self.enemyTeam[0]
        self.run = False
        self.runFailed = False
        self.wildCaught = False

        while not self.run and not self.wildCaught and \
            self.canFight(self.friendlyTeam) and self.canFight(self.enemyTeam):
            if self.friendlyOut.currentHP == 0:
                Menu.textBox(self.player.game, None, '%s fainted!' % \
                    (self.friendlyOut.name))
                self.friendlySwitch() # doesn't show pokemon with 0 health
            elif self.enemyOut.currentHP == 0: # enemy's fainted
                self.enemySwitch()

            if self.friendlyOut.currentHP != 0 and self.enemyOut.currentHP != 0:
                self.playTurn()

        # now it ends if one has all 0 hp's etc
        self.drawBackground()
        if self.battleType == 'wild':
            if self.run:
                Menu.textBox(self.player.game, None, 'Got away safely!')
            elif self.wildCaught:
                Menu.textBox(self.player.game, None, 'Wild %s captured!' % \
                    (self.enemyOut.name))
            else: # also check for caught with card!!
                Menu.textBox(self.player.game, None, 'Defeated wild %s!' % \
                    (self.enemyOut.name))
        elif self.canFight(self.friendlyTeam):
            Menu.textBox(self.player.game, None, 'Defeated trainer %s!' % \
                (self.trainer.name))

    def playTurn(self):
        if self.friendlyOut.getStat('speed') > self.enemyOut.getStat('speed'):
            friendlyFirst = True
        elif self.friendlyOut.getStat('speed') < self.enemyOut.getStat('speed'):
            friendlyFirst = False
        else:
            friendlyFirst = (random.randint(0, 1) == 1)

        friendlyAttack = self.friendlyTurn() # list of args
        enemyAttack = self.enemyTurn() # list of args
        
        if self.run:
            pass
        elif self.runFailed:
            Menu.textBox(self.player.game, None, 'Can\'t escape.')
            self.runFailed = False
            self.attack(self.enemyOut, enemyAttack, self.friendlyOut)
        elif friendlyFirst:
            if friendlyAttack != None and friendlyAttack != False:
                self.attack(self.friendlyOut, friendlyAttack, self.enemyOut)
            if self.enemyOut.currentHP != 0 and not self.wildCaught:
                self.attack(self.enemyOut, enemyAttack, self.friendlyOut)
        elif not self.wildCaught:
            self.attack(self.enemyOut, enemyAttack, self.friendlyOut)
            if friendlyAttack != None and self.friendlyOut.currentHP != 0:
                self.attack(self.friendlyOut, friendlyAttack, self.enemyOut)

        if self.enemyOut.currentHP == 0:
            Menu.textBox(self.player.game, None, '%s fainted!' % \
                (self.enemyOut.name))
            wild = self.battleType == 'wild'
            self.friendlyOut.updateXP(self, self.enemyOut, wild)
            self.drawBackground()

    def friendlyTurn(self):
        # figure out if wild or trainer, adjust menu options
        playerTurn = True
        attack = None
        choices = ['Attack', 'Item', 'Switch', 'Run']

        while playerTurn == True:
            self.drawBackground()
            action = choices[Menu.bottomMenu(self.player.game, choices)] # returns index
            if action == 'Attack': # only this one sets the attack to return
                if self.canAttack(self.friendlyOut):
                    attack = self.selectAttack()
                else:
                    attack = Game.allMoves['default'].generate()
                playerTurn = attack # set to True if turn goes on
            elif action == 'Switch':
                playerTurn = self.switch()
            elif action == 'Item':
                playerTurn = self.pickItem()
            elif action == 'Run':
                playerTurn = self.runAway()

        if attack == True or attack == False:
            attack = None

        return attack
    
    def selectAttack(self):
        # returns move or True if no move and turn goes on
        selectingAttack = True
        moveNames = [move.info() for move in self.friendlyOut.moves]
        
        while selectingAttack:
            choice = Menu.bottomMenu(self.player.game, moveNames, \
                backButton = True) # returns index or 'back'
            if choice == 'back':
                 selectingAttack = False
                 attack = True # sent through to keep turn going
            else:
                attack = self.friendlyOut.moves[choice]
                if attack.currentPP != 0:
                    selectingAttack = False
                else:
                    Menu.textBox(self.player.game, None, \
                        'No PP left for that move')
        return attack
    
    def switch(self):
        result = self.friendlySwitch()
        return result == 'noswitch' # true, keep turn going if no switch

    def pickItem(self):
        # pick item to use
        if self.battleType == 'trainer':
            items = copy.deepcopy(self.player.items.values())
        else:
            items = copy.deepcopy(self.player.items.values() + \
                self.player.cards.values())

        items = sorted(items, key = lambda item: item.cost)
        itemNames = [item.info() for item in items]

        choosingItem = True
        while choosingItem:
            choice = Menu.popupMenu(self.player.game, itemNames, 
                                    backButton = True)

            if choice == 'back':
                return True
            else:
                item = items[choice]
                if isinstance(item, Card):
                    self.useCard(item)
                    choosingItem = False
                else:
                    choosingItem = self.whichToUseItemOn(item)
        
        return False

    def whichToUseItemOn(self, item):
        # pick holomon to use it on
        friendlyTeamNames = [holomon.info() for holomon in self.friendlyTeam]

        choosingHolomon = True
        while choosingHolomon:
            choice = Menu.popupMenu(self.player.game, friendlyTeamNames, 
                                    backButton = True)

            if choice == 'back':
                return True
            else:
                holomon = self.friendlyTeam[choice]
                item.use(self.player, holomon)
                self.drawBackground()
                Menu.textBox(self.player.game, None, 'Used the %s!' % \
                    (item.name))
                choosingHolomon = False

        return False

    def useCard(self, card):
        # try to catch wild holomon
        self.drawBackground()
        Menu.textBox(self.player.game, None, 'Used the %s!' % (card.name))
        if card.use(self.player, self.enemyOut) == True:
            self.wildCaught = True
            if len(self.friendlyTeam) < 6:
                self.friendlyTeam.append(self.enemyOut)
                Menu.textBox(self.player.game, None, 
                    '%s joined your party!' % (self.enemyOut.name))
            elif len(self.PCList) < 17 ** 2:
                # heals holomon before placing in PC
                self.enemyOut.heal()
                self.player.PCList.append(self.enemyOut)
                Menu.textBox(self.player.game, None, 
                    '%s was sent to the PC.' % (self.enemyOut.name))
            else:
                Menu.textBox(self.player.game, None, 
                    'PC full. %s was released.' % (self.enemyOut.name))
        else:
            Menu.textBox(self.player.game, None, 'It broke free!')

    def runAway(self): # returns true if player's turn continues, else false
        if self.battleType == 'trainer':
            Menu.textBox(self.player.game, None, 
                'You can\'t run from a trainer battle!')
            return True
        else:
            enemySpeed = self.enemyOut.getStat('speed')
            enemySpeed += 1 if enemySpeed == 0 else 0
            escapeProbability = (self.friendlyOut.getStat('speed') * \
                128 / enemySpeed + 30 * self.escapes) % 256
            self.escapes += 1
            self.run = random.randint(0, 255) < escapeProbability
            self.runFailed = not self.run
            return False

    def enemyTurn(self):
        # runs enemy move selection
        if self.canAttack(self.enemyOut):
            validAttacks = []
            for move in self.enemyOut.moves:
                if move.currentPP != 0:
                    validAttacks.append(move)
            
            move = random.choice(validAttacks)
        else:
            move = Move.defaultMove
        return move

    def friendlySwitch(self): # returns 'noswitch' or 'success'
        switches = [holomon.info() for holomon in self.friendlyTeam]
         # just click current one to go back
        choice = Menu.popupMenu(self.player.game, switches, backButton = False)
        while self.friendlyTeam[choice].currentHP == 0:
            Menu.textBox(self.player.game, None, 'Can\'t use fainted Holomon!')
            choice = Menu.popupMenu(self.player.game, switches,
                backButton = False)

        if choice == 0:
            return 'noswitch'
        
        self.friendlyTeam[0], self.friendlyTeam[choice] = \
            self.friendlyTeam[choice], self.friendlyTeam[0]
        self.friendlyOut = self.friendlyTeam[0]
        return 'success'

    def enemySwitch(self):
        # switches first available in their team
        canSwitch = []
        for holomon in self.enemyTeam:
            if holomon.currentHP != 0:
                canSwitch.append(holomon)

        self.enemyOut = random.choice(canSwitch)

    def canAttack(self, holomon):
        for move in holomon.moves:
            if move.currentPP != 0:
                return True
        return False

    def attack(self, attacker, move, target):
        # draw when done (background, then text box)
        move.currentPP -= 1
        if move.accuracy != 100 and random.random() > move.accuracy / 100.0:
            # move missed
            self.drawBackground()
            Menu.textBox(self.player.game, None, '%s used %s, but it missed!' % (attacker.name, move.name))
        else:
            # move hits
            result = self.calculateModifier(attacker, move, target)
            modifier = result[0]
            postString = result[1]

            prefix = 'special' if move.moveType == 'special' else ''
            attack = attacker.getStat(prefix + 'attack')
            defense = target.getStat(prefix + 'defense')

            damage = ((2 * attacker.level + 10) / 250.0 * attack / defense * move.power + 2) * modifier
            damage = int(damage)

            target.currentHP -= damage
            if target.currentHP < 0:
                target.currentHP = 0

            self.drawBackground()
            Menu.textBox(self.player.game, None, '%s used %s.%s' % (attacker.name, move.name, postString))

    def calculateModifier(self, attacker, move, target):
        # formula for attack damage from bulbapedia.bulbagarden.net/wiki/Damage
        superEffective = False
        inEffective = False

        stab = 1.5 if attacker.holoType == move.holoType else 1
        if target.holoType in Game.allTypeMatchups[move.holoType]['double']:
            typeMult = 2
            resultString = ' It\'s super effective!'
        elif target.holoType in Game.allTypeMatchups[move.holoType]['half']:
            typeMult = .5
            resultString = ' It\'s not very effective...'
        else:
            typeMult = 1
            resultString = ''

        randomMult = random.uniform(.85, 1.0)
        totalModifier = stab * typeMult * randomMult

        return (totalModifier, resultString)
        
    def drawBackground(self):
        # make color of hp bar change, just draw oval, holomon, then info box
        game = self.player.game
        game.screen.fill(Game.paleBlue)
        game.screen.fill(Game.white, [0, (1 - Game.textBoxRatio) * Game.height, Game.width, Game.textBoxRatio * Game.height])
        self.drawOvals()
        self.drawHolomon()
        self.drawInfoBox(self.friendlyOut, Game.width / 4)
        self.drawInfoBox(self.enemyOut, 3 * Game.width / 4, XP = False)
        pygame.display.flip()

    def drawOvals(self):
        # ovals for holomon to stand on
        rectangle = pygame.Rect(0, 0, Game.width * .4, Game.height * .2)
        rectangle.centery = Game.height / 2 + 10
        rectangle.centerx = Game.width / 4
        pygame.draw.ellipse(self.player.game.screen, Game.paleGreen, rectangle)
        rectangle.centerx += Game.width / 2
        pygame.draw.ellipse(self.player.game.screen, Game.paleGreen, rectangle)

    def drawHolomon(self):
        # draw holomon on ovals
        self.friendlyOut.rect.centerx = Game.width / 4
        self.friendlyOut.rect.bottom = Game.height / 2 + 10
        self.enemyOut.rect.centerx = 3 * Game.width / 4
        self.enemyOut.rect.bottom = Game.height / 2 + 10
        self.friendlyOut.draw(game.screen)
        self.enemyOut.draw(game.screen)

    def drawInfoBox(self, holomon, xCenter, XP = True):
        # draw each info box
        game = self.player.game
        boxRect = pygame.Rect(0, 0, Game.width * .4, 3 * Game.smallFont.size('Text')[1])
        boxRect.centerx = xCenter
        boxRect.top = 15

        game.screen.fill(Game.white, boxRect)
        pygame.draw.rect(game.screen, Game.black, boxRect, 1)
        surface = Game.smallFont.render(holomon.info(), True, Game.black)
        textRect = surface.get_rect()
        textRect.centerx = xCenter
        textRect.top = 18
        game.screen.blit(surface, textRect)

        self.drawHPBar(boxRect, float(holomon.currentHP) / holomon.getStat('hp'))

        if XP == True:
            self.drawXPBar(boxRect, float(holomon.XP) / holomon.XPForNextLevel())

    def drawHPBar(self, boxRect, percentFull):
        # draw hp bars for both holomon
        if percentFull <= .2:
            color = Game.red
        elif percentFull <= .5:
            color = Game.yellow
        else:
            color = Game.green
        screen = self.player.game.screen
        size = Game.smallFont.size(' HP ')
        text = Game.smallFont.render(' HP ', True, Game.black)
        barRect = pygame.Rect(boxRect[0] + size[0], boxRect[1] + size[1] + 3, boxRect[2] - size[0] - 5, size[1])
        textPos = [boxRect[0], boxRect[1] + size[1] + 3]
        screen.blit(text, textPos)

        fillRect = barRect.copy()
        fillRect.width = int(barRect.width * percentFull)
        fillRect.left = barRect.left

        pygame.draw.rect(screen, color, fillRect)
        pygame.draw.rect(screen, Game.black, barRect, 1)

    def drawXPBar(self, boxRect, percentFull):
        # draw xp bars for both holomon
        screen = self.player.game.screen
        barRect = pygame.Rect(boxRect[0], boxRect.bottom - 10, boxRect[2], 10)

        fillRect = barRect.copy()
        fillRect.width = int(barRect.width * percentFull)
        fillRect.left = barRect.left

        pygame.draw.rect(screen, Game.cyan, fillRect)
        pygame.draw.rect(screen, Game.black, barRect, 1)

    def canFight(self, party):
        # check if all in list can fight
        for holomon in party:
            if holomon.currentHP != 0:
                return True
        return False

game = Game()
game.mainMenu()