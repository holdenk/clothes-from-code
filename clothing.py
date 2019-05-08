class CowCowItem:
    """The specification for an item of clothing or other print."""
    def __init__(self, name, cowcowid, panels):
        self.name = name
        self.cowcowid = cowcowid
        self.panels = panels


cowcow_items = {
    # These are the dress pieces for the dress with pockets on cowcow
    # Front(Center) : 1487 x 4796 or Higher
    # Front Left(Center) : 1053 x 4780 or Higher
    # Front Right(Center) : 1053 x 4780 or Higher
    # Back Right(Center) : 878 x 4803 or Higher
    # Sleeve Left(Center) : 1775 x 2140 or Higher
    # Pocket Right(Center) : 1067 x 704 or Higher
    # Back Left(Center) : 881 x 4818 or Higher
    # Back Rightside(Center) : 1039 x 4803 or Higher
    # Sleeve Right(Center) : 1775 x 2140 or Higher
    # Pocket Left(Center) : 1067 x 703 or Higher
    # Back Leftside(Center) : 1039 x 4803 or Higher
    "dress_with_pockets": CowCowItem("dress_with_pockets", "2170", [
        ("front", (1487, 4796)),
        ("front_left", (1053, 4780)),
        ("front_right", (1053, 4780)),
        ("back_right", (878, 4803)),
        ("sleeve_left", (1775, 2140)),
        ("pocket_right", (1067, 704)),
        ("back_left", (881, 4818)),
        ("back_rightside", (1039, 4803)),
        ("sleeve_right", (1775, 2140)),
        ("pocket_left", (1067, 703)),
        ("back_leftside", (1039, 4803)),
    ]),
    # Boxy/"Men's" Basketball tank tops (no pockets...)
    # Collar(Center) : 3000 x 270 or Higher
    # Back(Center) : 2887 x 4089 or Higher
    # Front(Center) : 2792 x 3978 or Higher
    "boxy_basketball_tank_top": CowCowItem("boxy_basketball_tank_top",  "1761", [
        ("collar", (3000, 270)),
        ("front", (2792, 3978)),
        ("back", (2887, 4089)),
    ]),
    # Fitted/"Women's" Basketball tank tops (no pockets...)
    # Strap(Center) : 2250 x 450 or Higher
    # Front(Center) : 2625 x 3750 or Higher
    # Back(Center) : 2676 x 3750 or Higher
    "fitted_basketball_tank_top": CowCowItem("fitted_basketball_tank_top",  "1762", [
        ("Strap", (2250, 450)),
        ("Front", (2625, 3750)),
        ("Back", (2676, 3750)),
    ]),
    # Hooded Pocket Cardigan
    # Pocket Right(Center) : 717 x 729 or Higher
    # Pocket Left(Center) : 717 x 729 or Higher
    # Front Left(Center) : 1288 x 3677 or Higher
    "hooded_pocket_cardigan": CowCowItem("hooded_pocket_cardigan",  "2168", [
        ("pocket_right", (717, 729)),
        ("pocket_left", (717, 729)),
        ("front_left", (1288, 3677)),
    ]),
    # A-Line Pocket Skirt
    # Skirt Back(Center) : 4200 x 2544 or Higher
    # Skirt Front(Center) : 4200 x 2397 or Higher
    # Waist Band(Center) : 3000 x 488 or Higher
    "aline_pocket_skirt": CowCowItem("aline_pocket_skirt",  "1937", [
        ("skirt_back", (4200, 2544)),
        ("skirt_front", (4200, 2397)),
        ("waist_band", (3000, 488)),
    ]),
    # 15 inch laptop sleeve
    "15inch_laptop_sleeve": CowCowItem("15inch_laptop_sleeve",  "455", [
        ("front", (2700, 2200)),
    ]),
}
