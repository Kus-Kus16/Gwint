import polib
from pathlib import Path

def main():
    locales_dir = Path("./")

    for po_path in locales_dir.rglob("*.po"):
        mo_path = po_path.with_suffix(".mo")

        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))

if __name__ == "__main__":
    main()