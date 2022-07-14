import sys

class ResponseControl:
    def __init__(self):
        self.word = ""
        self.asr = { "you": "", "is_final": False }
        self.sa = { "prevgrad" : 0.0,
                    "frequency": 0.0,
                    "grad"     : 0.0,
                    "power"    : 0.0,
                    "zerocross": 0   }

        sys.stdout.write('ResponseControl start up.\n')
        sys.stdout.write('=====================================================\n')

    def run(self):
        prev = ""
        carry = ""
        while True:
            if self.asr["is_final"] and prev != self.asr["you"]:
                sys.stdout.write('YOU : ' + carry+self.asr["you"] + '\n')
                if len(carry+self.word) < 6:
                    self.word = "dummy"
                    carry = carry + self.asr["you"]
                else:
                    self.word = carry+self.asr["you"]
                    carry = ""

                prev = self.asr["you"]
                

            if abs(self.sa["prevgrad"]) > 1.0 and self.sa["zerocross"] < 100 and prev != self.asr["you"]:
                sys.stdout.write('>YOU : ' + self.asr["you"] + '\n')
                if len(self.asr["you"]) > 3:
                    self.word = self.asr["you"]
                    carry = ""
                else:
                    self.word = "dummy"
          
                prev = self.asr["you"]

                
    def pubRC(self):
        return { "word":self.word }

    def updateASR(self, asr):
        self.asr["you"] = asr["you"]
        self.asr["is_final"] = asr["is_final"]
    
    def updateSA(self, sa):
        self.sa["prevgrad"] = sa["prevgrad"]
        self.sa["frequency"] = sa["frequency"]
        self.sa["grad"] = sa["grad"]
        self.sa["power"] = sa["power"]
        self.sa["zerocross"] = sa["zerocross"]