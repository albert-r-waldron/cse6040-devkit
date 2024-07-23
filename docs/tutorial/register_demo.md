# Registering Demos

## Python Example

We register functions as demos using the `register_demo` decorator. The docstring is optional, and templates render gracefully without it.  

````python
@bp.register_demo(ex_name='fizzbuzz')
def fizzbuzz_demo():
    """The demo function calls should display this output  

```
fizzbuzz_soln(12) -> Fizz
fizzbuzz_soln(10) -> Buzz
fizzbuzz_soln(15) -> FizzBuzz
fizzbuzz_soln(16) -> 16
```
    """
    for i in [12, 10, 15, 16]:
        print(f'fizzbuzz_soln({i}) -> {fizzbuzz_soln(i)}')
````

## Example output

The function body is included in the exercise solution cell, but it is de-dented to execute at the top level. The docstring is included in the markdown cell immediately below so that it's easy to compare results.

![alt text](register_demo.png)  
