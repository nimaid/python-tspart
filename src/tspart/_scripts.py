import argparse
import sys

from tspart.constants import DESCRIPTION


# Parse arguments
def parse_args(args):
    parser = argparse.ArgumentParser(
        description=f"{DESCRIPTION}\n\n"
                    f"Valid parameters are shown in {{braces}}\n"
                    f"Default parameters are shown in [brackets].",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    '''
    parser.add_argument("-1", "--first", dest="first_arg", type=float, required=True,
                        help="the first argument"
                        )

    parser.add_argument("-2", "--second", dest="second_arg", type=float, required=False, default=1.0,
                        help="the second argument [{default}]".format(
                            default=DEFAULTS["second"])
                        )

    parser.add_argument("-o", "--operation", dest="opcode", type=str, required=False, default="+",
                        help="the operation to perform on the arguments, either {{{values}}} [{default}]".format(
                            values=", ".join([x.value for x in OpCode]),
                        default=DEFAULTS["opcode"].value)
                        )
    '''

    parsed_args = parser.parse_args(args)

    '''
    # Interpret string arguments
    if parsed_args.opcode is not None:
        if parsed_args.opcode in [x.value for x in OpCode]:
            parsed_args.opcode = OpCode(parsed_args.opcode)
        else:
            parser.error(f"\"{parsed_args.opcode}\" is not a valid opcode")
    '''

    return parsed_args


def main(args):
    parsed_args = parse_args(args)




def run():
    main(sys.argv[1:])
