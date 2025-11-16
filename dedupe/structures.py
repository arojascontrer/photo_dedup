
class HashTable:
    def __init__(self, size=1024):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    def _index(self, key):
        return key % self.size

    def insert(self, key, value):
        index = self._index(key)
        bucket = self.buckets[index]

        for k, v in bucket:
            if k == key:
                v.append(value)
                return
        
        bucket.append((key, [value]))

    def get(self, key):
        index = self._index(key)
        bucket = self.buckets[index]

        for k, v in bucket:
            if k == key:
                return v
        return None

    def exists(self, key):
        return self.get(key) is not None

class BKTree:
    def __init__(self):
        self.root = None
    
    def add(self, hash_val, value):
        if self.root is None:
            self.root = (hash_val, {}, [value])
            return
        
        current = self.root
        while True:
            current_hash, children, values = current
            distance = bin(hash_val ^ current_hash).count('1')
            
            if distance == 0:
                values.append(value)
                return
            
            if distance not in children:
                children[distance] = (hash_val, {}, [value])
                return
            
            current = children[distance]
    
    def search(self, hash_val, threshold):
        if self.root is None:
            return []
        
        results = []
        candidates = [self.root]
        
        while candidates:
            current_hash, children, values = candidates.pop()
            distance = bin(hash_val ^ current_hash).count('1')
            
            if distance <= threshold:
                results.extend(values)
            
            for d in range(max(0, distance - threshold), 
                          distance + threshold + 1):
                if d in children:
                    candidates.append(children[d])
        
        return results
