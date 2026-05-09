from games.pixelKart.dao import circuit_dao
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.kart import QLearningKart
from games.pixelKart.model.race import Race

circuits = circuit_dao.get_all()
circuit_dto = circuits["Basic"]
circuit = Circuit.from_dto(circuit_dto)

kart = QLearningKart(
    name="Test",
    color="red",
    position=(1, 7),
    direction="EAST",
    speed=1,
)

race = Race(circuit=circuit, karts=[kart], total_laps=1)

print("Before:")
print("position =", kart.position)
print("speed =", kart.speed)
print("laps =", kart.laps_done)
print("finished =", kart.has_finished)

race.play_current_turn("pass")

print("\nAfter:")
print("position =", kart.position)
print("speed =", kart.speed)
print("laps =", kart.laps_done)
print("finished =", kart.has_finished)
print("race finished =", race.finished)
print("winner =", race.winner_name)