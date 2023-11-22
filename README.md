# SOVA.ai Speech-To-Text for Home Assistant

This integration allows to use [SOVA.ai Cloud Speech-to-Text](https://sova.ai/ru/asr-tts/) in Home Assistant.

## Install

You can install this integration via [HACS](https://hacs.xyz/). Go to HACS / Integrations / Three-dots menu / Custom repositories
and add:
- Repository: `https://github.com/whitepail/ha-sova-stt`
- Category: Integration

Then install the "SOVA.ai Speech-To-Text" integration.


## Configure

To use it you need to configure a local instance of sova.ai ASR, following the instructions in the
[SOVA.ai github repository](https://github.com/sovaai/sova-asr).
Then add the following to your `configuration.yaml`:

```yaml
stt:
  - platform: sova_stt
    server: your_sova_host:8888
```

After enabling the integration, you can configure a [Voice Assistant](https://www.home-assistant.io/blog/2023/04/27/year-of-the-voice-chapter-2/#composing-voice-assistants)
to use it by selecting `sova_stt` in the "Speech-to-text" option.

The only supported language now is Russian.


## FAQ

#### I get the following error in the Home Assistant system log

  ```
  The stt integration does not support any configuration parameters, got [{'platform': 'sova_stt', 'server': '....']. Please remove the configuration parameters from your configuration.
  ```

This is a known issue due to a [bug](https://github.com/home-assistant/core/issues/97161) in Home Assistant >= 2023.7. However, the reported message
does __not__ affect the functionality of this integration, it should still work as expected (if properly configured).

#### How much does it cost to use SOVA.ai Speech-To-Text?

SOVA.ai is completely free as long as you run it on your own hardware.
I use jetson TX2 to run several models, including SOVA, Piper, compreface, frigate etc...
Sova is available for x86_64 platform (https://github.com/sovaai/sova-asr) and ARM64 (https://github.com/whitepail/sova-asr-jetson)
