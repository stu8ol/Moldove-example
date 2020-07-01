from app import app
from app import socketio
from flask import render_template, flash, redirect, g, url_for, session, request
from flask_socketio import SocketIO, emit
from flask_socketio import join_room, leave_room
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.forms import LoginForm, CreateGame, JoinGame, EnterName, PlayAgain, UploadForm
from app import db
from app.forms import RegistrationForm
import game_play
import time
import threading
import quips
from datetime import datetime
import hashlib
from app import photos

start_time = time.time()
act_games = {}
player_code = {}


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.now()

@app.route('/')
@app.route('/index')
def index():
    return render_template('title.html', title ="Home", pl=url_for('create_or_join'))
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('create_or_join'))
    return render_template('login.html', title='Sign In', form=form, pl=url_for('create_or_join'))
    
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/rules')
def rules():
    return render_template('rules.html', title='Rules', pl=url_for('create_or_join'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, pl=url_for('create_or_join'))
  
    
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts, pl=url_for('create_or_join'))
    
   
@app.route('/upload/<username>', methods=['GET', 'POST'])
@login_required
def upload_file(username):
	#user = User.query.filter_by(username=username).first_or_404()
	form = UploadForm()
	if form.validate_on_submit():
		for filename in request.files.getlist('photo'):
			name = hashlib.md5(('admin' + str(time.time())).encode('utf-8')).hexdigest()[:15]
			a = photos.save(filename, name=name + '.')
		success = True
		print("Name", name)
		print(a)
		current_user.new_avatar(a)   
		return redirect(url_for('user', username=current_user.username))
	else:
		success = False
	return render_template('upload.html', form=form, success=success, pl=url_for('create_or_join'))


@app.route('/play', methods=['GET', 'POST'])
def create_or_join():
    print("There are {} games operational".format(len(act_games)))
    formC = CreateGame()
    if formC.validate_on_submit():
        game1=game_play.Game()
    	# once the number of players is entered and the submit button is pressed a new
        new_url = game1.get_new_url(formC.noof_players.data)
        url2 = get_code('wait_for_players', new_url) #This means we will be redirected to this route
        # adds game to dictionary and also addes it to cookies for it can be referred to.
        gc = game1.game_code[:]
        act_games[gc] = game1
        session["gc"] = gc
        return redirect(url2)
    formG = JoinGame()    
    if formG.validate_on_submit():
        for gid in act_games.values():
        	cap_gid = formG.game_id.data
        	if gid.game_code == cap_gid.upper():
                   if len(gid.players) < gid.player_count:
                       url2 = get_code('wait_for_players', gid.url) #This means we will be redirected to this route
                       session["gc"] = gid.game_code
                       return redirect(url2)
                   else:
                       flash('Game is full')
        return redirect('/play')
    return render_template('Create_or_join.html', title='Create or join game', formC=formC, formG=formG)
    
        

@app.route('/name/<code>', methods=['GET', 'POST'])
def wait_for_players(code):
	formC = EnterName()
	if formC.validate_on_submit():	  
		nickname=formC.player_name.data
		player = act_games[session["gc"]].new_nickname(nickname,session["gc"]).nickname
		session['player'] = player
		# The following urls will depend on game id and player
		next_url = get_code('waiting_to_start', hash(session['gc']+player))
		player_code[next_url[6:]] = [session['gc'], player, time.time()]
		print("Code for waiting page {}".format(next_url))
		return redirect(next_url)
	if current_user.is_authenticated:
		player = act_games[session["gc"]].new_nickname(current_user.username, session["gc"], current_user.avatar_path).nickname
		session['player'] = player
		# The following urls will depend on game id and player
		next_url = get_code('waiting_to_start', hash(session['gc']+player))
		player_code[next_url[6:]] = [session['gc'], player, time.time()]
		print("Code for waiting page {}".format(next_url))
		return redirect(next_url)
	gd = act_games[session["gc"]]
	gd.get_ready_players()

	return render_template('waiting2.html', title='Enter your name...', formC=formC, game_deets=gd)



@app.route('/wait/<code>')
def waiting_to_start(code):
	try:
		gd = act_games[player_code[code][0]]
		ready = gd.get_ready_players()
		pn = player_code[code][1]
		gd.nick_dict[pn].redirect_code = code
		if ready:
			if gd.game_ready:
				return redirect(get_code('moldove_table', code))
			gd.prep_round()
	except KeyError:
		return redirect('/play')
	return render_template('waiting3.html', title='Waiting for players', game_deets=gd, player_name=pn)
	

# this is the driver of the app
@app.route('/table/<code>')
def moldove_table(code):
	try:
		gd = act_games[player_code[code][0]]
		pn = gd.nick_dict[player_code[code][1]]
	except KeyError:
		return redirect('/play')
	pn.sort_hand()
	name = 'Game code: {0} - {2}: {1}'.format(gd.game_code, pn.nickname, pn.name)
	h = gd.get_card_imgs(pn.hand)
	f = gd.get_face_cards()
	cb = gd.card_back
	if len(gd.deck) < 1:
		cb = gd.crd_img_dict['place'] 
	pw = gd.last_picked_up(pn)
	bcs = gd.get_card_imgs(pn.blind_card_names, blind=True)
	ps=gd.pile_update()
	go_url = get_code('game_over', code)
	s=gd.get_sizes(pn)
	return render_template('Table2.html', name=name, ac=gd.active_card[0], hand=h, bc=cb, bcs=bcs, game_id=gd.game_code, pl=pn.nickname, pcs=f, ps=ps, go_url=go_url,pw=pw, sizes=s)


@app.route('/game_over/<code>', methods=['GET', 'POST'])
def game_over(code):
	try:
		gd = act_games[player_code[code][0]]
		pn = player_code[code][1]
	except KeyError:
		return redirect('/play')
	formA = PlayAgain()
	if len(gd.players) >= gd.player_count:
		formA.submit.render_kw={'disabled': 'disabled'}
	if formA.validate_on_submit():
		gd.players.append(gd.nick_dict[pn])
		print("Players-restart", gd.players)
		return redirect(get_code('waiting_to_start', code))
	return render_template('game_over.html', title='Game over!', game_deets=gd, cap=gd.cap, shot=quips.s(), formA=formA, lb=gd.loser_board)


def get_code(fun, url):
	# This gets the url for the next fuction based on the string created and the function name
	print(url)		
	with app.test_request_context():
		a = url_for(fun, code=url)
	return a
	
	
# Start of webosocket connections
# Handler for a message recieved over 'connect' channel
@socketio.on('connect')
def test_connect():
	print("Connection test good")
	emit('after connect',  {'data':'Lets dance'})
	gid = session['gc']
	game = act_games[gid]
	join_room(gid)
	print("\n\nGame ID: {}".format(gid))
	stat = game.status
	stat = "<br>".join(act_games[gid].status)
	game.update_stats()
	emit('after connect', {'data':stat}, broadcast=False, room=gid)
    
    
@socketio.on('status_update')
def play_go(status_update):
	print("Play button clicked....")
	gid = session['gc']
	game = act_games[gid]
	print("Game ID: {}".format(gid))
	player = game.nick_dict[status_update['player']]
	error_msg = game.valid_selection(status_update["selection"], status_update['player'])
	if error_msg['error']:
		print(error_msg)
		emit('private_message', error_msg, broadcast=False)
	else:
		stat = game.status
		stat = "<br>".join(act_games[gid].status)
		gd = game.update_stats()
		emit('status_updated', {'data':stat, 'game': gd}, broadcast=False, room=gid)
		if act_games[gid].game_complete:
			game.restart(db, User)
			print("\n++++++++++Should be Redirecting here+=======\n")
			emit('redirect_go', {'url': '-'}, broadcast=False, room=gid)
		emit('reload', "s", broadcast=False)			
	print("Finished status update for {} in {}".format(status_update['player'],gid))


def clean_up(st, T):
	print("\nClean up Arguements", st, T)
	while True:
		if st + T < time.time():
			st = time.time()
			# delete games that have not been touched in a while
			a = list(act_games.keys())
			for gid in a:
				if act_games[gid].last_interaction + 12*3600 < time.time():
					print("Deleting Game: ", gid)
					del act_games[gid]
			# delete player codes after a longer time after they have been created
			b = list(player_code.keys())
			for pc in b:
				if player_code[pc][2] + 48*3600  < time.time():
					print("Player code: ", pc, "\n")
					del player_code[pc]
		time.sleep(5)


x = threading.Thread(target=clean_up, args=(start_time,600), daemon=False)
x.start()
		

			
		
	
	
#TODO give error message if non iteger is entered
#TODO advice tells you what card you played on a blind card

	
