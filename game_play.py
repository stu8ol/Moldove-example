from app import app
import string
import random
import os
import math
import time
import datetime
from itertools import cycle, islice, dropwhile
import quips 
import pprint

pp = pprint.PrettyPrinter(width=50, compact=False)

class Game:

	def __init__(self):
		self.player_count= 0
		self.game_code = ''
		self.url = '' 
		self.players = []
		self.nickname = []
		self.avs = []
		self.active_card = [{'src':"", 'label':'Four to start'}]
		self.pile = []
		self.burn_pile = []
		self.deck = []
		self.player_order = []
		self.winner = []
		self.loser = None
		self.cap = 0
		self.pile_count = ""
		self.deck_count = "" 
		self.loser_board = []
		
		self.av_imgs = self.get_av_imgs()
		self.card_back = self.get_card_back()
		
		#switches
		self.game_ready = False
		self.fours = False
		
		
		#dicts
		self.nick_dict = {}
		self.crd_img_dict = {"Play anything": "",
				     "place": 'prince.jpg'}
			
		#States
		self.state = "game start"
		self.starting_player = None
		self.status = ["Game started"]
		self.turn = 0
		self.game_complete = False
		self.sec_turn = False
		self.first_round = True
		
		#Last interaction, allows the object to be deleted after a certain time period has passed without interaction
		self.last_interaction = time.time()
		
		
		
	def get_new_url(self, players):
		# Get a new game code, scramble it and supply it as an URl
		a = list(string.ascii_uppercase)
		random.shuffle(a)
		a="".join(a)
		self.game_code = a[:6]
		self.url = str(hash(self.game_code))
		# Set the number of players
		try:
			self.player_count = int(players)
			self.set_players()
		except: 
			self.url = '/play'	
		return self.url
		
	def new_status(self, s):
		today =  datetime.date.today()
		s="{}-> {}".format(time.strftime("%H:%M:%S", time.gmtime(time.time())), s)
		if not self.game_complete:
			self.status.append(s)
		if len(self.status) > 6:
			self.status = self.status[1:]
		
	def pile_update(self):
		ps = {}
		if len(self.pile) == 0:
			ps['p'] = "The pick up pile is empty"
		else:
			ps['p'] = "There are {} cards in the pile".format(len(self.pile))
		ps['d'] = "There are {} cards left in deck".format(len(self.deck))
		return ps	
	
	def set_players(self):
		try:	
			for i in range(self.player_count):
				self.players.append(Player("Player " + str(i)))
		except:
			print("Error in setting number of players - possibly {} unnacceptable".format(n))
			pass
	
	@staticmethod
	def increment_name(nn):
		a = 0
		for i in range(len(nn)):
			if nn[-(i+1)].isdigit():
				a = i+1
			else:
				break
		if a > 0:
			nn = nn[:-a] + str(int(nn[-a:])+1)
		else:
			nn = nn + str(2)
		return nn	
	
	
	def new_nickname(self, nn, game_id, av_p=None):
		for plyr in self.players:
			if nn == plyr.nickname:
				nn = self.increment_name(nn)
		np = Player(nn, game_id)
		self.players.append(np)
		self.nick_dict[nn] = np
		np.avatar_path = av_p
		if av_p is not None:
			np.reg_player = True
		#TODO capitalise nickname
		return np
		
		
	def get_ready_players(self):
		if self.first_round:
			for j, nn in enumerate(self.players):
				if nn.avatar_path == None:
					img_path = self.av_imgs[j]
					nn.avatar_path = img_path

		if len(self.players) == self.player_count:
			for i, plr in enumerate(self.players):
				plr.name = "Player " + str(i+1)
			return True
		else:
			return False
		
			
	def get_turn(self,su=True):
		pl = self.player_order[self.turn]
		if su:
			self.new_status("It is {}'s turn to play...".format(pl.nickname))
		return pl
		

	def get_av_imgs(self):
		av_im = []
		path = "app/static/avatars"
		valid_images = [".jpg",".gif",".png"]
		for f in os.listdir(path):
			ext = os.path.splitext(f)[1]
			if ext.lower() not in valid_images:
				continue
			f = '/static/avatars/' + f
			av_im.append(f)
		random.shuffle(av_im)
		return av_im
		
		
	def get_card_imgs(self, card_list, blind=False, face={}):
		card_imgs = []
		path = "/static/cards/"
		for i,c in enumerate(card_list):
			print("Getting card image source for ", c)
			if blind:
				card_imgs.append({'src':self.card_back['src'], 'label':c, 'higher':"???"})
			else:
				try:	
					if len(face) > 1:
						f=path+self.crd_img_dict[face[c]]
						alt = c
					else:	
						f=path+self.crd_img_dict[c]
						alt = "hand"+str(i)
					if c[:4] in "Seven":
						h = "LOWER"
					else: 
						h = 'HIGHER'
					card_imgs.append({'src':f, 'label':c, 'higher':h, 'alt':alt})
				except KeyError:
					pass
		return card_imgs
		
		
	def get_face_cards(self):
		print("Getting face cards")
		pcs=[]
		for pl in self.players:
			hc="Cards in hand: {}".format(len(pl.hand))
			bc="Blind Cards: {}".format(len(pl.blind_cards))
			av=pl.avatar_path		
			pcs.append({'name':pl.nickname, 'cds': self.get_card_imgs(pl.lf.keys(), face=pl.lf), 'hc':hc, 'bc':bc, 'avatar':av, 'player':pl.name})
			
		return pcs 
		

		
	#TODO get deck empty image	
	def get_card_back(self):
		cb = ["blue_back.png",
		      "gray_back.png",
		      "green_back.png",
		      "purple_back.png",
		      "red_back.png",
		      "yellow_back.png"]
		path="/static/cards/"
		random.shuffle(cb)
		return {'src':path+cb[0], 'label':cb[0][:-4]}  
		
	def get_sizes(self, player):
		sizes={}
		#height of hand
		#sizes['hand'] = str(100 + math.ceil(len(player.hand)/10)*170)+"px" 
		# width of face up sections
		if len(self.players) >= 4:
			sizes['player'] = "25%"
		elif len(self.players) == 0:
			sizes['player'] = "25%"
		else:
			sizes['player'] = "{:.2f}%".format(100/len(self.players))
		return sizes
				
	def shuffle(self):
		# set up deck of cards	
		suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
		#card_val = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
		card_val = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jordy", "Dom", "Kingy", "Ather"]
		suit_ini =  ['S', 'H', 'D', 'C']
		val_ini = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
		# Create dictionary of card values, this will allow the values of the cards to be compared
		val_dict = {k[:3]: v for v, k in enumerate(card_val)}
		val_dict["Pla"]=-1
		# calculate the number of decks required based on the number of player
		decks=self.decks(self.player_count)
		deck =  []
		for n in range(decks):
			if n == 0:
				r = ""
			else:
				r = str(n + 1)
			for i, suit in enumerate(suits):
				for j, card in enumerate(card_val):
					card_label = card + " of " + suit + r
					deck.append(card_label)
					self.crd_img_dict[card_label] = val_ini[j]+suit_ini[i]+".png"
		# Deck dict attaches value to car to allow hands to be sorted
		deck_dict = {k[:3]: v for v, k in enumerate(deck)}
		for player in self.players:
			player.dd = deck_dict
			player.val_dict = val_dict
		random.shuffle(deck)
		print("*** Deck shuffled***")
		self.new_status("*** Deck shuffled ***")
		return deck
	
	
	@staticmethod 	
	def deal(players, deck):
		# first section - blind cards
		print(players)
		for i in range(3):
			for player in players:
				print("{}, blind card: {}".format(player.name, deck[0]))
				player.blind_cards.append(deck[0])
				deck = deck[1:]
				
			
		for j in range(2):
			for player in players:
				player.hand= player.hand + deck[:3]
				deck = deck[3:]
				player.label_blind()
		return deck
	
	@staticmethod
	def decks(p):
		d = int(math.floor(p*9/52))+1
		print("{} players need {} decks".format(p,d))
		return d		
				
			
	def prep_round(self):
		if not self.game_ready:
			self.winner = []
			self.loser = []
			self.new_status("All {} players are ready!".format(self.player_count))
			deck = self.shuffle()
			self.deck = self.deal(self.players, deck)
			self.new_status("Choose your best cards to place face up")
			self.fours = self.check_for_fours()
			self.game_ready = True

	
	def restart(self, db, User):
		# record the number of shots
		self.cap = self.cap + 1
		print("Restart stage - Loser", self.loser)
		self.loser.loser_board = self.loser.loser_board + self.cap
		self.loser_board = []
		# Update values in database
		if self.loser.reg_player:
			user = User.query.filter_by(username=self.loser.nickname).first_or_404()
			user.games_lost = user.games_lost + 1
			user.shots_done =user.shots_done + self.cap
		
		
		# delete all cards in peoples hands
		for pl in self.players:
			self.loser_board.append({'name':pl.nickname, 'caps':pl.loser_board})
			pl.hand = []
			pl.blind_cards = []
			pl.blind_card_names = ["A", "B", "C"]
			pl.faceup_cards = []
			pl.dd = {}
			pl.val_dict = {}
			
			#label blind cards so that they cannot be identified
			pl.lb = {}
			pl.lf= {}
			
			if pl.reg_player:	
				user = User.query.filter_by(username=pl.nickname).first_or_404()
				user.games_played = user.games_played + 1
			
			
		#delete active card and cards in piles
		self.active_card = [{'src':"", 'label':'Four to start'}]
		self.pile = []
		self.burn_pile = []
		self.deck = []
		#Set game state to starting state
		self.game_ready=False
		self.game_complete=False
		self.starting_player = None
		self.player_order = []
		self.turn = 0
		self.state = "game start"
		self.players = []
		db.session.commit()
		print("Restart stage - loser board", self.loser_board)
		time.sleep(7)
		
		
		
		
		
		
	def check_for_fours(self):
		for player in self.players:
			for card in player.hand:
				if "Four" in card:
					self.new_status("Choose quickly! First to play a four starts")
					return True			
		return False
	
	
	@staticmethod
	def string_to_cards(sel):
		a = sel.split(",")
		return a
		
   		
	@staticmethod
	def all_fours(crds):
  		for crd in crds:
  			if crd[:4] != "Four":
  				return False
  		return True
  	
	
	def all_player_face(self):
		for player in self.players:
			if len(player.faceup_cards) != 3:
				return False
		return True
	
	def same_cards(self):
		if len(self.pile) <4:
			return False
		for n in range(3):
			#print("{} Last card {}".format(n,pile[-n-1])) 
			if self.pile[-n-1]['label'][:3] != self.pile[-n-2]['label'][:3]:
				return False
		return True
		
	def tidy(self):
		# Should the pile be burnt
		self.sec_turn = False # if the pile is burnt then the player gets another turn
		act_crd = self.active_card[0]['label']	
		if  act_crd[:3]=="Ten" or self.same_cards():
			self.burn_pile = self.burn_pile+self.pile
			self.pile = []
			self.new_status("The Pile has been burnt, there are {} cards in the burn pile".format(len(self.burn_pile)))
			print("The Pile has been burnt, there are {} cards in the burn pile".format(len(self.burn_pile)))
			print(self.burn_pile)
			self.sec_turn = True
			act_crd = "Play anything"
		
		crd = -1
		try:
			while self.pile[crd]['label'][:3] == "Thr":
				act_crd = self.pile[crd-1]['label']
				crd = crd - 1
		except IndexError:
			pass
		self.active_card = self.get_card_imgs([act_crd])
		print("Inside tidy", self.active_card)
		return self.sec_turn
	
	
	def last_picked_up(self, player):
		pw = ""
		if len(player.picked_up) == 1:
			pw = "You picked up a {}. ".format(player.picked_up[0])
		elif len(player.picked_up) == 2:
			pw = "You picked up a {} and a {}. ".format(player.picked_up[0], player.picked_up[1])
		elif len(player.picked_up) == 3:
			pw = "You picked up a {}, a {} and a {}. ".format(player.picked_up[0], player.picked_up[1], player.picked_up[2])
		elif len(player.picked_up) > 3:
			pw = "Error - picking up too many cards"
			
		if self.sec_turn:
			pw = pw + "Your turn again, play anything."	
		else:
			if len(player.picked_up) <= 0:
				pw = "Please wait..." 
		return pw
				
	
	def valid_selection(self, selection, player):
		self.last_interaction = time.time()
		card_selected = self.string_to_cards(selection)
		print("Cards selected")
		print(card_selected)
		pl = self.nick_dict[player]
		print("player {}".format(pl))
		print("player {}".format(pl.nickname))
		#Check that there has been a selection made		
		#if len(card_selected) == 0:
		#	return {'error': True, 'message': 'No selection was made'}
		print("Game State: {}".format(self.state))
		if self.state=="game start":
			print("Correct state")
			print("Active_card: {}".format(self.active_card))
			if card_selected[0] == 'pick_up':
				return {'error': True, 'message': 'No selection was made'}
			if len(pl.faceup_cards) >=3 and self.all_fours(card_selected) and self.active_card[0]['label'] =="Four to start":
				chk_card = pl.play_card(self.active_card, card_selected, need4=True)
				if chk_card['error']:
					return chk_card			
				else:
					self.active_card =self.get_card_imgs(chk_card['cd'])
					self.new_status("{} played the {}".format(player,selection))
					self.pile = self.pile + self.get_card_imgs(card_selected)	
				self.deck=pl.pick_up(self.deck)
				self.starting_player = pl
			# Check selection is no more than 3
			elif len(card_selected) + len(pl.faceup_cards) > 3:
				return {'error': True, 'message': 'Can only have 3 face up cards, Need a Four to start'}			
			# check that selection has come from the playing hand
			elif pl.what_deck(card_selected) != "Normal play":
				return {'error': True, 'message': 'Face up cards must be selected from your current hand'}
			# Check that the face up hand is not full
			elif len(pl.faceup_cards) >= 3 and not self.all_fours(card_selected) and not self.fours:
				return {'error': True, 'message': 'You can only play a Four to start the game'}

			else:
				# Make the cards change hand
				pl.face_up_selected(card_selected)
				self.new_status("{} played the {}".format(player,selection))

			# if every player has chosen their face up cards change state
			if self.all_player_face():
				if not self.check_for_fours():
					self.state = "turn_to_start"
				if self.starting_player is not None:
					self.state = "4start"
				
				
		if self.state == "turn_to_start":
			print("no fours - in turn_to_start state")
			self.new_status("Nobody has a four, first card in deck to start")
			st = True
			while st:
				self.active_card = self.get_card_imgs([self.deck[0]])
				print(self.active_card)
				self.deck = self.deck[1:]
				self.pile = self.pile + self.active_card
				st = self.tidy()
			# Game order
			cycled = cycle(self.players)  # cycle thorugh the list 'L'
			sliced = islice(cycled, None, 1000)  # take the first 1000 values
			self.player_order= list(sliced)  # create a list from iterator
			
			self.state = "normal play"
			self.new_status("It is {}'s turn to play".format(self.player_order[0].nickname))
			return {'error': False, 'message': 'No error'}
			
		if self.state == "4start":
			print("{} played a Four first".format(self.starting_player.nickname))	
			self.new_status("{} played a Four first".format(self.starting_player.nickname))
			print("Got past this1")		
			# Game order
			cycled = cycle(self.players)  # cycle thorugh the list 'L'
			print("Got past this2")
			player_order = dropwhile(lambda x: x.name != self.starting_player.name, cycled)  # drop the values until first plater
			print("Got past this3")
			sliced = islice(player_order, None, 1000)  # take the first 1000 values
			print("Got past this4")
			self.player_order = list(sliced)[1:]  # create a list from iterator
			print("Got past this5")
			self.state = "normal play"
			self.new_status("It is {}'s turn to play".format(self.player_order[0].nickname))
			return {'error': False, 'message': 'No error'}
				
				
		if self.state == "normal play":
			# Check that the correct player is playing
			if pl is self.get_turn(su=False):
				print('Pile at start of validation', self.pile)
				st = False # this is to allow people to keep taking shots if they are burning
				chk_card = pl.play_card(self.active_card, card_selected)			
				if chk_card['error']:
					return chk_card
				self.active_card =self.get_card_imgs(chk_card['cd'])
				print(chk_card['cd'][0], "Should say Play anything")	
				if chk_card['cd'][0] == 'Play anything':
					print("pile_before_pickup ", self.pile)
					pl.pick_up_pile(self.pile)
					print("hand after pick up", pl.hand)
					self.pile = []
					self.new_status("{}! {} is picking up the pile".format(quips.q(), pl.nickname))
					self.active_card = [{'src':"", 'label':'Play anything'}] 
				else:
					self.deck=pl.pick_up(self.deck)
					face_label = card_selected
					card_selected, a  = pl.face_card_fix(card_selected)
					self.new_status("{} played the {}".format(player, ','.join(card_selected)))						
					self.pile = self.pile + self.get_card_imgs(card_selected)
					print("Pile:", self.pile)
					st = self.tidy()
					if a:
						for l in face_label:
							try:
								pl.lf[l]="place"
							except KeyError:
								print("Face hand played at same time as other hand")
				if not st:
					self.turn = self.turn+1 
			else:
				self.new_status("Waiting on {} to play".format(self.get_turn(su=False).nickname))
				return {'error': True, 'message': 'It is not your turn'}
				
			self.is_out(pl)
			self.get_turn()
		return {'error': False, 'message': 'No error'}		
		
	def update_stats(self):
		game_data = {}
		#Active card
		game_data['ac_src'] = self.active_card[0]["src"]
		#Number of cards left in pile 

		game_data['pile_count'] = "There are {} cards in pile".format(len(self.pile))
		game_data['deck_count']= "There are {} card left in deck".format(len(self.deck))
		game_data['sources'] = {}
		game_data['hc'] = {}
		game_data['bc'] = {}
		#provide data on player states
		for p in self.players:
			game_data['hc'][p.nickname] = "Cards in hand: {}".format(len(p.hand))
			game_data['bc'][p.nickname] = "Blind Cards: {}".format(len(p.blind_cards))
			for face_label in p.lf.keys():
				print("Face labels", face_label)
				game_data['sources'][face_label] = self.get_card_imgs([p.lf[face_label]])[0]
		#provide data to the advice paragraph
		game_data['advice']={}
		lab = self.active_card[0]['label']
		if lab in ["Play anything", "Four to start"]:
			ph = lab +"!"
		else:		
			ph = "Play a card that is {} than a {} or a Two, a Three or a Ten.".format(self.active_card[0]['higher'],lab)
		game_data['advice']['note'] = "It is your turn to play - {}".format(ph)
		if len(self.player_order) > 1: 
			game_data['advice']['player'] = self.player_order[self.turn].nickname
		else:
			game_data['advice']['player'] = "beginner"		
		print("\nGame Data")
		pp.pprint(game_data)
		return game_data
		
		
	def is_out(self, player):
		c1=len(player.hand)	
		c2=len(player.faceup_cards)
		c3=len(player.blind_cards)
		
		n = self.turn
		
		if c1+c2+c3==0:
			print("++++++++++++{}, {} has no more cards left and is out!!!+++++++++++++".format(player.name, player.nickname))
			self.new_status("+++{}, {} has no more cards left and is out!!!+++".format(player.name, player.nickname))
			self.player_order = self.player_order[:n] + list(filter(lambda a: a.name != player.name, self.player_order[n:]))
			self.winner.append(player)
			print("Winner list:", self.winner)
			print(len(self.winner))
			print(self.player_count)
		
		if len(self.winner) >= (self.player_count-1):
			self.loser = self.player_order[-1]
			self.new_status("Game over!")
			self.game_complete = True
			print("Game complete:", self.game_complete)
			self.first_round = False
		

				
class Player:
	def __init__(self, name, game_id):
		self.name = ""
		self.hand = []
		self.blind_cards = []
		self.blind_card_names = ["A", "B", "C"]
		self.faceup_cards = []
		self.nickname = name
		self.game_id = game_id
		self.avatar_path = "" 
		self.loser_board = 0
		self.picked_up = []
		self.reg_player = False
		
		self.dd = {}
		self.val_dict = {}
		
		self.hand_count = ""
		self.blind_count = ""
		
		self.redirect_code=""
		
		#label blind cards so that they cannot be identified
		self.lb = {}
		self.lf = {}
		

	def deets(self):
		print("Name: {}".format(self.name))
		if self.nickname != '':
			print("Nickname: {}".format(self.nickname))
		print("Blind Cards: {}".format(self.blind_cards))
		print("Face up cards; {}".format(self.faceup_cards))
		print("Current Hand: {}".format(self.hand))
		print("\n")


	def print_current_hand(self):
		self.sort_hand()
		if len(self.hand) > 0:
			stage = "Normal play"
			hand = self.hand
		elif len(self.faceup_cards) > 0:
			stage = "Face up cards"
			hand = self.faceup_cards
		else:
			stage = "Blind cards"
			hand = self.blind_cards
			
		print("Current hand: {}".format(stage))
		return hand, stage
	
	
	def sort_hand(self):
		print("sorting hand for {}".format(self.nickname))
		temp_hand = self.hand[:]
		self.hand = sorted(temp_hand, key=lambda x: self.dd[x[:3]])


	def face_up_selected(self, slct_cards):
		print("Placing face up cards")
		for crd in slct_cards:
			self.hand.remove(crd)
			self.faceup_cards.append(crd)
		self.sort_hand()
		self.label_faces()
			

	def play_card(self, active_card, played_card, need4=False):
		self.picked_up = []
		hand, stage = self.print_current_hand()
		blind_bool=False
		face_bool=False
		print("Played card: {}".format(played_card))
		print("Played card: {}".format(played_card[0][:3]))
		if need4:
			if played_card[0][:3] not in 'Four':
				print("no")
				return {'error':True, 'message':"Must only play a Four to start game"}
		# if no selected cards, check that there are no cards that can be played - otherwise pick up
		if played_card[0] == "pick_up":
			for card in hand:
				print('Checking that a card can be played')
				e = self.rule_check(active_card[0]['label'], [card])
				if not e['error']:
					return {'error':True, 'message':"There are cards you can play"}
			# if no cards are playable then must pick up return 	
			return {'error':False, 'cd':["Play anything"]}
		# if it is a blind card then 
		if played_card[0] in self.blind_card_names:
			blind_label = played_card[0]
			print("label blind", self.lb)
			played_card[0] = self.lb[played_card[0]]
			blind_bool = True
		
		played_card, face_bool = self.face_card_fix(played_card)
		# check that selected card comes from the correct deck	
		if self.what_deck(played_card) != stage:
			print(self.what_deck(played_card), stage)
			return {'error':True, 'message':"You are on the {} stage. You cannot play that...".format(stage)}	
		# check that played card follows the rules
		e = self.rule_check(active_card[0]['label'], played_card)
		if e['error']:
			if blind_bool:
				self.blind_cards.remove(played_card[0])
				self.blind_card_names.remove(blind_label)
				self.hand = self.hand + played_card
				return {'error':False, 'cd':"pick up"}
			else:
				return e	
		for crd in played_card:
			hand.remove(crd)
		if blind_bool:
			self.blind_card_names.remove(blind_label)
		return {'error':False, 'cd':[played_card[0]]}
		
				
	def rule_check(self, active_card, played_card):
		blind_bool=False
		# check that all cards are the same 
		if self.multi_card(played_card):
			played_card = played_card[0]
		else:
			return {'error':True, 'message':"Can only play multiple cards if they have the same value", 'blind':blind_bool}
		
		# Lower than a 7 but not a ten
		if active_card[:5] in "Seven":
			if self.val_dict[played_card[:3]] > 5 and played_card[:3] not in "Ten":
				print("*** Must play a card Lower than a  7")
				return {'error':True, 'message':"Need to play lower than a Seven", 'blind':blind_bool}
		else:
			if played_card[:3] not in ["Two", "Thr", "Ten"]:
				if self.val_dict[played_card[:3]] < self.val_dict[active_card[:3]]:
					print("*** Must play a card HIGHER than a {}".format(active_card))
					return {'error':True, 'message':"Must play a card HIGHER than a {}".format(active_card), 'blind':blind_bool}
		return {'error':False, 'message':"No error"}
	
	
	def face_card_fix(self, played_cards):
		face_bool=False
		new_played_cards = []
		for pc in played_cards:
			if pc in self.lf.keys():
				new_played_cards.append(self.lf[pc])
				face_bool = True
			else:
				new_played_cards.append(pc)
		print("Face card fix", new_played_cards)
		return new_played_cards, face_bool
	
	
	def what_deck(self, selection):
		hands = []
		for card in selection:
			print("what deck", card, self.hand)
			if card in self.hand:
				hands.append("Normal play")
			print("what deck2", card, self.lf.keys())	
			if card in self.faceup_cards:
					hands.append("Face up cards")
			if card in self.blind_cards:
				hands.append("Blind cards")
		if self.checkEqual(hands) and len(hands)==len(selection):
			return hands[0]
		else:
			return None
	
	
	@staticmethod
	def checkEqual(iterator):
   		return len(set(iterator)) <= 1
	
		
	def pick_up(self, deck):
		if len(deck)>0:
			self.picked_up = []
			for i in range(3 - len(self.hand)):
				new_card = deck[0]
				self.picked_up.append(new_card)
				self.hand.append(new_card)
				print("Picking up {}".format(new_card))
				if len(deck) == 1:
					return []
				deck=deck[1:]
		return deck


	def pick_up_pile(self, pile):
		pile_cards = []
		for card in pile:
			pile_cards.append(card['label'])
		self.hand = self.hand + pile_cards

	
	def label_blind(self):
		for i, card in enumerate(self.blind_cards):
			self.lb[self.blind_card_names[i]] = card
			print("Label blind card dict", self.lb)


	def label_faces(self):
		for i, card in enumerate(self.faceup_cards):
			self.lf[self.nickname + "-" + self.blind_card_names[i]] = card
		print("Label face up cards dict", self.lf)
		print(self.faceup_cards)


	def multi_card(self, sels):
		values = []
		for x in sels:
			values.append(self.val_dict[x[:3]])
		return self.checkEqual(values)
	


		
			
	

