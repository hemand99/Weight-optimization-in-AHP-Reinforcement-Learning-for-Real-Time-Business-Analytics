# Weight-optimization-in-AHP-Reinforcement-Learning-for-Real-Time-Business-Analytics
We introduced a Reinforcement Learning (RL) agent inside AHP. The RL continuously adjusts AHP’s weights based on real-time feedback (rewards). This turns AHP into a dynamic learning system that evolves with the market or data environment. This is rarely done in literature; most papers keep RL and AHP separate.
Existing systems: Most AHP or RL papers use static datasets (survey data, old CSVs, offline business case studies). They do not react to changing data or live environments.
Our system:
Uses real-time stock market data from the Finnhub API.
Each decision cycle updates weights and rankings dynamically in response to actual market behavior.
This makes our framework real-time and continuously learning, ideal for business or trading decisions.
Let's review what I've developed (Prototype). Before we start, I'll discuss the Knob.
The “knob” is basically a sensitivity controller; it decides when the system should update the AHP weights.
Why We Need It? Without this knob, the weights would change every single cycle, even if the market change is tiny. That would make the system unstable, weights would keep jumping randomly and the recommendations would flicker.
How does it work? reward = new_avg_AHP_score - previous_avg_AHP_score
If |reward| > 0.02 → market changed noticeably → system updates AHP weights
If |reward| ≤ 0.02 → change is too small → system skips update
