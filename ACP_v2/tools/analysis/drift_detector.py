
class DriftDetector:
    def __init__(self, conn): self.conn = conn
    def detect_drift(self, fid, ver): 
        return {'added': 0, 'removed': 0, 'modified': 0}
