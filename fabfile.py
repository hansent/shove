'''shove fabfile'''

from fabric.api import prompt, local, settings, env  # , lcd

regup = './setup.py register sdist --format=bztar,gztar,zip upload'
nodist = 'rm -rf ./dist'
sphinxup = './setup.py upload_sphinx'


def _promptup():
    prompt('Enter tag: ', 'tag')
    with settings(warn_only=True):
        local('hg tag "%(tag)s"' % env)
        local('hg push ssh://hg@bitbucket.org/lcrees/shove')
        local('hg push github')


def _test(val):
    truth = val in ['py26', 'py27', 'py32']
    if truth is False:
        raise KeyError(val)
    return val


def tox():
    '''test shove'''
    local('tox')


#def docs():
#    with lcd('docs/'):
#        local('make clean')
#        local('make html')
#        local('make linkcheck')
#        local('make doctest')


def update_docs():
#    docs()
    with settings(warn_only=True):
        local('hg ci -m docmerge')
        local('hg push ssh://hg@bitbucket.org/lcrees/shove')
        local('hg push github')
    local(sphinxup)


def tox_recreate():
    '''recreate shove test env'''
    prompt(
        'Enter testenv: [py26, py27]',
        'testenv',
        validate=_test,
    )
    local('tox --recreate -e %(testenv)s' % env)


def release():
    '''release shove'''
    local('hg update pu')
    local('hg update next')
    local('hg merge pu; hg ci -m automerge')
    local('hg update maint')
    local('hg merge default; hg ci -m automerge')
    local('hg update default')
    local('hg merge next; hg ci -m automerge')
    local('hg update pu')
    local('hg merge default; hg ci -m automerge')
    _promptup()
    local(regup)
    local(sphinxup)
    local(nodist)


def releaser():
    '''shove releaser'''
#    docs()
    _promptup()
    local(regup)
    local(sphinxup)
    local(nodist)


def inplace():
    '''in-place shove'''
#    docs()
    with settings(warn_only=True):
        local('hg push ssh://hg@bitbucket.org/lcrees/shove')
        local('hg push github')
    local('./setup.py sdist --format=bztar,gztar,zip upload')
    local(sphinxup)
    local(nodist)


def release_next():
    '''release shove from `next` branch'''
    local('hg update maint')
    local('hg merge default; hg ci -m automerge')
    local('hg update default')
    local('hg merge next; hg ci -m automerge')
    local('hg update next')
    local('hg merge default; hg ci -m automerge')
    _promptup()
    local(regup)
    local(sphinxup)
    local(nodist)


def start_daemons():
    pass


def stop_daemons():
    pass