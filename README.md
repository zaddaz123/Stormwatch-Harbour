
# Stormwatch Harbour

This project is for CGD-460 Agentic Artificial Intelligence, Assignment 2.

## About the Project

I created a simple harbour simulation in Python. It has ships, dockworkers, cargo, and storms.

I tested two worker policies:
- Baseline Agent
- Model-Based Agent

I also added an AI Harbour Master using the GPT-OSS-20B model through the Groq API.

## How to Run

Install Python and open the project folder.

Run the simulation:

```bash
python run.py --seed 11 --policy model
```

To test the baseline agent:

```bash
python run.py --seed 11 --policy baseline
```

You can change the seed to 12 or 13.

## Kaggle Notebook

The `stormwatchharbour.ipynb` file contains the simulation, AI Harbour Master, results, and safety tests.

## Requirements

```bash
pip install pandas matplotlib groq
```

For the LLM tests, a Groq API key is required. Store it securely as `GROQ_API_KEY` in Kaggle Secrets.

## Results

The baseline agent delivered an average of 144 cargo units with 16 storm knock-outs.

The model-based agent delivered 130 units with no storm knock-outs.

The AI Harbour Master also delivered 130 units with no knock-outs in the tested runs.
