import math, random, time
import wandb

run = wandb.init(
    project="guagua-warmup",
    name=f"hello-{int(time.time())}",
    config={"learning_rate": 3e-4, "fake": True},
)

random.seed(42)
for step in range(100):
    reward = 100 * (1 - math.exp(-step / 25)) + random.gauss(0, 3)
    loss = math.exp(-step / 30) + random.uniform(0, 0.05)
    wandb.log({"reward": reward, "loss": loss}, step=step)

wandb.finish()
print("done. dashboard:", run.url)
