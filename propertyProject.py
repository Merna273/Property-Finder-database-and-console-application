import pandas as pd
from tabulate import tabulate
import pymysql 
import re

con = pymysql.connect(
host ='db4free.net',
user = 'mernaabdelbadie',
password='merna2732',
db="propertyfinder01")
loop = True


with con.cursor() as cur:
    while loop:
        print("""
        1. Register a user 
        2. Add a new user review on an agent
        3. View existing reviews of a given agent
        4. View aggregated rating of a brokerage company
        5. Show the location of a given development, along with the average price / sqm and the number of listings for each unit type
        6. Show all the properties of in a certain area, along with the average price / sqm for each unit type
        7. Show all the properties in a certain area in a given price range, with a given set of amenities 
        8. Show the top 10 areas by amount of inventory and price / sqm of a given unit type
        9. Show the top 5 brokerage companies by the amount of listings they have, along with their avg price / sqm, number of agents, and average listings per agent
        10. Show all the properties listed by a specific agent (given their first and last name and / or phone no) 
        11. exit
        """)

        userChoice = input("Choose from the options: ")

        if userChoice == '1':
            username = input("Enter username: ")
            email = input("Enter email: ")
            age = input("Enter age: ")
            gender = input("Enter gender (M/F): ")
            numOfAreas = input("Enter number of areas of focus: ")
            areas = []
            query1 = "INSERT INTO the_user VALUES ('{}', '{}', '{}', '{}');".format(username, email, int(age), gender)
            cur.execute(query1)
            con.commit()
            for i in range(0, int(numOfAreas)):
                areas.append(input("Enter area: ")) 
            for i in range(0, int(numOfAreas)): 
                query2 =  "INSERT INTO main_area_of_focus VALUES ('{}', '{}');".format(email, areas[i])
                cur.execute(query2)
                con.commit()
        elif userChoice == '2':
            review = input("Enter review: ")
            rating = input("Enter rating(1-10): ")
            email = input("Enter email: ")
            agentName = input("Enter agent name: ")
            query1 = "SELECT contact_number from agent where agent_name = '{}';".format(agentName)
            cur.execute(query1)
            ret = cur.fetchall()
            number = 0
            for [x] in ret:
                number = x
            query2 = "INSERT INTO reviews VALUES ('{}', '{}', '{}', '{}');".format(review, rating, email, number)
            cur.execute(query2)
            con.commit()
        elif userChoice == '3':
            agentName = input("Enter agent name: ")
            query = "SELECT textual_review, ratings from reviews R inner join agent A on A.contact_number = R.contact_number where agent_name = '{}';".format(agentName)
            cur.execute(query)
            ret = cur.fetchall()
            ret = pd.DataFrame(ret,columns=['review', 'rating'])
            ret = tabulate(ret, headers='keys', tablefmt='psql')
            print(ret)
        elif userChoice == '4':
            brokerCompany = input("Enter broker company name: ")
            query = "SELECT avg(ratings) from reviews R inner join agent A on A.contact_number = R.contact_number where A.company_name = '{}';".format(brokerCompany)
            cur.execute(query)
            ret = cur.fetchone()
            ret = str(ret)
            if ret[10:-4] == '':
                ret = '0'
                print("Aggregate Rating: ",ret)
            else: 
                print("Aggregate Rating: ",ret[10:-4])
        elif userChoice == '5':
            development = input("Enter development name: ")
            query = "SELECT D.location, avg(P.price/P.property_size), count(P.p_no), P.property_type from development_project D inner join property P on P.project_name = D.project_name  where D.project_name = '{}' group by 1, 4;".format(development)
            cur.execute(query)
            ret = cur.fetchall()
            ret = pd.DataFrame(ret,columns=['location', ' average price/sqm','number of listings', 'unit type'])
            ret = tabulate(ret, headers='keys', tablefmt='psql')
            print(ret) 
        elif userChoice == '6': #ask if this is right
           area = input("Enter area: ")
           query = "SELECT P.property_name, avg(P.price/P.property_size), P.property_type from property P where P.p_area = '{}' group by 1, 3;".format(area)
           cur.execute(query)
           ret = cur.fetchall()
           ret = pd.DataFrame(ret,columns=['property', ' average price/sqm', 'unit type'])
           ret = tabulate(ret, headers='keys', tablefmt='psql')
           print(ret) 
        elif userChoice == '7': #all of amenities should be there or some of them?
            area = input("Enter area: ")
            minPrice = input("Enter minimum price: ")
            maxPrice = input("Enter max price: ")
            amenitiesAmount = input("Enter number of amenities you will enter: ")
            amenities = []
            for i in range (0, int(amenitiesAmount)):
                amenities.append(input("Enter amenity: "))
            amenitiesCleaned = str(amenities)
            amenitiesCleaned = amenitiesCleaned.replace("[","")
            amenitiesCleaned = amenitiesCleaned.replace("]","")
            # print(amenitiesCleaned)
            query = "SELECT Distinct P.property_name, price from property P inner join amenities A on P.p_no = A.p_no  where amenity in ({}) and P.price >= '{}' and P.price < '{}' and P.p_area = '{}';".format(amenitiesCleaned, minPrice, maxPrice, area)
            cur.execute(query)
            ret = cur.fetchall()
            ret = pd.DataFrame(ret,columns=['property', 'price'])
            ret = tabulate(ret, headers='keys', tablefmt='psql')
            print(ret)
        elif userChoice == '8':
           unitType = input("Enter unit type: ")
           query = "Select p_area, count(p_no), price/property_size from property where property_type = '{}' Group by 1, 3 order by 2 desc, 3 desc limit 10;".format(unitType)
           cur.execute(query)
           ret = cur.fetchall()
           ret = pd.DataFrame(ret,columns=['area', 'amount of inventory', 'price/sqm'])
           ret = tabulate(ret, headers='keys', tablefmt='psql')
           print(ret) 
        elif userChoice == '9':
            query = "SELECT B.company_name, active_listings, avg(P.price/P.property_size), count(A.agent_name), count(P.p_no)/count(A.agent_name) From broker_company B inner join agent A on  B.company_name = A.company_name inner join property P on P.contact_number = A.contact_number Group by 1,2 order by 2 desc,3 desc,4 desc ,5 desc limit 5 "
            cur.execute(query)
            ret = cur.fetchall()
            ret = pd.DataFrame(ret,columns=['broker company', 'listing', 'average price/sqm', 'number of agents','average listings per agent'])
            ret = tabulate(ret, headers='keys', tablefmt='psql')
            print(ret)
        elif userChoice == '10':
            choice = input("Will you enter: \n 1. agent name  \n 2. phone number? \n ")
            if choice == '1':
                agentName = input("Enter agent name: ")
                query = "SELECT property_name from property P inner join agent A on A.contact_number = P.contact_number where A.agent_name = '{}';".format(agentName)
                cur.execute(query)
                ret = cur.fetchall()
                ret = pd.DataFrame(ret,columns=['property'])
                ret = tabulate(ret, headers='keys', tablefmt='psql')
                print(ret)
            elif choice == '2':
                agentNumber = input("Enter agent number: ")
                query = "SELECT property_name from property where contact_number = '{}';".format(agentNumber)
                cur.execute(query)
                ret = cur.fetchall()
                ret = pd.DataFrame(ret,columns=['property'])
                ret = tabulate(ret, headers='keys', tablefmt='psql')
                print(ret)
            else:
                print("Wrong Entry")
        elif userChoice == '11': 
            loop = False
        else:
            print("Wrong Input, Please try again")
                