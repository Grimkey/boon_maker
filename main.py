import argparse
import json

from boon import BoonType, Boon
from city import City


boon_values = [
    Boon(type=BoonType.Major, weight=5),
    Boon(type=BoonType.Standard, weight=20),
    Boon(type=BoonType.Minor, weight=50),
    Boon(type=BoonType.Trivial, weight=80),
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Boon Maker',
        description='This is a vampire boon management program')
    parser.add_argument('-p', '--print', action='store_true')
    parser.add_argument('-w', '--whatif', action='store_true')
    parser.add_argument('-n', '--new', action='store_true')

    parser.add_argument('--add', '-a', type=int, default=0, help='Number of boons to add')
    parser.add_argument('--remove', '-r', type=int, default=0, help='Number of boons to remove')

    args = parser.parse_args()

    boon_log_file = 'boon_log.json' if not args.new > 0 else None
    city = City.ctor('vampires.json', boon_log_file, boon_values)
    if args.new:
        print("------------------------------------")
        print("CREATING NEW CITY")
        print("------------------------------------")
    else:
        print("------------------------------------")
        print(f"LOADING BOONS from {boon_log_file}")
        print("------------------------------------")

    if args.remove > 0:
        removed_boon = city.remove_boons(args.remove)
        if len(removed_boon) > 0:
            print("------------------------------------")
            print(f"BOONS PAID OFF")
            print("------------------------------------")
            city.print_resolved_records(removed_boon)

    new_boons = []
    if args.add > 0:
        new_boons = city.add_boons(args.add)
        city.boon_log += new_boons
        print("------------------------------------")
        print(f"BOONS ADDED")
        print("------------------------------------")
        city.print_records(new_boons)

    if args.print:
        print("------------------------------------")
        print(f"CURRENT CITY BOONS")
        print("------------------------------------")
        city.print_log()
    if args.whatif:
        print("------------------------------------")
        print(f"TEST RUN. NOTHING RECORDED")
        print("------------------------------------")
    else:
        log_as_json = json.dumps(city.to_record(), indent=4)
        with open("boon_log.json", "w") as outfile:
            outfile.write(log_as_json)