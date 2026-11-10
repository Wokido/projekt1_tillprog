import csv
from dataclasses import dataclass, replace
from pathlib import Path


DATA_FILE = Path(__file__).with_name("generals.csv")
FIELDNAMES = [
    "id",
    "name",
    "nationality",
    "birth_year",
    "death_year",
    "known_for",
]


@dataclass
class General:
    id: int
    name: str
    nationality: str
    birth_year: int | None
    death_year: int | None
    known_for: str


def parse_year(value: str) -> int | None:
    value = value.strip()
    return int(value) if value else None


def load_generals(filename: Path = DATA_FILE) -> list[General]:
    if not filename.exists():
        save_generals([], filename)
        return []

    generals = []
    seen_ids = set()
    with filename.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not set(FIELDNAMES).issubset(reader.fieldnames):
            raise ValueError("CSV-filen saknar en eller flera kolumner.")

        for line_number, row in enumerate(reader, start=2):
            try:
                general_id = int(row["id"])
                name = row["name"].strip()
                nationality = row["nationality"].strip()
                known_for = row["known_for"].strip()
                birth_year = parse_year(row["birth_year"])
                death_year = parse_year(row["death_year"])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Ogiltiga uppgifter på rad {line_number} i CSV-filen."
                ) from error

            if general_id < 1 or general_id in seen_ids:
                raise ValueError(
                    f"Ogiltigt eller dubblerat ID på rad {line_number} i CSV-filen."
                )
            if not name or not nationality or not known_for:
                raise ValueError(
                    f"Obligatoriska uppgifter saknas på rad {line_number} i CSV-filen."
                )

            seen_ids.add(general_id)
            generals.append(
                General(
                    id=general_id,
                    name=name,
                    nationality=nationality,
                    birth_year=birth_year,
                    death_year=death_year,
                    known_for=known_for,
                )
            )
    return generals


def save_generals(generals: list[General], filename: Path = DATA_FILE) -> None:
    with filename.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for general in generals:
            writer.writerow(
                {
                    "id": general.id,
                    "name": general.name,
                    "nationality": general.nationality,
                    "birth_year": "" if general.birth_year is None else general.birth_year,
                    "death_year": "" if general.death_year is None else general.death_year,
                    "known_for": general.known_for,
                }
            )


def prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("Fältet får inte vara tomt.")


def prompt_year(label: str, current: int | None = None, editing: bool = False) -> int | None:
    while True:
        if editing:
            shown = "okänt" if current is None else str(current)
            value = input(f"{label} [{shown}] (Enter = behåll, - = okänt): ").strip()
            if not value:
                return current
            if value == "-":
                return None
        else:
            value = input(f"{label} (Enter om okänt): ").strip()
            if not value:
                return None

        try:
            return int(value)
        except ValueError:
            print("Ange ett heltal, eller lämna fältet tomt.")


def prompt_id(prompt: str) -> int | None:
    value = input(prompt).strip()
    try:
        general_id = int(value)
        if general_id < 1:
            raise ValueError
        return general_id
    except ValueError:
        print("Ange ett giltigt positivt ID.")
        return None


def list_generals(generals: list[General]) -> None:
    print("\n" + "=" * 78)
    print(f"{'ID':<5} {'Namn':<25} {'Nationalitet':<20} {'Levde':<20}")
    print("-" * 78)
    if not generals:
        print("Registret är tomt.")
    for general in generals:
        birth_year = "?" if general.birth_year is None else str(general.birth_year)
        death_year = "?" if general.death_year is None else str(general.death_year)
        years = f"{birth_year}–{death_year}"
        print(
            f"{general.id:<5} {general.name:<25.25} "
            f"{general.nationality:<20.20} {years:<20}"
        )
    print("=" * 78)


def find_general(generals: list[General]) -> General | None:
    if not generals:
        print("Det finns inga generaler i registret.")
        return None
    general_id = prompt_id("Ange generalens ID")
    if general_id is None:
        return None
    general = next((item for item in generals if item.id == general_id), None)
    if general is None:
        print(f"Ingen general med ID {general_id} hittades.")
    return general


def show_general(general: General) -> None:
    print("\n" + "=" * 50)
    print(f"ID:             {general.id}")
    print(f"Namn:           {general.name}")
    print(f"Nationalitet:   {general.nationality}")
    print(f"Födelseår:      {general.birth_year if general.birth_year is not None else 'Okänt'}")
    print(f"Dödsår:         {general.death_year if general.death_year is not None else 'Okänt'}")
    print(f"Känd för:       {general.known_for}")
    print("=" * 50)


def add_general(generals: list[General], filename: Path = DATA_FILE) -> None:
    print("\nLÄGG TILL GENERAL")
    general = General(
        id=max((item.id for item in generals), default=0) + 1,
        name=prompt_required("Namn"),
        nationality=prompt_required("Nationalitet"),
        birth_year=prompt_year("Födelseår"),
        death_year=prompt_year("Dödsår"),
        known_for=prompt_required("Känd för"),
    )
    generals.append(general)
    try:
        save_generals(generals, filename)
    except OSError as error:
        generals.pop()
        print(f"Kunde inte spara ändringen: {error}")
        return
    print(f"{general.name} har lagts till med ID {general.id}.")


def edit_general(generals: list[General], filename: Path = DATA_FILE) -> None:
    general = find_general(generals)
    if general is None:
        return

    print("Tryck Enter för att behålla nuvarande textvärde.")
    updated = replace(
        general,
        name=input(f"Namn [{general.name}]: ").strip() or general.name,
        nationality=input(
            f"Nationalitet [{general.nationality}]: "
        ).strip()
        or general.nationality,
        birth_year=prompt_year("Födelseår", general.birth_year, editing=True),
        death_year=prompt_year("Dödsår", general.death_year, editing=True),
        known_for=input(f"Känd för [{general.known_for}]: ").strip()
        or general.known_for,
    )
    index = generals.index(general)
    generals[index] = updated
    try:
        save_generals(generals, filename)
    except OSError as error:
        generals[index] = general
        print(f"Kunde inte spara ändringen: {error}")
        return
    print(f"Uppgifterna om {updated.name} har uppdaterats.")


def delete_general(generals: list[General], filename: Path = DATA_FILE) -> None:
    general = find_general(generals)
    if general is None:
        return
    confirmation = input(f"Ta bort {general.name}? (j/n): ").strip().lower()
    if confirmation != "j":
        print("Borttagningen avbröts.")
        return

    index = generals.index(general)
    generals.pop(index)
    try:
        save_generals(generals, filename)
    except OSError as error:
        generals.insert(index, general)
        print(f"Kunde inte spara ändringen: {error}")
        return
    print(f"{general.name} har tagits bort.")


def main() -> None:
    try:
        generals = load_generals()
    except (OSError, csv.Error, ValueError) as error:
        print(f"Kunde inte läsa generals.csv: {error}")
        print("Kontrollera filen. Originalfilen har inte skrivits över.")
        return

    while True:
        print(
            "\nLAGERHANTERARE – HISTORIENS GENERALER\n"
            "1. Visa alla generaler\n"
            "2. Visa detaljer om en general\n"
            "3. Lägg till general\n"
            "4. Redigera general\n"
            "5. Ta bort general\n"
            "Q. Avsluta"
        )
        choice = input("Välj ett alternativ: ").strip().lower()

        try:
            if choice == "1":
                list_generals(generals)
            elif choice == "2":
                general = find_general(generals)
                if general is not None:
                    show_general(general)
            elif choice == "3":
                add_general(generals)
            elif choice == "4":
                edit_general(generals)
            elif choice == "5":
                delete_general(generals)
            elif choice == "q":
                print("Registret är sparat. Hej då!")
                break
            else:
                print("Ogiltigt val. Välj 1–5 eller Q.")
        except (EOFError, KeyboardInterrupt):
            print("\nProgrammet avslutas.")
            break


if __name__ == "__main__":
    main()
