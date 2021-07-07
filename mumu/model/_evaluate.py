# coding: utf8
# =======================================================
# Project: mumu
# File: model/_evaluate.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021-01-26 00:01:00
# Description:
# =======================================================
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics import roc_curve, auc


def plot_ks_auc(fig=None, target=None, predicted=None, save_image_path=None, display=True):
    """Display KS and auc

    :param fig:
    :param target:
    :param predicted:
    :param save_image_path:
    :param display:
    :return:
    """
    fpr, tpr, thresholds = roc_curve(y_true=target, y_score=predicted)
    auc_ = auc(fpr, tpr)
    ks_ = max(tpr - fpr)

    if not display:
        return round(ks_, 3), round(auc_, 3)

    max_idx = np.nonzero(np.ravel(tpr - fpr == ks_))
    target_rate = 1.0 * sum(target) / len(target)
    cum_total = tpr * target_rate + fpr * (1 - target_rate)
    min_idx = np.nonzero(np.ravel(abs(cum_total - target_rate) == min(abs(cum_total - target_rate))))

    if len(min_idx) > 0:
        min_idx = min_idx[0]

    if fig:
        ax = fig.add_subplot(131)
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)

    ax.plot(fpr, tpr)
    ax.plot([0, 1], [0, 1], c="k", ls="--", lw=2)
    ax.set_title("KS=" + str(round(ks_, 2)) + " AUC=" + str(round(auc_, 3)), fontsize=20)
    ax.plot([fpr[max_idx], fpr[max_idx]], [fpr[max_idx], tpr[max_idx]], lw=4, c="r")
    ax.plot([fpr[min_idx]], [tpr[min_idx]], "k.", markersize=10)

    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_xlabel("False Positive", fontsize=20)
    ax.set_ylabel("True Positive", fontsize=20)

    if not fig and save_image_path:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        save_img_path = os.path.join(save_image_path, "ks_auc_", now, ".png")

        if os.path.exists(save_image_path):
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")
        else:
            os.mkdir(save_img_path)
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")


def plot_score_dist(fig=None, target=None, predicted=None, save_image_path=None):
    """

    :param fig:
    :param target:
    :param predicted:
    :param save_image_path:
    :param display:
    :return:
    """
    # Score distribution
    if fig:
        ax = fig.add_subplot(132)
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)

    ax.hist(predicted, bins=20)
    ax.axvline(x=np.mean(predicted), ls="--")
    ax.axhline(y=np.mean(target), ls="--", c="g")

    ax.set_title("N=" + str(len(target))
                 + " TR=" + str(round(np.mean(target), 3))
                 + " Pred=" + str(round(np.mean(predicted), 3)))
    ax.set_xlabel("Target Rate", fontsize=20)
    ax.set_xlabel("Count", fontsize=20)

    if not fig and save_image_path:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        save_img_path = os.path.join(save_image_path, "score_dist_", now, ".png")

        if os.path.exists(save_image_path):
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")
        else:
            os.mkdir(save_img_path)
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")


def plot_slopping(fig=None, target=None, predicted=None, bin_num=10, save_image_path=None):
    """

    :param fig:
    :param target:
    :param predicted:
    :param bin_num:
    :param save_image_path:
    :return:
    """
    if fig:
        ax = fig.add_subplot(133)
    else:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)

    bin_num = bin_num
    mean_predicted = np.zeros(bin_num)
    mean_target = np.zeros(bin_num)
    indices = np.argsort(predicted)
    bin_size = int(1.0 * len(predicted) / bin_num)

    for i in range(bin_num):
        start_idx = i * bin_size
        end_idx = min(len(predicted), (i + 1) * bin_size)
        mean_predicted[i] = np.mean(predicted[indices[start_idx:end_idx]])
        mean_target[i] = np.mean(target[indices[start_idx:end_idx]])

    ax.plot(mean_predicted, "b.--", label="Pred", markersize=5)
    ax.plot(mean_target, "r.-", label="Truth", markersize=5)
    ax.set_title("Slopping by {0} bins".format(bin_num))
    ax.set_xlabel("Percentile", fontsize=20)
    ax.set_ylabel("Percentile", fontsize=20)
    plt.legend(loc="lower right")

    if not fig and save_image_path:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        save_img_path = os.path.join(save_image_path, "sloping_", now, ".png")

        if os.path.exists(save_image_path):
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")
        else:
            os.mkdir(save_img_path)
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")


def plot_all(target=None, predicted=None, save_image_path=None):
    """

    :param target:
    :param predicted:
    :param save_image_path:
    :return:
    """
    fig = plt.figure(figsize=(20, 6))
    plot_ks_auc(fig=fig, target=target, predicted=predicted)
    plot_score_dist(fig=fig, target=target, predicted=predicted)
    plot_slopping(fig=fig, target=target, predicted=predicted)

    if save_image_path:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        save_img_path = os.path.join(save_image_path, "all_", now, ".png")

        if os.path.exists(save_image_path):
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")
        else:
            os.mkdir(save_img_path)
            fig.savefig(save_img_path, dpi=200, bbox_inches="tight")

    return fig
