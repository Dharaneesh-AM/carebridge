# \# CareBridge

# 

# \*\*Offline AI-powered companion for memory support, voice interaction, computer vision, IoT control, and safety assistance.\*\*

# 

# CareBridge is an edge-AI assistive companion designed to provide a natural, private, and reassuring interaction experience using locally running AI models and connected hardware.

# 

# The user-facing companion is called \*\*Mitra\*\*.

# 

# \## What CareBridge Does

# 

# CareBridge combines several local components into one assistive system:

# 

# \- Voice interaction using Whisper.cpp for speech-to-text

# \- Natural voice responses using Piper TTS

# \- Local LLM reasoning using Qwen through llama.cpp

# \- Context-aware conversation using structured local memory

# \- Person/reference resolution for natural phrases such as "my daughter"

# \- Computer vision for camera-based interaction

# \- SQLite memory for people, memories, routines, and events

# \- IoT control through ESP32

# \- Safety detection and alerts

# \- Local dashboard

# \- Raspberry Pi OLED interface

\- Offline-first architecture to keep core interaction local

## Design Principles

#Offline-first
===

# 

# Core AI interaction is designed to run locally on the Raspberry Pi rather than depending on a cloud AI service.

# 

# Context before generation

# 

# Structured information such as people, memories, routines, locations, and events is retrieved locally and supplied as context instead of expecting the language model to invent or infer personal facts.

# 

# Natural interaction

# 

# Mitra is designed to communicate like a calm and supportive companion rather than treating conversation as a test.

# 

# Safety-aware interaction

# 

# Safety-related input is handled separately from normal conversational generation so that potential safety events can trigger the appropriate alert path.

# 

# Privacy

# 

# CareBridge is designed around local processing.

# 

# This public repository intentionally does not include:

# 

# populated SQLite databases

# biometric face embeddings

# recorded audio

# local model weights

# runtime logs

# local virtual environments

# backup files

# 

# These files remain local to the deployment environment.

# 

# Running the Project

# 

# CareBridge is primarily designed for its Raspberry Pi deployment environment.

# 

# The repository contains the application source code, configuration patterns, startup scripts, diagnostics, and demonstration components.

# 

# Local model binaries and hardware-specific configuration must be installed separately.

# 

# Example environment configuration:

# 

# export CAREBRIDGE\_LLM\_URL="http://127.0.0.1:8080"

# export CAREBRIDGE\_LLM\_MODEL="ggml-org/Qwen3.5-0.8B-GGUF:Q4\_0"

# 

# export WHISPER\_BIN="$HOME/whisper.cpp/build/bin/whisper-cli"

# export WHISPER\_MODEL="$HOME/whisper.cpp/models/ggml-tiny.en.bin"

# 

# export PIPER\_BIN="$HOME/CareBridge/.venv/bin/piper"

# export PIPER\_MODEL="$HOME/CareBridge/models/piper/en\_US-lessac-medium.onnx"

# 

# Hardware-specific values such as microphone, speaker, and ESP32 targets should be configured locally rather than committed to the repository.

# 

# Current Scope

# 

# CareBridge currently demonstrates an integrated edge-AI system combining:

# 

# Voice input

# Speech recognition

# Intent detection

# Context retrieval

# Local LLM response generation

# Text-to-speech

# Memory and event storage

# Computer vision

# IoT interaction

# Safety handling

# Dashboard and hardware feedback

# Development

# 

# The engineering decisions, implementation problems, debugging process, and lessons learned during development are documented separately in:

# 

# DEVELOPMENT\_NOTES.md

# 

# Limitations

# 

# CareBridge is an engineering prototype and is not a medical device or a replacement for professional medical care.

# 

# The system can make mistakes in speech recognition, computer vision, intent detection, memory retrieval, and language generation. Safety-related functionality should therefore be treated as an additional assistance mechanism rather than a guaranteed emergency-response system.

# 

# Future Work

# 

# Potential future improvements include:

# 

# stronger long-term memory retrieval

# improved natural conversation handling

# more robust vision-based context detection

# better hardware fault handling

# improved caregiver interfaces

# expanded IoT integration

# stronger automated testing

improved deployment and installation tooling


===

# \## Architecture

# 

# ```text

# &#x20;                ┌─────────────────────┐

# &#x20;                │       Mitra         │

# &#x20;                │  User Interaction   │

# &#x20;                └──────────┬──────────┘

# &#x20;                           │

# &#x20;             ┌─────────────┴─────────────┐

# &#x20;             │                           │

# &#x20;       Voice Input                  Camera Input

# &#x20;             │                           │

# &#x20;       Whisper.cpp                  OpenCV / Vision

# &#x20;             │                           │

# &#x20;             └─────────────┬─────────────┘

# &#x20;                           │

# &#x20;                   Context / Intent

# &#x20;                           │

# &#x20;             ┌─────────────┴─────────────┐

# &#x20;             │                           │

# &#x20;       Local Memory                 Safety Engine

# &#x20;         SQLite                         │

# &#x20;             │                           │

# &#x20;             └─────────────┬─────────────┘

# &#x20;                           │

# &#x20;                   Local Qwen LLM

# &#x20;                      llama.cpp

# &#x20;                           │

# &#x20;                   ┌───────┴───────┐

# &#x20;                   │               │

# &#x20;                Piper           ESP32 IoT

# &#x20;                  TTS

# &#x20;                   │

# &#x20;                Speaker

