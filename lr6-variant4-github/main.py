"""Лабораторная работа № 6. Булова Екатерина, БИ 2-1, вариант 4."""

import argparse
import csv
import gc
import json
import platform
import sys
from functools import partial
from pathlib import Path
from random import Random
from statistics import median
from time import perf_counter_ns

from basics import RingQueue, SinglyLinkedList, Stack
from structures import ArrayDeque, BrowserHistory, DoublyLinkedList

ROOT = Path(__file__).resolve().parent
SIZES = (2_000, 4_000, 8_000)
FACTORIES = {"linked": DoublyLinkedList, "deque": ArrayDeque, "list": list}
OPERATIONS = ("front", "back", "alternating")
REPEATS = 15


def save_csv(name, rows):
    with (ROOT / "results" / name).open("w", newline="", encoding="utf-8") as file:
        out = csv.DictWriter(file, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def sequence_text(container):
    return "[" + ", ".join(map(str, container)) + "]"


def small_example():
    linked, ring, reference = DoublyLinkedList(), ArrayDeque(4), []
    rows = []
    operations = [("push_front" if i % 2 else "push_back", i) for i in range(1, 13)]
    operations += [("pop_front", None), ("pop_back", None)]
    for step, (action, value) in enumerate(operations, 1):
        if action == "push_front":
            linked.push_front(value)
            ring.push_front(value)
            reference.insert(0, value)
            result = "—"
        elif action == "push_back":
            linked.push_back(value)
            ring.push_back(value)
            reference.append(value)
            result = "—"
        else:
            from_list = getattr(linked, action)()
            from_ring = getattr(ring, action)()
            result = reference.pop(0 if action == "pop_front" else -1)
            assert from_list == from_ring == result
        assert list(linked) == list(ring) == reference
        assert len(linked) == len(ring) == len(reference)
        call = f"{action}({'' if value is None else value})"
        rows.append(dict(step=step, action=call, returned=result, size=len(ring),
                         capacity=ring.capacity, contents=sequence_text(ring)))
    return rows


def history_example():
    history = BrowserHistory("/home")
    rows = []
    moves = [("старт", None), ("назад", None), ("открыть", "/catalog"),
             ("открыть", "/item"), ("назад", None), ("вперёд", None),
             ("назад", None), ("открыть", "/cart"), ("вперёд", None),
             ("назад", None), ("назад", None)]
    expected = ["/home", "/home", "/catalog", "/item", "/catalog", "/item",
                "/catalog", "/cart", "/cart", "/catalog", "/home"]
    for i, (action, page) in enumerate(moves):
        if action == "открыть":
            history.visit(page)
        elif action == "назад":
            history.back()
        elif action == "вперёд":
            history.forward()
        assert history.current == expected[i]
        rows.append(dict(step=i, action=" ".join(filter(None, (action, page))),
                         past=sequence_text(history.past), current=history.current,
                         future=sequence_text(history.future)))
    return rows


def check():
    small_example()
    history_example()
    for factory in (SinglyLinkedList, DoublyLinkedList):
        values = factory()
        values.push_front(2)
        values.push_back(4)
        values.insert(1, 3)
        assert list(values) == [2, 3, 4] and len(values) == 3
        assert values.get(1) == 3 and values.find(4) == 2 and values.find(0) == -1
        assert values.pop_front() == 2
    stack, queue = Stack(), RingQueue()
    for x in range(12):
        stack.push(x)
        queue.enqueue(x)
    assert stack.top() == 11
    assert [stack.pop() for _ in range(12)] == list(reversed(range(12)))
    assert [queue.dequeue() for _ in range(12)] == list(range(12))
    for factory in (ArrayDeque, DoublyLinkedList):
        empty = factory()
        for pop in (empty.pop_front, empty.pop_back):
            try:
                pop()
            except IndexError:
                pass
            else:
                raise AssertionError("Извлечение из пустой структуры")


def time_batch(factory, mode, values):
    container = factory()
    if factory is list:
        front, back = partial(container.insert, 0), container.append
    else:
        front, back = container.push_front, container.push_back
    if mode == "alternating":
        start = perf_counter_ns()
        for i, value in enumerate(values):
            if i % 2 == 0:
                front(value)
            else:
                back(value)
    else:
        push = front if mode == "front" else back
        start = perf_counter_ns()
        for value in values:
            push(value)
    elapsed = perf_counter_ns() - start
    assert len(container) == len(values)
    return elapsed


def timings():
    rows = []
    rng = Random(4)
    for n in SIZES:
        values = tuple(range(n))
        cases = [(name, mode) for name in FACTORIES for mode in OPERATIONS]
        samples = {case: [] for case in cases}
        enabled = gc.isenabled()
        gc.disable()
        try:
            for repeat in range(REPEATS + 1):
                rng.shuffle(cases)
                for name, mode in cases:
                    elapsed = time_batch(FACTORIES[name], mode, values)
                    if repeat:
                        samples[name, mode].append(elapsed)
                    if name == "linked":
                        gc.collect()  # Циклические ссылки убираются вне измерения.
        finally:
            if enabled:
                gc.enable()
        for (name, mode), series in samples.items():
            ns = median(series)
            rows.append(dict(n=n, structure=name, operation=mode,
                             batch_ms=ns / 1_000_000, ns_per_op=ns / n))
    return rows


def memory(n=10_000):
    payload = list(range(n))
    payload_bytes = sum(map(sys.getsizeof, payload))
    rows = []
    for name, factory in FACTORIES.items():
        obj = factory()
        push = obj.append if name == "list" else obj.push_back
        for value in payload:
            push(value)
        own = sys.getsizeof(obj)
        extra = 0
        if name == "linked":
            node = obj.head
            while node is not None:
                extra += sys.getsizeof(node)
                node = node.next
        elif name == "deque":
            extra = sys.getsizeof(obj._data)
        rows.append(dict(structure=name, n=n, header_bytes=own, storage_bytes=extra,
                         structure_bytes=own + extra, bytes_per_item=(own + extra) / n,
                         payload_bytes=payload_bytes, total_bytes=own + extra + payload_bytes))
    return rows


def run():
    (ROOT / "results").mkdir(exist_ok=True)
    save_csv("demo.csv", small_example())
    save_csv("history.csv", history_example())
    for row in small_example():
        print(f"{row['step']:2d}. {row['action']:<15} {row['contents']}")
    save_csv("timings.csv", timings())
    save_csv("memory.csv", memory())
    meta = dict(python=platform.python_version(), system=platform.system(),
                repeats=REPEATS, sizes=SIZES, memory_n=10_000)
    (ROOT / "results" / "run.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    from plots import draw
    draw(ROOT)
    print("Проверки пройдены. Таблицы находятся в results/, графики — в figures/.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="только проверить структуры")
    args = parser.parse_args()
    check()
    if args.check:
        print("Проверки структур и истории пройдены.")
    else:
        run()
