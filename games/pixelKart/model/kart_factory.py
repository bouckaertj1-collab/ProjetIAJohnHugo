from games.pixelKart.model.kart import HumanKart, Kart, QLearningKart, RandomAIKart


class KartFactory:
    """
    Factory responsible for creating PixelKart kart instances.

    The factory centralizes the creation of the different kart types used by
    the game:
        - HumanKart for a player-controlled kart;
        - RandomAIKart for a simple AI choosing random actions;
        - QLearningKart for an AI using a learned Q-table.

    This avoids duplicating kart creation logic in controllers and in the
    automated training script. The factory does not contain race logic,
    movement logic or learning logic. It only decides which Kart subclass must
    be instantiated from the provided type and configuration.
    """

    @staticmethod
    def create(kart_type: str, config: dict) -> Kart:
        """
        Create a kart instance from a kart type and a configuration dictionary.

        Required configuration keys:
            - name: kart name displayed in the interface;
            - color: kart color used by the graphical view;
            - position: initial position as a tuple (row, col).

        Optional configuration keys:
            - direction: initial direction, default is EAST;
            - q_table: learned Q-table used only by QLearningKart;
            - epsilon: exploration rate used only by QLearningKart;
            - alpha: learning rate used only by QLearningKart;
            - gamma: discount factor used only by QLearningKart.

        Args:
            kart_type: Type of kart to create. Expected values are:
                "human", "random" or "ql".
            config: Dictionary containing the values needed to initialize
                the selected kart type.

        Returns:
            A Kart instance matching the requested type.

        Raises:
            ValueError: If kart_type does not match any known kart type.

        Example:
            KartFactory.create(
                kart_type="ql",
                config={
                    "name": "AI",
                    "color": "blue",
                    "position": (1, 1),
                    "q_table": {},
                    "epsilon": 0.0,
                    "alpha": 0.2,
                    "gamma": 0.95,
                },
            )
        """
        name = config["name"]
        color = config["color"]
        position = config["position"]
        direction = config.get("direction", "EAST")

        if kart_type == "human":
            return HumanKart(name, color, position, direction=direction)

        if kart_type == "random":
            return RandomAIKart(name, color, position, direction=direction)

        if kart_type == "ql":
            return QLearningKart(
                name,
                color,
                position,
                direction=direction,
                q_table=config.get("q_table", {}),
                epsilon=config.get("epsilon", 0.9),
                alpha=config.get("alpha", 0.2),
                gamma=config.get("gamma", 0.95),
            )

        raise ValueError(f"Unknown kart type: {kart_type}")