# BriscolaAI

## Installation

```
git clone https://github.com/Tortar/BriscolaAI.git
pip install -e BriscolaAI/briscolaAI
```

## Training and Evaluation

- You can run the training by copy pasting the code in [`briscolaAI/main`](https://github.com/Tortar/BriscolaAI/blob/main/briscolaAI/main.py)
- You can run the evaluation by running the code in [`agent_predictions.ipynb`](https://github.com/Tortar/BriscolaAI/blob/main/agent_predictions.ipynb)

## Models and Results

- Some trained models are available in the [`models`](https://github.com/Tortar/BriscolaAI/tree/main/models) folder, `checkpoint_dqn_episode_94000` is the strongest DQN-agent.
- Some summarizing results are available in the [`results`](https://github.com/Tortar/BriscolaAI/tree/main/results) folder, e.g. the training process involved making the agent play     games against an agent playing randomly and a rule-based agent (with a 82% win-rate against the random agent), DQN-agent strength increased substantially during training as can be seen from these two graphs


<figure class="half" style="display:flex">
    <img style="width:48%" src="https://github.com/user-attachments/assets/48968f3a-5a76-4262-9aa6-4b14d819f85c">
    <img style="width:48%" src="https://github.com/user-attachments/assets/8f7ac4f7-60f1-4477-aca9-78d05140750a" >
    <figcaption>Caption describing these two images.</figcaption>
</figure>


