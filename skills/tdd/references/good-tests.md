# Good tests

Load when writing or changing tests, adding a mock or test double, or adding a test helper. Examples are pseudocode; translate to the project's framework (ExUnit, Zig `test`, a C harness, busted, ...).

Two principles: **every test names the break it catches**, and **every test exercises the real thing**.

## Name the break

Before the body: what production change would make this fail, and is that change a bug or a decision?

| Answer | Do |
|---|---|
| Can't name one | Redesign around an observable behaviour |
| "The source text changed" | Run the artifact; assert outputs, side effects, exit codes |
| Only intentional decisions | Change detector: test the behaviour that depends on the decision |

**Independent expected values.** The expectation must not be computed by the code under test or its helpers.

```
# BAD: tautological, passes by construction
items    = [{price: 10}, {price: 5}]
expected = sum(i.price for i in items)
assert total(items) == expected

# GOOD: known literal
assert total([{price: 10}, {price: 5}]) == 15
```

Prefer table-driven tests with literal `want` columns.

**No change detectors.** Not `assert MAX_RETRIES == 5` but "a failing call is retried 5 times and the 6th never happens."

**Your code, not the framework.** Test the contract your code makes at its boundary (the message you send, the query you emit, the bytes you write). Constructors, getters, and trivial forwarding earn tests only when they validate, normalise, default, derive, or cause side effects.

## Test through the interface

```
# BAD: verifies through a side channel
create_user(name: "Alice")
assert db.query("SELECT * FROM users WHERE name = 'Alice'") != empty

# GOOD: verifies through the interface
u = create_user(name: "Alice")
assert get_user(u.id).name == "Alice"
```

Red flags: mocking internal collaborators, testing private functions, asserting call counts or order on your own modules, a test that breaks on a refactor that kept behaviour, a test name that describes how.

## Mocks and doubles

Mock only at **system boundaries**: external services, clock, randomness, hardware/audio devices, sometimes filesystem or database (prefer a real temp dir / test DB). Never your own modules.

- **Inject the boundary.** Pass the dependency in rather than constructing it inside (a function argument, a behaviour/protocol, a vtable or function pointer in C, an interface struct in Zig, a module param in Lua).
- **One function per external operation** (`get_user`, `create_order`) beats a generic `request(endpoint, opts)`: each double returns one shape, with no conditional logic in the test.
- **Learn the real side effects before replacing them.** Mock the slow/external layer below what the test depends on.
- **Mirror the real data completely**, not just the fields this test reads; partial doubles pass while integration breaks.
- **Make doubles specific** when arguments or ordering are part of the boundary contract; give each branch (ok / error / malformed) its own fixture.
- **The mock earns no assertions.** If removing the mock would fail the test, you are testing the mock.
- **Setup outgrows the test** → switch to an integration test with real components.
- **Test-only cleanup** lives in test helpers, never as a production function.

## Mutation check

Before finishing, mentally mutate the code; some test should fail for each:

- wrong constant or argument
- wrong branch taken
- missing state change or side effect
- empty / zero / default return
- missing validation for zero, empty, nil/null, out-of-range, malformed input

A mutation nothing catches is unprotected behaviour, or a tautological test.

## Warning signs

- setup and assertion share the same object, guaranteeing equality
- the test can only fail by crashing
- it fails on every intentional change and never on accidental breakage
- expected values hidden behind loops, builders, or helpers
- it greps source text, or asserts a removed symbol stays removed
- mock setup is more than half the test
- it exists for coverage and checks no outcome
