from games.cubee.trainer import CubeeTrainer

trainer = CubeeTrainer(size=4)
results = trainer.benchmark_parameters(
    train_episodes=100000,
    eval_games=2000,
    save_qtables=True,
)

for row in results:
    print(row)