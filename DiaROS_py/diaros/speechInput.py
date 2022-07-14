import time
import pyaudio
import wave
from six.moves import queue
from diaros.acousticAnalysis import AcousticAnalysis

STREAMING_LIMIT = 10000

class SpeechInput:
    """
    音声認識ストリーミング
    """

    def __init__(self, rate, chunk_size, device):
        """
        Arguments:
            rate {int} -- サンプルレート
            chunk_size {int} -- チャンクサイズ
            device {int} -- マイクデバイスのインデックス番号
        """
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = int(round(time.time() * 1000))
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self.mic_info = self._audio_interface.get_default_input_device_info()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            # input_device_index=device,
            input_device_index=self.mic_info["index"],
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        self.frequency = 0.0
        self.grad = 0.0
        self.power = 0.0
        self.zerocross = 0
        self.prevgrad = 0.0
        self.analysis = AcousticAnalysis(self._rate)

    def __enter__(self):
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""

        result = self.analysis.outputAubio(in_data)
        
        self.prevgrad = self.grad
        self.frequency = result[0]
        self.grad = result[1]
        self.power = result[2]
        self.zerocross = result[3]
        """
        print(self.grad, 1 if result[3] > 100 else 0)
        if result[3] < 80 and self.grad < -1:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """
        ストリーミング起動
        """

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)
                
                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round((self.final_request_end_time -
                                            self.bridging_offset) / chunk_time)

                    self.bridging_offset = (round((
                        len(self.last_audio_input) - chunks_from_ms)
                                                  * chunk_time))

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False
            
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
           
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b''.join(data)