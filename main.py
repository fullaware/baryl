import logging
import mine_asteroid

asteroid_name = " 1986 Plaut (1935 SV1)"
uid = "Brandon"
extraction_rate = 1000  # Set the maximum extraction rate

mine_asteroid.log(f"Retrieving asteroid info for {asteroid_name}", logging.INFO)
asteroid = mine_asteroid.get_asteroid_by_name(asteroid_name)
mine_asteroid.log(f"Asteroid mass before mining: {asteroid['mass']} kg", logging.INFO)
mine_asteroid.log(f"Mining asteroid...{asteroid_name}", logging.INFO)
asteroid, total_elements_mined = mine_asteroid.mine_asteroid(asteroid, extraction_rate, uid)


mine_asteroid.log(f"Asteroid mass after mining: {asteroid['mass']} kg", logging.INFO)
mine_asteroid.log(f"Your uid : {asteroid['uid']}", logging.INFO)
mine_asteroid.log(f"This asteroids mined mass : {asteroid['total_elements_kg']}", logging.INFO)

# Uncomment the following line to update the asteroid in the database
mine_asteroid.update_asteroid(asteroid)