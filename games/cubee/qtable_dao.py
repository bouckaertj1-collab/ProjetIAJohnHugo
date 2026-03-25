import json

class QTableDAO:
    @staticmethod
    def save(filename, q_table, epsilon, alpha, gamma):
        data = {
            "epsilon": epsilon,
            "alpha": alpha,
            "gamma": gamma,
            "q_table": q_table
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "epsilon": 0.9,
                "alpha": 0.2,
                "gamma": 0.9,
                "q_table": {}
            }

        q_table = {}
        raw_q_table = data.get("q_table", {})

        for state, actions in raw_q_table.items():
            q_table[state] = {}
            for action, value in actions.items():
                q_table[state][action] = float(value)

        return {
            "epsilon": float(data.get("epsilon", 0.9)),
            "alpha": float(data.get("alpha", 0.2)),
            "gamma": float(data.get("gamma", 0.9)),
            "q_table": q_table
        }