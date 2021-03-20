"""Demo data
"""

from shopapi.schemas import api, schemas

users = [
    api.LoginUserIn(email="test.user1@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user2@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user3@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user4@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user5@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user6@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user7@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user8@demo-shopapi.demo", password="demouser"),
    api.LoginUserIn(email="test.user9@demo-shopapi.demo", password="demouser"),
]

tags = [
    schemas.TagInput(name="sporty"),
    schemas.TagInput(name="black friday"),
    schemas.TagInput(name="absinth-like"),
    schemas.TagInput(name="used")
]
