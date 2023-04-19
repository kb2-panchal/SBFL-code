import sys
import argparse
import json

current = []
testCovLines = {}


def traceLine(frame, event, arg):
    if event == 'line':
        lineno = frame.f_lineno
        testCovLines[current]['coverlines'].add(lineno)
    return traceLine


def initCovMatrix(res, modName):
    with open('./testCode/{}.py'.format(modName)) as f:
        for i, line in enumerate(f):
            res.append({
                '_line_no': i+1,
                'code': line,
                'n_cover': [0, 0],
                'n_uncover': [0, 0],
                'coverage': [],
                # 'fl': {}
            })
    return i + 1


def makeCovMatrix(res, totalLine):
    for t in testCovLines.values():
        r = t['result']
        for i in range(totalLine):
            stat = 'O'
            if i+1 in t['coverlines']:
                if r == 0:
                    stat = 'P'
                else:
                    stat = 'F'
                res[i]['n_cover'][r] += 1
            else:
                res[i]['n_uncover'][r] += 1
            res[i]['coverage'].append(stat)


def outputCovMatrix(res, modName, pf):
    resJson = {
        'name': modName,
        'total_passes': pf[0],
        'total_fails': pf[1],
        'coverage_matrix': res
    }
    with open('result_matrix.json', 'w') as f:
        json.dump(resJson, f, indent=2)


def start(modName, funcName, testcases):
    global current
    module = __import__('testCode.{}'.format(modName))
    func = getattr(getattr(module, modName), funcName)
    try:
        with open(testcases) as json_data:
            tests = json.load(json_data)
    except FileNotFoundError:
        print(
            'Error: Could not find {}.json in /testCases'.format(testcases),
            '\n..Abort..'
        )
        sys.exit(2)

    totalPF = [0, 0]
    for test in tests:
        current = tuple(test['input'])
        if current not in testCovLines:
            testCovLines[current] = {'coverlines': set()}

            sys.settrace(traceLine)
            output = func(test['input'])
            sys.settrace(None)

            temp = int(not(output == test['result']))
            totalPF[temp] += 1
            testCovLines[current]['result'] = temp

    res = []
    totalLine = initCovMatrix(res, modName)
    makeCovMatrix(res, totalLine)
    outputCovMatrix(res, modName, totalPF)
    print('Done! The Coverage Matrix Data is outputted to result_matrix.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate coverage matrix from testcase json file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'module',
        type=str,
        help='Name of the test module file (without .py) in /tmods'
    )
    parser.add_argument(
        'func',
        type=str,
        help='Name of the entry function'
    )
    parser.add_argument(
        'src',
        type=str,
        help='Name of the testcase (.json) in /testCases'
    )

    args = parser.parse_args()
    start(
        args.module,
        args.func,
        './testCases/{}'.format(args.src)
    )
