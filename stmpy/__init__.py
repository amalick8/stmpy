import importlib
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
#For Python 3.8+, to avoid SyntaxWarning: "is" with a literal. Did you mean "=="?

__all__ = ['tools']

from stmpy.io import load, save


def __getattr__(name):
    """Load optional modules only when they are requested."""
    modules = {
        'tools': '.tools',
        'matio': '.matio',
        'image': '.image',
        'palette': '.color.palette',
    }

    if name in modules:
        value = importlib.import_module(modules[name], __name__)
    elif name == 'cm':
        value = importlib.import_module('.color.colormap', __name__).cm
    elif name == 'saturate':
        value = importlib.import_module('.image', __name__).saturate
    elif name == 'drift':
        try:
            value = importlib.import_module('.driftcorr', __name__)
        except ModuleNotFoundError as error:
            if error.name not in {'cv2', 'skimage'}:
                raise
            raise ModuleNotFoundError(
                'Drift correction requires opencv-python and scikit-image. '
                'Install both packages to use stmpy.drift.'
            ) from error
    else:
        raise AttributeError("module {!r} has no attribute {!r}".format(__name__, name))

    globals()[name] = value
    return value
