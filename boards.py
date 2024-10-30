from shapes import process

configs = []
# Configuration examples for boards
configs.append("""
rrbbg
rbbgg
rppgg
ppyoo
pyyyo
""")

configs.append("""
g__g_
g_gg_
_g___
__gg_
g__g_
""")

configs.append("""
_____
_____
_____
_____
_____
""")

configs.append("""
____b
opp_b
_p__r
_g_yr
ggy__
""")



BOARDS = {i + 1: process(configs[i]) for i in range(len(configs))}

# Board setup for the battleship game
boardSetup = [
    [1, 0, 0],
    [2, 0, 0],
    [1, 0, 0]
]

LOCATIONS = [  # B spaces are boundaries, L spaces are playable
    'B00', 'B10', 'B20', 'B30', 'B40',
    'B01', 'L11', 'L12', 'L13', 'B01',
    'B02', 'L21', 'L22', 'L23', 'B02',
    'B03', 'L31', 'L32', 'L33', 'B03',
    'B04', 'B14', 'B24', 'B34', 'B44'
]

LOCATIONS2D = [
    ['B00', 'B10', 'B20', 'B30', 'B40'],
    ['B01', 'L11', 'L12', 'L13', 'B01'],
    ['B02', 'L21', 'L22', 'L23', 'B02'],
    ['B03', 'L31', 'L32', 'L33', 'B03'],
    ['B04', 'B14', 'B24', 'B34', 'B44']
]
