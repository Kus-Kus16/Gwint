import threading

from presenter.GamePresenter import GamePresenter
from view.PyGameView import PygameView

def main():
    view = PygameView()
    presenter = GamePresenter(view)
    view.set_observer(presenter)
    threading.Thread(target=presenter.run, daemon=True).start()
    view.run()

if __name__ == "__main__":
    main()