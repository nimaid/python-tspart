import os
import sys
import re
import shutil
import keyboard

PROG_FILE = os.path.realpath(__file__)
PATH = os.path.dirname(PROG_FILE)


# Main class
class Python3TemplateInit:
    def __init__(self,
                 name,
                 module_name,
                 simple_name,
                 author,
                 author_username,
                 author_email,
                 description,
                 version
                 ):
        self.info = {
            "name": name,
            "module_name": module_name,
            "simple_name": simple_name,
            "author": author,
            "author_username": author_username,
            "author_email": author_email,
            "description": description,
            "version": version
        }

        self.file_list = {
            "build": {
                "main": "build.bat",
                "template": "build.bat.template"
            },
            "build_pypi": {
                "main": "build_pypi.bat",
                "template": "build_pypi.bat.template"
            },
            "build_docs": {
                "main": "build_docs.bat",
                "template": "build_docs.bat.template"
            },
            "docs_conf": {
                "main": os.path.join("docs", "src", "conf.py"),
                "template": os.path.join("docs", "src", "conf.py.template"),
            },
            "docs_index": {
                "main": os.path.join("docs", "src", "index.rst"),
                "template": os.path.join("docs", "src", "index.rst.template"),
            },
            "init": {
                "main": os.path.join("src", "module_name", "__init__.py"),
                "template": os.path.join("src", "module_name", "__init__.py.template")
            },
            "env": {
                "main": "environment.yml",
                "template": "environment.yml.template"
            },
            "pyproject": {
                "main": "pyproject.toml",
                "template": "pyproject.toml.template"
            },
            "readme": {
                "main": "README.md",
                "template": "README.md.template"
            },
            "readme-pypi": {
                "main": "README_pypi.md",
                "template": "README_pypi.md.template"
            },
            "program": {
                "main": f"{self.info['name']}.py",
                "template": "name.py.template"
            },
            "version": {
                "main": os.path.join("src", "module_name", "version.yml"),
                "template": os.path.join("src", "module_name", "version.yml.template")
            },
            "links": {
                "main": os.path.join("src", "module_name", "constants", "links.py"),
                "template": os.path.join("src", "module_name", "constants", "links.py.template")
            },
            "manifest": {
                "main": "MANIFEST.in",
                "template": "MANIFEST.in.template"
            }
        }

    def copy_all_files(self):
        for v, k in enumerate(self.file_list):
            shutil.copy(self.file_list[k]["template"], self.file_list[k]["main"])

    @staticmethod
    def replace_key_in_file(file_in, key, value, delim_start="{[", delim_end="]}"):
        full_key = f"{delim_start}{key}{delim_end}"

        with open(file_in, "r") as f:
            file_text = f.read()

        new_text = file_text.replace(full_key, value)

        with open(file_in, "w") as f:
            f.write(new_text)

    def replace_key_in_all_files(self, key, value):
        for v, k in enumerate(self.file_list):
            self.replace_key_in_file(self.file_list[k]["main"], key, value)

    def cleanup(self):
        # Delete source templates
        for v, k in enumerate(self.file_list):
            os.remove(self.file_list[k]["template"])
        # Suicide
        os.remove(PROG_FILE)

    def run(self):
        print()
        print("Project Info Summary")
        print("--------------------")
        for v, k in enumerate(self.info):
            print(f"{k}: {self.info[k]}")
        print()

        print("Project File Renaming")
        print("---------------------")
        for v, k in enumerate(self.file_list):
            template = self.file_list[k]["template"]
            new_file = self.file_list[k]["main"]
            print(f"{template} --> {new_file}")
        print("src{sep}module_name{sep} --> src{sep}{val}{sep}".format(
            val=self.info["module_name"],
            sep=os.path.sep)
        )
        print()

        print("Press [Enter] to continue, any other button to quit...")
        if keyboard.read_key() != "enter":
            exit(1)
        print()

        # Copy new files
        self.copy_all_files()

        # Replace the keys in the new files
        for v, k in enumerate(self.info):
            self.replace_key_in_all_files(k, self.info[k])

        # Delete old files
        self.cleanup()

        # Rename the module dir
        os.rename(os.path.join("src", "module_name"), os.path.join("src", self.info["module_name"]))


# General purpose stripper
def strip_all(input_text):
    return input_text.strip().strip("\n").strip("\r").strip()


# Interactive prompt
def user_prompt(prompt_text):
    prompt_text_stripped = strip_all(prompt_text)
    user_input = input(f"{prompt_text_stripped}: ")
    return strip_all(user_input)


# Tests if a version number is valid
def version_is_valid(version_number):
    if re.match(r"^\d+\.\d+\.\d+$", version_number):
        return True
    else:
        return False


def main(args):
    print()
    name = user_prompt("GitHub name (short, no spaces)")
    module_name = user_prompt("Module name (short, no spaces)")
    simple_name = user_prompt("User-friendly name")
    author = user_prompt("Project author")
    author_username = user_prompt("Project author's username")
    author_email = user_prompt("Project author's email")
    description = user_prompt("Project description")

    is_valid_version = False
    default_version = "0.1.0"
    while not is_valid_version:
        version = user_prompt(f"Starting version number [default: {default_version}]")
        if version == "":
            version = default_version
            is_valid_version = True
        elif not version_is_valid(version):
            print("  ERROR: Version number must be in the format #.#.#")
            print("  (three decimal numbers separated by three periods)")
            print("  Please enter a valid version number, or press")
            print("  enter to accept the default value.")
        else:
            is_valid_version = True

    python_3_template_init = Python3TemplateInit(
        name=name,
        module_name=module_name,
        simple_name=simple_name,
        author=author,
        author_username=author_username,
        author_email=author_email,
        description=description,
        version=version
    )

    python_3_template_init.run()


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
