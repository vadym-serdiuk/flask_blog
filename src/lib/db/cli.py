from argparse import ArgumentParser

from app import get_app, get_config
from lib.db.models import db


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('command')
    # create_tables_command = parser.add_subparsers(title='createtables')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    if args.command == 'create_tables':
        from . import models
        app = get_app(get_config())
        with app.app_context():
            db.create_all()
        print('Tables were created')


if __name__ == '__main__':
    main()
