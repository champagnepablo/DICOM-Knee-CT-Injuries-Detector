import argparse
from gooey import Gooey, GooeyParser
from functools import reduce

@Gooey(program_name= " TA-TG TC Knee Detector")
def main():
    desc = "Example application to show Gooey's various widgets"
    file_help_msg = "Name of the file you want to process"
    my_cool_parser = GooeyParser(description=desc)
    my_cool_parser.add_argument("Select .dcm or image  file of Femur", help='Choose a directory', widget="FileChooser")
    my_cool_parser.add_argument("Select .dcm file or img  of Tibia", help='Choose a directory', widget="FileChooser")
    my_cool_parser.parse_args()
    display_message()
    print()

main()