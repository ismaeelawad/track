# track
### [Video Demo](https://youtu.be/IziL7g-OZ3I)
#### Description:
  **track** is a web app that allows you to record your times for running _(or really any timed sport)_. It automatically calculates your personal records, allows you to see a graph of your progress, and you can even set goals for yourself.

#### Technical details
  **track** uses HTML, CSS and JavaScript for the frontend and Python and SQL for the backend.

The modules used are:
  - `flask` (and `flask_session`) as the web framework,
  - `cs50` for using SQL,
  - `functools` for function decorators,
  - `datetime` for managing dates,
  - and `hashlib` to hash passwords for storage.

It also uses Plotly.js to render graphs.

##### Files:
- `app.py` the Python code for the web app.
- `project.db` database containing the users, times, goals, etc..
- `static/` contains the logo, favicons and CSS stylesheet.
- `templates/` contains the .html files for the web pages.

## Usage
### Starting the app
#### PythonAnywhere
You can click [here](https://ismaeel.pythonanywhere.com/) to visit the version of the web app hosted on PythonAnywhere's server. I'm not entrirely sure if this will remain online forever, so you might find that it has changed or went down if you're viewing this in the far future.

#### Locally
You can easily run a local version on your computer by cloning the repo and installing all the requirements in the Technical Details section. You then just run `app.py` and click the link that it outputs to the console. The database already comes with an account with the username **user** and the password **123** if you want to mess around.

### Creating an Account
When visiting the website, you'll be prompted to log in or register a new account. Clicking on Register New Account allows you to set a username for your account and a password. Usernames have to be unique, if your username is already taken, you'll get an error message. There are, however, no requirements for your password.

### Adding Distances
After logging in and before logging any times, you need to add the distances or events you run e.g. 100m, 400m, 5Km, etc.. Clicking on Distances in the top bar and the Add Distance button allows you to do that. 

### Logging times
In order to start logging times, you need to have at least one distance added. Click on Log in the top bar and then Add New Entry button to start. Here you need to choose the distance, enter your time, and enter the date you acheived the time on. After submitting you will be taken back to the Log page. To remove an entry, simply press the ✖ symbol next to it and enter your password.

### Tracking progress
Click on the Distances menu and choose one of your distances. Here you'll see your current PR, a graph of your progress over time and all the times you have logged for that distance. You also have the option of changing the name of the distance or removing the distance and all its times completely. 

### Setting Goals
Click on Goals in the top bar and Set New Goal. Here you need to choose the distance, enter your target time and the date you're aiming to acheive the goal before. When redirected to the Goals page again, you'll be able to see all the goals you've set for yourself. Goals in blue are in progress, goals in yellow are overdue and goals in green are completed. To remove a goal, press the ✖ next to it and enter your password.


That's basically it!

## 
The idea for this web app came to me because I very recently started running and I thought it would be cool to have something that I could track my progress on. There is probably a much better alternative app or website out there, but I just wanted the experience of building something like that.

As you might be able to tell from looking at the code, its not the most robust or well designed web app out there. This is mostly because I kind or made it up as I went along, so there are many things that could be improved. The CSS I wrote for it is especially terrible, with so many repeated things and many completely unrelated elements using the same classes, so a lot of things ended up looking weird and having to be fixed with inline style attributes in the HTML. I have to admit, I referenced the `finance` Problem Set a lot during the making of this, the setup of the `session` and the `@login_required` decorator are taken directly from it. Of course, the `cs50` module is what handles the SQL code, I honestly found it much simpler to just use it for my purposes than learning SQLAlchemy. I also feel like the code also had many repetitions and a lot of tasks are done pretty inefficiently, so I hope to improve that in the future. 

Some other things I hope to add in the future are more profile customization options (e.g. profile pictures), support for more sports that are not timed, (e.g. javelin throw, pole vault, etc.), and definitely try and make the web app more scalable, because I think the database management is pretty inefficient.
