from games.pixelKart.model.kart import HumanKart, Kart, QLearningKart, RandomAIKart


class KartFactory:
    """Create kart instances from a kart type and configuration."""

    @staticmethod
    def create(kart_type: str, config: dict) -> Kart:
        """
        Create a kart instance.

        Args:
            kart_type: Type of kart to create: "human", "random" or "ql".
            config: Values used to initialize the kart.

        Returns:
            Kart instance matching the requested type.

        Raises:
            ValueError: If the kart type is unknown.
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