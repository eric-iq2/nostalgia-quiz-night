# Quiz #7 round content. Order = sheet order (#7 Sounds / #7 Videos rows 3-12).
SETTINGS = {"title": "Quiz Night #7", "venue": "Antonakis Music Hall"}  # venue confirmed 2026-10-15
# Neon colours sampled from the green-brick poster: "Night" cyan + "QUIZ" red-orange tube
THEME = {"accentColor": "#2AE2F0", "secondaryAccent": "#F05020"}
# Final prizes from Eric, 2026-10-16. Order 5th..1st: (headline, subtext HTML)
PRIZES = [
    ("Wine Bottles", ""),  # Eric's note said "worth €15 each?", so no value shown
    ("Vouchers", "for <em>Pantheon Cinema</em> &mdash; worth &euro;10 each"),
    ("Vouchers", "for <em>Ella Music House</em> &mdash; worth &euro;15 each"),
    ("Vouchers", "at <em>Interni Moda Bagno</em> &mdash; worth &euro;50 each"),
    ("Complimentary Table", "the full cost of your evening covered &mdash;<br>tickets, food &amp; drinks!<br><br><strong>+ 2 complimentary sandwich platters</strong><br>by <em>Misfit Union Catering</em> &mdash; worth &euro;70"),
]

# Charity slide shown before the prizes (2026-10-16): Quiz #7 is a fundraiser for Voice for Autism.
# White background so the cafe photo sits cleanly; image from voiceforautism.org/the-cafe/
CHARITY = {
    "image": "media/voice-for-autism-cafe.jpg",
    "heading": "Tonight, all net proceeds go to Voice for Autism",
    "lines": [  # the thank-you is said by Chris, the host, so it's not on the slide
        "Visit the <strong>True Heart Cafe</strong> in downtown Nicosia, Cyprus&rsquo; first social enterprise "
        "giving young people with autism real jobs and training. Every coffee helps!",
    ],
}

ARTIST_TITLE_MV = [("Name the artist", 1), ("Name the title", 1)]

import json as _json, os as _os
_MC = _json.load(open(_os.path.join(_os.path.dirname(__file__), "mc.json")))  # from sheet '#7 MC Q''s' rows 2-11 / 13-22, validated 2026-10-15
R1 = _MC["R1"]
# Music videos — sheet "#7 Music Videos" rows 2-10. Metallica added at Q9 2026-10-15; Freedom moved to Q10.
R3 = [
    {"parts": ARTIST_TITLE_MV, "answer": "The Buggles — ‘Video Killed the Radio Star’", "note": "1979 (the first video ever played on MTV, 1981)"},
    {"parts": ARTIST_TITLE_MV, "answer": "Beastie Boys — ‘Sabotage’", "note": "1994, directed by Spike Jonze"},
    {"parts": ARTIST_TITLE_MV, "answer": "Sinéad O’Connor — ‘Nothing Compares 2 U’", "note": "1990, written by Prince"},
    {"parts": ARTIST_TITLE_MV, "answer": "Dire Straits — ‘Money for Nothing’", "note": "1985"},
    {"parts": ARTIST_TITLE_MV, "answer": "Jamiroquai — ‘Virtual Insanity’", "note": "1996"},
    {"parts": ARTIST_TITLE_MV, "answer": "Δέσποινα Βανδή (Despina Vandi) — ‘Γεια’ (‘Gia’)", "note": "2001"},
    {"parts": ARTIST_TITLE_MV, "answer": "Lady Gaga — ‘Bad Romance’", "note": "2009"},
    {"parts": ARTIST_TITLE_MV, "answer": "Katy Perry — ‘Roar’", "note": "2013"},
    {"parts": ARTIST_TITLE_MV, "answer": "Metallica — ‘I Disappear’", "note": "2000, from the Mission: Impossible 2 soundtrack"},
    {"parts": ARTIST_TITLE_MV, "answer": "George Michael — ‘Freedom! ’90’", "note": "1990, supermodels lip-syncing"},
]
R4 = _MC["R4"]
# Pictures: 10 album covers, Eric's final list 2026-10-15, shuffled so neighbours are 8+ years apart. Text cropped/blurred off each cover.
ALBUM_Q = [("Name the artist", 1), ("Name the album", 1)]
R5 = [{"parts": ALBUM_Q, "answer": f"{art} — ‘{alb}’", "note": yr} for art, alb, yr in [
    ("Moby", "Play", "1999"),
    ("Rihanna", "Good Girl Gone Bad", "2007"),
    ("Oasis", "Definitely Maybe", "1994"),
    ("The Beatles", "Revolver", "1966"),
    ("Coldplay", "Parachutes", "2000"),
    ("Taylor Swift", "Fearless", "2008"),  # replaced The Life of a Showgirl (2025) — too recent
    ("Alanis Morissette", "Jagged Little Pill", "1995"),
    ("U2", "The Joshua Tree", "1987"),
    ("Gorillaz", "Demon Days", "2005"),
    ("Iron Maiden", "Best of the Beast", "1996"),
]]

ARTIST_TITLE = [("Name the artist", 1), ("Name the title", 1)]
R2 = [  # shuffled 2026-10-15 at Eric's request; TV show kept last
    {"parts": ARTIST_TITLE, "answer": "Marvin Gaye — ‘Sexual Healing’", "note": "1982"},
    {"parts": [('Name the sound <span class="q-warn">(be specific)</span>', 2)],
     "answer": "Windows XP + shutting down", "note": "(2001) Microsoft Windows XP shutdown sound"},
    {"parts": [("Name the movie", 1), ("Name the song", 1)],
     "answer": "Rocky — ‘Gonna Fly Now’", "note": "(1976)"},
    {"parts": ARTIST_TITLE, "answer": "Macklemore &amp; Ryan Lewis — ‘Thrift Shop’", "note": "2012"},
    {"parts": [("Name the video game", 2)],
     "answer": "World of Warcraft", "note": "(2004) login screen music, ‘Legends of Azeroth’"},
    {"parts": [("Name the movie", 1), ("Name the narrator", 1)],
     "answer": "The Shawshank Redemption — Morgan Freeman", "note": "(1994)"},
    {"parts": ARTIST_TITLE, "answer": "The Beatles — ‘When I’m Sixty-Four’", "note": "1967"},
    {"parts": [("Name the sound", 2)],
     "answer": "Dial-up internet modem", "note": "56k modem, 1990s"},
    {"parts": ARTIST_TITLE, "answer": "Nina Simone — ‘My Baby Just Cares for Me’", "note": "1958"},
    {"parts": [("Name the TV show", 2)],
     "answer": "Family Matters", "note": "(1989–1998)"},
]

MOVIE = [("Name the movie", 2)]
R6 = [
    {"parts": MOVIE, "answer": "Shaun of the Dead", "note": "(2004) Simon Pegg &amp; Nick Frost"},
    {"parts": MOVIE, "answer": "Perfect", "note": "(1985) John Travolta &amp; Jamie Lee Curtis"},
    {"parts": MOVIE, "answer": "Jurassic Park", "note": "(1993) directed by Steven Spielberg"},
    {"parts": MOVIE, "answer": "He’s Just Not That Into You",
     "note": "(2009) Ben Affleck, Jennifer Aniston, Drew Barrymore, Jennifer Connelly, Bradley Cooper, Scarlett Johansson"},
    {"parts": MOVIE, "answer": "Carrie", "note": "(1976) Sissy Spacek, directed by Brian De Palma"},
    {"parts": MOVIE, "answer": "Το ξύλο βγήκε από τον παράδεισο", "note": "(1959) Aliki Vougiouklaki &amp; Dimitris Papamichael"},
    {"parts": MOVIE, "answer": "Brave", "note": "(2012) Disney·Pixar"},
    {"parts": MOVIE, "answer": "Top Gun", "note": "(1986) Tom Cruise &amp; Val Kilmer"},
    {"parts": MOVIE, "answer": "Mrs. Doubtfire", "note": "(1993) Robin Williams"},
    {"parts": MOVIE, "answer": "Ghost", "note": "(1990) Patrick Swayze &amp; Demi Moore"},
]


# Half-time scores (R1+R2+R3) from the '#7 SCORES' tab, 2026-10-16. Sheet order; the builder ranks them.
HALFTIME = [  # from the '#7 SCORES' tab via sheet_scores.py
    ('Se7en', 40),
    ('QUIZARD OF OZ', 41),
    ('3 Olives & 1 Tomato', 33),
    ('Wine Wallopers', 17),
    ('The King of Queens', 38),
    ('The Fredibles', 34),
    ('CURLY WURLIES', 42),
    ('The Geordies', 18),
    ('Omorfosogo', 29),
    ('The Ellen Show', 41),
    ("Aragorn's Broken Toe", 42),
    ('Quizteama Aguilera', 42),
    ('WHAT HAVE THE ROMANS GIVEN US?', 35),
    ('Kachow!!', 27),
    ('KOUTOUROU', 22),
    ('Psorokatti', 38),
    ('Only Football Fans', 28),
    ('THE 4-GETFULLS', 33),
    ("What's the capital of Kuwait?", 34),
    ('Para Pente', 21),
    ('Quizulicious', 35),
    ('FRIDAY FREAKS (FFS)', 34),
    ('Attack on Braincells', 41),
    ('Better late than clever', 34),
    ("Man Bite's Dog", 37),
    ('Mahale-ballz', 31),
    ('Tequila Mockingbird', 33),
    ('The Witches', 32),
    ('Lady & The Tramps', 36),
    ("SEM'S (table 28)", 13),
    ('30s', 35),
    ('To Soi', 27),
]

FINAL = [  # from the '#7 SCORES' tab via sheet_scores.py
    ('Se7en', 72),
    ('QUIZARD OF OZ', 79),
    ('3 Olives & 1 Tomato', 67),
    ('Wine Wallopers', 34),
    ('The King of Queens', 70),
    ('The Fredibles', 64),
    ('CURLY WURLIES', 82),
    ('The Geordies', 32),
    ('Omorfosogo', 52),
    ('The Ellen Show', 77),
    ("Aragorn's Broken Toe", 69),
    ('Quizteama Aguilera', 82),
    ('WHAT HAVE THE ROMANS GIVEN US?', 69),
    ('Kachow!!', 53),
    ('KOUTOUROU', 52),
    ('Psorokatti', 77),
    ('Only Football Fans', 57),
    ('THE 4-GETFULLS', 63),
    ("What's the capital of Kuwait?", 74),
    ('Para Pente', 42),
    ('Quizulicious', 69),
    ('FRIDAY FREAKS (FFS)', 66),
    ('Attack on Braincells', 79),
    ('Better late than clever', 69),
    ("Man Bite's Dog", 77),
    ('Mahale-ballz', 66),
    ('Tequila Mockingbird', 60),
    ('The Witches', 68),
    ('Lady & The Tramps', 75),
    ("SEM'S (table 28)", 27),
    ('30s', 64),
    ('To Soi', 55),
]

# Sudden-death winners decided live on the night (rank of the tie -> winning team)
TIE_WINNERS = {1: "CURLY WURLIES", 3: "Attack on Braincells", 5: "Man Bite's Dog"}
