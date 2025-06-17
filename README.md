<h3>Attendance Modifications module for EYK (forcefx)</h3>

Requirements:

Project: Create a custom Odoo15 community Edition app 

1)Milestone 	Limit and Display of monthly Work hours per User

⦁	Optional Set Limit of Monthly workhours per User (Screenshot HR Settings)
⦁	Check every 5 min if the Monthly total workhours are full, than checkout and add to „Pin Code“ 99 to the user can not checkin again. Nice would be an Email notify when this happened.
⦁	Show total workhours this month and when there is a Monthly Limit is Set show hours left this month. Both after kiosk checkin or checkout (Like on Screenshot)
⦁	Nice would be if I can set the Pin Code suffix which will be added to the Pin in the attendance settings mene.

2.	2)	Milestone 	Split Attendance entrys if neccesary

We need to make sure for every employee  break times are present in all entrys according to following ruleset:
More than 6 Working Hours a Day Total of 30min break
More than 9 Working Hours a Day Total of 45min break

Every Morning check and modify the entrys from the Day before.
⦁	Sum up all working hours for the Day
⦁	Sum up all „break“ times from the first checkin entry till the last checkout entry of the Day. 
⦁	If the break time is lower than the listed in the ruleset for the amount of working hours than the entrys have to get changed.
⦁	Examples of Entrys and how to change them are in the attached file.

3.	3)  Milestone 	Get a PDF Report for every employee and month  
-List all attendance and breaks

In General: 
⦁	Please use English for comments in the code an text shown to user
⦁	Please leave short comments in the code  so if we later need to change something its easier to understand
⦁	Please be aware of timezones. So use the local time of the system.
⦁	Every String shown to User please use „translate feature“ so we can later add a German translation
⦁	The App should be installable like every other third party Oddo app
(Place it in the add-on folder on the server an install it via Oddo webgui)

