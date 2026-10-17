# 20 Paper Prompts — Research Gap Hunter Dataset

Copy each prompt (everything inside the code block) into your LLM, then save the output as a PDF named after its ID (`P01.pdf`, `P02.pdf`, ...).

All names, authors, institutions and venues are **fictional**. Real dataset names (HotpotQA, MedQA, PubMedQA, Natural Questions, TACRED) are used only as dataset labels.

The matching structured data (citations, authors, ground truth) lives in `papers_metadata.json` — keep the two in sync if you change anything.

---

## P01

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically (e.g. "a keyword-search baseline") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: DenseRet: Learning Dual-Encoder Representations for Open-Domain Passage Retrieval
Authors: Anders Vik (Fjordline Institute)
Venue & Year: Conference on Natural Language Systems (CNLS), 2020
Proposed method: DenseRet
Methods used: Dual Encoder, Contrastive Learning
Datasets: Natural Questions
Tasks: Open-domain QA, Passage Retrieval
Key idea: Replace sparse keyword retrieval with two transformer encoders (one for questions, one for passages) trained with contrastive learning, so relevant passages land close together in vector space.
Results guidance: Report Recall@20 and Recall@100 on Natural Questions. DenseRet beats a keyword-search baseline by about 9 points Recall@20.

CITATIONS: none. This is a foundational paper; do not cite any prior work.

REFERENCES: none. Write "References: None." under the References heading.
```

---

## P02

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically (e.g. "a rule-based baseline") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: RelForge: Neural Relation Extraction for Automatic Knowledge Graph Construction
Authors: Priya Raman (Fjordline Institute)
Venue & Year: Conference on Natural Language Systems (CNLS), 2020
Proposed method: RelForge
Methods used: Transformer Encoder, Knowledge Graph
Datasets: TACRED
Tasks: Relation Extraction, Knowledge Graph Construction
Key idea: A transformer encoder reads sentences, tags entity pairs and classifies the relation between them; extracted (subject, relation, object) triples are merged into a Knowledge Graph with entity de-duplication.
Results guidance: Report F1 on TACRED. RelForge beats a rule-based baseline by about 11 F1. Also report the size of a Knowledge Graph built from 1M sentences (nodes and edges).

CITATIONS: none. This is a foundational paper; do not cite any prior work.

REFERENCES: none. Write "References: None." under the References heading.
```

---

## P03

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically (e.g. "a closed-book generator") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks
Authors: Anders Vik (Fjordline Institute)
Venue & Year: Conference on Natural Language Systems (CNLS), 2021
Proposed method: RetGen
Methods used: DenseRet, Seq2Seq Generator
Datasets: Natural Questions, HotpotQA
Tasks: Open-domain QA
Key idea: First retrieve the top passages with DenseRet, then condition a Seq2Seq Generator on the question plus retrieved passages, so answers are grounded in evidence instead of memorized parameters.
Results guidance: Report Exact Match on Natural Questions and HotpotQA. RetGen beats a closed-book generator by about 12 EM on Natural Questions, with a smaller gain on HotpotQA (note multi-hop questions remain hard).

CITATIONS:
[1] Builds directly on the method of [1]: uses DenseRet as its retriever.

REFERENCES:
[1] Vik, A. (2020). DenseRet: Learning Dual-Encoder Representations for Open-Domain Passage Retrieval. Conference on Natural Language Systems (CNLS).
```

---

## P04

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words): describe how the benchmark was built.
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Models may only be described generically (e.g. "a 7B open model", "a 175B model") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: FactProbe: A Benchmark for Measuring Hallucination in Large Language Models
Authors: Hana Novak (Northbridge University)
Venue & Year: Transactions on Language Evaluation (TLE), 2022
Proposed method: FactProbe (a benchmark)
Methods used: Large Language Model
Datasets: FactProbe
Tasks: Hallucination Detection
Key idea: A benchmark of 5,000 questions with verified answers and annotated "hallucination spans", plus an automatic hallucination-rate metric. Shows that even retrieval-augmented systems still hallucinate.
Results guidance: Report hallucination rate (%) for 3 generic models (small, medium, large Large Language Model) and for RetGen. Larger models hallucinate less but still above 15%; RetGen reduces hallucination but not to zero.

CITATIONS:
[1] Cite as background/motivation: retrieval-augmented generation [1] was expected to fix hallucination, but this paper shows it only partially does.

REFERENCES:
[1] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
```

---

## P05

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: GraphHop: Knowledge Graph-Augmented Retrieval for Multi-Hop Question Answering
Authors: Lena Okafor (Northbridge University)
Venue & Year: Conference on Natural Language Systems (CNLS), 2023
Proposed method: GraphHop
Methods used: Knowledge Graph, RelForge, RetGen
Datasets: HotpotQA
Tasks: Multi-hop QA
Key idea: Build a Knowledge Graph from the corpus using RelForge, then answer multi-hop questions by walking entity links in the graph to collect evidence passages, which are fed to a RetGen-style generator.
Results guidance: Report Exact Match and F1 on HotpotQA. GraphHop beats RetGen by about 8 EM, with the biggest gains on questions needing 3+ hops.

CITATIONS:
[1] Builds directly on the method of [1]: uses RelForge to construct the Knowledge Graph.
[2] Builds directly on the method of [2]: extends RetGen with graph-based evidence retrieval and uses it as the main baseline.

REFERENCES:
[1] Raman, P. (2020). RelForge: Neural Relation Extraction for Automatic Knowledge Graph Construction. Conference on Natural Language Systems (CNLS).
[2] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
```

---

## P06

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: SubGround: Retrieving Query-Specific Subgraphs to Ground Language Model Answers
Authors: Ravi Menon (Northbridge University)
Venue & Year: Conference on Natural Language Systems (CNLS), 2023
Proposed method: SubGround
Methods used: Knowledge Graph, Graph Neural Network, Large Language Model
Datasets: HotpotQA, FactProbe
Tasks: Multi-hop QA, Hallucination Reduction
Key idea: For each question, a Graph Neural Network scores and extracts a small query-specific subgraph from a Knowledge Graph; the subgraph is serialized into the prompt of a Large Language Model so every answer is grounded in explicit facts.
Results guidance: Report EM on HotpotQA and hallucination rate on FactProbe. SubGround cuts hallucination rate roughly in half versus plain retrieval-augmented generation, with a modest EM gain.

CITATIONS:
[1] Builds directly on the method of [1]: Knowledge Graph built with RelForge.
[2] Cite as background: retrieval-augmented generation [2] retrieves passages, not structured facts.
[3] Compares against / reuses the results of [3]: evaluates on the FactProbe benchmark and its hallucination metric.

REFERENCES:
[1] Raman, P. (2020). RelForge: Neural Relation Extraction for Automatic Knowledge Graph Construction. Conference on Natural Language Systems (CNLS).
[2] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
[3] Novak, H. (2022). FactProbe: A Benchmark for Measuring Hallucination in Large Language Models. Transactions on Language Evaluation (TLE).
```

---

## P07

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: CommSumm: Community Summaries for Answering Global Questions over Knowledge Graphs
Authors: Lena Okafor (Northbridge University)
Venue & Year: Conference on Natural Language Systems (CNLS), 2024
Proposed method: CommSumm
Methods used: Knowledge Graph, Leiden Clustering, Large Language Model
Datasets: GlobalQ-200
Tasks: Query-focused Summarization
Key idea: Global questions ("What are the main themes in this corpus?") cannot be answered by retrieving a few passages. CommSumm partitions a Knowledge Graph with Leiden Clustering, has a Large Language Model pre-summarize each community, then combines community summaries at query time.
Results guidance: Introduce GlobalQ-200 (200 global questions, judged by human raters). Report win-rate for comprehensiveness and diversity; CommSumm wins about 70% of comparisons against GraphHop-style local retrieval.

CITATIONS:
[1] Builds directly on the method of [1]: reuses the GraphHop graph construction and uses GraphHop as the local-retrieval baseline.
[2] Cite as background: subgraph grounding [2] works for specific questions but not global ones.

REFERENCES:
[1] Okafor, L. (2023). GraphHop: Knowledge Graph-Augmented Retrieval for Multi-Hop Question Answering. Conference on Natural Language Systems (CNLS).
[2] Menon, R. (2023). SubGround: Retrieving Query-Specific Subgraphs to Ground Language Model Answers. Conference on Natural Language Systems (CNLS).
```

---

## P08

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Models may only be described generically (e.g. "a 13B open model") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: GraphVerify: Reducing Hallucination through Knowledge Graph Fact Verification
Authors: Lena Okafor (Northbridge University), Ravi Menon (Northbridge University)
Venue & Year: Conference on Natural Language Systems (CNLS), 2024
Proposed method: GraphVerify
Methods used: Knowledge Graph, SubGround, Relational Fact Lattice, Large Language Model
Datasets: FactProbe, HotpotQA
Tasks: Hallucination Reduction, Fact Verification
Key idea: Post-hoc verification. After a Large Language Model drafts an answer, GraphVerify splits it into atomic claims, checks each claim against a Knowledge Graph (retrieved with SubGround), and rewrites or flags unsupported claims. The claim-to-graph matching borrows the lattice indexing idea of the Relational Fact Lattice.
Results guidance: Report hallucination rate on FactProbe and EM on HotpotQA. GraphVerify reduces hallucination rate from ~18% to ~7% on FactProbe with no EM loss.

CITATIONS:
[1] Compares against / reuses the results of [1]: evaluated with the FactProbe hallucination metric.
[2] Builds directly on the method of [2]: uses SubGround to retrieve evidence subgraphs.
[3] Builds directly on the method of [3]: adapts the Relational Fact Lattice indexing for fast claim lookup. Describe [3] as "an early clinical system that grounded compact generators in structured relational memory" and credit it as an overlooked inspiration.

REFERENCES:
[1] Novak, H. (2022). FactProbe: A Benchmark for Measuring Hallucination in Large Language Models. Transactions on Language Evaluation (TLE).
[2] Menon, R. (2023). SubGround: Retrieving Query-Specific Subgraphs to Ground Language Model Answers. Conference on Natural Language Systems (CNLS).
[3] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```

---

## P09

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically (e.g. "a general-purpose 70B model") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Do NOT mention knowledge graphs, graphs, or small/compact models anywhere.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: CuraLM-70B: Adapting a Large Language Model to Clinical Text
Authors: Sofia Brandt (Halden Medical Institute)
Venue & Year: Journal of Clinical AI (JCAI), 2023
Proposed method: CuraLM-70B
Methods used: Large Language Model, Instruction Tuning
Datasets: MedQA, PubMedQA
Tasks: Medical QA
Key idea: Continue pre-training a 70-billion-parameter Large Language Model on de-identified clinical notes and medical literature, then apply Instruction Tuning on medical question-answer pairs.
Results guidance: Report accuracy on MedQA and PubMedQA. CuraLM-70B beats a general-purpose 70B model by ~10 points on MedQA. Note in the conclusion that the model still hallucinates on rare conditions and is too large to run in hospitals without data-center hardware.

CITATIONS:
[1] Cite as background: retrieval-augmented generation [1] is an alternative to domain adaptation that this paper does not use.
[2] Compares against / reuses the results of [2]: reports that general models show high hallucination rates on FactProbe, motivating domain adaptation.

REFERENCES:
[1] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
[2] Novak, H. (2022). FactProbe: A Benchmark for Measuring Hallucination in Large Language Models. Transactions on Language Evaluation (TLE).
```

---

## P10

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Do NOT evaluate on or mention any question-answering dataset. This paper is only about building the graph.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: ClinoKG: Constructing a Medical Knowledge Graph from Biomedical Literature
Authors: Priya Raman (Fjordline Institute), Tomas Reyes (Halden Medical Institute)
Venue & Year: Journal of Clinical AI (JCAI), 2023
Proposed method: ClinoKG
Methods used: RelForge, Knowledge Graph, Relational Fact Lattice
Datasets: PubMed Abstracts
Tasks: Knowledge Graph Construction
Key idea: Apply RelForge (adapted to biomedical text) to 2 million PubMed Abstracts to build a medical Knowledge Graph of drugs, diseases, genes and symptoms. The graph is stored using the Relational Fact Lattice layout for fast lookup.
Results guidance: Report graph size (about 1.2M entities, 6M relations) and precision of a manually checked sample (~91%). Compare relation precision against a dictionary-based baseline.

CITATIONS:
[1] Builds directly on the method of [1]: adapts RelForge to biomedical text.
[2] Builds directly on the method of [2]: stores the graph in a Relational Fact Lattice.

REFERENCES:
[1] Raman, P. (2020). RelForge: Neural Relation Extraction for Automatic Knowledge Graph Construction. Conference on Natural Language Systems (CNLS).
[2] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```

---

## P11

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Do NOT mention knowledge graphs or graphs. This system uses vector retrieval of text passages only.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: MedRetGen: Retrieval-Augmented Generation for Medical Question Answering
Authors: Sofia Brandt (Halden Medical Institute), Daniel Osei (Halden Medical Institute)
Venue & Year: Journal of Clinical AI (JCAI), 2024
Proposed method: MedRetGen
Methods used: RetGen, DenseRet, CuraLM-70B
Datasets: MedQA, PubMedQA
Tasks: Medical QA
Key idea: Index medical textbooks and guidelines with DenseRet, retrieve passages for each question, and generate answers with CuraLM-70B in a RetGen pipeline.
Results guidance: Report accuracy on MedQA and PubMedQA. MedRetGen improves CuraLM-70B by ~4 points on MedQA. Limitation to state clearly: retrieved passages sometimes contradict each other and the model cannot reason across multiple facts.

CITATIONS:
[1] Builds directly on the method of [1]: follows the RetGen retrieve-then-generate pipeline.
[2] Builds directly on the method of [2]: uses CuraLM-70B as the generator.

REFERENCES:
[1] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
[2] Brandt, S. (2023). CuraLM-70B: Adapting a Large Language Model to Clinical Text. Journal of Clinical AI (JCAI).
```

---

## P12

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words): describe how the evaluation suite was built.
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Models may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: ClinHalluEval: Measuring Hallucination in Clinical Language Models
Authors: Sofia Brandt (Halden Medical Institute)
Venue & Year: Journal of Clinical AI (JCAI), 2024
Proposed method: ClinHalluEval (an evaluation suite)
Methods used: FactProbe, Large Language Model
Datasets: ClinHalluEval, MedQA
Tasks: Hallucination Detection, Medical QA
Key idea: Extend the FactProbe methodology to medicine: 3,000 clinical questions derived from MedQA, each answer annotated by physicians for fabricated drugs, dosages or interactions.
Results guidance: Report hallucination rates for CuraLM-70B and two generic models. Even CuraLM-70B fabricates drug-interaction facts in ~14% of answers; dosage errors are the most dangerous category.

CITATIONS:
[1] Builds directly on the method of [1]: adopts the FactProbe annotation scheme and metric.
[2] Compares against / reuses the results of [2]: evaluates CuraLM-70B as the strongest system.
[3] Cite as background: [3] showed early that grounding clinical text generators in structured drug-interaction facts reduces fabricated statements; argue the field has largely ignored it.

REFERENCES:
[1] Novak, H. (2022). FactProbe: A Benchmark for Measuring Hallucination in Large Language Models. Transactions on Language Evaluation (TLE).
[2] Brandt, S. (2023). CuraLM-70B: Adapting a Large Language Model to Clinical Text. Journal of Clinical AI (JCAI).
[3] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```

---

## P13

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Teacher/student models may only be described generically (e.g. "a 70B teacher", "a 1.3B student").
- Cite only the references listed. Never invent other references.
- Do NOT mention knowledge graphs, graphs, medicine or hallucination.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: TinyDistill: Knowledge Distillation into Compact Language Models
Authors: Mei Tanaka (Kestrel AI Lab)
Venue & Year: Workshop on Efficient Language Models (WELM), 2023
Proposed method: TinyDistill
Methods used: Knowledge Distillation, Small Language Model
Datasets: Natural Questions
Tasks: Model Compression, Open-domain QA
Key idea: Distill a 70B teacher into a 1.3B Small Language Model using layer-wise Knowledge Distillation plus synthetic question-answer pairs generated by the teacher.
Results guidance: Report EM on Natural Questions, model size and inference latency. The 1.3B student keeps ~85% of teacher accuracy at 50x lower latency.

CITATIONS:
[1] Cite as background: retrieval-augmented generation [1] is a complementary way to make models knowledgeable, left for future work.

REFERENCES:
[1] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
```

---

## P14

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically (e.g. "full fine-tuning") or by citing the references given.
- Cite only the references listed. Never invent other references.
- Do NOT mention knowledge graphs, graphs, medicine or hallucination.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: LoRA-QA: Parameter-Efficient Fine-Tuning of Sub-8B Models for Question Answering
Authors: Mei Tanaka (Kestrel AI Lab)
Venue & Year: Workshop on Efficient Language Models (WELM), 2024
Proposed method: LoRA-QA
Methods used: Low-Rank Adaptation, Small Language Model, TinyDistill
Datasets: Natural Questions, HotpotQA
Tasks: Open-domain QA
Key idea: A recipe for adapting any Small Language Model under 8B parameters to question answering with Low-Rank Adaptation adapters trained on a single consumer GPU, starting from TinyDistill checkpoints.
Results guidance: Report EM on Natural Questions and HotpotQA for 1.3B, 3B and 7B models, plus GPU hours. LoRA-QA matches full fine-tuning within 1 EM while using 1% of trainable parameters.

CITATIONS:
[1] Builds directly on the method of [1]: starts from TinyDistill student checkpoints.

REFERENCES:
[1] Tanaka, M. (2023). TinyDistill: Knowledge Distillation into Compact Language Models. Workshop on Efficient Language Models (WELM).
```

---

## P15

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Large comparison models may only be described generically (e.g. "a 70B closed-book model").
- Cite only the references listed. Never invent other references.
- Do NOT mention knowledge graphs, graphs or medicine.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: SmallRAG: When Compact Models with Retrieval Outperform Large Models
Authors: Mei Tanaka (Kestrel AI Lab), Jonah Pierce (Kestrel AI Lab)
Venue & Year: Workshop on Efficient Language Models (WELM), 2024
Proposed method: SmallRAG
Methods used: RetGen, TinyDistill, Small Language Model
Datasets: HotpotQA, Natural Questions
Tasks: Open-domain QA, Multi-hop QA
Key idea: A 3B Small Language Model (distilled with TinyDistill) plus RetGen-style retrieval beats a 70B closed-book model on knowledge-heavy questions, because retrieval supplies the facts the small model cannot memorize.
Results guidance: Report EM on Natural Questions and HotpotQA. SmallRAG-3B beats the 70B closed-book model on Natural Questions, but falls behind on multi-hop HotpotQA questions. State this multi-hop weakness clearly as the main open problem.

CITATIONS:
[1] Builds directly on the method of [1]: uses the RetGen pipeline.
[2] Builds directly on the method of [2]: uses a TinyDistill student as the generator.

REFERENCES:
[1] Vik, A. (2021). Retrieve-then-Generate: Augmenting Language Models with Retrieved Passages for Knowledge-Intensive Tasks. Conference on Natural Language Systems (CNLS).
[2] Tanaka, M. (2023). TinyDistill: Knowledge Distillation into Compact Language Models. Workshop on Efficient Language Models (WELM).
```

---

## P16

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Do NOT use or mention knowledge graphs or graphs. Grounding the model in external facts is explicitly left as future work.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: PocketClinic: An On-Device Clinical Assistant Built on a 3B-Parameter Model
Authors: Jonah Pierce (Kestrel AI Lab), Daniel Osei (Kestrel AI Lab)
Venue & Year: Journal of Clinical AI (JCAI), 2025
Proposed method: PocketClinic
Methods used: LoRA-QA, Small Language Model
Datasets: MedQA
Tasks: Medical QA
Key idea: A 3B Small Language Model fine-tuned with LoRA-QA on medical data runs fully on a hospital tablet, so no patient data leaves the device.
Results guidance: Report MedQA accuracy, on-device latency and memory. PocketClinic reaches ~80% of CuraLM-70B's MedQA accuracy offline. Key limitation: it hallucinates drug interactions more often than large models.

CITATIONS:
[1] Cite as background: CuraLM-70B [1] is accurate but needs data-center hardware.
[2] Builds directly on the method of [2]: fine-tunes with LoRA-QA.
[3] Cite as background: in future work, mention that grounding compact clinical generators in structured relational memory, as in [3], could reduce fabricated drug interactions.

REFERENCES:
[1] Brandt, S. (2023). CuraLM-70B: Adapting a Large Language Model to Clinical Text. Journal of Clinical AI (JCAI).
[2] Tanaka, M. (2024). LoRA-QA: Parameter-Efficient Fine-Tuning of Sub-8B Models for Question Answering. Workshop on Efficient Language Models (WELM).
[3] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```

---

## P17 (the hidden gem)

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every phrase listed under METHODS USED, DATASETS and TASKS verbatim at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods.
- Cite only the references listed. Never invent other references.
- FORBIDDEN WORDS — never use these anywhere, including title, abstract and keywords: "knowledge graph", "graph", "hallucination", "hallucinate", "small", "LLM", "large language model", "language model", "question answering", "RAG", "retrieval-augmented".
- Use this vocabulary instead: "structured relational memory", "fact lattice", "compact text generator", "confabulation", "fabricated statements", "lightweight".
- The paper should read primarily as a clinical pharmacy software paper about drug interaction lookup; the grounding idea is presented as the technical contribution inside that system.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: Relational Fact Lattices for Grounding Compact Clinical Text Generators
Authors: Priya Raman (Fjordline Institute)
Venue & Year: Clinical Informatics Letters (CIL), 2022
Proposed method: Relational Fact Lattice
Methods used: structured relational memory, compact text generator, RelForge
Datasets: RxInteract-5K
Tasks: drug interaction lookup, confabulation reduction
Key idea: A hospital pharmacy tool where a lightweight compact text generator writes plain-language drug-interaction explanations for nurses. Before writing, it must look up every drug pair in a structured relational memory organised as a Relational Fact Lattice (drug–enzyme–drug relations extracted with RelForge). Any sentence not backed by a lattice entry is removed, which sharply reduces confabulation.
Results guidance: Introduce RxInteract-5K (5,000 drug-pair queries reviewed by pharmacists). Report the rate of fabricated statements: ~21% for the generator alone vs ~4% with the Relational Fact Lattice, and note it runs on a single hospital workstation CPU.

CITATIONS:
[1] Builds directly on the method of [1]: uses RelForge to extract drug–enzyme–drug relations into the lattice.

REFERENCES:
[1] Raman, P. (2020). RelForge: Neural Relation Extraction for Automatic Knowledge Graph Construction. Conference on Natural Language Systems (CNLS).

(Note: the reference title above is allowed to contain the word "Graph"; the forbidden-word rule applies to everything you write yourself.)
```

---

## P18 (the closest competitor)

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- Do NOT mention MedQA anywhere. Evaluate on PubMedQA only.
- Do NOT discuss small, compact or on-device models. State clearly that the system depends on the 70-billion-parameter CuraLM-70B.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: CuraGraph: Knowledge Graph-Grounded Medical Question Answering with Large Language Models
Authors: Tomas Reyes (Halden Medical Institute), Daniel Osei (Halden Medical Institute)
Venue & Year: Journal of Clinical AI (JCAI), 2025
Proposed method: CuraGraph
Methods used: Knowledge Graph, ClinoKG, SubGround, GraphVerify, CuraLM-70B
Datasets: PubMedQA
Tasks: Medical QA, Hallucination Reduction
Key idea: Combine the ClinoKG medical Knowledge Graph with SubGround subgraph retrieval and GraphVerify claim checking, using CuraLM-70B as the generator. Answers to medical questions are grounded in, and verified against, the graph.
Results guidance: Report PubMedQA accuracy and hallucination rate. CuraGraph beats MedRetGen by ~5 accuracy points and halves hallucination rate. Limitation: requires multiple data-center GPUs per query.

CITATIONS:
[1] Builds directly on the method of [1]: uses SubGround for subgraph retrieval.
[2] Builds directly on the method of [2]: uses GraphVerify for claim checking.
[3] Builds directly on the method of [3]: uses ClinoKG as the medical Knowledge Graph.
[4] Compares against / reuses the results of [4]: MedRetGen is the main baseline.
[5] Cite as background: [5] was an early clinical system that grounded generated text in structured drug-interaction facts.

REFERENCES:
[1] Menon, R. (2023). SubGround: Retrieving Query-Specific Subgraphs to Ground Language Model Answers. Conference on Natural Language Systems (CNLS).
[2] Okafor, L., & Menon, R. (2024). GraphVerify: Reducing Hallucination through Knowledge Graph Fact Verification. Conference on Natural Language Systems (CNLS).
[3] Raman, P., & Reyes, T. (2023). ClinoKG: Constructing a Medical Knowledge Graph from Biomedical Literature. Journal of Clinical AI (JCAI).
[4] Brandt, S., & Osei, D. (2024). MedRetGen: Retrieval-Augmented Generation for Medical Question Answering. Journal of Clinical AI (JCAI).
[5] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```

---

## P19

```
You are writing a short, realistic but FICTIONAL academic research paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words): motivate the problem and discuss each cited work by its reference number, as described in CITATIONS.
- 2. Method (~200 words)
- 3. Experiments (~150 words plus one small results table)
- 4. Conclusion (~80 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under METHODS USED, DATASETS and TASKS verbatim (exact spelling) at least once in the body.
- Do not mention any other named datasets, benchmarks, models or methods. Baselines may only be described generically or by citing the references given.
- Cite only the references listed. Never invent other references.
- General-domain only: do NOT mention medicine, clinical settings, MedQA or PubMedQA. In the conclusion, say domain-specific applications are future work, without naming any domain.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: TinyVeri: Knowledge Graph Verification for 3B-Parameter Language Models
Authors: Ravi Menon (Northbridge University), Jonah Pierce (Kestrel AI Lab)
Venue & Year: Workshop on Efficient Language Models (WELM), 2025
Proposed method: TinyVeri
Methods used: GraphVerify, Knowledge Graph, Small Language Model, SmallRAG, Relational Fact Lattice
Datasets: HotpotQA, FactProbe
Tasks: Hallucination Reduction, Multi-hop QA
Key idea: Make GraphVerify cheap enough for a 3B Small Language Model: a lightweight claim splitter plus Relational Fact Lattice indexing lets verification against a Knowledge Graph run in under 50 ms. Combined with SmallRAG, it fixes SmallRAG's multi-hop weakness.
Results guidance: Report EM on HotpotQA and hallucination rate on FactProbe. TinyVeri-3B matches GraphVerify with a 13B model on FactProbe and closes most of SmallRAG's multi-hop gap on HotpotQA.

CITATIONS:
[1] Builds directly on the method of [1]: compresses GraphVerify for small models.
[2] Builds directly on the method of [2]: SmallRAG is the base system and baseline.
[3] Builds directly on the method of [3]: uses Relational Fact Lattice indexing for fast lookup.

REFERENCES:
[1] Okafor, L., & Menon, R. (2024). GraphVerify: Reducing Hallucination through Knowledge Graph Fact Verification. Conference on Natural Language Systems (CNLS).
[2] Tanaka, M., & Pierce, J. (2024). SmallRAG: When Compact Models with Retrieval Outperform Large Models. Workshop on Efficient Language Models (WELM).
[3] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```

---

## P20 (the survey)

```
You are writing a short, realistic but FICTIONAL academic survey paper for a hackathon demo dataset. Follow the structure and spec exactly.

STRUCTURE (use these exact section headings, in this order):
- Title
- Authors & Affiliations
- Venue & Year
- Abstract (150–200 words)
- Keywords (4–6)
- 1. Introduction (~150 words)
- 2. Measuring Hallucination (~100 words)
- 3. Retrieval-Based Mitigation (~100 words)
- 4. Graph-Based Mitigation (~150 words)
- 5. Open Challenges (~100 words)
- References (exactly the list given, no additions)
- Last line, in italics: "Synthetic paper created for the Neo4j Graph Builder Build Sprint. Not a real publication."

RULES:
- Use every name listed under TASKS verbatim at least once.
- Discuss every reference at least once, by its reference number, in the section indicated in CITATIONS.
- Do not mention any named datasets or benchmarks other than FactProbe and ClinHalluEval. Do not mention MedQA, PubMedQA or HotpotQA.
- No results tables. This is a survey; it proposes no new method.
- Cite only the references listed. Never invent other references.
- Output clean Markdown, ready to export as a PDF.

SPEC:
Title: Mitigating Hallucination in Language Models: A Survey of Retrieval and Graph-Based Approaches
Authors: Hana Novak (Northbridge University)
Venue & Year: Transactions on Language Evaluation (TLE), 2025
Proposed method: none (survey)
Tasks: Hallucination Reduction
Key idea: Organise hallucination mitigation into measurement, retrieval-based and graph-based approaches, and argue that graph-based grounding is the most promising direction.
Open Challenges to list: (a) making graph verification cheap enough for compact models, (b) bringing graph grounding into high-stakes domains, (c) evaluation in specialised fields remains fragmented.

CITATIONS (all cited as background):
[1] Section 2: the FactProbe benchmark.
[2] Section 2: ClinHalluEval, the clinical extension of FactProbe.
[3] Section 3: CuraLM-70B, domain adaptation as a mitigation strategy.
[4] Section 3: SmallRAG, compact models with retrieval.
[5] Section 4: SubGround, subgraph grounding.
[6] Section 4: GraphVerify, post-hoc graph verification.
[7] Section 4: describe [7] as an early, under-cited precursor of graph grounding from clinical informatics.

REFERENCES:
[1] Novak, H. (2022). FactProbe: A Benchmark for Measuring Hallucination in Large Language Models. Transactions on Language Evaluation (TLE).
[2] Brandt, S. (2024). ClinHalluEval: Measuring Hallucination in Clinical Language Models. Journal of Clinical AI (JCAI).
[3] Brandt, S. (2023). CuraLM-70B: Adapting a Large Language Model to Clinical Text. Journal of Clinical AI (JCAI).
[4] Tanaka, M., & Pierce, J. (2024). SmallRAG: When Compact Models with Retrieval Outperform Large Models. Workshop on Efficient Language Models (WELM).
[5] Menon, R. (2023). SubGround: Retrieving Query-Specific Subgraphs to Ground Language Model Answers. Conference on Natural Language Systems (CNLS).
[6] Okafor, L., & Menon, R. (2024). GraphVerify: Reducing Hallucination through Knowledge Graph Fact Verification. Conference on Natural Language Systems (CNLS).
[7] Raman, P. (2022). Relational Fact Lattices for Grounding Compact Clinical Text Generators. Clinical Informatics Letters (CIL).
```
