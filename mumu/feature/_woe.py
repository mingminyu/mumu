# coding: utf-8
# ================================================
# Project: mumu
# File: feature/_woe.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/24 18:24
# Description:
# ================================================
import os
import string
import logging
import math
import xlsxwriter
import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from sklearn import tree
from matplotlib.font_manager import FontProperties
from ._contingency import chi2_contingency


def __woe_calc(bad=None, good=None, bad_freq=None, good_freq=None):
    """Calculate woe

    :param bad: int or float,
        count of samples(target=1) in single bin
    :param good: int or float
        count of samples(target=0) in single bin
    :param bad_freq: int or float
        count of samples(target=1) in all samples
    :param good_freq: int or float
        count of samples(target=0) in all samples
    :return:
    """
    target_rt = bad / float(bad_freq)
    non_target_rt = good / float(good_freq)

    if float(bad) != 0.0 and bad / float(bad + good) != 1.0:
        woe = math.log(float(target_rt / non_target_rt))
    elif target_rt == 0.0:
        woe = -99999999.0
    elif bad / float(bad + good) == 1.0:
        woe = 99999999.0
    else:
        woe = -99999999.0

    return woe


def __iv_calc(ds=None):
    """Calculate iv value of the variable

    :param ds: DataFrame
    :return: iv, float
    """
    bad_dist = ds['1'] / float(ds['1'].sum())
    good_dist = ds['0'] / float(ds['0'].sum())
    bad_dist = bad_dist.apply(lambda x: 0.0001 if x == 0 else x)
    ds['iv'] = (bad_dist - good_dist) * np.log(bad_dist / good_dist)
    iv = ds['iv'].sum()

    return iv


def __target_check(df_master=None, target="target"):
    """Check target is right, target column only includes 0 and 1 in theory.

    :param df_master: DataFrame
    :param target: str
    :return:
    """
    # 检查target是否只有0和1两个取值
    if set(df_master[target].unique()) != {0, 1}:
        raise ValueError('Target are not only 0 and 1!')


def init_binning(df_master=None, var_name=None, target=None, max_bin_num=200, missing=False, cut_points=None):
    """Cut bins for numerical variables(`var_name`) and describe distribution of target in each bin.

    :param df_master: DataFrame
    :param var_name: str
    :param target: str
    :param max_bin_num: int, default 200,
        max num of bins cut
    :param missing: bool, default False
        whether if the variable has missing value.
    :param cut_points: list, 指定的切分点，若不指定则根据分位点分bin
        specified cut points, if not, then cut bins according to cut points.
    :return: ds: DataFrame,
        statistical information for bins cut of the variable.
    """
    df_tmp = df_master[[var_name, target]].copy()

    # Initialization cut points
    if cut_points is not None:
        if len(cut_points) == 0:
            raise ValueError('wrong cut points: {0}'.format(var_name))

        if np.max(df_tmp[var_name]) >= cut_points[-1]:
            # last value of bins is inf
            cut_points[-1] = np.inf

        if np.min(df_tmp[var_name]) < cut_points[0]:
            # # last value of bins is minimum
            cut_points[0] = np.min(df_tmp[var_name])  # bins第一个值改为min value, 防止忘记填最小值

    # If #(unique value) < max_bin_num, then each value will be a bin.
    elif len(df_tmp[var_name].unique()) < max_bin_num:
        cut_points = np.sort(df_tmp[var_name].unique())
        cut_points = np.append(cut_points, np.inf)

    # If #(unique value) >= max_bin_num, then cut `max_bin_num` bins according to cut points.
    else:
        pct = np.arange(max_bin_num + 1) / max_bin_num
        # calculate cut points and drop duplicates.
        cut_points = df_tmp[var_name].quantile(pct, interpolation='higher').unique()  # 计算分位点并去重
        cut_points[-1] = np.inf

    # when missing is true, put `-1.0` into a single bin
    if missing:
        if cut_points[0] == -1.0:
            tmp_ary1 = np.asarray([-1.0, 0.0])
            tmp_ary2 = np.asarray(cut_points[2:])
            cut_points = np.concatenate((tmp_ary1, tmp_ary2), axis=0)
        else:
            logging.warning('Expect variable has missing value but actually no missing')

    # cut bins according to cut points and calculate distribution of target in each bin.
    # 按切分点分bin，并计算每个bin中target的分布
    df_tmp[var_name + '_bin'] = np.digitize(df_tmp[var_name], bins=cut_points, right=False)
    ds = df_tmp.groupby(var_name + '_bin')[target].value_counts().unstack().fillna(value=0)
    ds['total'] = ds[0] + ds[1]
    ds['bin'] = [[cut_points[i - 1], cut_points[i]] for i in list(ds.index)]
    ds['bin_lb'] = [cut_points[i - 1] for i in list(ds.index)]
    ds = ds.sort_values(by='bin_lb', axis=0, ascending=True).reset_index(drop=True)  # 根据bin的下界进行排序
    ds.columns = ['0', '1', 'total', 'bin', 'bin_lb']

    return ds


def __value_match(map_dict=None, key_list=None):
    """Return corresponding key of the value according to `map_dict`
    example: [1,3,4,5] → ['本科','大专','高中','研究生']

    :param map_dict: dict
    :param key_list: list
    :return: list,
    """
    result = []

    for key in key_list:
        if key in map_dict:
            result.append(map_dict[key])
        else:
            result.append('base')

    return result


def __mergebin(ds=None, idx_list=None, idx=None, var_type=None):
    """Merge adjacent bins, and calculate statistical information of the merged bin and chi value

    :param ds: DataFrame
    :param idx_list: list
    :param idx: int
        index of bins in list will be merged
    :param var_type: str, options ['numerical', 'categorical']
        type of the variable.
    :return: ds: DataFrame
    """
    # merge two bins, and recalculate distribution of target.
    ds.at[idx_list[idx], ['0', '1']] = ds.loc[idx_list[idx], ['0', '1']] + ds.loc[idx_list[idx + 1], ['0', '1']]
    ds.at[idx_list[idx], 'total'] = ds.loc[idx_list[idx], 'total'] + ds.loc[idx_list[idx + 1], 'total']

    # recalculate range of the merged bin
    if var_type == 'numerical':
        ds.at[idx_list[idx], 'bin'] = [ds.loc[idx_list[idx], 'bin'][0], ds.loc[idx_list[idx + 1], 'bin'][1]]
    elif var_type == 'categorical':
        ds.at[idx_list[idx], 'bin'] = ds.loc[idx_list[idx:idx + 2], 'bin'].sum()

    # drop original bin after merged
    ds = ds.drop(idx_list[idx + 1], axis=0)
    # drop the index of original bins after merged
    idx_list.pop(idx + 1)

    # recalculate chi values of the merged bin, previous bin and later bin
    # if the merged bin is not first, then don't need to calculate the chi value of the previous bin
    if idx != 0:
        ds.at[idx_list[idx - 1], 'chisq'] = chi2_contingency(ds.loc[idx_list[(idx - 1):(idx + 1)], ['0', '1']])[0]

    # if the merged bin is not last, then don't need to calculate the chi value of the later bin
    if idx < ds.shape[0] - 1:
        ds.at[idx_list[idx], 'chisq'] = chi2_contingency(ds.loc[idx_list[idx:idx + 2], ['0', '1']])[0]
    else:
        ds.at[idx_list[idx], 'chisq'] = 9999999.0

    return ds


def generate_reference(ds=None, var_name=None, var_type=None):
    """generate reference table of woe of the variable.

    :param ds: DataFrame
    :param var_name: str
    :param var_type: str, options ['numerical', 'categorical']
    :return: DataFrame, reference table
    """
    # calculate woe and iv value for each bin
    good_freq = ds['0'].sum()
    bad_freq = ds['1'].sum()
    ds['woe_value'] = ds.apply(lambda x: __woe_calc(x['1'], x['0'], bad_freq, good_freq), axis=1)
    iv = __iv_calc(ds)

    # generate reference table
    df_ref_table = pd.DataFrame(columns=['Var_Name', 'Var_Type', 'Bin_No', 'Var_Value', 'Ref_Value',
                                         'Count_0', 'Count_1', 'Total', 'Target_Rate', 'Proportion', 'IV'])
    df_ref_table['Bin_No'] = range(1, ds.shape[0] + 1)  # Bin的编号，从1开始
    df_ref_table['Var_Value'] = ds['bin'].astype(str)  # 将list转成字符串
    df_ref_table['Ref_Value'] = ds['woe_value']
    df_ref_table['Count_0'] = ds['0']
    df_ref_table['Count_1'] = ds['1']
    df_ref_table['Total'] = ds['total']
    df_ref_table['Target_Rate'] = 1.0 * df_ref_table['Count_1'] / df_ref_table['Total']
    df_ref_table['Proportion'] = 1.0 * df_ref_table['Total'] / ds['total'].sum()
    df_ref_table['IV'] = iv
    df_ref_table['Var_Name'] = var_name
    df_ref_table['Var_Type'] = var_type

    return df_ref_table


def __get_list_str(x):
    """Get value of the categorical variable, and put 3 value in one line

    :param x: str
    :return: list
    """
    str_list = x.split('\001')
    s = ''
    for i in range(len(str_list)):
        s += str_list[i] + ','
        if (i + 1) % 3 == 0 and i + 1 != len(str_list):
            s += '\n'

    return s[:-1]


def plot_reference(df_ref=None, save_path=None, figsize=(10, 4)):
    """Woe plotting according to  reference table

    :param df_ref: DataFrame
    :param save_path: str, the path of image saved
    :param figsize: tuple, size of the figure, default  (10, 4)
    :return:
    """
    x = np.arange(df_ref.shape[0])
    y = df_ref['Ref_Value'].values
    z = df_ref['Target_Rate'].values
    var_name = df_ref['Var_Name'].iloc[0]
    iv = round(df_ref['IV'].iloc[0], 5)

    plt.figure(figsize=figsize, dpi=200)
    plt.bar(x, df_ref['Proportion'], color='royalblue', label='0', align='center')
    plt.bar(x, df_ref['Proportion'] * df_ref['Target_Rate'], color='firebrick', label='1', align='center')

    # draw label of x axis
    if df_ref['Var_Type'].iloc[0] == 'numerical':
        xticks_list = df_ref['Var_Value'].values
        xticks_list = [tuple([float(j) for j in i.strip('([] ').split(',')]) for i in xticks_list]
        xticks_list = [[round(i[0], 4), round(i[1], 4)] for i in xticks_list]
        plt.xticks(x, xticks_list)

    package_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    font_path = os.path.join(package_path, "resources", "fonts", "simsun.ttc")

    # noinspection PyBroadException
    try:
        zh_font = FontProperties(fname=font_path)
    except Exception:
        zh_font = FontProperties()

    if df_ref['Var_Type'].iloc[0] == 'categorical':
        xticks_list = df_ref['Var_Value'].apply(__get_list_str).tolist()
        plt.xticks(x, xticks_list, fontproperties=zh_font)

    plt.ylabel('proportion')
    plt.legend(loc=1, fontsize=9)
    ax2 = plt.twinx()
    plt.plot(x, y, '.-k', lw=2, markersize=8)

    for i, j, k in zip(x, y, z):
        ax2.annotate('%.2f(%.2f%%)' % (j, k * 100), xy=(i, j), va='center', ha='center',
                     bbox={'boxstyle': 'round', 'fc': 'w'})

    plt.ylabel('Woe value(Target rate)')
    plt.title('{0}: IV={1}'.format(var_name, iv), fontproperties=zh_font, fontsize=15)

    # save image
    if save_path is not None:
        if save_path.endswith('.png') or save_path.endswith('.jpg'):
            plt.savefig(save_path, bbox_inches='tight')
        elif os.path.isdir(save_path):
            plt.savefig(os.path.join(save_path, '{0}.png'.format(var_name)), bbox_inches='tight')
        else:
            raise ValueError('No such file or directory: {0}'.format(save_path))

    plt.show()
    plt.close()


def numwoe_autobinning(df_master=None, var_name=None, target='target', max_bins=6,
                       min_prop_in_bin=0.05, missing=True, max_bin_init=200,
                       method='chisq', to_plot=True, save_path=None):
    """Cut bins for numerical variable automatically, and calculate woe, iv value

    :param df_master: DataFrame
    :param var_name:
    :param target:
    :param max_bins: int, default 6
    :param min_prop_in_bin: float, default 0.05
        minimum sample ratio in each bin
    :param missing: bool, default True
        if missing is true, only support that cast `-1.0` into missing value now
    :param max_bin_init: int, default 200
        max num of bin when initialization cut, determined by the size of samples and unique value
    :param method: str, option ['chisq', 'entropy']
        methods of cut bins
    :param to_plot: bool, default True
        whether to plot reference table
    :param save_path: str, the path of image saved
    :return: df_ref_table: DataFrame, woe reference table
    """
    # calculate size of samples for each bin
    min_samples_in_bin = int(df_master.shape[0] * min_prop_in_bin)

    if method == 'chisq':
        ds = init_binning(df_master, var_name=var_name, target=target, max_bin_num=max_bin_init, missing=missing)
        # calculate chi value of adjacent bins
        chisq = []

        for i in range(ds.shape[0] - 1):
            chisq.append(chi2_contingency(ds.iloc[[i, i + 1], [0, 1]])[0])

        chisq.append(9999999.0)
        ds['chisq'] = chisq

        # cut missing value into a single bin
        if missing:
            if ds[ds['bin_lb'] == -1.0].shape[0] > 0:
                ds_miss = ds[ds['bin_lb'] == -1.0].copy()
                ds = ds[ds['bin_lb'] != -1.0]
            else:
                ds_miss = pd.DataFrame()

        # merge two bins with small chi value
        ds_idx_list = list(ds.index)

        while (ds.shape[0] > max_bins) | (ds['chisq'].min() <= scipy.stats.chi2.ppf(0.95, 1)):
            # 找到卡方值最小的bin的index在index list中的位置
            k = ds_idx_list.index(ds['chisq'].idxmin())
            ds = __mergebin(ds=ds, idx_list=ds_idx_list, idx=k, var_type='numerical')

        # limit size of samples in each bin
        while (ds['total'].min() < min_samples_in_bin) & (ds.shape[0] > 2):
            # find the bin with minimum size of samples
            k = ds_idx_list.index(ds['total'].idxmin())

            # if chi value of previous bin < later bin, choose previous bin to merge
            if (k == len(ds_idx_list) - 1) | (
                    ds.loc[ds_idx_list[k], 'chisq'] > ds.loc[ds_idx_list[k - 1], 'chisq']):
                k -= 1
            ds = __mergebin(ds, idx_list=ds_idx_list, idx=k, var_type='numerical')

    elif method == 'entropy':
        max_depth = int(math.log(max_bins, 2))

        if missing:
            df_miss = df_master.loc[df_master[var_name] == -1.0, [var_name, target]].reset_index(drop=True)
            df_no_miss = df_master.loc[df_master[var_name] != -1.0, [var_name, target]].reset_index(drop=True)

            if df_miss.shape[0] > 0:
                ds_miss = init_binning(df_master=df_miss, var_name=var_name, target=target,
                                            cut_points=[-1.0, -0.5], missing=False)
            else:
                ds_miss = pd.DataFrame()

            min_value = -0.5
        else:
            df_no_miss = df_master
            min_value = df_no_miss[var_name].min()

        clf = tree.DecisionTreeClassifier(criterion='entropy', max_depth=max_depth,
                                          min_samples_leaf=min_samples_in_bin)
        clf.fit(df_no_miss[var_name].values.reshape(-1, 1), df_no_miss[target])
        cut_points = np.sort(clf.tree_.threshold[clf.tree_.threshold != -2.0])
        cut_points = np.append([min_value], cut_points)
        cut_points = np.append(cut_points, df_no_miss[var_name].max())
        ds = init_binning(df_no_miss, var_name=var_name, target=target, cut_points=cut_points, missing=False)

    else:
        raise ValueError('wrong method, only choose "chisq" or "entropy"!')

    # generate final reference table
    if missing:
        ds = pd.concat([ds_miss, ds])

    ds = ds.reset_index(drop=True)
    df_ref_table = generate_reference(ds=ds, var_name=var_name, var_type='numerical')

    # plotting
    if to_plot:
        plot_reference(df_ref_table, save_path=save_path)

    return df_ref_table


def numwoe_aptbinning(df_master=None, var_name=None, target=None, bins=None, to_plot=True, save_path=None):
    """Cut bins of numerical variables according to specified cut points, and calculate woe, iv value

    :param df_master: DataFrame
    :param var_name: str, variable name
    :param target: str, target name
    :param bins: list,
        specified cut points, eg. [0.0, 1.0, 3.0, 10.0]
    :param to_plot: bool, default True
        whether to plot reference table
    :param save_path: str, the path of image saved
    :return: df_ref_table: DataFrame, woe reference table
    """
    ds = init_binning(df_master, var_name=var_name, target=target, cut_points=bins, missing=False)
    df_ref_table = generate_reference(ds, var_name=var_name, var_type='numerical')

    if to_plot:
        plot_reference(df_ref_table, save_path=save_path)

    return df_ref_table


def catwoe_autobinning(df_master=None, var_name=None, target=None,
                       max_bins=6, min_prop_in_bin=0.05, min_samples_init=1,
                       missing_value=None, to_plot=True, save_path=None):
    """Cut bins of categorical variables according to specified cut points, and calculate woe, iv value

    :param: df_master: DataFrame
    :param: var_name: str, variable name
    :param: target: str, target name
    :param: max_bins: int
    :param: min_samples_init: int, default 1
        minimum size of cut bins on initialization, merge bins with small size of samples
    :param: min_prop_in_bin: float, default None
        minimum sample ratio in each bin
    :param: missing_value: str, default None
        if missing is true, will put the value into a single bin
    :param: to_plot: bool, default True
        whether to plot reference table
    :param: save_path: str, default None
        str, the path of image saved
    :return: df_ref_table: DataFrame, woe reference table
    """
    min_samples_in_bin = int(df_master.shape[0] * min_prop_in_bin)
    ds = pd.crosstab(df_master[var_name], df_master[target]).fillna(value=0).reset_index(drop=False)
    ds['total'] = ds[1] + ds[0]
    # index for each bin
    ds['bin'] = [[i] for i in ds.index]
    ds.columns = ['value', '0', '1', 'total', 'bin']
    # generate a mapping dict of index and real value
    map_dict = dict(zip(ds.index, ds['value']))

    # whether to put missing value into a single bin
    if missing_value is not None:
        ds_miss = ds[ds['value'] == missing_value].copy()
        ds = ds[ds['value'] != missing_value]

    # sort the bin order by size of samples in each bin
    ds = ds.sort_values(by=['total'], ascending=True)

    # merge bins with small size of samples
    idx_small_bin = list(ds[ds['total'] < min_samples_init].index)

    if len(idx_small_bin) >= 2:
        ds.at[idx_small_bin[0], ['0', '1']] = ds.loc[idx_small_bin, ['0', '1']].sum()
        ds.at[idx_small_bin[0], 'total'] = ds.loc[idx_small_bin, 'total'].sum()
        ds.at[idx_small_bin[0], 'bin'] = idx_small_bin
        ds = ds.drop(idx_small_bin[1:], axis=0)

    # calculate target rate for each bin
    ds['target_rt'] = ds['1'] / (ds['0'] + ds['1'])
    # sort order by target rate of each bin
    ds = ds.sort_values(by='target_rt', ascending=True)

    # calculate chi value of two adjacent bins
    chisq = []

    for i in range(ds.shape[0] - 1):
        # noinspection PyBroadException
        try:
            chisq.append(chi2_contingency(ds.iloc[[i, i + 1], [1, 2]])[0])
        except Exception:
            chisq.append(chi2_contingency(ds.iloc[[i, i + 1], [0, 1]])[0])

    chisq.append(9999999.0)
    ds['chisq'] = chisq

    # loop of merging two adjacent bins, recalculate chi value of previous and later bin
    ds_idx_list = list(ds.index)

    while (ds.shape[0] > max_bins) | (ds.chisq.min() <= scipy.stats.chi2.ppf(0.95, 1)):
        k = ds_idx_list.index(ds['chisq'].idxmin())
        ds = __mergebin(ds, idx_list=ds_idx_list, idx=k, var_type='categorical')

    # limit size of samples for each bin
    while (ds['total'].min() < min_samples_in_bin) & (ds.shape[0] > 2):
        # find the bin with minimum size of samples
        k = ds_idx_list.index(ds['total'].idxmin())

        if (k == len(ds_idx_list) - 1) | (ds.loc[ds_idx_list[k], 'chisq'] > ds.loc[ds_idx_list[k - 1], 'chisq']):
            k -= 1

        ds = __mergebin(ds, idx_list=ds_idx_list, idx=k, var_type='categorical')

    # generate reference table
    if missing_value is not None:
        ds = pd.concat([ds_miss, ds])

    ds = ds.reset_index(drop=True)
    ds['bin'] = ds['bin'].apply(lambda x: __value_match(map_dict, x))  # 将索引还原成变量原本的取值
    ds['bin'] = ds['bin'].apply(lambda x: '\001'.join(x))  # 用特殊符号'\001'拼接value，防止出现value中有标点符号
    df_ref_table = generate_reference(ds, var_name=var_name, var_type='categorical')

    # plotting
    if to_plot:
        plot_reference(df_ref_table, save_path=save_path)

    return df_ref_table


def catwoe_aptbinning(df_master=None, var_name=None, target=None, bins=None, to_plot=True, save_path=None):
    """Cut bins of categorical variables according to specified cut points, and calculate woe, iv value

    :param: df_master: DataFrame
    :param: var_name: str
    :param: target: str
    :param: bins: list
        rules of grouping, eg. [['初中', '高中'], ['大专', '本科', '硕士研究生'], ['博士研究生']]
    :param: to_plot: bool, default True
        whether to plot reference table
    :param: save_path: str, the path of image saved
    :return: df_ref_table: DataFrame, woe reference table
    """
    unique_values = set(sum(bins, []))

    if len(unique_values) != len(sum(bins, [])):
        raise ValueError('Value is repetitive, please check bins is correct')

    ds = pd.crosstab(df_master[var_name], df_master[target]).fillna(value=0).reset_index(drop=False)
    ds['total'] = ds[1] + ds[0]
    ds.columns = ['bin', '0', '1', 'total']

    # cut bins according to the specified method
    for bin in bins:
        idx_list = []

        for value in bin:
            idx_list.append(int(ds[ds['bin'] == value].index.values))
        ds.at[idx_list[0], ['0', '1']] = ds.loc[idx_list, ['0', '1']].sum()
        ds.at[idx_list[0], 'total'] = ds.loc[idx_list, 'total'].sum()
        ds.at[idx_list[0], 'bin'] = bin
        ds = ds.drop(idx_list[1:], axis=0)

    ds = ds.reset_index(drop=True)

    # generate reference table
    ds['bin'] = ds['bin'].apply(lambda x: '\001'.join(x))  # 用特殊符号'\001'拼接value，防止出现value中有标点符号
    df_ref_table = generate_reference(ds, var_name=var_name, var_type='categorical')

    # plotting
    if to_plot:
        plot_reference(df_ref_table, save_path=save_path)

    return df_ref_table


def __str_convert(x):
    """Cast types of variable into str

    :param x:
    :return:
    """
    if type(x) in [int, float, np.float64]:
        return str(int(x))
    elif type(x) is str:
        return x
    else:
        return x


def __restore_list(s=None, value_type=None):
    """Restore list with str format into original list
        eg:'[1, 2]' → [1,2]

    :param s: str, need to restored
    :param value_type: str, options ['numerical', 'categorical']
        type of value
    :return:
    """
    if value_type == 'numerical':
        return [np.float(i.strip('[] ')) for i in s.split(',')]
    elif value_type == 'categorical':
        return s.split('\001')
    else:
        raise ValueError('Wrong value type!')


def __cvlookup(value=None, map_dict=None):
    """Find corresponding woe value of the variable

    :param value: str,
    :param map_dict: dict, mapping dict
    :return: woe_value: float, woe value
    """
    if value in map_dict.keys():
        woe_value = map_dict[value]
    else:
        woe_value = 0.0

    return woe_value


def numwoe_apply(df_master=None, ref_table=None, var_name=None):
    """Replace original value with woe value for single numerical variable
    if `bin_lb[i] ≤ X ＜ bin_ub[i]` is meet, replace X with `ref_value[i]`

    :param: df_master: DataFrame
    :param: ref_table: DataFrame, reference table
    :param: var_name: str, variable name
    """
    interval = ref_table['Var_Value'].apply(lambda x: __restore_list(x, 'numerical')).values
    # minimum
    bin_lb = np.asarray([i[0] for i in interval]).reshape((1, -1))  # bin的下界
    bin_lb[0][0] = -np.Infinity  # 把第一个bin的下界替换成负无穷
    base_woe = ref_table['Ref_Value'].iloc[0]  # 取第一个值作为baseline
    x = (df_master[var_name].values.reshape((-1, 1)) >= bin_lb) * 1.0
    w = ref_table['Ref_Value'].diff(periods=1).fillna(base_woe).values  # 进行1阶差分
    df_master['nwoe_' + var_name] = np.dot(x, w)


def catwoe_apply(df_master=None, ref_table=None, var_name=None):
    """Replace original value with woe value for single categorical variable

    :param: df_master: DataFrame
    :param: ref_table: DataFrame, reference table
    :param: var_name: str, variable name
    """
    var_value = ref_table['Var_Value'].apply(lambda x: __restore_list(x, 'categorical')).values
    df_master[var_name] = df_master[var_name].apply(lambda x: __str_convert(x))

    # build a dict of values
    value_list = []
    ref_value_list = []

    for i, lst in enumerate(var_value):
        value_list += lst
        ref_value_list += [ref_table['Ref_Value'].iloc[i]] * len(lst)

    value_dict = dict(zip(value_list, ref_value_list))
    df_master['cwoe_' + var_name] = df_master[var_name].apply(lambda x: __cvlookup(x, value_dict))


def woeref_old2new(ref_woe=None):
    """Replace old woe reference table with the new

    :param ref_woe: DataFrame
        old woe reference table
    :return: ref_new_woe: DataFrame
        new woe reference table
    """
    ref_woe_copy = ref_woe.copy()
    ref_woe_copy = ref_woe_copy.loc[ref_woe_copy['Var_Value'] != 'base']
    ref_woe_copy['Total'] = ref_woe_copy['Count_0'] + ref_woe_copy['Count_1']
    ref_woe_copy = ref_woe_copy.rename(columns={'Ratio_1': 'Target_Rate', 'Ratio_All': 'Proportion'})
    ref_woe_copy['Var_Value'] = ref_woe_copy['Var_Value'].apply(lambda x: str(x).split('_'))

    ref_new_woe = ref_woe_copy.groupby(['Var_Name', 'Var_Type', 'IV', 'Ref_Value'], as_index=False, ) \
        .agg({'Var_Value': 'sum', 'Count_0': 'sum', 'Count_1': 'sum', 'Total': 'sum', 'Proportion': 'sum', })

    ref_new_woe['Target_Rate'] = ref_new_woe['Count_1'] / ref_new_woe['Total']

    ref_new_woe['Var_Value'].loc[ref_new_woe['Var_Type'] == 'categorical'] = ref_new_woe['Var_Value'].loc[
        ref_new_woe['Var_Type'] == 'categorical'].apply(lambda x: "\001".join(x))

    ref_new_woe['Bin_No'] = ref_new_woe[['Var_Name', 'Ref_Value']].groupby(['Var_Name']).rank(method='dense',
                                                                                              ascending=True)
    ref_new_woe['Var_Value'] = ref_new_woe['Var_Value'].apply(lambda x: str(x).replace("'", ""))

    return ref_new_woe


def iv_extract(woe_ref=None, save_path=None):
    """Extract iv value according to woe reference table, order by desc

    :param woe_ref: DataFrame
        woe reference table
    :param save_path: str, default None
        the path of csv file saved
    :return: df_iv: DataFrame
    """
    iv = []

    for var in woe_ref.Var_Name.unique():
        iv.append([var, woe_ref['IV'][woe_ref['Var_Name'] == var].iloc[0]])

    df_iv = pd.DataFrame(iv, columns=['Var_Name', 'IV'])
    df_iv = df_iv.sort_values(by='IV', ascending=False)

    if not save_path:
        df_iv.to_csv(save_path, index=False)

    return df_iv


def replace_var_woe_ref(woe_ref_all=None, woe_ref_var=None):
    """Replace the specified reference table of variable in all with the new

    :param: woe_ref_all: DataFrame
        reference tables of all variables
    :param: woe_ref_var: DataFrame
        reference table of the specified variable
    :return: woe_ref_new: DataFrame
        new reference table
    """
    replace_var = woe_ref_var['Var_Name'].unique()[0]
    woe_ref_new = woe_ref_all.loc[woe_ref_all['Var_Name'] != replace_var, :].copy()
    woe_ref_new = pd.concat([woe_ref_new, woe_ref_var], axis=0, ignore_index=True)

    return woe_ref_new


def save_pictures_in_excel(file_name=None, img_loc=None, var_list=None, columns_num=1, img_rows=20, sheet_name='images'):
    """Save the image in excel

    :param file_name: str, default xlsx format
    :param img_loc: str, path of the image
    :param var_list: list, default None
        variables will saved in excel, if None, will embed all images in excel
    :param columns_num: int, default 1
        columns for the image
    :param img_rows: int, default 20
        rows for the image
    :param sheet_name：str, default 'images'
        excel sheet name
    :return:
    """

    if not img_loc.endswith('/'):
        img_loc = img_loc + '/'

    book = xlsxwriter.Workbook(file_name)
    sheet = book.add_worksheet(sheet_name)

    # generate a list of images
    if var_list is not None:
        img_list = ['{0}.png'.format(var) for var in var_list]
    else:
        img_list = [img for img in os.listdir(img_loc) if img.split(".")[-1] in ['jpg', 'png', 'bmp']]

    img_list.sort(reverse=True)

    # list of A - Z
    location_list = [i for i in string.ascii_uppercase]

    for i, img in zip(range(len(img_list)), img_list):
        location_x = location_list[(i % columns_num) * 2 + 1]

        if i < columns_num:
            # set 90px of width
            sheet.set_column('{0}:{0}'.format(location_x), 90)

        location_y = img_rows * (i // columns_num) + 1
        sheet.write('{0}{1}'.format(location_x, location_y), img)
        sheet.insert_image('{0}{1}'.format(location_x, location_y + 1), img_loc + img,
                           options={'x_scale': 0.8, 'y_scale': 0.88})
    book.close()
