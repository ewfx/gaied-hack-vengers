# 🚀 Gen AI Orchestrator for Email and Document Triage/Routing

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Inspiration](#inspiration)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
This project is designed to classify and process incoming emails by detecting duplicate emails, extracting structured information, and categorizing requests into predefined types using OpenRouter DeepSeek API. The goal is to automate email handling for financial transactions and improve efficiency in request management.

## 🎥 Demo
🔗 [Live Demo](https://5a22d97aff81cd28f6.gradio.live/)
📹 [Video Demo](https://github.com/ewfx/gaied-hack-vengers/blob/main/artifacts/demo/video-recording.mp4)
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
Manually processing high volumes of financial request emails is time-consuming and prone to errors. This project aims to automate email classification and processing using AI to ensure accurate and fast decision-making.

## ⚙️ What It Does
- Detects duplicate emails based on hash values to prevent redundant processing.

- Classifies email content into predefined request types such as Commitment Change, Fee Payment, and Money Movement.

- Extracts key details (deal name, amount, expiration date) from emails using regex.

- Integrates OpenRouter DeepSeek API for intelligent classification.

## 🛠️ How We Built It
- Used Python for backend processing.

- Integrated Gradio for interactive email processing.

- Utilized OpenRouter DeepSeek API for classification.

- Implemented Regex for structured data extraction.

- Managed email storage using JSON-based local storage.

## 🚧 Challenges We Faced
- Handling unstructured email formats with varied content.

- Improving the accuracy of request classification.

- Managing duplicate detection efficiently.

- Ensuring API response parsing remains consistent.

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaied-hack-vengers.git
   ```
2. Install dependencies  
   ```sh
   pip install -r requirements.txt
   ```
3. Run the project  
   ```sh
   python app.py
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: Gradio
- 🔹 Backend: FastAPI, Hugging Face
- 🔹 Other: DeepSeek

## 👥 Team
- **Poojitha Keshav** - [GitHub](#) | [LinkedIn](#)
- **Praveen Pitchaiah** - [GitHub](#) | [LinkedIn](#)
- **Radhakrishnan J** - [GitHub](#) | [LinkedIn](#)
- **Anshuman Tripathi** - [GitHub](#) | [LinkedIn](#)