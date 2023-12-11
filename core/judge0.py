from .models import Exercise
from unidecode import unidecode
from time import sleep
import requests
import asyncio
import aiohttp

def format_output(output):
    '''Función utilizada para estandarizar el formato de la salida esperada de los casos de prueba y la salida real del código del usuario. En caso de que output pueda ser convertido a float, regresa el número redondeado a 1 decimal.
    '''
    output = unidecode(output) if output is not None else ''
    output = output.strip()
    output = output.replace('\r', '')
    try:
        number = float(output)
        return '{:.1f}'.format(number)
    except:
        return output


async def test_code(code, test_cases):
    '''Prueba código ingresado por el usuario con los casos de prueba de un ejercicio de codificación enviados como argumento. Regresa un diccionario con las llaves 'tests_passed' cuyo valor es una lista de booleanos que representan si el código ingresado pasó cada uno de los casos de prueba y 'stdout_list' que contiene una lista con strings que representan el output real de la evaluación de cada uno de los casos de prueba.
    '''
    # Esta línea es necesaria para eliminar caracteres no compatibles con ASCII, requerimiento de Judge0
    code = unidecode(code)
    tests_passed = []
    stdout_list = []
    expected_output_list = []
    input_list = []
    
    actions = []
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:     
            input_str = unidecode(test_case[0].replace('|', '\n'))
            expected_output = format_output(test_case[1])
            
            expected_output_list.append(expected_output)
            input_list.append(input_str)
            
            actions.append(asyncio.ensure_future(run_test_case(session, code, input_str)))
        
        test_results = await asyncio.gather(*actions)
        # ~ print('test_results = ' + str(test_results))
        for i, result in enumerate(test_results):
            stdout = format_output(result.get('stdout'))
            stdout_list.append(stdout)
            
            if result['stderr']:
                tests_passed.append(False)
            else:
                if stdout == expected_output_list[i]:
                    tests_passed.append(True)
                else:
                    tests_passed.append(False)
    
        # ~ print('tests_passed =', tests_passed)
        # ~ print('expected_output_list =', expected_output_list)
        # ~ print('stdout_list =', stdout_list)
        return {'tests_passed': tests_passed, 'stdout_list': stdout_list, 'expected_output_list': expected_output_list, 'input_list':input_list}
    
    
async def run_test_case(session, code, input_str):
    '''Ejectuta un caso de prueba de un ejercicio de forma asíncrona y regresa un diccionario que contiene los resultados de la ejecución.
    '''
    data = {
        "source_code": code,
        "language_id": 71,
        "number_of_runs": "1",
        "stdin": input_str,
        "expected_output": None,
        "cpu_time_limit": "5",
        "cpu_extra_time": "0.5",
        "wall_time_limit": "10",
        "memory_limit": "128000",
        "stack_limit": "64000",
        "max_processes_and_or_threads": "60",
        "enable_per_process_and_thread_time_limit": False,
        "enable_per_process_and_thread_memory_limit": False,
        "max_file_size": "1024",
        "redirect_stderr_to_stdout": True,
    }
    
    async with session.post("http://server:2358/submissions", data=data) as response:
        token = await response.json()
        test_result = None
        c = 0
    
        while c <= 10:
            await asyncio.sleep(0.5)
            async with session.get("http://server:2358/submissions/" + token['token']) as res:
                test_result = await res.json()
                if test_result['status']['id'] >= 3:
                    break

            c += 1
        
        return test_result


def run_code(code, input_str=None):
    '''Ejecuta código del usuario con Judge0 y regresa la respuesta como un diccionario
    '''
    data = {
        "source_code": code,
        "language_id": 71,
        "number_of_runs": "1",
        "stdin": input_str,
        "expected_output": None,
        "cpu_time_limit": "5",
        "cpu_extra_time": "0.5",
        "wall_time_limit": "10",
        "memory_limit": "128000",
        "stack_limit": "64000",
        "max_processes_and_or_threads": "60",
        "enable_per_process_and_thread_time_limit": False,
        "enable_per_process_and_thread_memory_limit": False,
        "max_file_size": "1024",
        "redirect_stderr_to_stdout": True,
    }
        
    token = requests.post("http://server:2358/submissions", data=data).json()
    res = None
    time = 0
    
    while time <= 5:
        sleep(1)
        res = requests.get("http://server:2358/submissions/" + token['token']).json()
        # ~ print('response', res)
        if res['status']['id'] >= 3:
            break

        time += 1
    
    return res
        
