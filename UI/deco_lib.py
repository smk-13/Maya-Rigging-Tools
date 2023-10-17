from maya import cmds
import functools


# https://discourse.techart.online/t/pyqt-in-maya-question/186/8



def d_undoable(f):
    """
     A decorator that will make commands undoable in maya
    """
    @functools.wraps(f)
    def func(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        functionReturn = None
        try:
            functionReturn = f(*args, **kwargs)
        except RuntimeError as e:
            print(e.message)

        finally:
            cmds.undoInfo(closeChunk=True)
            return functionReturn

    return func


# @d_undoable
# def someFunction():
#     for i in range(10):
#        print("blah")

