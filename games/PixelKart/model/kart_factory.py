from games.PixelKart.model.kart import HumanKart,RandomAIKart,QLearningKart 

class KartFactory:
    """

    """
    @staticmethod
    def create(kart_type,config):
        """
        
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