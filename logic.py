import logging
import pprint
from collections import defaultdict

from dash.exceptions import PreventUpdate
from pandas import DataFrame
import plotly.graph_objs as go
import numpy as np
from plotly import tools

import data
from data import MongoManager

logger = logging.getLogger('dashvision.{}'.format(__name__))

class AppLogic():

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def experiment_options(self, db_name):
        exp_names = self.data_manager.get_experiment_names(db_name)
        exps_selector_options = ([{'label': name, 'value': name} for name in exp_names])
        return exps_selector_options


    def database_options(self, ):
        database_name = self.data_manager.get_database_names()
        database_options = []
        for db_name in database_name:
            database_options += [{'label': db_name, 'value': db_name}]
        return database_options

    def table_content_from_exp_names(self, db_name, exp_names, columns):
        cursor = self.data_manager.get_rows_from_exp_names(db_name, exp_names, columns)
        table_content = self.generate_experiment_table_rows(cursor, columns)
        return table_content


    def table_content_from_ids(self, db_name, selected_ids, columns):
        cursor = self.data_manager.get_rows_from_ids(db_name, selected_ids, columns)
        table = self.generate_experiment_table_rows(cursor, columns)
        return table


    def configs_from_ids(self, db_name, selected_ids):
        cursor = self.data_manager.get_configs_from_ids(db_name, selected_ids)
        res = []
        for elt in cursor:
            res.append(pprint.pformat(elt['config'], indent=4))

        return res


    def get_nested(self, d, keys):
        """
        get_nested(d, keys) create a list of key : value
        :param d: dict containing the wanted value
        :param keys: list of nested keys to get
        :return: the value corresponding to the nested keys
        """

        for k in keys:
            d = d[k]

        return d

    def generate_experiment_table_rows(self, cursor, columns):
        warn_missing = set()

        rows = []
        for exp in cursor:
            row = {}
            for col in columns:
                try:
                    row[col] = self.get_nested(exp, col.split('.'))
                except KeyError:
                    if col not in warn_missing:
                        warn_missing.add(col)
                        logger.warning('Requesting missing value: {}'.format(col))
                    row[col] = None
            rows.append(row)
        return rows

    def filter_rows_by_query(self, rows, query):
        '''
        Returns rows that are filtered by the query.
        Uses the pandas.DataFrame.query method
        '''

        if query.strip() == '':
            return rows

        df = DataFrame(rows)

        # temporarily replacing '.' in columns to '__'
        # for pandas syntax reasons
        normalize_col_names = lambda x: x.replace('.', '___')

        df_renamed = df.rename(columns=normalize_col_names)

        # filter rows with query
        try:
            df_filtered = df_renamed.query(normalize_col_names(query), local_dict={})
        except Exception as e:
            logger.warning(f'Error in query "{query}": {e}')
            raise PreventUpdate

        # recovering origin column names
        denormalize_col_names = lambda x: x.replace('___', '.')
        df_filtered = df_filtered.rename(columns=denormalize_col_names)

        # check column integrity
        if (df_filtered.columns != df.columns).any():
            col_diff = [f'{c} -> {cf}' for c, cf in zip(df.columns, df_filtered.columns) if c != cf]
            logger.warning(f'Columns {", ".join(col_diff)} differ before and after query.')
            raise PreventUpdate

        filtered_rows = df_filtered.to_dict('rows')
        return filtered_rows

    def metric_names_from_ids(self, db_name, selected_ids):
        cursor = self.data_manager.get_metrics_infos(db_name, selected_ids)
        names = set()
        for elt in cursor:
            if 'metrics' in elt['info']:
                names.update([m['name'] for m in elt['info']['metrics']])
        return list(names)

    def metric_data_from_ids(self, metric_name, db_name, selected_ids):
        cursor = self.data_manager.get_metric_data(metric_name, db_name, selected_ids)
        return cursor

    def get_pareto_curves(self, pareto_x, pareto_y, db_name, selected_ids):
        res = self.data_manager.get_metrics_data([pareto_x, pareto_y], db_name, selected_ids)

        res = self.data_manager.init_connection_to_metrics(db_name).aggregate([
            {"$match": {"name": {"$in": [pareto_x, pareto_y]}, "run_id": {"$in": selected_ids}}},
            {"$group":
                {"_id": "$run_id",
                 "metrics": {"$push":  {"name": "$name",  "steps": "$steps",  "values": "$values"}}
                 }
             }]
        )
        res = list(res)
        result = defaultdict(list)
        for exp in res:
            orig = None
            for metric in exp['metrics']:
                result[metric['name']].extend(metric['values'])
                new_orig = [(exp['_id'], int(step)) for step in metric['steps']]
                assert orig is None or new_orig == orig
                orig = new_orig
            result['_orig_'].extend(orig)

        res_paret = paretize_exp(result, pareto_x, pareto_y, pareto_y)

        layout = go.Layout(
            title='Curve {}/{}'.format(pareto_x, pareto_y),
        )
        # traces = []
        trace = go.Scatter(
                x=res_paret[pareto_x],
                y=res_paret[pareto_y],
                mode='markers',
                text=res_paret['_orig_'],
                name='pareto front',
            )
        fig = go.Figure(data=[trace], layout=layout)
        return fig

    def traj_step_from_id_options(self, db_name, selected_id):
        steps = self.data_manager.get_from_run_info('evaluation_trajectories', db_name, selected_id)
        return [{'label': step, 'value': filename} for step, filename in steps]

    # def get_trajectory_plot(self, step_idx, step, db_name, selected_id):
    def get_trajectory_plot(self, artifact_name, db_name, selected_id):
        param_names = self.data_manager.get_from_run_info('all_params_name', db_name, selected_id)
        feature_names = self.data_manager.get_from_run_info('all_params_name', db_name, selected_id)
        trajectories_data = self.data_manager.get_artifact(db_name, artifact_name, selected_id)

        n_params = len(param_names)

        idx = 0
        # values = res['eval_sequence_probas'][idx]

        rewards = trajectories_data['rewards']
        arch_probas = trajectories_data['architecture_probas']
        all_obs = trajectories_data['obs']

        traces = _get_dynamics_traces(param_names, arch_probas)
        if trajectories_data['obs'] is None:
            steps = []
            for i, r in zip(range(len(arch_probas)), rewards):
                cur_step = dict(
                    method='restyle',
                    args=['visible', [False] * len(traces)],
                    label='{}-R={}'.format(i, r),
                )
                cur_step['args'][1][i * n_params:(i + 1) * n_params] = [True] * n_params
                steps.append(cur_step)

            sliders = [dict(
                active=1,
                currentvalue={"prefix": "Traj "},
                # pad={"l": 50},
                steps=steps
            )]

            layout = dict(sliders=sliders,
                          title=artifact_name)

            fig = dict(data=traces, layout=layout)
        else:
            hm_traces = _get_heatmap_traces(all_obs, feature_names)
            all_traces = traces + hm_traces

            steps = []
            for i, r in enumerate(rewards):
                cur_step = dict(
                    method='restyle',
                    args=['visible', [False] * len(all_traces)],
                    label='{}-R={}'.format(i, r),
                )
                cur_step['args'][1][i * n_params:(i + 1) * n_params] = [True] * n_params
                cur_step['args'][1][len(traces) + i] = True
                steps.append(cur_step)

            slider = [dict(
                active=1,
                currentvalue={"prefix": "Traj "},
                steps=steps
            )]

            fig = tools.make_subplots(rows=2, cols=1)
            for trace in traces:
                fig.append_trace(trace, row=1, col=1)
            for trace in hm_traces:
                trace.showscale = False
                fig.append_trace(trace, row=2, col=1)

            fig['layout'].update(sliders=slider, title='Trajectories')
        return go.Figure(fig)


def _get_dynamics_traces(param_names, seq_probas):
    data = []
    for i, traj in enumerate(seq_probas):
        traj = np.array(traj)
        for j, (param_p, name) in enumerate(zip(np.split(traj, traj.shape[1], 1), param_names)):
            d = dict(
                visible=i == 1,
                mode='lines',
                name=name,
                x=np.arange(0, param_p.shape[0]),
                y=param_p.squeeze())
            data.append(d)
    return data


def _get_heatmap_traces(data, names):
    plot_data = []
    for i, traj_data in enumerate(data):
        traj_data = np.array(traj_data)
        plot_data.append(go.Heatmap(
            visible=i == 1,
            z=traj_data.transpose(),
            x=list(range(traj_data.shape[0])),
            y=names,
            colorscale='Viridis',
        ))
    return plot_data


def paretize_exp(data, x_name, crit_name, value_name=None):
    if value_name is None:
        value_name = crit_name

    final_x = []
    final_crit = []
    final_vals = []
    final_origins = []
    cur_best_crit = None
    cur_best_x = None
    for x, crit, val, orig in sorted(zip(data[x_name], data[crit_name], data[value_name], data['_orig_'])):
        if len(final_x) == 0 or crit > cur_best_crit:
            cur_best_crit = crit
            if x == cur_best_x:
                final_crit[-1] = crit
                final_vals[-1] = val
                final_origins[-1] = orig
            else:
                final_x.append(x)
                final_crit.append(crit)
                final_vals.append(val)
                final_origins.append(orig)
            cur_best_x = x
    return {x_name: final_x,
            crit_name: final_crit,
            value_name: final_vals,
            '_orig_': final_origins}