class MinHeap:
    """
    Implementación propia de Min-Heap (montículo mínimo).
    
    Complejidades:
    - push: O(log n)
    - pop: O(log n)
    - peek: O(1)
    """
    
    def __init__(self):
        self._heap = []
    
    def push(self, item):
        """Inserta un elemento y mantiene la propiedad del heap"""
        self._heap.append(item)
        self._sift_up(len(self._heap) - 1)
    
    def pop(self):
        """Extrae y retorna el elemento mínimo"""
        if not self._heap:
            raise IndexError("pop from empty heap")
        
        # Intercambiar root con el último elemento
        self._swap(0, len(self._heap) - 1)
        min_item = self._heap.pop()
        
        # Restaurar propiedad del heap
        if self._heap:
            self._sift_down(0)
        
        return min_item
    
    def peek(self):
        """Retorna el mínimo sin extraerlo"""
        if not self._heap:
            return None
        return self._heap[0]
    
    def _sift_up(self, index):
        """Mueve un elemento hacia arriba hasta su posición correcta"""
        parent = (index - 1) // 2
        
        # Mientras no sea la raíz y sea menor que su padre
        while index > 0 and self._heap[index] < self._heap[parent]:
            self._swap(index, parent)
            index = parent
            parent = (index - 1) // 2
    
    def _sift_down(self, index):
        """Mueve un elemento hacia abajo hasta su posición correcta"""
        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2
            
            # Comparar con hijo izquierdo
            if left < len(self._heap) and self._heap[left] < self._heap[smallest]:
                smallest = left
            
            # Comparar con hijo derecho
            if right < len(self._heap) and self._heap[right] < self._heap[smallest]:
                smallest = right
            
            # Si el elemento está en su lugar correcto
            if smallest == index:
                break
            
            self._swap(index, smallest)
            index = smallest
    
    def _swap(self, i, j):
        """Intercambia dos elementos"""
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
    
    def __len__(self):
        return len(self._heap)
    
    def __bool__(self):
        return bool(self._heap)
    
    def __iter__(self):
        """Permite iterar sobre el heap"""
        return iter(self._heap)
    
    def clear(self):
        """Limpia el heap"""
        self._heap.clear()