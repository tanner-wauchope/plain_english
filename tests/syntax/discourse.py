from plain_english.language.syntax.discourse import (
    interpret,
    Discourse,
)

factorial_english = """a Number N has a 'Factorial'.
if N is 0,
\tthe Factorial is 1.
otherwise,
\tit is N times the Factorial of N minus 1.
"""

factorial_python = """a.Number(N).has(a.Factorial_)(
\t'''if_(N.is_(0))(
\t\t"the.Factorial.is_(1)")''',
\t'''otherwise(
\t\t"it.is_(N(times(the.Factorial(of(N(minus(1)))))))")''')
"""


def test_interpret_standalone():
    assert interpret(factorial_english) == factorial_python


def test_interpret_discourse():
    discourse = Discourse()
    for line in factorial_english.split('\n')[:-1]:
        discourse.interpret(line)
    assert discourse.interpret('\n') == factorial_python