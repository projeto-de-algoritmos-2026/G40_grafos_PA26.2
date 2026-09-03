def heap_inserir(heap, elemento):

    heap.append(elemento)

    i = len(heap) - 1

    while i > 0:

        pai = (i-1) // 2 

        if heap[pai][0] <= heap[i][0]:
            break

        heap[pai], heap[i] = heap[i], heap[pai]
        i = pai 


def heap_remover(heap):

    if len(heap) == 0:
        raise IndexError("Heap vazia.")

    if len(heap) == 1:
        return heap.pop()

    minimo = heap[0]
    heap[0] = heap.pop()

    i = 0
    while True:
        esquerda = 2 * i + 1
        direita = 2 * i + 2
        menor = i

        if esquerda < len(heap) and heap[esquerda][0] < heap[menor][0]:
            menor = esquerda

        if direita < len(heap) and heap[direita][0] < heap[menor][0]:
            menor = direita

        if menor == i:
            break

        heap[i], heap[menor] = heap[menor], heap[i]
        i = menor

    return minimo