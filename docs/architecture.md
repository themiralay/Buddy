```markdown
# ICEx Buddy Architecture

This document provides an overview of ICEx Buddy's architecture and how the various components interact.

## System Overview

ICEx Buddy is designed as a modular system with several key components:

![Architecture Diagram](images/architecture-diagram.png)

## Core Components

### 1. Assistant Core

The central component that coordinates all functionality:

- **PersonalAssistant Class**: Main entry point that initializes and manages all components
- **Context Manager**: Manages conversation context and history
- **Response Generator**: Creates responses using LLM services
- **Profile Manager**: Builds and maintains the user profile

### 2. Memory System

Responsible for storing and retrieving information:

- **Database**: SQLite database for persistent storage of conversations, tasks, etc.
- **Vector Store**: ChromaDB for semantic search capabilities
- **Conversation Memory**: Manages conversation history
- **Knowledge Base**: Stores user-specific information

### 3. Voice Capabilities

Handles speech-to-text and text-to-speech functionality:

- **Speech Recognition**: Converts spoken input to text
- **Text-to-Speech**: Converts text responses to speech
- **Voice Cloning**: Creates a personalized voice
- **Hotword Detection**: Listens for wake words

### 4. Integration Layer

Connects with external services and platforms:

- **OpenAI Client**: Communicates with OpenAI API
- **ElevenLabs/Coqui Client**: Voice synthesis integration
- **Messaging Platforms**: Telegram, WhatsApp, Discord integrations

### 5. Multi-Agent System

A team of specialized agents for different tasks:

- **Agent Manager**: Coordinates multiple specialized agents
- **Research Agent**: Looks up information
- **Planning Agent**: Helps with scheduling and task management
- **Creative Agent**: Assists with creative content
- **Reasoning Agent**: Provides logical analysis

## Data Flow

1. User input is received (text or voice)
2. Input is processed and context is gathered
3. The appropriate agent(s) handle the request
4. Response is generated using the LLM
5. Response is delivered to the user (text or voice)
6. Conversation is stored in memory
7. User profile is updated as needed

## File Structure

The project follows a modular structure:
