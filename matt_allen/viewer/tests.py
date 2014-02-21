import tkutils

def test_diff_genomes():
    start = 'aaaa'
    end = 'aaaa'
    assert len(tkutils.diff_genomes(start, end)) == 0

    end = 'aaab'
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 1
    assert changes[0] == ('diff', 3, 1, 'b')

    end = 'aabaa'
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 1
    assert changes[0] == ('ins', 2, 1, 'b')

    end = 'aaaaa'
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 1
    assert changes[0] == ('ins', 4, 1, 'a')

    end = 'aaa'
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 1
    assert changes[0] == ('del', 3, 1, '')

    end = ''
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 1
    assert changes[0] == ('del', 0, 4, '')

    start = ''
    end = ''
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 0

    start = 'abcdefghij'
    end = 'aqcdefhij'
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 2
    assert changes[0] == ('diff', 1, 1, 'q')
    assert changes[1] == ('del', 6, 1, '')

    start = 'abcdefghij'
    end = 'qbcdefghij'
    changes = tkutils.diff_genomes(start, end)
    assert len(changes) == 1
    assert changes[0] == ('diff', 0, 1, 'q')

