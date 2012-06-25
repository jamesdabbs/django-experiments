import hotshot
import hotshot.stats
import os

from wide_tables.models import Small, Medium, Large


# We'll repeat each test and average the results to smooth out any noise. This
# parameter controls the number of repetitions
REPS = 1000


def profile(func):
    """ Wraps a function in a hotshot profile and prints the results after the
        function is run
    """
    PROFILE_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'profiles'
    )

    def _inner(*args, **kwargs):
        # Start a hotshot profile
        file_path = os.path.join(PROFILE_PATH, '{}.prof'.format(func.__name__))
        profile = hotshot.Profile(file_path)
        print 'Profiling {} with args={} and kwargs ={} ...'.format(
            func.__name__, args, kwargs)
        profile.runcall(func, *args, **kwargs)
        profile.close()

        # Read the results and report on them
        print 'Compiling results ...'
        stats = hotshot.stats.load(file_path)
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(10)
    return _inner


@profile
def save_test(model):
    """ Instantiates and saves the given `model` """
    for i in range(0, REPS):
        model().save()


@profile
def retrieve_test(model):
    """ Retrieves and evaluates a QuerySet containing all objects of the given
        `model`
    """
    # Note that calling list() on the queryset forces its evaluation
    for i in range(0, REPS):
        list(model.objects.all())


@profile
def select_test(model, columns):
    """ Retrieves and evaluates a ValuesQuerySet containing all objects of the
        given `model`, but limited to `columns` many columns
    """
    # Bail out if we're trying to select more columns than there are
    if columns > model.width:
        print 'Cannot select {} columns from {}; it only has {}.'.format(
            columns, model, model.width)
        return
    # Otherwise, retrieve the objects, but limit the values returned
    values = ['col_{}'.format(i) for i in range(0, columns)]
    for i in range(0, REPS):
        list(model.objects.all().values(*values))


@profile
def update_test(model):
    """ Updates the entire object by calling its save method """
    for obj in model.objects.all():
        obj.save()


@profile
def update_fields_test(model, columns):
    """ Updates the given number of `columns` on the object `obj` """
    if columns > model.width:
        print 'Cannot update {} columns from {}; it only has {}.'.format(
            columns, model, model.width)
        return
    update_fields = ['col_{}'.format(i) for i in range(0, columns)]
    for obj in model.objects.all():
        obj.save(update_fields=update_fields)


def run_benchmarks():
    """ Runs the various test methods at given parameter values """
    models = [Small, Medium, Large]  # For ease of subsequent iteration

    # Clean up from earlier test runs, just in case
    for model in models:
        model.objects.all().delete()

    # Test saving
    # If you are actually adding this many objects at once (and are using
    # Django 1.4 or later), you should be using bulk_create. Here, we're
    # interested in the time it takes to save one object and are repeating the
    # test and averaging to smooth out potential noise.
    for model in models:
        save_test(model)

    # Test default retrieval vs. selecting using values
    for model in models:
        retrieve_test(model)
        for i in [10, 100, 1000]:
            select_test(model, i)

    # Test default update vs. saving using update_fields
    # Note that the `update_fields` argument is new as of Django 1.5
    for model in models:
        update_test(model)
        for i in [10, 100, 1000]:
            update_fields_test(model, i)
