# 0 - Not Checked
# 1 - Miss
# 2 - Hit
# Does not include boundaries
# Board setup for the battleship game
boardSetup = [
    [1, 2, 0],
    [2, 2, 0],
    [1, 0, 0]
]

LOCATIONS = [  # B spaces are boundaries, L spaces are playable
    'B00', 'B10', 'B20', 'B30', 'B40',
    'B01', 'L11', 'L21', 'L31', 'B41',
    'B02', 'L12', 'L22', 'L32', 'B42',
    'B03', 'L13', 'L23', 'L33', 'B43',
    'B04', 'B14', 'B24', 'B34', 'B44'
]

LOCATIONS2D = [
    ['B00', 'B10', 'B20', 'B30', 'B40'],
    ['B01', 'L11', 'L21', 'L31', 'B41'],
    ['B02', 'L12', 'L22', 'L32', 'B42'],
    ['B03', 'L13', 'L23', 'L33', 'B43'],
    ['B04', 'B14', 'B24', 'B34', 'B44']
]
