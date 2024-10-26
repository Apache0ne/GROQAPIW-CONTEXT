# GROQ LLM Node With Context

This repository hosts a forked version of the GROQ LLM Node from @MNeMoNiCuZ. Added the context ability for Groq’s API. The forked Node now can hold context from all chats using a random uuid4 ID key to call the chats context from the JSON file that has all the saved chats. Below I will leave the og way to use the node and then add my extra ways under. I highly recommend checking out the rest of @MNeMoNiCuZ nodes. 

## Groq LLM API W/CONTEXT
This node makes an API call to groq, and returns the response in text format.

![image](https://github.com/user-attachments/assets/eac84632-39d5-45de-b2be-4cd5c3545ecc)

### Setup
You need to manually enter your [groq API key](https://console.groq.com/keys) into the `GroqConfig.ini` file.

Currently, the Groq API can be used for free, with very friendly and generous [rate limits](https://console.groq.com/docs/rate-limits).


### Settings
**model**: Choose from a drop-down one of the available models. The list need to be manually updated when they add additional models.

**preset**: This is a dropdown with a few preset prompts, the user's own presets, or the option to use a fully custom prompt. See examples and presets below.

**system_message**: The system message to send to the API. This is only used with the `Use [system_message] and [user_input]` option in the preset list. The other presets provide their own system message.

**user_input**: This is used with the `Use [system_message] and [user_input]`, but can also be used with presets. In the system message, just mention the USER to refer to this input field. See the presets for examples.

**temperature**: Controls the randomness of the response. A higher temperature leads to more varied responses.

**max_tokens**: The maximum number of tokens that the model can process in a single response. Limits can be found [here](https://console.groq.com/docs/models).

**top_p**: The threshold for the most probable next token to use. Higher values result in more predictable results.

**seed**: Random seed. Change the `control_after_generate` option below if you want to re-use the seed or get a new generation each time.

**control_after_generate**: Standard comfy seed controls. Set it to `fixed` or `randomize` based on your needs.

**stop**: Enter a word or stopping sequence which will terminate the AI's output. The string itself will not be returned.

* Note: `stop` is not compatible with `json_mode`.

**json_mode**: If enabled, the model will output the result in JSON format.

* Note: You must include a description of the desired JSON format in the system message. See the examples below.

* Note: `json_mode` is not compatible with `stop`.


For additional information, please visit the [project's GitHub page](https://github.com/MNeMoNiCuZ/ComfyUI-mnemic-nodes?tab=readme-ov-file#-groq-llm-api-node).

# Installation instructions

You may need to manually install the requirements. They should be listed in `requirements.txt`
You may need to install the following libraries using `pip install XXX`:
```
configparser
groq
torch
```
