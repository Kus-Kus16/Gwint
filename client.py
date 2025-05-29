import threading

from presenter.game_presenter import GamePresenter
from view.pygame_view import PygameView

def main():
    view = PygameView()
    presenter = GamePresenter(view)
    view.set_observer(presenter)
    threading.Thread(target=presenter.run, daemon=True).start()
    view.run()

if __name__ == "__main__":
    main()