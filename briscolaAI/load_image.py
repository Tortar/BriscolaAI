from IPython.display import Image, display

name_to_image = {
    'AceCoins': '1_denari',
    '2Coins': '2_denari',
    'ThreeCoins': '3_denari',
    '4Coins': '4_denari',
    '5Coins': '5_denari',
    '6Coins': '6_denari',
    '7Coins': '7_denari',
    'QueenCoins': '8_denari',
    'KnightCoins': '9_denari',
    'KingCoins': '10_denari',
    'AceSwords': '1_spade',
    '2Swords': '2_spade',
    'ThreeSwords': '3_spade',
    '4Swords': '4_spade',
    '5Swords': '5_spade',
    '6Swords': '6_spade',
    '7Swords': '7_spade',
    'QueenSwords': '8_spade',
    'KnightSwords': '9_spade',
    'KingSwords': '10_spade',
    'AceCups': '1_coppe',
    '2Cups': '2_coppe',
    'ThreeCups': '3_coppe',
    '4Cups': '4_coppe',
    '5Cups': '5_coppe',
    '6Cups': '6_coppe',
    '7Cups': '7_coppe',
    'QueenCups': '8_coppe',
    'KnightCups': '9_coppe',
    'KingCups': '10_coppe',
    'AceBatons': '1_bastoni',
    '2Batons': '2_bastoni',
    'ThreeBatons': '3_bastoni',
    '4Batons': '4_bastoni',
    '5Batons': '5_bastoni',
    '6Batons': '6_bastoni',
    '7Batons': '7_bastoni',
    'QueenBatons': '8_bastoni',
    'KnightBatons': '9_bastoni',
    'KingBatons': '10_bastoni'
}

def image(name):
	if name == "None": namef = "empty"
	else: namef = name_to_image[name]
	return "./briscola_cards/" + namef + ".png"