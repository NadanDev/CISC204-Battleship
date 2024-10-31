# 0 - Not Checked
# 1 - Miss
# 2 - Hit
# Does not include boundaries
# Board setup for the battleship game
boardSetup = [
    [1, 0, 2],
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
