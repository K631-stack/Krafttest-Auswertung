import matplotlib.pyplot as plt
from warnings import simplefilter
import os

simplefilter(action='ignore', category=FutureWarning)


def specify_plot_parameters_separate(data, name, test, plot_dir):
    # TODO: Change ylabel depending on mode
    # TODO: move legend to the outside of the plot
    data.plot(style="-o",
              ylabel='Maximale Kraft in Kg',
              xlabel='Datum',
              title=f"{name} {test}")
    plt.legend(title="Hand")
    plt.grid()
    plt.savefig(f"{plot_dir}/{name}_{test}.pdf", format="pdf", bbox_inches="tight")
    plt.close()


def plot_data_separate(measurements_per_person, plot_dir):
    for name, data_person in measurements_per_person.items():
        print(f"plotting {name}")

        # Plots for different tests
        test_types = ['Finger', '90', '120']
        for i, test in enumerate(test_types):

            data_plot = data_person.loc[:, ([test], ['L', 'R'])]

            if not data_plot.empty:
                specify_plot_parameters_separate(data_plot, name, test, plot_dir)

        # summary plot of all tests for both hands combined
        person_both = data_person.loc[:, (['Finger', '90', '120'], ['both'])]
        specify_plot_parameters_separate(person_both, name, 'both')


def specify_plot_parameters_grid(data, name, test, x, y, axis):
    # TODO: move legend to the outside of the plot
    # create subplots for individual tests
    axis[x, y].plot(data, 'o', ls="-")
    axis[x, y].set_title(f"{name} {test}")
    axis[x, y].set_xticks(axis[x, y].get_xticks(),
                          axis[x, y].get_xticklabels(),
                          rotation=45,
                          ha='right')
    axis[x, y].grid()
    axis[x, y].legend(list(data.columns.map(' '.join)))


def plot_data_grid(measurements_per_person, plot_dir):
    for name, data_person in measurements_per_person.items():
        print(f"plotting {name}")

        # Plots for different tests
        test_types = ['Finger', '90', '120']
        fig, axs = plt.subplots(2, 2)

        for i, test in enumerate(test_types):

            data_plot = data_person.loc(axis=1)[[test], ['L', 'R']]

            if not data_plot.empty:
                # get index for subplots
                x = max(i - 1, 0)
                y = i % 2

                specify_plot_parameters_grid(data_plot, name, test, x, y, axs)

        # summary plot of all tests for both hands combined
        person_both = data_person.loc(axis=1)[['Finger', '90', '120'], ['both']]
        specify_plot_parameters_grid(person_both, name, 'beide Hände', 1, 1, axs)

        fig.tight_layout()
        fig.savefig(f"{plot_dir}/{name}.pdf", format="pdf", bbox_inches="tight")
        plt.close()


def create_plot_folder(dir_name):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(root_dir, dir_name)
    if not os.path.exists(plots_dir):
        os.mkdir(plots_dir)


def plot_data(df, plot_type, plot_dir):

    create_plot_folder(plot_dir)

    if plot_type == 'grid':
        plot_data_grid(df, plot_dir)
    elif plot_type == 'separate':
        plot_data_separate(df, plot_dir)
    else:
        raise ValueError('Plot type needs to be grid or separate')


