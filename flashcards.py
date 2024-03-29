import json
import sys
from argparse import ArgumentParser
from dataclasses import asdict, dataclass
from io import StringIO
from pathlib import Path
from random import choices
from shutil import copyfileobj
from typing import Callable


log_file: StringIO = StringIO()


def print_and_log(text: object = "") -> None:
    print(text, file=log_file)
    print(text)


def input_and_log(prompt: object = "") -> str:
    user_input = input(prompt)
    print(prompt, user_input, sep="", file=log_file)
    return user_input


@dataclass
class Card:
    term: str
    definition: str
    errors: int


class Controller:
    import_from: str or None
    export_to: str or None
    cards: dict[str, Card] = {}

    def __init__(self, **kwargs) -> None:
        self.import_from = kwargs.get("import_from")
        self.export_to = kwargs.get("export_to")

    def start(self) -> None:
        if self.import_from is not None:
            self.import_cards(self.import_from)

        options: dict[str, Callable] = {
            "add": self.add_cards,
            "remove": self.remove_cards,
            "import": self.import_cards,
            "export": self.export_cards,
            "ask": self.ask_cards,
            "exit": self.exit,
            "log": self.log,
            "hardest card": self.hardest_card,
            "reset stats": self.reset_stats,
        }

        while True:
            choice = input_and_log(f"Input the action ({', '.join(options)}):\n")
            if choice in options:
                options[choice]()
            print_and_log()

    def add_cards(self) -> None:
        term = input_and_log("The card:\n")
        while term in self.cards.keys():
            term = input_and_log(f'The card "{term}" already exists. Try again:\n')

        definition = input_and_log("The definition of the card:\n")
        while definition in [card.definition for card in self.cards.values()]:
            definition = input_and_log(f'The definition "{definition}" already exists. Try again:\n')

        print_and_log(f'The pair ("{term}":"{definition}") has been added.')
        self.cards[term] = Card(term, definition, 0)

    def remove_cards(self) -> None:
        term = input_and_log("Which card?\n")
        if term in self.cards.keys():
            print_and_log("The card has been removed.")
            del self.cards[term]
        else:
            print_and_log(f'Can\'t remove "{term}": there is no such card.')

    def import_cards(self, file_name: str or None = None) -> None:
        if file_name is None:
            file_name = input_and_log("File name:\n")
        try:
            cards = json.loads(Path(file_name).read_text())
        except FileNotFoundError:
            print_and_log(f'File "{file_name}" not found.')
        else:
            self.cards = {card["term"]: Card(**card) for card in cards}
            print_and_log(f"{len(self.cards)} cards have been loaded.")

    def export_cards(self, file_name: str or None = None) -> None:
        if file_name is None:
            file_name = input_and_log("File name:\n")
        Path(file_name).write_text(
            json.dumps([asdict(card) for card in self.cards.values()])
        )
        print_and_log(f"{len(self.cards)} cards have been saved.")

    def ask_cards(self) -> None:
        def wrong(answer_def, correct_def) -> str:
            if existing := list(
                filter(lambda x: x.definition == answer_def, self.cards.values())
            ):
                msg = [
                    f'Wrong. The right answer is "{correct_def}", ',
                    f'but your definition is correct for "{existing[0].term}".',
                ]
            else:
                msg = [f'Wrong. The right answer is "{correct_def}".']
            return "".join(msg)

        times_to_ask = int(input_and_log("How many times to ask?\n"))

        for card in choices(list(self.cards.values()), k=times_to_ask):
            answer = input_and_log(f'Print the definition of "{card.term}":\n')
            if answer == card.definition:
                print_and_log("Correct!")
            else:
                print_and_log(wrong(answer, card.definition))
                card.errors += 1

    def hardest_card(self) -> None:
        if with_errors := list(filter(lambda x: x.errors > 0, self.cards.values())):
            hardest = sorted(with_errors, key=lambda x: x.errors, reverse=True)
            top = [card for card in hardest if card.errors == hardest[0].errors]
            if len(top) > 1:
                msg = [
                    "The hardest cards are ",
                    ", ".join(f'"{card.term}"' for card in top),
                    f". You have {top[0].errors} errors answering them.",
                ]
            else:
                msg = [
                    "The hardest card is ",
                    f'"{hardest[0].term}". ',
                    f"You have {hardest[0].errors} errors answering it.",
                ]
            print_and_log("".join(msg))
        else:
            print_and_log("There are no cards with errors.")

    def reset_stats(self) -> None:
        for card in self.cards.values():
            card.errors = 0
        print_and_log("Card statistics have been reset.")

    def exit(self) -> None:
        print_and_log("Bye bye!")
        if self.export_to is not None:
            self.export_cards(self.export_to)
        sys.exit()

    @staticmethod
    def log() -> None:
        file_name = input_and_log("File name:\n")
        with Path(file_name).open(mode="a") as file:
            log_file.seek(0)
            copyfileobj(log_file, file)
        print_and_log("The log has been saved.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--import_from")
    parser.add_argument("--export_to")
    args = parser.parse_args()

    Controller(**vars(args)).start()
