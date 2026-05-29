# Your-Self-Assistant-AI-Jarvis
This is an AI which you can run with LM Studio based on Qwen3-8B model. 

# AI Assistant Based on Qwen3-8B

This project is an AI assistant that runs locally with **LM Studio** using the **Qwen3-8B** model.

---

# Requirements

Before starting, make sure you have:

* Python installed
* LM Studio installed
* Qwen3-8B model downloaded

---

# Installation Guide

## Step 1 — Install LM Studio

Download and install LM Studio from the official website:

https://lmstudio.ai/

---

## Step 2 — Download the Qwen3-8B Model

Open LM Studio and download the **Qwen3-8B** model from the model browser.

---

# Configuration Guide

You need to edit both:

* HTML code
* Proxy code (Python)

---

# HTML Configuration

You must edit the following lines in the HTML file:

* Line 6
* Line 347
* Line 388
* Line 393
* Line 394

## Line 6

You can customize this line however you want.

## Line 347

Change the port to your default LM Studio server port.

## Line 388

Define a proxy port number.

Requirements:

* Must be different from the LM Studio server port
* Must NOT be `7788`

## Line 393

Get a free OpenWeather API key and paste it into this line.

API Website:
https://openweathermap.org/api

## Line 394

Change the location and country to your own defaults.

---

# Proxy Configuration (Python)

You must edit the following lines in the Python proxy file:

* Line 26
* Line 27
* Line 78
* Lines 211–217

## Line 26

Paste the same proxy port you used in the HTML file.

## Line 27

Paste your LM Studio server port.

The server address usually starts with:

```python id="rxs8am"
localhost:
```

## Line 78

Use the same value as Line 27.

## Lines 211–217

You can freely customize these lines with your own creativity.

---

# Notes

* Make sure the LM Studio local server is running before starting the project.
* Ensure the ports do not conflict with other applications.
* Keep your OpenWeather API key private.
* The entire AI system is configured in Turkish by default.
* If you want, you can manually change the language inside the code files.

---

# Credits

* LM Studio
* Qwen3-8B
* OpenWeather API
