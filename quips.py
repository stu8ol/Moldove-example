import random
print("Loading quips")

qs = ["Ho Ho, What a fanny",
      "Bastart",
      "Bummer mate",
      "Nae way",
      "Hot diggity dog",
      "Gah",
      "Ya dancer",
      "Ha ha, ya tit",
      "Pick 'em up, Prick",
      "Hawl Mogli",
      "Haw Haw ya dobber",
      "Gutted",
      "Dollary Dizzle",
      "Bobby Dazzler",
      "Hah! Ya Walloper",
      "Pickin up the pile like a dafty",
      "Yer arse",
      "Disgustin",
      "Nae Luck",
      "Shots comin your way",
      "There's a shot with your name on it"
      ]
      
gmo = ["Shots!, shots!, shots!",
	"Down it! Down it!",
	"Looooooooser!",
	"Tequila time!",
	"Boke: Bailey's & Coke",
	"A wee dram",
	"You better lose yourself in the music, the moment, you own it, you better never let it go, You only get one shot!",
	"I take my cap off to you.",
	"Shoot your shot!",
	"Bang Bang, shot you down...",
	"This is your shot!",
	"Shit, Shat, Shot",
	"A shot through the heart, and you're to blame!",
	"Bottoms up!",
	"Aye aye, Captain",
	"You lose!",
	"The shot heard around the world...",
	"Hotshot!",
	"One cap fits all!",
	"One cap wonder!"
	]	
      
def q():
	a = qs
	random.shuffle(a)
	return a[0]

def s():
	a = gmo
	random.shuffle(a)
	return a[0]	
      

