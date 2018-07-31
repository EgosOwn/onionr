# Onionr UI

## About

The default GUI for Onionr

## Setup

To compile the application, simply execute the following:

```
python3 compile.py
```

If you are wanting to compile Onionr UI for another language, execute the following, replacing `[lang]` with the target language (supported languages include `eng` for English, `spa` para español, and `zho`为中国人):

```
python3 compile.py [lang]
```

## FAQ
### Why "compile" anyway?
This web application is compiled for a few reasons:
1. To make it easier to update; this way, we do not have to update the header in every file if we want to change something about it.
2. To make the application smaller in size; there is less duplicated code when the code like the header and footer can be stored in an individual file rather than every file.
3. For multi-language support; with the Python "tags" feature, we can reference strings by variable name, and based on a language file, they can be dynamically inserted into the page on compilation.
4. For compile-time customizations.

### What exactly happens when you compile?
Upon compilation, files from the `src/` directory will be copied to `dist/` directory, header and footers will be injected in the proper places, and Python "tags" will be interpreted.


### How do Python "tags" work?
There are two types of Python "tags":
1. Logic tags (`<$ logic $>`): These tags allow you to perform logic at compile time. Example: `<$ import datetime; lastUpdate = datetime.datetime.now() $>`: This gets the current time while compiling, then stores it in `lastUpdate`.
2. Data tags (`<$= data $>`): These tags take whatever the return value of the statement in the tags is, and write it directly to the page. Example: `<$= 'This application was compiled at %s.' % lastUpdate $>`: This will write the message in the string in the tags to the page.

**Note:** Logic tags take a higher priority and will always be interpreted first.

### How does the language feature work?
When you use a data tag to write a string to the page (e.g. `<$= LANG.HELLO_WORLD $>`), the language feature simply takes dictionary of the language that is currently being used from the language map file (`lang.json`), then searches for the key (being the variable name after the characters `LANG.` in the data tag, like `HELLO_WORLD` from the example before). It then writes that string to the page. Language variables are always prefixed with `LANG.` and should always be uppercase (as they are a constant).

### I changed a few things in the application and tried to view the updates in my browser, but nothing changed!
You most likely forgot to compile. Try running `python3 compile.py` and check again. If you are still having issues, [open up an issue](https://gitlab.com/beardog/Onionr/issues/new?issue[title]=Onionr UI not updating after compiling).