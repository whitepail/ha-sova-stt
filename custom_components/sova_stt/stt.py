"""Support for the cloud for speech to text service."""
from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterable
import json
import aiohttp
import struct

import async_timeout
import voluptuous as vol

from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    AudioSampleRates,
    Provider,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_SERVER = "server"

SUPPORTED_LANGUAGES = [
    "ru-RU",
]


PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SERVER): cv.string,
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up Sova STT component."""
    server = config.get(CONF_SERVER)

    return SovaSTTProvider(hass, server)


class SovaSTTProvider(Provider):
    """The Sova STT API provider."""

    def __init__(self, hass, server) -> None:
        """Init Azure STT service."""
        self.hass = hass
        self.name = "Sova STT"


        self._server = server
        self._client = None

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def supported_formats(self) -> list[AudioFormats]:
        """Return a list of supported formats."""
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        """Return a list of supported codecs."""
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        """Return a list of supported bitrates."""
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        """Return a list of supported channels."""
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(
        self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]
    ) -> SpeechResult:

        def pcm2wav(sample_rate, pcm_voice):
            if pcm_voice.startswith("RIFF".encode()):
                return pcm_voice
            else:
                sampleNum = len(pcm_voice)
                rHeaderInfo = "RIFF".encode()
                rHeaderInfo += struct.pack('i', sampleNum + 44)
                rHeaderInfo += 'WAVEfmt '.encode()
                rHeaderInfo += struct.pack('i', 16)
                rHeaderInfo += struct.pack('h', 1)
                rHeaderInfo += struct.pack('h', 1)
                rHeaderInfo += struct.pack('i', sample_rate) 
                rHeaderInfo += struct.pack('i', sample_rate * int(16 / 8))
                rHeaderInfo += struct.pack("h", int(16 / 8))
                rHeaderInfo += struct.pack("h", 16)
                rHeaderInfo += "data".encode()
                rHeaderInfo += struct.pack('i', sampleNum)
                rHeaderInfo += pcm_voice
                return rHeaderInfo

        # Collect data
        audio_data = b''
        async for chunk in stream:
            audio_data += chunk

        url = self._server + "/asr"

        # start the request immediately (before we have all the data), so that
        # it finishes as early as possible. aiohttp will fetch the data
        # asynchronously from 'stream' as they arrive and send them to the server.
        try:
            data = aiohttp.FormData()
            data.add_field('audio_blob_0',
                pcm2wav(16000,audio_data),
                filename='stream.wav',
                content_type='audio/wav')
            async with async_timeout.timeout(15), aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as resp:
                    response_json = await resp.json(content_type=None)
                    _LOGGER.debug("sova stt returned %s", response_json)
                    _LOGGER.debug("respcode: %s", response_json['r'][0]['response_code'])
                    if response_json['r'][0]['response_code'] == 0:
                        _LOGGER.debug("text: %s", response_json['r'][0]['response'][0]['text'])
                        return SpeechResult(
                            response_json['r'][0]['response'][0]['text'],
                            SpeechResultState.SUCCESS,
                        )
                    else:
                        return SpeechResult("",SpeechResultState.ERROR)
        except:
            _LOGGER.exception("Error running sova stt")

            return SpeechResult("", SpeechResultState.ERROR)
