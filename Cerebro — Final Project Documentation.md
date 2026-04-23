# **Cerebro — Final Project Documentation**

## **Riley Brown | Creativity in AI | April 23, 2026**

Live app: [https://cerebro-tau-taupe.vercel.app/](https://cerebro-tau-taupe.vercel.app/)

---

## **1\. User Experience Design**

### **Design Vision**

Cerebro is a brainstorming chatbot where users can consult with AI personas of historical philosophers to help them develop and expand their ideas. The final version launches with three philosopher personas: Socrates, Aristotle, and Noam Chomsky.

### **Design Evolution**

I hadn't felt the need to derive too much from the initial UI design, it was initially very yellow and beige in a way that was not only ugly but distracting, so for the final design I switched to blue as the app's primary color and tried to make everything really simple and not too large. I wanted it to feel as calming as possible and for the UI to take the backseat and let the actual conversations speak for themselves.

As far as functionality goes, the early versions of the app had hardcoded responses and ran locally just to make sure everything was working properly and to be able to make changes quickly. Once I had my RAG set up and was able to start testing and tweaking the bot's system prompt, my initial reaction was that compared to typical chatbots it felt kind of annoying? In the true nature of Socrates, its answers were intended more to keep me thinking and asking the important questions rather than just giving me what I want directly. I started to change this, but then realized to do so would be missing the point. Socrates' whole thing was asking the right questions and inspiring thought, which might be more helpful for brainstorming than if Socrates just told you what to do, and this is of course also more accurate to what Socrates might've been like, so I kept that part of his nature.

The last big change during the prototype phase was figuring out deployment, because I thought it would be nice for people to be able to test the service without having to run and build everything locally, so I landed on Render for the backend and Vercel for the frontend, since both had decent free options. Vercel has a RAM limit of 500mb on the free tier which I was hitting so I had to pre-build the FAISS index and chunk metadata to prevent ML models from having to load at startup and do that work, basically just did my best to shrink what the backend needed to do in general and it fits fine now.

For the final version, I added Aristotle and Chomsky as additional personas. Each philosopher has its own RAG corpus and FAISS index, and the backend routes each conversation to the correct index based on which persona the user selects. I also added real profile photos to the landing page cards (sourced from Wikimedia Commons, all public domain or freely licensed) rather than just showing the first letter of each philosopher's name. The philosopher selection cards were also cleaned up so all three "Start Conversation" buttons sit at the same vertical position regardless of description length.

**Current Design**

(PICTURES GO HERE)

---

## **2\. Technical Overview**

### **Tech Stack**

* **Frontend:** React (Vite) \+ Tailwind CSS  
* **Backend:** Python / FastAPI  
* **LLM:** OpenAI GPT-4o  
* **Embeddings:** OpenAI text-embedding-3-small  
* **RAG Pipeline:** FAISS for vector search, paragraph-level chunking (\~500 words per chunk)  
* **Corpus:**
  * **Socrates** — 29 Plato dialogues \+ 2 Xenophon texts (all public domain, Project Gutenberg)
  * **Aristotle** — 6 major works: *Nicomachean Ethics*, *Politics*, *Poetics*, *Metaphysics*, *De Anima*, *Rhetoric* (public domain, Project Gutenberg)
  * **Chomsky** — 8 freely available essays and papers, including *The Responsibility of Intellectuals*, *What Makes Mainstream Media Mainstream*, and *Can Civilization Survive Capitalism?*

### **Architecture**

User message → React frontend → FastAPI backend → Persona routing → FAISS retrieval (philosopher-specific index) → Build prompt (persona system prompt \+ retrieved context \+ conversation history) → OpenAI API → Response back to frontend

### **Prompt Engineering**

* Each philosopher persona is defined via a system prompt covering identity, reasoning style, communication style, key beliefs, and limitations  
* RAG injects relevant passages from that philosopher's actual writings into each prompt so responses are grounded in source material  
* Socrates stays true to the Socratic method — questioning and prompting reflection rather than giving direct answers  
* Aristotle takes a more systematic and analytical tone, drawing on his frameworks across ethics, logic, and natural philosophy  
* Chomsky engages critically with power, institutions, and language, grounded in his essays and academic work

### **Tools Used**

* **Claude.ai** — brainstorming, spec writing, project planning, step-by-step guidance  
* **Claude Code** — scaffolding the React app, building the chat UI, wiring OpenAI integration, integrating the RAG backend, adding Aristotle and Chomsky  
* **Google Colab** — building and testing the RAG pipeline  
* **VSCodium** — IDE; code editing  
* **Git/GitHub** — version control and codebase hosting  
* **Render** — backend hosting  
* **Vercel** — frontend hosting

---

## **3\. Demo**

[https://youtu.be/u9xh3M8oMfQ](https://youtu.be/u9xh3M8oMfQ)

\*It feels important to note that I was just riffing for the purposes of the demo, I'm not actually a lawyer or anything, I'm technically a film major\*

---

## **4\. Source Code & Links**

* **GitHub repo:** https://github.com/ballsle/Cerebro  
* **Live demo:** https://cerebro-tau-taupe.vercel.app/  
* **RAG notebook:** Submitted separately as Assignment 9

---

## **5\. Troubleshooting Log**

### **Challenge: Downloading the corpus**

* Project Gutenberg texts seemed like the best option for the RAG knowledge base  
* Wrote a Python scraper to download all 31 Socrates-related texts, but Gutenberg blocked automated requests from certain environments  
* **Solution:** Ran the download script locally instead

### **Challenge: API key exposed in Git**

* GitHub Push Protection blocked a commit because I had accidentally left the OpenAI API key in the frontend  
* **Solution:** Replaced the key with a placeholder with the real key hidden in the backend environment, squashed Git history to remove the old commit containing the key, force-pushed

### **Challenge: Wiring RAG into the app**

* The RAG pipeline was built and tested in the Colab notebook, but needed to be integrated into the live web app  
* **Solution:** Created a FastAPI backend that loads the pre-built FAISS index on startup and exposes a `/api/chat` endpoint. Frontend calls the backend instead of OpenAI directly.

### **Challenge: Chunking strategy**

* The Socrates corpus is much larger than a typical RAG demo (31 texts), so chunking strategy mattered  
* **Solution:** Used paragraph-level chunking grouped to \~500 words, which preserves the natural dialogue structure of Plato's texts. Applied the same strategy to the Aristotle and Chomsky corpora.

### **Challenge: Scaling to multiple philosophers**

* Adding Aristotle and Chomsky meant the single hardcoded index approach wouldn't work anymore  
* **Solution:** Parameterized the index builder to accept a philosopher name and output named files (`faiss_index_aristotle.bin`, `chunks_aristotle.json`, etc.). The backend loads all available indexes at startup into a dictionary and routes each request by the `persona` field sent from the frontend.

### **Challenge: Chomsky corpus copyright**

* Most of Chomsky's books are still under copyright and couldn't be used  
* **Solution:** Limited the Chomsky corpus to freely available essays from his website and one open-access academic paper, which still provides enough grounding for the RAG pipeline to work well

### **Challenge: RAM limits on free hosting tier**

* Render's free tier has limited RAM; loading sentence-transformer models at startup was pushing the limit  
* **Solution:** Switched to OpenAI's `text-embedding-3-small` API for embeddings (no local model to load) and pre-built all FAISS indexes, so the backend only needs to load the index files on startup rather than any ML models

---

## **6\. Reflection**

The thing I'm most proud of with this project is how coherent each philosopher feels in conversation. Socrates genuinely doesn't give you straight answers, Aristotle tends to categorize and systematize everything, and Chomsky immediately reframes questions in terms of power and institutions. That's not just the system prompt — it's the RAG doing its job, pulling in actual source material that colors how each persona responds.

If I kept working on this, the main thing I'd want to do is make the conversations feel more continuous and give users a way to save or revisit past sessions. Right now every conversation starts fresh. I'd also want to add more philosophers — there's a pretty obvious case for Marx, Plato as his own persona (separate from the Socratic dialogues), and maybe someone like Hannah Arendt who would bring a different kind of political philosophy than Chomsky.

One honest limitation: Chomsky's corpus is thin compared to the other two (8 essays vs. hundreds of pages of Plato or Aristotle), so his responses sometimes feel less grounded. That could be improved with a larger freely available text base, or by purchasing access to some of his books and handling the licensing properly.
