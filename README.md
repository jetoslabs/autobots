# Autobots
![CICD](https://github.com/jetoslabs/autobots/actions/workflows/CICD.yaml/badge.svg?branch=main)

### Description

Autobots is a Software as a Service (SaaS) application designed to automate the process of achieving a goal through a sequence of user-defined actions. Leveraging Large Language Model, Autobots can generate dynamic, human-like text for executing actions and making decisions, providing users with a flexible tool for a wide range of tasks.

## Steps to run the app
1. Create a .env.local file alongside .env.sample
2. Add env vars to `.env.local` file
3. Run `poetry install` / `poetry update`
4. Run `uvicorn src.autobots.main:app` or `python -m src.autobots.main`

## Steps to run tests
1. Run `pytest -vv -n 5`

### Features

* **Automated Goal Completion**: Our core functionality is to automate the process of reaching a user-defined goal through a sequence of actions.

* **User-defined Goals and Actions**: Users have the ability to define their own goals and actions, providing versatility in tasks that can be accomplished using Autobots.

* **Large Language Model Integration**: Autobots integrates with Large Language Model to generate human-like text, useful for generating creative ideas, deciding the next course of action, and more.

* **Context Management**: Autobots maintains a context of the actions performed and their results to inform decision-making and determine whether a goal has been completed.

* **Dynamic Prompt Generation**: Autobots dynamically generates prompts for interacting with GPT-4, improving the relevancy and quality of the output.

* **Analytics and Insights**: In addition to executing actions, Autobots provides analytical insights based on the actions performed and their results.

* **Security and Privacy**: Autobots ensures that user data is handled securely with features such as end-to-end encryption, access controls, and compliance with privacy regulations.

### Building blocks

#### Action
**Every Action contains ActionGraph. ActionGraph gets run**
1. ReadUrls(list of url)
2. LLMChat(list of message) -> *generate_decision, *is_goal_completed
3. CreatePromptForLLMChat(goal) -> generate_decision_prompt, is_goal_completed_prompt
4. Create new Action by defining Action Graph (** Every Action contains ActionGraph. ActionGGraph gets run)

#### ActionGraph
**if len(Value) == 1 AND Key == Value[0] then add Value[0] to list of allowed actions in ActionGraph**
1. ReadUrls: { ReadUrls: {} }
2. LLMChat: { LLMChat: {} }
3. CreatePromptForLLMChat: { LLMChat:{} }
4. generate_decision_prompt: { LLMChat:{} }
5. generate_goal_prompt: { LLMChat:{} }
6. extract_action_from_decision: { LLMChat:{} }
7. decide_next_action: { generate_decision_prompt: {LLMChat: {}}, LLMChat: {extract_action_from_decision: {}} }
8. map_output_to_boolean: [__call__()]
9. goal_completed: { generate_goal_prompt: {LLMChat: {}}, LLMChat: {map_output_to_boolean: {}} }
10. execute_action: [__call__()]
This concludes uni-directional graph state changes (Can implement up until the while loop of goal_completed)
Next steps... Allow users to create automaton using state_diagram (https://en.wikipedia.org/wiki/Automata_theory#/media/File:DFAexample.svg)
Agents are state diagram (Automata Theory)
11. Automated Goal Completion - input_goal -> START_LOOP if goal_completed == 0 -> decide_next_action, execute_action else -> break END_LOOP

#### Goal
**User Goals, including setting, tracking, and checking the completion of goals. It will interact with the Action module to execute actions toward achieving these goals.**

#### Journey
**Loop with a combination of actions until user goal is achieved**

#### Context
**History of actions, action graphs during completion of user goal**

#### Data
**Data Lake for semantic search**

#### Integration
**External services connection, will be consumed by related actions**

#### User
**Human entity representation**

#### Bot
**Forever loop with diff Tasks**
