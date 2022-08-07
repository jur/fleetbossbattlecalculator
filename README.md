# Star trek timelines fleet boss battles.

In fleet boss battles the correct combinations of traits need to be found.
The script helps to list the possible combinations.

## Steps
1. Download https://datacore.app/structured/crew.json and save as crew.json where the script is, for example `wget https://datacore.app/structured/crew.json`. This needs to be updated when new crew is added to the game.
1. Login into the game using a web browser.
2. Go to web page https://stt.disruptorbeam.com/fleet_boss_battles/refresh?desc_id=4&client_api=19, this needs to be updated when someone used the correct crew in the fleet boss battle or the battle is restarted.
3. Safe the web page where the script is located, (file name refresh.json).
4. Run the script analyse\_fleet\_boss.py on command line (tested with Linux)

This will print combinations and crew which might unlock.
Only one crew with a selected trait combination has to be tested. When this
does not work a crew with a different trait combination needs to be tested.
"desc\_id" select the difficulty level, 4 is brutal.

|desc\_id|Difficulty Level |
|--------|-----------------|
|      1 | Easy            |
|      2 | Normal          |
|      3 | Hard            |
|      4 | Brutal          |
|      5 | Nightmare       |
|      6 | Ultra Nightmare |

## Reducing slots
The script tries to find slots where all posisble combinations uses the same
trait. The script will remove that trait and check if there are less
combinations left. The script will print the reduced list also.

## Tested crew
When you tested crew, you can tell the script with the parameter "-s" that a
crew was tested and not working. For example:
```./analyse_fleet_boss.py -s "3:Ambassador Spock"```
