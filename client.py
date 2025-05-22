import threading

from presenter.GamePresenter import GamePresenter
from view.PyGameView import PygameView

def main():
    try:
        view = PygameView()
        presenter = GamePresenter(view)
        view.set_observer(presenter)
        threading.Thread(target=presenter.run, daemon=True).start()
        view.run()
    except Exception as e:
        print(f"Error: {e}")

main()