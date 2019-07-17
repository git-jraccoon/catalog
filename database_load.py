from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

# engine = create_engine('sqlite:///itemcatalog.db')
engine = create_engine('postgresql://catalog:catalog@localhost/itemcatalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create a dummy user
user1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(user1)
session.commit()

# Create categories
category1 = Category(name="Pop")
session.add(category1)
session.commit()

category2 = Category(name="R&B")
session.add(category2)
session.commit()

category3 = Category(name="Rap")
session.add(category3)
session.commit()

category4 = Category(name="Country")
session.add(category4)
session.commit()

category5 = Category(name="Rock")
session.add(category5)
session.commit()

# Create items
item1 = Item(user_id=1, title="21", description="25 is the third studio album by English singer-songwriter Adele, released on 20 November 2015 by XL Recordings and Columbia Records.", category=category1)
session.add(item1)
session.commit()

item2 = Item(user_id=1, title="Lemonade", description="Lemonade is the sixth studio album by American singer Beyonce, released on April 23, 2016, by Parkwood Entertainment and Columbia Records.", category=category2)
session.add(item2)
session.commit()

item3 = Item(user_id=1, title="Purpose", description="Purpose is the fourth studio album by Canadian singer and songwriter Justin Bieber.", category=category1)
session.add(item3)
session.commit()

item4 = Item(user_id=1, title="Views", description="Views is the fourth studio album by Canadian rapper Drake. It was released on April 29, 2016, by Cash Money Records, Republic Records and Young Money Entertainment.", category=category3)
session.add(item4)
session.commit()

item5 = Item(user_id=1, title="A Sailor's Guide to Earth", description="A Sailor's Guide to Earth is the third studio album by American country singer-songwriter Sturgill Simpson.", category=category4)
session.add(item5)
session.commit()

item6 = Item(user_id=1, title="24K Magic", description="24K Magic (stylized as XXIVK Magic) is the third studio album by American singer and songwriter Bruno Mars. It was released worldwide on November 18, 2016, by Atlantic Records.", category=category2)
session.add(item6)
session.commit()

item7 = Item(user_id=1, title="Awaken, My Love!", description="Awaken, My Love! is the third studio album by American rapper Donald Glover, under his stage name Childish Gambino.", category=category2)
session.add(item7)
session.commit()

item8 = Item(user_id=1, title="4:44", description="4:44 is the thirteenth studio album by American rapper Jay-Z.", category=category3)
session.add(item8)
session.commit()

item9 = Item(user_id=1, title="Damn", description="Damn (stylized as DAMN.) is the fourth studio album by American rapper Kendrick Lamar.", category=category3)
session.add(item9)
session.commit()

item10 = Item(user_id=1, title="Melodrama", description="Melodrama is the second studio album by New Zealand singer Lorde, released through Universal, Lava and Republic Records on 16 June 2017.", category=category1)
session.add(item10)
session.commit()

item11 = Item(user_id=1, title="Golden Hour", description="Golden Hour is the fourth studio album by American country music singer and songwriter Kacey Musgraves, released on March 30, 2018, through MCA Nashville.", category=category4)
session.add(item11)
session.commit()

print("added catalog items!")