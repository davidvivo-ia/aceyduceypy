"""Small Textual widgets used by the TUI."""

from __future__ import annotations

from textual.widgets import Static

from aceyducey.domain import Card
from aceyducey.presentation.card_art import render_back, render_card


class CardWidget(Static):
    """Renders a single card as ASCII art with a CSS class for its color."""

    DEFAULT_CSS = ""

    def __init__(
        self,
        card: Card | None = None,
        *,
        highlighted: bool = False,
        widget_id: str | None = None,
    ) -> None:
        text = self._build_text(card, highlighted=highlighted)
        super().__init__(text, id=widget_id)
        self._refresh_classes(card, highlighted=highlighted)

    @staticmethod
    def _build_text(card: Card | None, *, highlighted: bool) -> str:
        lines = render_back() if card is None else render_card(card, highlighted=highlighted)
        return "\n".join(lines)

    def _refresh_classes(self, card: Card | None, *, highlighted: bool) -> None:
        self.remove_class("red")
        self.remove_class("highlight")
        if highlighted:
            self.add_class("highlight")
        if card is not None and card.suit.is_red:
            self.add_class("red")

    def show(self, card: Card | None, *, highlighted: bool = False) -> None:
        self.update(self._build_text(card, highlighted=highlighted))
        self._refresh_classes(card, highlighted=highlighted)
