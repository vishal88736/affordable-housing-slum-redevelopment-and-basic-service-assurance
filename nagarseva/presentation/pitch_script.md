# NagarSeva pitch script

All figures in this script and the deck are explicitly **synthetic,
calibrated demo numbers**, not official statistics. Replace with cited official
figures and approved municipal data before public policy use.

## Speaker notes — 7-minute version

### 1. Title — 25 seconds

“NagarSeva means city service. Our proposition is simple: plan safer homes,
then prove the services arrive. We built a decision-support layer for the MMR
that connects housing, redevelopment finance, service standards and resident
voice.”

### 2. The problem — 35 seconds

“Housing delivery and service delivery are experienced as one thing by a
resident, but managed as separate things by a city. The first problem is
prioritisation. The second is financial viability. The third is the post-
handover blind spot: a new building is not the same as water, toilets, power,
waste collection and a response to a complaint.”

### 3. Why existing approaches fail — 30 seconds

“Three failure modes keep repeating: fragmented data, one-size intervention,
and no closed loop. NagarSeva creates a common evidence layer from pocket to
project to service SLA.”

### 4. Solution — 35 seconds

“The flow is intentionally understandable. Synthetic pocket and service data
goes through ward-safe feature engineering. Models produce a priority score,
intervention options, service failure probability, cost bands and a grievance
classification. FastAPI makes those outputs inspectable. The React product
gives officers and residents different views of the same decision trail.”

### 5. Data & methodology — 35 seconds

“The demo includes about 1,500 pockets, 20,000 multilingual grievances, 400
project histories and 10,000 households, all generated with a fixed seed. The
generator injects realistic directionality, missingness and noise. Crucially,
these are not real settlements. We documented real plug points: Census,
data.gov.in, NFHS, OSM, Sentinel, WorldPop, MoHUA and city open data.”

### 6. AI models — 45 seconds

“We chose CPU-friendly, explainable methods. The held-out-ward priority model
gets an R-squared of 0.981 in the synthetic benchmark and exposes plain-
language contributors. Intervention recommendations return the top two
pathways, not an opaque single answer. Service gaps use minimum standards such
as four hours of water and fifteen toilets per one hundred people. Cost and
delay return uncertainty bands. Grievance NLP uses character n-grams to be
more forgiving across scripts and Hinglish. The perfect template NLP score is
clearly labelled as non-realistic.”

### 7. Product walkthrough — 45 seconds

“On the map, a judge can filter by city, ward, tier and hazard. Click the
critical pocket and the profile answers: what is happening, why did the model
rank it here, which service is failing, and what are the top two pathways? The
explanation also says what the model cannot decide: resident consent,
statutory clearance and field validation.”

### 8. Financial engine — 35 seconds

“The simulator makes a familiar cross-subsidy conversation computable. Land
area times FSI creates gross area. Rehab entitlement is reserved first. The
remaining saleable area, market rate, sales share, TDR and costs produce a
screening verdict. Move a slider and show the tornado: the value is in making
trade-offs visible before a DPR, not in pretending to replace project
finance.”

### 9. Resident design — 35 seconds

“A public programme needs a resident entry point. The eligibility wizard uses
simple language and explains that it is only screening. The grievance form
accepts English, Hindi, Marathi and Hinglish, with a browser voice button. It
predicts category and urgency, shows an expected response window and produces
a reference number. Officers see a queue, not a hidden score.”

### 10. Impact — 30 seconds

“Our counters show the scale of the demo universe and a planning scenario, not
realised impact: 1,500 pockets, 547 gaps and a synthetic cost signal. The
credible impact claim is process impact: faster comparison, clearer
assumptions, and a measurable post-handover loop aligned to PMAY-U, SRA,
SBM-U, AMRUT, Jal Jeevan Mission, SDG 6 and SDG 11.”

### 11. Scale — 25 seconds

“The first customer is a ULB, SRA or MHADA team piloting two wards. Funding can
combine a municipal licence, CSR resident layer and PPP partners. The moat is
the decision trail: provenance, reason, consultation and outcome.”

### 12. Ethics — 25 seconds

“We are explicit about limits. The demo does not decide demolition,
displacement or eligibility. Real deployment needs data minimisation,
consent, fairness audits, appeals, and human decisions. Synthetic data is a
safety boundary, not something we hide.”

### 13. Ask — 20 seconds

“Our ask is one ward, one service-assurance pilot and access to approved data.
Let’s measure not only how many homes are delivered, but what residents
actually receive after handover. Plan safer homes. Prove services arrive.”

## 3-minute elevator pitch

Cities face a connected problem but manage it in fragments. They need to know
which informal pockets are most urgent, which pathway is safest and most
viable, and whether a resident actually receives water, sanitation, power,
waste and health services after redevelopment.

NagarSeva is an explainable decision-support and service-assurance platform
for the MMR. It screens pockets with a transparent priority model, recommends
the top two pathways — in-situ, upgrading, relocation or rental — simulates
cross-subsidy viability and allocates budgets with vulnerable-share and ward
fairness constraints. After handover it turns service thresholds and grievance
signals into an accountability board.

The product is deliberately resident-first: multilingual eligibility screening,
voice-input grievances, a reference number and an officer queue sorted by
predicted urgency. Every result shows reasons, uncertainty and the human
decision handoff.

We built a reproducible local demo with synthetic calibrated data, not a claim
about any named settlement. That lets a city validate the workflow safely. Our
ask is a pilot in one ward with approved, consented data. The outcome we want
to measure is simple: not only homes delivered, but services received.

## Likely judge questions and strong answers

1. **Are these real slum numbers?**  No. They are seeded synthetic records
   calibrated to public-policy ranges and labelled throughout. The repository
   documents how Census, OGD, NFHS, OSM, MoHUA and city data would plug in.
2. **Why should anyone trust the priority score?**  It is a screening signal,
   not a verdict. The features, weights/target, held-out-ward metrics and
   plain-language reasons are visible, and an officer/resident review is part
   of the workflow.
3. **Could this accelerate displacement?**  Not by design. The product never
   makes a demolition or relocation decision. Restricted land/hazard signals
   surface questions for statutory review; resident consent and human approval
   are explicit requirements.
4. **Why not just use a dashboard?**  A dashboard reports. NagarSeva connects
   prioritisation, intervention choice, financial feasibility, budget trade-
   offs and post-handover SLAs in one decision trail.
5. **How does it handle fairness?**  Training splits by ward to reduce leakage;
   production audits should compare city, income, language, gender, disability
   and tenure groups. We also expose minimum vulnerable share and per-ward
   coverage constraints in optimisation.
6. **Is the financial model realistic?**  It is an auditable screening model,
   not a DPR or investment model. It makes FSI, rehab area, market rate, TDR,
   cost and sales share explicit and returns sensitivity so experts can
   challenge assumptions.
7. **What happens when the API is down?**  The website ships a representative
   fallback JSON and the simulator has client-side maths. The product remains
   demo-ready while the API is restarted.
8. **How will real residents use it?**  A ward help-desk or approved public
   portal can expose the resident flows, with language, voice and simple next
   steps. Personal identifiers stay in the approved grievance system.
9. **What is the business model?**  A municipal/SRA subscription for the
   evidence layer, implementation support, and a CSR/PPP-funded resident
   access module, with open data contracts to prevent lock-in.
10. **What is the next experiment?**  Pilot two wards: compare model ranking
    against an officer/resident panel, test service measurements against field
    logs, audit subgroup outcomes, and measure response time and post-handover
    SLA compliance before expanding.
