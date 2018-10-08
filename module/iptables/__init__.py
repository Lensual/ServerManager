config = {
    "interval": 10,
    "groups": [
        {
            "name": "VRRP",
            "hosts": ["Meow", "Nyan", "WolfVRRP", "DogeVRRP"],
            "priority":1
        },
        {
            "name": "AttackLimit",
            "hosts": ["Meow", "Nyan", "WolfVRRP", "DogeVRRP"],
            "priority":0
        },
        {
            "name": "Meow",
            "hosts": ["Meow"],
            "priority":101
        },
        {
            "name": "Nyan",
            "hosts": ["Nyan"],
            "priority":102
        },
        {
            "name": "WolfVRRP",
            "hosts": ["WolfVRRP"],
            "priority":102
        },
        {
            "name": "DogeVRRP",
            "hosts": ["DogeVRRP"],
            "priority":102
        }
    ]
}
