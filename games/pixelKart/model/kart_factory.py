from games.pixelKart.model.kart import HumanKart,RandomAIKart,QLearningKart 

class KartFactory:
    """Factory class to create instances of different kart types."""

    @staticmethod
    def create(kart_type,config):
        """
        Create a kart instance based on the specified type and configuration.

        Args:
            kart_type: Type of kart to create ("human", "random", or "ql").
            config: Dictionary containing kart configuration (name, color, position, etc.).

        Returns:
            An instance of the specified kart type.

        Raises:
            ValueError: If the kart type is unknown.
        """
        
        name = config["name"]
        color = config["color"]
        position = config["position"]

        if kart_type == "human":
            return HumanKart(name, color, position, direction="EAST")

        elif kart_type == "random":
            return RandomAIKart(name, color, position, direction="EAST")

        elif kart_type == "ql":
            return QLearningKart(
                name, color, position, direction="EAST",
                q_table=config.get("q_table", {}),
                epsilon=config.get("epsilon", 0.9),
                alpha=config.get("alpha", 0.2),
                gamma=config.get("gamma", 0.95)
    )

        else:
            raise ValueError(f"Unknown kart type: {kart_type}")