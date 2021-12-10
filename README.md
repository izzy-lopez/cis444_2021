# Hogwarts Bookstore

Although this repository stores all of my work done in CIS444, my Hogwarts Bookstore project is what I would like to highlight in this repository. This application is a refactor of my previous bookstore assignment. With the help of [Cordova](https://cordova.apache.org/), my original web application was converted into a cross-platform mobile application. Being the Potterhead that I am, I also took the opportunity during refactor to theme the bookstore around The Wizarding World of Harry Potter.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the dependencies for this project under the hogwarts_bookstore directory.

```bash
pip install -r requirements.txt
```

## Usage

```bash
# starts the Flask server
python3 app.py

# emulates an ios app
cordova emulate ios

# emulates an android app
cordova emulate android
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
